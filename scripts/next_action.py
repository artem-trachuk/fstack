#!/usr/bin/env python3
"""Pick the next fstack action from a state snapshot, and check an event before it is recorded.

The orchestrator reads the feature and its chunks from Notion, writes them as one JSON
snapshot, and passes it on stdin. This script never reads or writes Notion, and it never
changes the snapshot. It only answers two questions:

    next                 Which rule in state/transitions.yaml matches first, and what to do.
    record EVENT [...]   Whether EVENT is legal from the current statuses, and the new statuses.

The rule order, actions, details, and event statuses come from state/transitions.yaml.
Each rule's `when` text is implemented once in CONDITIONS below, keyed by the rule id.
A rule in the table with no condition here is an error, so the two cannot drift apart.

Snapshot shape (every key is optional unless noted):

    {
      "session": "id of this orchestrator session, compared with lease.owner",
      "now": "2026-11-06T12:00:00Z",
      "feature": {                     # required. Field names are feature_fields in the table.
        "state_version": 1,
        "feature_status": "building",  # required
        "waiting_on": "",
        "lease": {"owner": "", "expires_at": ""},
        "repos": ["web"],
        "base_shas": {"web": "abc123"},
        "release_order": [],
        "review_approval": ""
      },
      "chunks": [                      # field names are chunk_fields in the table
        {
          "id": "01-login",            # required
          "status": "planned",         # required
          "repo": "web", "depends_on": [], "branch": "", "attempt": 0,
          "attempts_since_decision": 0, "agent_id": "", "verifier_agent_id": "",
          "head_sha": "", "verified_sha": "", "accepted_sha": "",
          "needs_restack": false, "needs_reverify": false, "tiebreak_for_attempt": null,
          "observed": {                # facts the orchestrator looked up this turn
            "diff_attached": false,    # the diff page for this attempt exists
            "range_diff_recorded": false,
            "tiebreak_finished": false,  # the tie-break for this attempt finished or was skipped
            "pr_head_sha": "",         # the pull request head on the forge
            "pr_merged": false,        # the forge says the pull request is merged
            "ci": ""                   # "", pending, failing, passing, or none
          }
        }
      ],
      "verifications": [               # verification pages not yet applied
        {"chunk": "01-login", "attempt": 1, "head_sha": "def456", "applied": false}
      ],
      "observed": {
        "default_heads": {"web": "abc123"},  # current default-branch commit per location
        "single_chunk_plan": true,     # the work is one chunk per repo. The decision-policy default
        "tiebreak_same_model": false,  # the resolved tie-break model equals the verifier model
        "tiebreak_reserve_used": false
      },
      "config": {"max_failures_before_escalation": 2}
    }

Exit codes: 0 answered, 2 the snapshot or the event was refused (the reason is in the JSON
on stdout), 1 the table or this script is broken.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
TABLE_PATH = ROOT / "state" / "transitions.yaml"

FINISHED = {"verified", "accepted_by_human", "merged"}
READY_FOR_REVIEW = {"verified", "accepted_by_human"}
CI_VALUES = {"", "pending", "failing", "passing", "none"}
CI_NOT_READY = {"", "pending", "failing"}

CHUNK_OBSERVED = {"diff_attached", "range_diff_recorded", "tiebreak_finished", "pr_head_sha", "pr_merged", "ci"}
TOP_OBSERVED = {"default_heads", "single_chunk_plan", "tiebreak_same_model", "tiebreak_reserve_used"}
TOP_KEYS = {"session", "now", "feature", "chunks", "verifications", "observed", "config"}
VERIFICATION_KEYS = {"chunk", "attempt", "head_sha", "applied", "verdict"}
CONFIG_KEYS = {"max_failures_before_escalation"}
DEFAULT_MAX_FAILURES = 2

# Which skill the orchestrator follows for each rule. A slot is resolved through the
# workflow binding (configure-workflow). A skill is followed directly. None means stop.
RULE_TARGETS: dict[str, tuple[str, str] | None] = {
    "migrate": None,
    "lease": None,
    "stopped": None,
    "done": ("skill", "fstack-status"),
    "waiting": ("skill", "fstack-status"),
    "draft": ("skill", "collect-requirements"),
    "survey": ("slot", "survey"),
    "survey_skip": ("slot", "survey"),
    "survey_wait": ("slot", "survey"),
    "gap": ("slot", "gap_analysis"),
    "coverage_questions": ("skill", "fstack-status"),
    "coverage_gate": ("skill", "fstack-status"),
    "single_chunk": ("slot", "split"),
    "split": ("slot", "split"),
    "plan_gate": ("skill", "fstack-status"),
    "base_drift": ("skill", "pick-next-task"),
    "blocked": ("skill", "escalate"),
    "resume_implementer": ("slot", "implement"),
    "prepare_verify": ("skill", "build-context"),
    "launch_verifier": ("skill", "pick-next-task"),
    "apply_filed_verdict": ("skill", "pick-next-task"),
    "not_implemented": ("skill", "fstack-status"),
    "resume_verifier": ("skill", "pick-next-task"),
    "dispute_same_model": ("slot", "advise"),
    "dispute_budget": ("slot", "advise"),
    "dispute_tiebreak": ("slot", "advise"),
    "dispute_decide": ("skill", "pick-next-task"),
    "failure_cap": ("skill", "escalate"),
    "retry_failed": ("slot", "implement"),
    "changes": ("slot", "implement"),
    "restack": ("slot", "release"),
    "range_diff": ("slot", "release"),
    "implement_next": ("slot", "implement"),
    "stack_review": ("slot", "review"),
    "release_question": ("slot", "release"),
    "sha_mismatch": ("slot", "release"),
    "already_merged": ("slot", "release"),
    "merge_restack": ("slot", "release"),
    "merge_ci": ("slot", "release"),
    "merge_one": ("slot", "release"),
    "release_command": ("slot", "release"),
    "update_graph": ("slot", "update_graph"),
    "stuck": ("skill", "escalate"),
}


class Refused(Exception):
    """The snapshot or the event is not acceptable. Exit 2."""


def load_table(path: Path = TABLE_PATH) -> dict:
    try:
        import yaml
    except ImportError as error:  # pragma: no cover - depends on the machine
        raise SystemExit("next_action.py needs PyYAML: pip install pyyaml") from error
    return yaml.safe_load(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- snapshot


def parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        moment = datetime.fromisoformat(text)
    except ValueError as error:
        raise Refused(f"not an ISO time: {value!r}") from error
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment


def chunk_number(chunk_id: str) -> tuple[int, str]:
    match = re.match(r"^(\d+)-", chunk_id)
    return (int(match.group(1)) if match else 10**9, chunk_id)


class Snapshot:
    """A checked, read-only view of the JSON the orchestrator passed."""

    def __init__(self, data: Any, table: dict):
        if not isinstance(data, dict):
            raise Refused("the snapshot must be a JSON object")
        unknown = set(data) - TOP_KEYS
        if unknown:
            raise Refused(f"unknown snapshot keys: {sorted(unknown)}")
        feature = data.get("feature")
        if not isinstance(feature, dict):
            raise Refused("the snapshot needs a feature object")
        feature_fields = set(table.get("feature_fields") or [])
        unknown = set(feature) - feature_fields
        if unknown:
            raise Refused(f"unknown feature fields: {sorted(unknown)}")
        status = feature.get("feature_status")
        if status not in (table.get("feature_statuses") or []):
            raise Refused(f"unknown feature_status: {status!r}")
        self.feature = feature
        self.status: str = status

        chunk_fields = set(table.get("chunk_fields") or []) | {"observed"}
        chunk_statuses = set(table.get("chunk_statuses") or [])
        chunks = data.get("chunks") or []
        if not isinstance(chunks, list):
            raise Refused("chunks must be a list")
        seen = set()
        for chunk in chunks:
            if not isinstance(chunk, dict) or not chunk.get("id"):
                raise Refused("every chunk needs an id")
            if chunk["id"] in seen:
                raise Refused(f"duplicate chunk id {chunk['id']}")
            seen.add(chunk["id"])
            unknown = set(chunk) - chunk_fields
            if unknown:
                raise Refused(f"chunk {chunk['id']} has unknown fields: {sorted(unknown)}")
            if chunk.get("status") not in chunk_statuses:
                raise Refused(f"chunk {chunk['id']} has unknown status: {chunk.get('status')!r}")
            observed = chunk.get("observed") or {}
            unknown = set(observed) - CHUNK_OBSERVED
            if unknown:
                raise Refused(f"chunk {chunk['id']} has unknown observed keys: {sorted(unknown)}")
            if observed.get("ci", "") not in CI_VALUES:
                raise Refused(f"chunk {chunk['id']} ci must be one of {sorted(CI_VALUES)}")
        self.chunks: list[dict] = sorted(chunks, key=lambda chunk: chunk_number(chunk["id"]))
        self.by_id = {chunk["id"]: chunk for chunk in self.chunks}

        verifications = data.get("verifications") or []
        for item in verifications:
            if not isinstance(item, dict) or set(item) - VERIFICATION_KEYS:
                raise Refused(f"verification entries use only {sorted(VERIFICATION_KEYS)}")
        self.verifications: list[dict] = verifications

        observed = data.get("observed") or {}
        unknown = set(observed) - TOP_OBSERVED
        if unknown:
            raise Refused(f"unknown observed keys: {sorted(unknown)}")
        self.observed = observed

        config = data.get("config") or {}
        unknown = set(config) - CONFIG_KEYS
        if unknown:
            raise Refused(f"unknown config keys: {sorted(unknown)}")
        self.max_failures = int(config.get("max_failures_before_escalation", DEFAULT_MAX_FAILURES))

        self.session = str(data.get("session") or "")
        self.now = parse_time(data.get("now")) or datetime.now(timezone.utc)

    # Helpers that name the phrases the rules use.

    def seen(self, chunk: dict, key: str, default: Any = None) -> Any:
        return (chunk.get("observed") or {}).get(key, default)

    def earliest_unfinished(self) -> dict | None:
        return next((chunk for chunk in self.chunks if chunk["status"] not in FINISHED), None)

    def release_sha(self, chunk: dict) -> str:
        if chunk["status"] == "verified":
            return str(chunk.get("verified_sha") or "")
        if chunk["status"] == "accepted_by_human":
            return str(chunk.get("accepted_sha") or "")
        return ""

    def pending_range_diff(self, chunk: dict) -> bool:
        return bool(chunk.get("needs_reverify")) and not self.seen(chunk, "range_diff_recorded", False)

    def release_queue(self) -> list[dict]:
        """Unmerged chunks in release order: by release_order location, then by stack order."""
        order = list(self.feature.get("release_order") or []) or list(self.feature.get("repos") or [])
        rank = {name: index for index, name in enumerate(order)}
        unmerged = [chunk for chunk in self.chunks if chunk["status"] != "merged"]
        return sorted(unmerged, key=lambda chunk: (rank.get(chunk.get("repo"), len(rank)), chunk_number(chunk["id"])))

    def lease_held_by_other(self) -> bool:
        lease = self.feature.get("lease") or {}
        if not isinstance(lease, dict):
            raise Refused("lease must be an object with owner and expires_at")
        owner = str(lease.get("owner") or "")
        expires = parse_time(lease.get("expires_at"))
        return bool(owner) and owner != self.session and expires is not None and expires > self.now


# ---------------------------------------------------------------- rule conditions
#
# Each condition returns None when the rule does not match, or a dict of context when it
# does. The context names the chunk or location the action applies to.


def on(chunk: dict | None) -> dict[str, Any] | None:
    return {"chunk": chunk["id"]} if chunk else None


def status_is(*statuses: str) -> Callable[[Snapshot], dict | None]:
    return lambda s: {} if s.status in statuses else None


def earliest_is(status: str, extra: Callable[[Snapshot, dict], bool] = lambda s, c: True) -> Callable[[Snapshot], dict | None]:
    def check(s: Snapshot) -> dict | None:
        chunk = s.earliest_unfinished()
        if chunk and chunk["status"] == status and extra(s, chunk):
            return on(chunk)
        return None

    return check


def first_chunk(predicate: Callable[[Snapshot, dict], bool]) -> Callable[[Snapshot], dict | None]:
    def check(s: Snapshot) -> dict | None:
        return on(next((chunk for chunk in s.chunks if predicate(s, chunk)), None))

    return check


def merging(predicate: Callable[[Snapshot], dict | None]) -> Callable[[Snapshot], dict | None]:
    return lambda s: predicate(s) if s.status == "merging" else None


def base_drift(s: Snapshot) -> dict | None:
    if s.status not in ("building", "merging"):
        return None
    pinned = s.feature.get("base_shas") or {}
    for location, head in (s.observed.get("default_heads") or {}).items():
        if head and pinned.get(location) != head:
            return {"location": location}
    return None


def filed_verdict(s: Snapshot) -> dict | None:
    for chunk in s.chunks:
        if chunk["status"] not in ("in_review", "needs_verify"):
            continue
        for item in s.verifications:
            if (
                item.get("chunk") == chunk["id"]
                and not item.get("applied")
                and item.get("attempt") == chunk.get("attempt")
                and item.get("head_sha") == chunk.get("head_sha")
            ):
                return on(chunk)
    return None


def implement_next(s: Snapshot) -> dict | None:
    chunk = next((chunk for chunk in s.chunks if chunk["status"] == "planned"), None)
    if chunk is None:
        return None
    for dependency in chunk.get("depends_on") or []:
        parent = s.by_id.get(dependency)
        if parent is None or parent["status"] not in FINISHED:
            return None
    return on(chunk)


def stack_review(s: Snapshot) -> dict | None:
    if not s.chunks or s.feature.get("review_approval"):
        return None
    for chunk in s.chunks:
        if chunk["status"] not in READY_FOR_REVIEW or chunk.get("needs_restack") or chunk.get("needs_reverify"):
            return None
    return {}


def sha_mismatch(s: Snapshot) -> dict | None:
    for chunk in s.release_queue():
        head = s.seen(chunk, "pr_head_sha", "")
        if head and head != s.release_sha(chunk):
            return on(chunk)
    return None


def merge_restack(s: Snapshot) -> dict | None:
    for chunk in s.release_queue():
        parents = [s.by_id.get(dependency) for dependency in chunk.get("depends_on") or []]
        if any(parent and parent["status"] == "merged" for parent in parents):
            if chunk.get("needs_restack") or s.pending_range_diff(chunk):
                return on(chunk)
    return None


def merge_ci(s: Snapshot) -> dict | None:
    queue = s.release_queue()
    if queue and s.seen(queue[0], "ci", "") in CI_NOT_READY:
        return on(queue[0])
    return None


def merge_one(s: Snapshot) -> dict | None:
    queue = s.release_queue()
    if not queue:
        return None
    chunk = queue[0]
    sha = s.release_sha(chunk)
    ready = (
        bool(sha)
        and s.seen(chunk, "pr_head_sha", "") == sha
        and not chunk.get("needs_restack")
        and not s.pending_range_diff(chunk)
        and s.seen(chunk, "ci", "") not in CI_NOT_READY
    )
    return on(chunk) if ready else None


CONDITIONS: dict[str, Callable[[Snapshot], dict | None]] = {
    "migrate": lambda s: {} if str(s.feature.get("state_version", "")) != "1" else None,
    "lease": lambda s: {} if s.lease_held_by_other() else None,
    "stopped": status_is("stopped"),
    "done": status_is("done"),
    "waiting": lambda s: {} if s.feature.get("waiting_on") else None,
    "draft": status_is("requirements_draft"),
    "survey": lambda s: {} if s.status == "requirements_confirmed" and s.feature.get("repos") else None,
    "survey_skip": lambda s: {} if s.status == "requirements_confirmed" and not s.feature.get("repos") else None,
    "survey_wait": status_is("surveying"),
    "gap": status_is("surveyed"),
    "coverage_questions": status_is("questions_open"),
    "coverage_gate": status_is("awaiting_coverage_approval"),
    "single_chunk": lambda s: {}
    if s.status == "ready_to_plan" and not s.chunks and s.observed.get("single_chunk_plan", True)
    else None,
    "split": lambda s: {} if s.status == "ready_to_plan" and not s.chunks else None,
    "plan_gate": status_is("awaiting_plan_approval"),
    "base_drift": base_drift,
    # The table says "the earliest chunk in stack order". Read as the earliest unfinished
    # chunk, the same reading the other chunk rules use. A merged first chunk cannot be blocked.
    "blocked": earliest_is("blocked"),
    "resume_implementer": earliest_is("implementing", lambda s, c: bool(c.get("agent_id"))),
    "prepare_verify": earliest_is("needs_verify", lambda s, c: not s.seen(c, "diff_attached", False)),
    "launch_verifier": earliest_is(
        "needs_verify", lambda s, c: bool(s.seen(c, "diff_attached", False)) and not c.get("verifier_agent_id")
    ),
    "apply_filed_verdict": filed_verdict,
    "not_implemented": first_chunk(lambda s, c: c["status"] == "awaiting_verification_decision"),
    # "the chunk" in the rules below is the earliest unfinished chunk.
    "resume_verifier": earliest_is("in_review", lambda s, c: bool(c.get("verifier_agent_id"))),
    "dispute_same_model": earliest_is("disputed", lambda s, c: bool(s.observed.get("tiebreak_same_model"))),
    "dispute_budget": earliest_is("disputed", lambda s, c: bool(s.observed.get("tiebreak_reserve_used"))),
    "dispute_tiebreak": earliest_is("disputed", lambda s, c: c.get("tiebreak_for_attempt") != c.get("attempt")),
    "dispute_decide": earliest_is("disputed", lambda s, c: bool(s.seen(c, "tiebreak_finished", False))),
    "failure_cap": earliest_is("failed", lambda s, c: int(c.get("attempts_since_decision") or 0) >= s.max_failures),
    "retry_failed": earliest_is("failed", lambda s, c: int(c.get("attempts_since_decision") or 0) < s.max_failures),
    "changes": earliest_is("changes_requested"),
    "restack": first_chunk(lambda s, c: bool(c.get("branch")) and bool(c.get("needs_restack"))),
    "range_diff": first_chunk(lambda s, c: s.pending_range_diff(c)),
    "implement_next": implement_next,
    "stack_review": stack_review,
    "release_question": status_is("awaiting_release"),
    "sha_mismatch": merging(sha_mismatch),
    "already_merged": merging(first_chunk(lambda s, c: c["status"] != "merged" and bool(s.seen(c, "pr_merged", False)))),
    "merge_restack": merging(merge_restack),
    "merge_ci": merging(merge_ci),
    "merge_one": merging(merge_one),
    "release_command": merging(lambda s: {} if s.chunks and all(c["status"] == "merged" for c in s.chunks) else None),
    "update_graph": status_is("awaiting_graph_update"),
    "stuck": lambda s: {},
}


# ---------------------------------------------------------------- answers


def check_table(table: dict) -> None:
    """The table and this script name the same rules, and stuck is the last one."""
    ids = [rule.get("id") for rule in table.get("next_rules") or []]
    missing = [rule_id for rule_id in ids if rule_id not in CONDITIONS]
    extra = [rule_id for rule_id in CONDITIONS if rule_id not in ids]
    if missing or extra:
        raise SystemExit(f"next_action.py and state/transitions.yaml disagree. Missing: {missing}. Extra: {extra}.")
    untargeted = [rule_id for rule_id in ids if rule_id not in RULE_TARGETS]
    if untargeted:
        raise SystemExit(f"next_action.py names no skill for rules: {untargeted}")
    if not ids or ids[-1] != "stuck":
        raise SystemExit("the last next rule must be stuck")


def state_changing(event: dict) -> bool:
    return bool(event.get("to") or event.get("chunk_to"))


def allowed_events(table: dict, snapshot: Snapshot, chunk_id: str | None) -> list[str]:
    chunk = snapshot.by_id.get(chunk_id) if chunk_id else None
    names = []
    for event in table.get("events") or []:
        if not state_changing(event):
            continue
        if event.get("from") and snapshot.status not in event["from"]:
            continue
        if event.get("chunk_from") and (chunk is None or chunk["status"] not in event["chunk_from"]):
            continue
        names.append(event["name"])
    return names


def next_action(table: dict, data: Any) -> dict:
    check_table(table)
    snapshot = Snapshot(data, table)
    for rule in table["next_rules"]:
        context = CONDITIONS[rule["id"]](snapshot)
        if context is None:
            continue
        answer: dict[str, Any] = {"rule": rule["id"], "action": rule.get("action")}
        target = RULE_TARGETS[rule["id"]]
        if target:
            answer[target[0]] = target[1]
        answer.update(context)
        if rule.get("detail"):
            answer["detail"] = rule["detail"]
        answer["allowed_events"] = allowed_events(table, snapshot, context.get("chunk"))
        return answer
    raise SystemExit("no next rule matched, and stuck should always match")  # pragma: no cover


def pick(choice: str | None, options: list[str] | None, label: str) -> str | None:
    if not options:
        if choice:
            raise Refused(f"this event does not set {label}")
        return None
    if choice:
        if choice not in options:
            raise Refused(f"{label} {choice!r} is not one of {options}")
        return choice
    if len(options) == 1:
        return options[0]
    raise Refused(f"choose {label} from {options}")


def record_event(table: dict, data: Any, name: str, chunk_id: str | None = None, to: str | None = None, chunk_to: str | None = None) -> dict:
    check_table(table)
    snapshot = Snapshot(data, table)
    event = next((item for item in table.get("events") or [] if item.get("name") == name), None)
    if event is None:
        raise Refused(f"unknown event {name!r}")
    if str(snapshot.feature.get("state_version", "")) != "1":
        raise Refused("state_version is not 1. Migrate before recording anything")
    if name != "take_lease" and snapshot.lease_held_by_other():
        raise Refused("another session holds the lease. take_lease needs a human quote")
    if event.get("from") and snapshot.status not in event["from"]:
        raise Refused(f"{name} starts from {event['from']}, not {snapshot.status}")

    chunk = None
    if event.get("chunk_from") or event.get("chunk_to"):
        if not chunk_id and event.get("chunk_from"):
            raise Refused(f"{name} needs --chunk")
        if chunk_id:
            chunk = snapshot.by_id.get(chunk_id)
            if chunk is None:
                raise Refused(f"no chunk {chunk_id!r} in the snapshot")
    elif chunk_id:
        raise Refused(f"{name} does not change a chunk")
    if event.get("chunk_from") and chunk is not None and chunk["status"] not in event["chunk_from"]:
        raise Refused(f"{name} needs chunk {chunk_id} in {event['chunk_from']}, not {chunk['status']}")

    new_status = pick(to, event.get("to"), "--to") or snapshot.status
    answer: dict[str, Any] = {"event": name, "skill": event.get("skill"), "feature_status": new_status}
    if chunk is not None:
        answer["chunk"] = chunk["id"]
        answer["chunk_status"] = pick(chunk_to, event.get("chunk_to"), "--chunk-to") or chunk["status"]
    elif chunk_to:
        raise Refused(f"{name} needs --chunk to set a chunk status")
    if event.get("guard"):
        answer["guard"] = event["guard"]
    return answer


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pick the next fstack action, or check an event. Reads a JSON snapshot on stdin.")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("next", help="the first next rule that matches")
    record = commands.add_parser("record", help="check that an event is legal and return the new statuses")
    record.add_argument("event")
    record.add_argument("--chunk")
    record.add_argument("--to")
    record.add_argument("--chunk-to")
    args = parser.parse_args(argv)

    table = load_table()
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as error:
        print(json.dumps({"error": f"the snapshot is not JSON: {error}"}))
        return 2
    try:
        if args.command == "next":
            answer = next_action(table, data)
        else:
            answer = record_event(table, data, args.event, args.chunk, args.to, args.chunk_to)
    except Refused as error:
        print(json.dumps({"error": str(error)}))
        return 2
    print(json.dumps(answer, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
