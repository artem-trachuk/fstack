#!/usr/bin/env python3
"""Validate the fstack plugin layout, config, and cross-references."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

SKILLS = [
    "setup-project",
    "collect-requirements",
    "gap-analysis",
    "split-into-chunks",
    "pick-next-task",
    "implement-chunk",
    "verify",
    "build-context",
    "tldr",
    "advisors",
    "escalate",
    "release",
]

PROMPT_ACTIONS = [
    "collect-requirements",
    "gap-analysis",
    "split-into-chunks",
    "pick-next-task",
    "implement-chunk",
    "verify",
    "advisors",
    "escalate",
    "release",
]

FEATURE_TEMPLATES = [
    "templates/feature/requirements.md",
    "templates/feature/questions.md",
    "templates/feature/plan.md",
    "templates/feature/decisions.md",
    "templates/feature/advisors.md",
    "templates/feature/chunks/chunk.md",
    "templates/feature/verification/result.md",
    "templates/workspace-readme.md",
]

KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
AGENT_PLUGIN_KEYS = {
    "$schema",
    "name",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
    "extensions",
}


def main() -> int:
    errors: list[str] = []
    checks = 0

    def check(condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            errors.append(message)

    root_manifest = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    check(root_manifest.get("$schema", "").endswith("plugin.schema.json"), "root plugin.json needs the Agent Plugins schema")
    check(root_manifest.get("name") == "fstack", "root plugin name must be fstack")
    check(KEBAB.match(root_manifest.get("name", "")) is not None, "root plugin name must be kebab-case")
    check(set(root_manifest) <= AGENT_PLUGIN_KEYS, f"root plugin.json has unknown keys: {sorted(set(root_manifest) - AGENT_PLUGIN_KEYS)}")
    author = root_manifest.get("author", {})
    check(set(author) <= {"name", "email", "url"}, "root plugin author has unknown keys")

    cursor_manifest = json.loads((ROOT / ".cursor-plugin" / "plugin.json").read_text(encoding="utf-8"))
    check(cursor_manifest.get("name") == "fstack", "Cursor plugin name must be fstack")
    check(cursor_manifest.get("version") == "0.1.0", "Cursor plugin version must be 0.1.0")
    for field in ("skills", "agents", "rules", "logo"):
        value = cursor_manifest.get(field, "")
        check(isinstance(value, str) and value and ".." not in value and not value.startswith("/"), f"manifest {field} must be a relative path")
    check((ROOT / cursor_manifest["logo"]).is_file(), "logo path must exist")
    check((ROOT / "skills").is_dir(), "skills directory must exist")
    check((ROOT / "agents").is_dir(), "agents directory must exist")
    check((ROOT / "rules").is_dir(), "rules directory must exist")

    for skill in SKILLS:
        path = ROOT / "skills" / skill / "SKILL.md"
        check(path.is_file(), f"missing skill {skill}")
        if not path.is_file():
            continue
        meta, body = split_frontmatter(path.read_text(encoding="utf-8"))
        check(meta.get("name") == skill, f"{skill} frontmatter name must match its folder")
        description = str(meta.get("description", "")).strip()
        check(bool(description) and "use" in description.lower(), f"{skill} description must say when to use it")
        check("lorem ipsum" not in body.lower(), f"{skill} contains placeholder text")
        if skill == "collect-requirements":
            check(meta.get("disable-model-invocation") is True, "collect-requirements must set disable-model-invocation: true")
        else:
            check(meta.get("disable-model-invocation") is not True, f"{skill} must stay available to the orchestrator or verifier")

    for skill in SKILLS:
        if skill == "collect-requirements":
            continue
        body = (ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
        check(
            "Follow `skills/collect-requirements/SKILL.md`" not in body,
            f"{skill} must not start collect-requirements",
        )

    gap = (ROOT / "skills" / "gap-analysis" / "SKILL.md").read_text(encoding="utf-8")
    check("Do not follow that skill yourself." in gap, "gap-analysis must refuse to start collect-requirements")
    check(
        "agents/verifier.md" in (ROOT / "skills" / "implement-chunk" / "SKILL.md").read_text(encoding="utf-8"),
        "implement-chunk must hand off to the verifier agent",
    )
    check(
        "You never start collection yourself." in (ROOT / "agents" / "orchestrator.md").read_text(encoding="utf-8"),
        "orchestrator must not start requirements collection",
    )

    build_context = (ROOT / "skills" / "build-context" / "SKILL.md").read_text(encoding="utf-8")
    for action in PROMPT_ACTIONS:
        check(f"`{action}`" in build_context, f"build-context must name the {action} action")
        prompt = ROOT / "templates" / "prompts" / f"{action}.md"
        check(prompt.is_file(), f"missing prompt template {action}")

    verify_prompt = (ROOT / "templates" / "prompts" / "verify.md").read_text(encoding="utf-8")
    check("Do not attach implementer notes." in verify_prompt, "verify prompt must exclude implementer notes")
    check(
        re.search(r"^#{1,6} +Implementer notes\s*$", verify_prompt, re.MULTILINE) is None,
        "verify prompt must not contain an Implementer notes section",
    )
    for token in ("{{spec}}", "{{acceptance_criteria}}", "{{diff_source}}"):
        check(token in verify_prompt, f"verify prompt must include {token}")

    for relative in FEATURE_TEMPLATES:
        check((ROOT / relative).is_file(), f"missing template {relative}")
    chunk = (ROOT / "templates" / "feature" / "chunks" / "chunk.md").read_text(encoding="utf-8")
    check("## Implementer notes" in chunk, "chunk template keeps implementer notes in the chunk file")
    check("status: planned" in chunk, "chunk template starts planned")

    config_text = (ROOT / "fstack.yaml").read_text(encoding="utf-8")
    config = yaml.safe_load(config_text)
    check(config.get("version") == "0.1", "config version must be 0.1")
    workspace = str(config.get("workspace", ""))
    check(workspace == "features" and not workspace.startswith("/") and ".." not in workspace, "workspace must be the relative path features")
    advisors = config.get("advisors", {})
    check(advisors.get("planner_review", {}).get("model") == "opus", "planner_review model must be opus")
    check(advisors.get("planner_review", {}).get("when") == ["gap-analysis", "split-into-chunks"], "planner_review when-list drifted")
    check(advisors.get("verify_tiebreak", {}).get("model") == "argon", "verify_tiebreak model must be argon")
    check(advisors.get("verify_tiebreak", {}).get("when") == ["verifier-disputed"], "verify_tiebreak when-list drifted")
    check(advisors.get("max_calls_per_feature") == 6, "max_calls_per_feature must be 6")
    for snippet in (
        "model: opus        # e.g. Claude Opus 5.5 in Cursor",
        "model: argon       # Gemini 4 Argon in Cursor",
        "when: [gap-analysis, split-into-chunks]",
        "when: [verifier-disputed]",
        "max_calls_per_feature: 6",
    ):
        check(snippet in config_text, f"advisors block missing exact line: {snippet}")
    gates = config.get("human_gates", {})
    check(gates.get("merge") == "require_approval", "merge gate drifted")
    check(gates.get("release") == "require_approval", "release gate drifted")
    check(gates.get("outward_messages") == "require_approval", "outward message gate drifted")
    check(gates.get("collect_requirements") == "manual_only", "collect_requirements gate drifted")
    check(config.get("verify", {}).get("max_failures_before_escalation") == 2, "failure cap drifted")
    models = config.get("models", {})
    check(models.get("opus") == "claude-opus-5-5", "opus family prefix drifted")
    check(models.get("argon") == "gemini-4-argon", "argon family prefix drifted")
    check(models.get("resolution") == "pending", "shipped config must leave resolution pending")

    roles = config.get("roles", {})
    check(set(roles) == {"orchestrator", "verifier", "implementer"}, "roles must be orchestrator, verifier, and implementer")
    orchestrator_skills = roles["orchestrator"]["skills"]
    verifier_skills = roles["verifier"]["skills"]
    check("collect-requirements" not in orchestrator_skills, "orchestrator must not auto-run collect-requirements")
    for skill in orchestrator_skills + verifier_skills + roles["implementer"]["skills"]:
        check(skill in SKILLS, f"role references unknown skill {skill}")
    check(roles["implementer"]["agent"] == "cursor-coding-agent", "implementer agent id drifted")

    for agent_name in ("orchestrator", "verifier"):
        path = ROOT / "agents" / f"{agent_name}.md"
        check(path.is_file(), f"missing agent {agent_name}")
        meta, body = split_frontmatter(path.read_text(encoding="utf-8"))
        check(meta.get("name") == agent_name, f"agent {agent_name} name mismatch")
        check(bool(str(meta.get("description", "")).strip()), f"agent {agent_name} needs a description")
        for skill in roles[agent_name]["skills"]:
            check(f"skills/{skill}/SKILL.md" in body, f"agent {agent_name} must reference {skill}")

    rule_path = ROOT / "rules" / "human-gates.mdc"
    rule_meta, rule_body = split_frontmatter(rule_path.read_text(encoding="utf-8"))
    check(bool(str(rule_meta.get("description", "")).strip()), "human-gates rule needs a description")
    check(rule_meta.get("alwaysApply") is True, "human-gates must always apply")
    check("/collect-requirements" in rule_body, "human-gates rule must keep collection manual")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for heading in ("## Install", "## Quick start", "## Flow", "## Configuration", "## Workspace", "## Adding a bot or a skill"):
        check(heading in readme, f"README missing {heading}")
    check("```mermaid" in readme, "README needs a mermaid flow diagram")
    check("max_calls_per_feature: 6" in readme, "README must show the advisor cap")

    banned = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in {".md", ".mdc", ".yml", ".yaml", ".json", ".py", ".svg"}:
            continue
        relative = path.relative_to(ROOT).as_posix()
        # The checker names the strings it rejects.
        if relative == "scripts/validate_plugin.py":
            continue
        text = path.read_text(encoding="utf-8")
        if re.search(r"lorem ipsum", text, re.IGNORECASE):
            banned.append(f"{relative} contains lorem ipsum")
        if re.search(r"/Users/|/home/|[A-Za-z]:\\\\", text):
            banned.append(f"{relative} contains a machine-specific path")
        if relative != "README.md" and "~/.cursor" in text:
            banned.append(f"{relative} hardcodes a Cursor home path")
    check(not banned, "; ".join(banned) if banned else "paths are portable")

    if errors:
        for message in errors:
            print(f"error: {message}", file=sys.stderr)
        print(f"{len(errors)} error(s), {checks} checks", file=sys.stderr)
        return 1
    print(f"ok: {checks} checks passed")
    return 0


def split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    loaded = yaml.safe_load(raw) or {}
    if not isinstance(loaded, dict):
        return {}, body
    return loaded, body


if __name__ == "__main__":
    sys.exit(main())
