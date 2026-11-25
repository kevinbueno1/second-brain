"""Install the reviewed personal skill and precise Codex access settings."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import uuid
from datetime import datetime, timezone

import tomlkit

ROOT = Path(__file__).resolve().parent.parent
VAULT = ROOT / "second-brain"
SOURCE_SKILL = ROOT / "second-brain-tools" / "skills" / "second-brain"
CODEX_HOME = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).resolve()
TARGET_SKILL = Path.home() / ".agents" / "skills" / "second-brain"
CONFIG = CODEX_HOME / "config.toml"
INSTRUCTIONS = CODEX_HOME / ("AGENTS.override.md" if (CODEX_HOME / "AGENTS.override.md").is_file() else "AGENTS.md")
MANIFEST = ROOT / ".second-brain-runtime" / "installed.json"
START = "<!-- second-brain:begin -->"
END = "<!-- second-brain:end -->"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def skill_content(source):
    """Resolve the public template using this checkout, not its author's paths."""
    if source.name == "SKILL.md":
        text = source.read_text(encoding="utf-8")
        text = text.replace("{{SECOND_BRAIN_VAULT}}", VAULT.as_posix())
        text = text.replace("{{SECOND_BRAIN_HELPER}}", (ROOT / "second-brain-tools" / "brain.py").as_posix())
        return text.encode("utf-8")
    return source.read_bytes()


def guidance():
    return f"""{START}
## Personal second brain

For prior personal/project knowledge, durable decisions, ideas and learning, use the `second-brain` skill at `{TARGET_SKILL.as_posix()}/SKILL.md`.
The shared vault is `{VAULT.as_posix()}`. Read its `AGENTS.md` for the current ingest/query/review protocol. Consult relevant notes before decisions; record reusable findings at meaningful milestones with their origin, state and project reference.
The same vault serves different project folders. Keep code and detailed tickets in their own projects. Use granted filesystem access; report a missing directory permission without bypassing it. Routine edits that add no durable knowledge need no memory update.
{END}"""


def update_guidance(previous):
    if START in previous:
        if END not in previous or previous.count(START) != 1 or previous.count(END) != 1:
            raise ValueError("El bloque global existente esta incompleto o duplicado; se requiere revisarlo.")
        before, remaining = previous.split(START, 1)
        _, after = remaining.split(END, 1)
        return before + guidance() + after
    return previous.rstrip() + ("\n\n" if previous.strip() else "") + guidance() + "\n"


def plan():
    config_text = CONFIG.read_text(encoding="utf-8-sig") if CONFIG.exists() else ""
    document = tomlkit.parse(config_text)
    if "sandbox_workspace_write" not in document:
        document["sandbox_workspace_write"] = tomlkit.table()
    section = document["sandbox_workspace_write"]
    roots = list(section.get("writable_roots", []))
    for path in [VAULT, ROOT / "second-brain-backups"]:
        if not any(str(path).casefold() == str(existing).casefold() for existing in roots):
            roots.append(str(path))
    section["writable_roots"] = roots
    current = INSTRUCTIONS.read_text(encoding="utf-8-sig") if INSTRUCTIONS.exists() else ""
    return document, update_guidance(current)


def check():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    document = tomlkit.parse(CONFIG.read_text(encoding="utf-8-sig")) if CONFIG.exists() else {}
    roots = list(document.get("sandbox_workspace_write", {}).get("writable_roots", []))
    instructions = INSTRUCTIONS.read_text(encoding="utf-8-sig") if INSTRUCTIONS.exists() else ""
    matching = TARGET_SKILL.is_dir() and all((TARGET_SKILL / path.relative_to(SOURCE_SKILL)).is_file() and hashlib.sha256(skill_content(path)).hexdigest() == sha(TARGET_SKILL / path.relative_to(SOURCE_SKILL)) for path in SOURCE_SKILL.rglob("*") if path.is_file())
    result = {"installed": bool(manifest), "skill_matches_source": matching, "global_guidance_present": guidance() in instructions, "vault_writable_default": str(VAULT) in roots, "backup_writable_default": str(ROOT / "second-brain-backups") in roots, "skill_path": str(TARGET_SKILL), "instructions_path": str(INSTRUCTIONS), "vault": str(VAULT), "transport": "native-files", "mcp_server_installed": False}
    result["ok"] = all(result[key] for key in ["installed", "skill_matches_source", "global_guidance_present", "vault_writable_default", "backup_writable_default"])
    return result


def apply():
    document, instructions = plan()
    previous = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else None
    if TARGET_SKILL.exists() and (not previous or previous.get("managed_by") != "workflow-second-brain"):
        raise ValueError("Ya existe una skill personal con este nombre que no pertenece a esta instalacion.")
    snapshot = ROOT / "second-brain-backups" / ("global-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8])
    snapshot.mkdir(parents=True)
    for name, path in [("config.toml", CONFIG), (INSTRUCTIONS.name, INSTRUCTIONS)]:
        if path.exists():
            shutil.copy2(path, snapshot / name)
    if TARGET_SKILL.exists():
        shutil.copytree(TARGET_SKILL, snapshot / "second-brain-skill")
    # All changes are scoped to the personal skill, its marked guidance and two writable roots.
    TARGET_SKILL.mkdir(parents=True, exist_ok=True)
    for source in SOURCE_SKILL.rglob("*"):
        if source.is_file():
            destination = TARGET_SKILL / source.relative_to(SOURCE_SKILL)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(skill_content(source))
    CODEX_HOME.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(tomlkit.dumps(document), encoding="utf-8")
    INSTRUCTIONS.write_text(instructions, encoding="utf-8")
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    manifest = {"managed_by": "workflow-second-brain", "version": "1.0.0", "installed_utc": datetime.now(timezone.utc).isoformat(), "skill_path": str(TARGET_SKILL), "global_instructions": str(INSTRUCTIONS), "config_path": str(CONFIG), "previous_files_backup": str(snapshot), "instructions_existed_before": (snapshot / INSTRUCTIONS.name).exists(), "skill_existed_before": (snapshot / "second-brain-skill").exists(), "vault": str(VAULT), "transport": "native-files"}
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return check()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.apply:
        result = apply()
    elif args.check:
        result = check()
    else:
        document, instructions = plan()
        result = {"action": "preview-only", "skill_source": str(SOURCE_SKILL), "skill_target": str(TARGET_SKILL), "instructions_target": str(INSTRUCTIONS), "instructions_block": guidance(), "config_target": str(CONFIG), "writable_roots": list(document["sandbox_workspace_write"]["writable_roots"]), "backup_parent": str(ROOT / "second-brain-backups")}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        raise SystemExit(main())
    except (ValueError, OSError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(2)
