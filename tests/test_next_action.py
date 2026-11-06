"""Tests for scripts/next_action.py against the shipped state/transitions.yaml.

Each rule in next_rules has at least one test that reaches it. A few tests pin behaviour
the table has today that looks like a gap. They are named test_gap_* so a change to the
table shows up as a deliberate test change, not a silent one.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import next_action  # noqa: E402
from next_action import Refused, next_action as pick_next, record_event  # noqa: E402

TABLE = next_action.load_table()


def chunk(chunk_id: str, status: str, **fields) -> dict:
    observed = fields.pop("observed", None)
    item = {"id": chunk_id, "status": status, "repo": "web", **fields}
    if observed is not None:
        item["observed"] = observed
    return item


def snap(status: str = "building", chunks: list | None = None, observed: dict | None = None, **feature) -> dict:
    data = {
        "session": "me",
        "now": "2026-11-06T12:00:00Z",
        "feature": {"state_version": 1, "feature_status": status, "repos": ["web"], "base_shas": {"web": "base0"}, **feature},
        "chunks": chunks or [],
    }
    if observed is not None:
        data["observed"] = observed
    return data


def rule(data: dict) -> str:
    return pick_next(TABLE, data)["rule"]


class TableSync(unittest.TestCase):
    def test_every_rule_has_one_condition_and_one_target(self):
        ids = [item["id"] for item in TABLE["next_rules"]]
        self.assertEqual(sorted(ids), sorted(next_action.CONDITIONS))
        self.assertEqual(sorted(ids), sorted(next_action.RULE_TARGETS))
        self.assertEqual(ids[-1], "stuck")

    def test_targets_name_real_slots_and_skills(self):
        import yaml

        slots = set(yaml.safe_load((ROOT / "fstack.yaml").read_text(encoding="utf-8"))["workflow"]["slots"])
        skills = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
        for rule_id, target in next_action.RULE_TARGETS.items():
            if target is None:
                continue
            kind, name = target
            self.assertIn(kind, ("slot", "skill"), rule_id)
            self.assertIn(name, slots if kind == "slot" else skills, rule_id)

    def test_a_missing_condition_is_an_error(self):
        broken = dict(TABLE, next_rules=TABLE["next_rules"] + [{"id": "invented", "when": "x", "action": "y"}])
        with self.assertRaises(SystemExit):
            pick_next(broken, snap())


class Snapshots(unittest.TestCase):
    def test_unknown_feature_status_is_refused(self):
        with self.assertRaises(Refused):
            pick_next(TABLE, snap("almost_done"))

    def test_unknown_chunk_status_is_refused(self):
        with self.assertRaises(Refused):
            pick_next(TABLE, snap(chunks=[chunk("01-a", "kinda_verified")]))

    def test_unknown_fields_are_refused(self):
        with self.assertRaises(Refused):
            pick_next(TABLE, snap(statuss="building"))
        with self.assertRaises(Refused):
            pick_next(TABLE, snap(chunks=[chunk("01-a", "planned", agent="x")]))
        with self.assertRaises(Refused):
            pick_next(TABLE, snap(chunks=[chunk("01-a", "planned", observed={"diff": True})]))
        with self.assertRaises(Refused):
            pick_next(TABLE, snap(observed={"heads": {}}))

    def test_bad_ci_value_is_refused(self):
        with self.assertRaises(Refused):
            pick_next(TABLE, snap(chunks=[chunk("01-a", "verified", observed={"ci": "green"})]))

    def test_chunks_are_read_in_stack_order(self):
        data = snap(chunks=[chunk("10-late", "planned"), chunk("02-early", "planned")])
        self.assertEqual(pick_next(TABLE, data)["chunk"], "02-early")


class FeatureRules(unittest.TestCase):
    def test_migrate(self):
        data = snap()
        data["feature"]["state_version"] = 2
        self.assertEqual(rule(data), "migrate")
        del data["feature"]["state_version"]
        self.assertEqual(rule(data), "migrate")

    def test_state_version_from_a_notion_text_field(self):
        data = snap("done")
        data["feature"]["state_version"] = "1"
        self.assertEqual(rule(data), "done")

    def test_lease_held_by_someone_else(self):
        lease = {"owner": "other", "expires_at": "2026-11-06T12:10:00Z"}
        self.assertEqual(rule(snap("building", lease=lease)), "lease")

    def test_lease_expired_or_mine_does_not_stop(self):
        expired = {"owner": "other", "expires_at": "2026-11-06T11:00:00Z"}
        mine = {"owner": "me", "expires_at": "2026-11-06T12:10:00Z"}
        self.assertEqual(rule(snap("done", lease=expired)), "done")
        self.assertEqual(rule(snap("done", lease=mine)), "done")

    def test_stopped_wins_over_waiting(self):
        self.assertEqual(rule(snap("stopped", waiting_on="Q-x")), "stopped")

    def test_done(self):
        self.assertEqual(rule(snap("done")), "done")
        self.assertEqual(pick_next(TABLE, snap("done"))["skill"], "fstack-status")

    def test_waiting_wins_over_every_status_rule(self):
        for status in ("requirements_draft", "questions_open", "awaiting_release", "merging", "escalated"):
            self.assertEqual(rule(snap(status, waiting_on="Q-x")), "waiting", status)

    def test_draft(self):
        self.assertEqual(rule(snap("requirements_draft")), "draft")

    def test_survey_with_locations(self):
        answer = pick_next(TABLE, snap("requirements_confirmed"))
        self.assertEqual((answer["rule"], answer["slot"]), ("survey", "survey"))

    def test_survey_skip_without_locations(self):
        self.assertEqual(rule(snap("requirements_confirmed", repos=[])), "survey_skip")

    def test_survey_wait(self):
        self.assertEqual(rule(snap("surveying")), "survey_wait")

    def test_gap(self):
        self.assertEqual(rule(snap("surveyed")), "gap")

    def test_coverage_questions(self):
        self.assertEqual(rule(snap("questions_open")), "coverage_questions")

    def test_coverage_gate(self):
        self.assertEqual(rule(snap("awaiting_coverage_approval")), "coverage_gate")

    def test_single_chunk_is_the_default_plan(self):
        self.assertEqual(rule(snap("ready_to_plan")), "single_chunk")

    def test_split_when_the_work_is_not_one_chunk_per_repo(self):
        self.assertEqual(rule(snap("ready_to_plan", observed={"single_chunk_plan": False})), "split")

    def test_plan_gate(self):
        self.assertEqual(rule(snap("awaiting_plan_approval")), "plan_gate")

    def test_release_question(self):
        self.assertEqual(rule(snap("awaiting_release", chunks=[chunk("01-a", "verified")], review_approval="yes")), "release_question")

    def test_update_graph(self):
        self.assertEqual(rule(snap("awaiting_graph_update", chunks=[chunk("01-a", "merged")])), "update_graph")


class ChunkRules(unittest.TestCase):
    def test_base_drift(self):
        answer = pick_next(TABLE, snap(chunks=[chunk("01-a", "planned")], observed={"default_heads": {"web": "base1"}}))
        self.assertEqual((answer["rule"], answer["location"]), ("base_drift", "web"))

    def test_base_drift_only_while_building_or_merging(self):
        data = snap("surveyed", observed={"default_heads": {"web": "base1"}})
        self.assertEqual(rule(data), "gap")

    def test_no_drift_when_the_head_matches(self):
        data = snap(chunks=[chunk("01-a", "planned")], observed={"default_heads": {"web": "base0"}})
        self.assertEqual(rule(data), "implement_next")

    def test_blocked(self):
        self.assertEqual(rule(snap(chunks=[chunk("01-a", "blocked")])), "blocked")

    def test_blocked_reads_the_earliest_unfinished_chunk(self):
        data = snap(chunks=[chunk("01-a", "verified"), chunk("02-b", "blocked")])
        self.assertEqual(pick_next(TABLE, data)["chunk"], "02-b")

    def test_resume_implementer(self):
        answer = pick_next(TABLE, snap(chunks=[chunk("01-a", "implementing", agent_id="agent-1")]))
        self.assertEqual((answer["rule"], answer["slot"]), ("resume_implementer", "implement"))

    def test_prepare_verify(self):
        self.assertEqual(rule(snap(chunks=[chunk("01-a", "needs_verify")])), "prepare_verify")

    def test_launch_verifier(self):
        answer = pick_next(TABLE, snap(chunks=[chunk("01-a", "needs_verify", observed={"diff_attached": True})]))
        self.assertEqual(answer["rule"], "launch_verifier")
        self.assertIn("verifier_launched", answer["allowed_events"])

    def test_apply_filed_verdict(self):
        data = snap(chunks=[chunk("01-a", "in_review", attempt=1, head_sha="h1", verifier_agent_id="v1")])
        data["verifications"] = [{"chunk": "01-a", "attempt": 1, "head_sha": "h1", "applied": False}]
        self.assertEqual(rule(data), "apply_filed_verdict")

    def test_a_verdict_for_an_old_head_is_not_applied(self):
        data = snap(chunks=[chunk("01-a", "in_review", attempt=1, head_sha="h2", verifier_agent_id="v1")])
        data["verifications"] = [{"chunk": "01-a", "attempt": 1, "head_sha": "h1", "applied": False}]
        self.assertEqual(rule(data), "resume_verifier")

    def test_not_implemented_waits_and_does_not_start_the_next_chunk(self):
        data = snap(chunks=[chunk("01-a", "awaiting_verification_decision"), chunk("02-b", "planned", depends_on=[])])
        answer = pick_next(TABLE, data)
        self.assertEqual((answer["rule"], answer["chunk"]), ("not_implemented", "01-a"))
        self.assertIn("Verification is not implemented yet", answer["detail"])

    def test_resume_verifier(self):
        self.assertEqual(rule(snap(chunks=[chunk("01-a", "in_review", verifier_agent_id="v1")])), "resume_verifier")

    def test_dispute_same_model(self):
        data = snap(chunks=[chunk("01-a", "disputed", attempt=1)], observed={"tiebreak_same_model": True})
        self.assertEqual(rule(data), "dispute_same_model")

    def test_dispute_budget(self):
        data = snap(chunks=[chunk("01-a", "disputed", attempt=1)], observed={"tiebreak_reserve_used": True})
        self.assertEqual(rule(data), "dispute_budget")

    def test_dispute_tiebreak(self):
        answer = pick_next(TABLE, snap(chunks=[chunk("01-a", "disputed", attempt=1)]))
        self.assertEqual((answer["rule"], answer["slot"]), ("dispute_tiebreak", "advise"))

    def test_dispute_decide(self):
        data = snap(chunks=[chunk("01-a", "disputed", attempt=1, tiebreak_for_attempt=1, observed={"tiebreak_finished": True})])
        self.assertEqual(rule(data), "dispute_decide")

    def test_failure_cap_uses_greater_than_or_equal(self):
        data = snap(chunks=[chunk("01-a", "failed", attempts_since_decision=2)])
        self.assertEqual(rule(data), "failure_cap")
        data["config"] = {"max_failures_before_escalation": 3}
        self.assertEqual(rule(data), "retry_failed")

    def test_retry_failed(self):
        self.assertEqual(rule(snap(chunks=[chunk("01-a", "failed", attempts_since_decision=1)])), "retry_failed")

    def test_changes(self):
        self.assertEqual(rule(snap(chunks=[chunk("01-a", "changes_requested")])), "changes")

    def test_restack(self):
        data = snap(chunks=[chunk("01-a", "verified", branch="fstack/a", needs_restack=True)])
        self.assertEqual(rule(data), "restack")

    def test_range_diff(self):
        self.assertEqual(rule(snap(chunks=[chunk("01-a", "verified", needs_reverify=True)])), "range_diff")

    def test_implement_next_waits_for_dependencies(self):
        data = snap(chunks=[chunk("01-a", "in_review", verifier_agent_id="v1"), chunk("02-b", "planned", depends_on=["01-a"])])
        self.assertEqual(rule(data), "resume_verifier")
        data["chunks"][0] = chunk("01-a", "accepted_by_human", accepted_sha="h1")
        answer = pick_next(TABLE, data)
        self.assertEqual((answer["rule"], answer["chunk"]), ("implement_next", "02-b"))
        self.assertEqual(answer["allowed_events"].count("agent_launched"), 1)

    def test_stack_review(self):
        data = snap(chunks=[chunk("01-a", "verified"), chunk("02-b", "accepted_by_human")])
        answer = pick_next(TABLE, data)
        self.assertEqual((answer["rule"], answer["slot"]), ("stack_review", "review"))

    def test_no_stack_review_once_approved(self):
        data = snap("awaiting_release", chunks=[chunk("01-a", "verified")], review_approval="yes")
        self.assertEqual(rule(data), "release_question")

    def test_stuck(self):
        self.assertEqual(rule(snap(chunks=[chunk("01-a", "implementing")])), "stuck")


class MergeRules(unittest.TestCase):
    def ready(self, chunk_id: str, **observed) -> dict:
        seen = {"pr_head_sha": "h-" + chunk_id, "ci": "passing", **observed}
        return chunk(chunk_id, "verified", verified_sha="h-" + chunk_id, observed=seen)

    def test_sha_mismatch(self):
        data = snap("merging", review_approval="yes", chunks=[self.ready("01-a", pr_head_sha="moved")])
        self.assertEqual(rule(data), "sha_mismatch")

    def test_accepted_chunk_releases_its_accepted_sha(self):
        accepted = chunk("01-a", "accepted_by_human", accepted_sha="h1", observed={"pr_head_sha": "h1", "ci": "none"})
        self.assertEqual(rule(snap("merging", review_approval="yes", chunks=[accepted])), "merge_one")

    def test_already_merged(self):
        data = snap("merging", review_approval="yes", chunks=[self.ready("01-a", pr_merged=True)])
        self.assertEqual(rule(data), "already_merged")

    def test_merge_restack(self):
        later = self.ready("02-b")
        later.update(depends_on=["01-a"], needs_reverify=True)
        data = snap("merging", review_approval="yes", chunks=[chunk("01-a", "merged"), later])
        self.assertEqual(rule(data), "range_diff")  # the general range_diff rule is earlier in the table

    def test_merge_ci_waits_for_the_next_chunk(self):
        for value in ("", "pending", "failing"):
            data = snap("merging", review_approval="yes", chunks=[self.ready("01-a", ci=value)])
            self.assertEqual(rule(data), "merge_ci", value)

    def test_merge_one_merges_the_next_chunk_only(self):
        data = snap("merging", review_approval="yes", chunks=[chunk("01-a", "merged"), self.ready("02-b"), self.ready("03-c")])
        answer = pick_next(TABLE, data)
        self.assertEqual((answer["rule"], answer["chunk"]), ("merge_one", "02-b"))

    def test_release_order_picks_the_location_first(self):
        api = self.ready("02-api")
        api["repo"] = "api"
        data = snap("merging", review_approval="yes", chunks=[self.ready("01-web"), api], repos=["web", "api"], release_order=["api", "web"])
        self.assertEqual(pick_next(TABLE, data)["chunk"], "02-api")

    def test_release_command(self):
        data = snap("merging", review_approval="yes", chunks=[chunk("01-a", "merged"), chunk("02-b", "merged")])
        self.assertEqual(rule(data), "release_command")


class Gaps(unittest.TestCase):
    """Behaviour the table has today that looks wrong. Fix the table, then change these tests."""

    def test_gap_tiebreak_in_flight_falls_to_stuck(self):
        # Launched for this attempt and not finished yet. No rule waits for it.
        data = snap(chunks=[chunk("01-a", "disputed", attempt=1, tiebreak_for_attempt=1)])
        self.assertEqual(rule(data), "stuck")

    def test_gap_budget_skip_repeats_and_decide_is_unreachable(self):
        # After tiebreak_skipped for budget, dispute_budget still matches before dispute_decide.
        data = snap(
            chunks=[chunk("01-a", "disputed", attempt=1, tiebreak_for_attempt=1, observed={"tiebreak_finished": True})],
            observed={"tiebreak_reserve_used": True},
        )
        self.assertEqual(rule(data), "dispute_budget")

    def test_gap_merge_restack_is_shadowed_by_restack_and_range_diff(self):
        # While merging, every chunk has a branch. restack and range_diff come earlier and
        # match first, so merge_restack only matches a chunk with no branch.
        later = chunk("02-b", "verified", depends_on=["01-a"], branch="fstack/b", needs_restack=True)
        merged = chunk("01-a", "merged")
        self.assertEqual(rule(snap("merging", review_approval="yes", chunks=[merged, later])), "restack")
        del later["branch"]
        self.assertEqual(rule(snap("merging", review_approval="yes", chunks=[merged, later])), "merge_restack")


class Record(unittest.TestCase):
    def test_a_legal_event_returns_the_new_statuses(self):
        answer = record_event(TABLE, snap(chunks=[chunk("01-a", "planned")]), "agent_launched", chunk_id="01-a")
        self.assertEqual((answer["feature_status"], answer["chunk_status"]), ("building", "implementing"))
        self.assertIn("Increment attempt", answer["guard"])

    def test_wrong_feature_status_is_refused(self):
        with self.assertRaises(Refused):
            record_event(TABLE, snap("done", chunks=[chunk("01-a", "planned")]), "agent_launched", chunk_id="01-a")

    def test_wrong_chunk_status_is_refused(self):
        with self.assertRaises(Refused):
            record_event(TABLE, snap(chunks=[chunk("01-a", "verified")]), "agent_launched", chunk_id="01-a")

    def test_several_targets_need_a_choice(self):
        data = snap(chunks=[chunk("01-a", "in_review")])
        with self.assertRaises(Refused):
            record_event(TABLE, data, "apply_verdict", chunk_id="01-a")
        answer = record_event(TABLE, data, "apply_verdict", chunk_id="01-a", chunk_to="awaiting_verification_decision")
        self.assertEqual(answer["chunk_status"], "awaiting_verification_decision")
        with self.assertRaises(Refused):
            record_event(TABLE, data, "apply_verdict", chunk_id="01-a", chunk_to="merged")

    def test_release_approval_only_from_awaiting_release(self):
        with self.assertRaises(Refused):
            record_event(TABLE, snap("awaiting_review"), "approve_release")
        answer = record_event(TABLE, snap("awaiting_release"), "approve_release")
        self.assertEqual(answer["feature_status"], "merging")

    def test_nothing_is_recorded_under_someone_elses_lease(self):
        lease = {"owner": "other", "expires_at": "2026-11-06T12:10:00Z"}
        with self.assertRaises(Refused):
            record_event(TABLE, snap("awaiting_release", lease=lease), "approve_release")
        record_event(TABLE, snap("awaiting_release", lease=lease), "take_lease")

    def test_a_log_event_keeps_the_statuses(self):
        answer = record_event(TABLE, snap("surveyed"), "advisor_launched")
        self.assertEqual(answer["feature_status"], "surveyed")
        self.assertNotIn("chunk_status", answer)

    def test_unknown_event_is_refused(self):
        with self.assertRaises(Refused):
            record_event(TABLE, snap(), "ship_it")

    def test_every_event_with_a_chunk_from_needs_a_chunk(self):
        for event in TABLE["events"]:
            if not event.get("chunk_from"):
                continue
            status = (event.get("from") or ["building"])[0]
            with self.assertRaises(Refused, msg=event["name"]):
                record_event(TABLE, snap(status), event["name"])


class CommandLine(unittest.TestCase):
    def run_script(self, args: list[str], data) -> tuple[int, dict]:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "next_action.py"), *args],
            input=data if isinstance(data, str) else json.dumps(data),
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode, json.loads(result.stdout)

    def test_next(self):
        code, answer = self.run_script(["next"], snap("surveyed"))
        self.assertEqual((code, answer["rule"]), (0, "gap"))

    def test_record_refusal_exits_2(self):
        code, answer = self.run_script(["record", "approve_release"], snap("building"))
        self.assertEqual(code, 2)
        self.assertIn("awaiting_release", answer["error"])

    def test_bad_json_exits_2(self):
        code, answer = self.run_script(["next"], "{not json")
        self.assertEqual(code, 2)
        self.assertIn("not JSON", answer["error"])


if __name__ == "__main__":
    unittest.main()
