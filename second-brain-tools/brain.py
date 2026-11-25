"""Portable file operations for the personal vault. Python 3.12+, standard library."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import time
import unicodedata
import uuid
import zipfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, unquote, urlparse

DEFAULT_VAULT = Path(__file__).resolve().parent.parent / "second-brain"
NOTE_FOLDERS = {"00-entrada", "10-proyectos", "20-areas", "30-conocimiento", "40-archivo"}
GENERATED = {"index.md", "log.md"}


def stamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def atomic_text(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=".brain-tmp-", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def inside(root, relative):
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError("Usa una ruta relativa dentro de la boveda, sin '..'.")
    target = (root / candidate).resolve()
    if not target.is_relative_to(root):
        raise ValueError("La ruta sale de la boveda.")
    return target


@contextmanager
def writer(root, timeout=8):
    runtime = root / ".brain"
    runtime.mkdir(exist_ok=True)
    lock = runtime / "write.lock"
    deadline = time.monotonic() + timeout
    while True:
        try:
            descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise RuntimeError("Otra escritura mantiene .brain/write.lock. Comprueba el proceso antes de retirar un bloqueo abandonado.")
            time.sleep(0.05)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            output.write(json.dumps({"pid": os.getpid(), "started_utc": stamp()}))
        yield
    finally:
        lock.unlink(missing_ok=True)


def event(root, operation, details):
    record = {"id": str(uuid.uuid4()), "at_utc": stamp(), "operation": operation, **details}
    events_path = root / ".brain" / "events.jsonl"
    previous = events_path.read_text(encoding="utf-8") if events_path.exists() else ""
    atomic_text(events_path, previous + json.dumps(record, ensure_ascii=False) + "\n")
    log_path = root / "log.md"
    log = log_path.read_text(encoding="utf-8") if log_path.exists() else "# Registro de operaciones\n\nFechas en UTC. Generado desde `.brain/events.jsonl`.\n\n"
    entry = f"## [{record['at_utc']}] {operation} | {record['id']}\n\n```json\n{json.dumps(details, ensure_ascii=False, indent=2)}\n```\n\n"
    atomic_text(log_path, log + entry)
    return record


def without_frontmatter(text):
    return re.sub(r"\A---\r?\n.*?\r?\n---\r?\n", "", text, count=1, flags=re.S)


def title_of(path, text):
    match = re.search(r"^#\s+(.+)$", without_frontmatter(text), re.M)
    return match.group(1).strip() if match else path.stem


def notes(root):
    for folder in sorted(NOTE_FOLDERS):
        location = root / folder
        if not location.exists():
            continue
        for path in sorted(location.rglob("*.md")):
            if path.is_file() and path.resolve().is_relative_to(root) and not path.is_symlink():
                yield path


def catalog(root):
    lines = ["# Indice de conocimiento", "", "Generado por `brain.py reindex`. Consulta las paginas y sus fuentes antes de concluir.", ""]
    found = list(notes(root))
    lines += [f"Paginas: {len(found)}", ""]
    previous_folder = None
    for path in found:
        relative = path.relative_to(root).as_posix()
        folder = relative.split("/")[0]
        if folder != previous_folder:
            lines += [f"## {folder}", ""]
            previous_folder = folder
        text = path.read_text(encoding="utf-8-sig")
        title = title_of(path, text).replace("[", "\\[").replace("]", "\\]")
        paragraphs = [line.strip() for line in without_frontmatter(text).splitlines() if line.strip() and not line.startswith(("#", "---", "```", "|", "- "))]
        # Summaries live at the vault root; copied relative links would change destination.
        summary_text = paragraphs[0] if paragraphs else "Nota de referencia"
        summary_text = re.sub(r"!?\[([^\]\n]+)\]\([^)]+\)", r"\1", summary_text)
        summary_text = re.sub(r"\[\[([^\]\n]+)\]\]", lambda match: match.group(1).split("|")[-1], summary_text)
        summary = summary_text[:160].replace("\n", " ")
        lines.append(f"- [{title}]({quote(relative, safe='/')}) — {summary}")
    return "\n".join(lines) + "\n"


def reindex(root):
    content = catalog(root)
    index = root / "index.md"
    changed = not index.exists() or index.read_text(encoding="utf-8") != content
    if changed:
        atomic_text(index, content)
    return {"changed": changed, "pages": len(list(notes(root))), "path": str(index)}


def capture(root, input_path, title, origin):
    data = Path(input_path).read_bytes()
    sha = digest(data)
    raw = root / "80-fuentes"
    raw.mkdir(exist_ok=True)
    for meta in raw.glob("*.source.json"):
        previous = json.loads(meta.read_text(encoding="utf-8"))
        if previous["sha256"] == sha:
            existing = inside(root, previous["path"])
            if not existing.is_file() or digest(existing.read_bytes()) != sha:
                raise ValueError("Una fuente registrada fue alterada o falta; ejecuta lint antes de continuar.")
            return {"created": False, **previous}
    suffix = Path(input_path).suffix.lower()
    if not re.fullmatch(r"\.[a-z0-9]{1,12}", suffix):
        suffix = ".bin"
    target = raw / (sha + suffix)
    with target.open("xb") as output:
        output.write(data)
    metadata = {"sha256": sha, "path": target.relative_to(root).as_posix(), "title": title, "origin": origin, "original_name": Path(input_path).name, "captured_utc": stamp()}
    atomic_text(target.with_suffix(target.suffix + ".source.json"), json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")
    event(root, "capture-source", {"path": metadata["path"], "origin": origin, "sha256": sha})
    return {"created": True, **metadata}


def source_line(root, target, source):
    if urlparse(source).scheme in {"https", "http"}:
        return f"- <{source}>"
    source_path = root / source
    if source_path.is_file() and source_path.resolve().is_relative_to(root):
        relative = os.path.relpath(source_path, target.parent).replace(os.sep, "/")
        return f"- [{source}]({quote(relative, safe='/')})"
    return "- " + source.replace("\n", " ")


def publish(root, relative, title, body_path, sources, project, kind, state):
    target = inside(root, relative)
    if target.relative_to(root).parts[0] not in NOTE_FOLDERS or target.suffix.lower() != ".md":
        raise ValueError("Publica una nota .md dentro de una carpeta de notas, no en fuentes o archivos de sistema.")
    body = Path(body_path).read_text(encoding="utf-8-sig").strip()
    if body.startswith("---\n"):
        raise ValueError("El archivo de cuerpo debe contener Markdown sin frontmatter; los metadatos se pasan como argumentos.")
    note_id = "note-" + digest(target.relative_to(root).as_posix().encode())[:16]
    metadata = {"id": note_id, "tipo": kind, "estado": state, "actualizado_utc": stamp(), "proyecto": project, "fuentes": sources}
    header = "---\n" + "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in metadata.items()) + "\n---\n\n"
    content = header + f"# {title}\n\n{body}\n\n## Fuentes\n\n" + "\n".join(source_line(root, target, source) for source in sources) + "\n"
    previous = target.read_text(encoding="utf-8-sig") if target.exists() else None
    stable = lambda value: re.sub(r"^actualizado_utc:.*$", "", value, flags=re.M)
    if previous is not None and stable(previous) == stable(content):
        return {"changed": False, "path": str(target), "id": note_id}
    if previous is not None:
        history = root / ".brain" / "history" / note_id / (str(uuid.uuid4()) + ".md")
        atomic_text(history, previous)
    atomic_text(target, content)
    reindex(root)
    record = event(root, "publish-note", {"path": relative, "project": project, "state": state, "sources": sources, "sha256": digest(content.encode())})
    return {"changed": True, "path": str(target), "id": note_id, "operation_id": record["id"]}


def normalized(value):
    return "".join(char for char in unicodedata.normalize("NFKD", value.casefold()) if not unicodedata.combining(char))


def search(root, query, limit=8):
    terms = re.findall(r"\w+", normalized(query))
    if not terms:
        return []
    results = []
    for path in notes(root):
        text = path.read_text(encoding="utf-8-sig")
        title = title_of(path, text)
        body = normalized(without_frontmatter(text))
        title_normal = normalized(title)
        score = sum(body.count(term) + 5 * title_normal.count(term) for term in terms)
        if score:
            offset = min((body.find(term) for term in terms if term in body), default=0)
            snippet = without_frontmatter(text)[max(0, offset - 80):offset + 300].replace("\n", " ")
            results.append({"path": path.relative_to(root).as_posix(), "title": title, "score": score, "snippet": snippet})
    return sorted(results, key=lambda item: (-item["score"], item["path"]))[:limit]


def lint(root):
    issues = []
    documents = [path for path in root.rglob("*.md") if not any(part.startswith(".") for part in path.relative_to(root).parts) and path.relative_to(root).parts[0] not in {"80-fuentes", "90-plantillas"}]
    by_stem = {}
    for path in documents:
        by_stem.setdefault(path.stem.casefold(), []).append(path)
    for path in documents:
        text = path.read_text(encoding="utf-8-sig")
        clean = re.sub(r"^```.*?^```[^\n]*$", "", text, flags=re.M | re.S)
        clean = re.sub(r"`[^`\n]+`", "", clean)
        links = re.findall(r"(?<!!)\[[^\]\n]+\]\(([^)]+)\)", clean)
        for link in links:
            target_text = unquote(link.strip().strip("<>").split("#")[0])
            if not target_text or urlparse(target_text).scheme:
                continue
            target = path.parent / target_text
            if not target.exists():
                issues.append({"type": "broken-link", "page": path.relative_to(root).as_posix(), "target": link})
        for target in re.findall(r"\[\[([^\]]+)\]\]", clean):
            target = target.split("|")[0].split("#")[0]
            if target and not (path.parent / target).exists() and not (root / target).exists() and Path(target).stem.casefold() not in by_stem:
                issues.append({"type": "broken-wikilink", "page": path.relative_to(root).as_posix(), "target": target})
    for metadata_path in (root / "80-fuentes").glob("*.source.json") if (root / "80-fuentes").exists() else []:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        source = inside(root, metadata["path"])
        if not source.is_file() or digest(source.read_bytes()) != metadata["sha256"]:
            issues.append({"type": "source-integrity", "source": metadata["path"]})
    index = root / "index.md"
    if not index.exists() or index.read_text(encoding="utf-8") != catalog(root):
        issues.append({"type": "stale-index", "repair": "reindex"})
    return {"ok": not issues, "issues": issues, "pages_checked": len(documents), "scope": "Structural checks and source hashes; factual contradictions require review by the assistant and user."}


def backup(root, destination=None):
    destination = Path(destination).resolve() if destination else root.parent / "second-brain-backups"
    if destination.is_relative_to(root):
        raise ValueError("Guarda las copias fuera de la boveda para evitar incluirlas de nuevo.")
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / ("second-brain-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8] + ".zip")
    with zipfile.ZipFile(target, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.resolve().is_relative_to(root) and path.name != "write.lock" and not path.name.startswith(".brain-tmp-"):
                archive.write(path, path.relative_to(root).as_posix())
    record = event(root, "backup", {"path": str(target), "sha256": digest(target.read_bytes())})
    return {"path": str(target), "sha256": record["sha256"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", type=Path, default=DEFAULT_VAULT)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("status")
    commands.add_parser("reindex")
    commands.add_parser("lint")
    query = commands.add_parser("search")
    query.add_argument("query")
    query.add_argument("--limit", type=int, default=8)
    source = commands.add_parser("capture-source")
    source.add_argument("--input", required=True, type=Path)
    source.add_argument("--title", required=True)
    source.add_argument("--origin", required=True)
    note = commands.add_parser("publish")
    note.add_argument("--path", required=True)
    note.add_argument("--title", required=True)
    note.add_argument("--body", required=True, type=Path)
    note.add_argument("--source", required=True, action="append")
    note.add_argument("--project", default="personal")
    note.add_argument("--kind", choices=["conocimiento", "proyecto", "aprendizaje", "decision", "idea"], default="conocimiento")
    note.add_argument("--state", choices=["confirmado", "propuesto", "hipotesis", "obsoleto"], default="propuesto")
    journal = commands.add_parser("journal")
    journal.add_argument("--operation", choices=["ingest", "query", "review", "decision", "maintenance"], required=True)
    journal.add_argument("--message", required=True)
    journal.add_argument("--project", default="personal")
    copy = commands.add_parser("backup")
    copy.add_argument("--destination", type=Path)
    args = parser.parse_args(argv)
    root = args.vault.resolve()
    try:
        if not root.is_dir():
            raise ValueError(f"No existe la boveda: {root}")
        if args.command == "search":
            result = search(root, args.query, args.limit)
        elif args.command == "lint":
            result = lint(root)
        elif args.command == "status":
            result = {"vault": str(root), "pages": len(list(notes(root))), "index_exists": (root / "index.md").is_file(), "log_exists": (root / "log.md").is_file(), "obsidian_ready": (root / ".obsidian" / "app.json").is_file(), "transport": "native-files", "background_service": False}
        else:
            with writer(root):
                if args.command == "publish":
                    result = publish(root, args.path, args.title, args.body, args.source, args.project, args.kind, args.state)
                elif args.command == "capture-source":
                    result = capture(root, args.input, args.title, args.origin)
                elif args.command == "reindex":
                    result = reindex(root)
                    if result["changed"]:
                        event(root, "reindex", result)
                elif args.command == "backup":
                    result = backup(root, args.destination)
                else:
                    result = event(root, args.operation, {"message": args.message, "project": args.project})
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if args.command == "lint" and not result["ok"] else 0
    except (ValueError, RuntimeError, OSError, json.JSONDecodeError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
