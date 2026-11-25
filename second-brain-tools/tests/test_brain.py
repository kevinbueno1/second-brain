import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

SCRIPT = Path(__file__).resolve().parents[1] / "brain.py"
spec = importlib.util.spec_from_file_location("brain", SCRIPT)
brain = importlib.util.module_from_spec(spec)
spec.loader.exec_module(brain)


class BrainTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="second-brain-test-")
        self.base = Path(self.temporary.name).resolve()
        self.vault = self.base / "vault"
        self.vault.mkdir()
        self.body = self.base / "body.md"
        self.body.write_text("Una carga idempotente puede repetirse conservando el resultado.\n", encoding="utf-8")

    def tearDown(self):
        self.temporary.cleanup()

    def run_cli(self, *arguments, cwd=None):
        result = subprocess.run([sys.executable, str(SCRIPT), "--vault", str(self.vault), *arguments], cwd=cwd, capture_output=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        return json.loads(result.stdout)

    def publish(self, path="30-conocimiento/idempotencia.md", title="Idempotencia"):
        return self.run_cli("publish", "--path", path, "--title", title, "--body", str(self.body), "--source", "conversacion:prueba", "--project", "project-a", "--state", "confirmado")

    def test_source_is_content_addressed_and_integrity_checked(self):
        first = self.run_cli("capture-source", "--input", str(self.body), "--title", "Fuente", "--origin", "fixture")
        second = self.run_cli("capture-source", "--input", str(self.body), "--title", "Fuente", "--origin", "fixture")
        self.assertTrue(first["created"])
        self.assertFalse(second["created"])
        self.assertEqual(first["path"], second["path"])
        self.run_cli("reindex")
        (self.vault / first["path"]).write_text("Alteracion", encoding="utf-8")
        self.assertIn("source-integrity", [issue["type"] for issue in brain.lint(self.vault)["issues"]])

    def test_idempotent_publication_and_revision_history(self):
        first = self.publish()
        again = self.publish()
        self.assertTrue(first["changed"])
        self.assertFalse(again["changed"])
        self.body.write_text("Explicacion corregida con evidencia nueva.", encoding="utf-8")
        changed = self.publish()
        self.assertEqual(first["id"], changed["id"])
        history = list((self.vault / ".brain" / "history").rglob("*.md"))
        self.assertEqual(len(history), 1)
        self.assertIn("carga idempotente", history[0].read_text(encoding="utf-8"))

    def test_retrieval_from_another_project_uses_same_vault(self):
        self.publish(title="Idempotencia y repeticiones")
        project_b = self.base / "project-b"
        project_b.mkdir()
        results = self.run_cli("search", "IDEMPOTÉNCIA", cwd=project_b)
        self.assertEqual(results[0]["path"], "30-conocimiento/idempotencia.md")
        self.assertEqual(list(project_b.iterdir()), [])
        self.assertIn("project-a", (self.vault / results[0]["path"]).read_text(encoding="utf-8"))

    def test_path_escape_and_system_writes_are_rejected(self):
        for path in ["../escape.md", "80-fuentes/change.md", "AGENTS.md"]:
            with self.assertRaises(ValueError):
                brain.publish(self.vault, path, "Bad", self.body, ["fixture"], "a", "idea", "propuesto")
        self.assertFalse((self.base / "escape.md").exists())

    def test_broken_link_and_stale_index_are_reported(self):
        self.publish()
        with (self.vault / "30-conocimiento/idempotencia.md").open("a", encoding="utf-8") as output:
            output.write("\n[No existe](missing.md)\n")
        report = brain.lint(self.vault)
        self.assertIn("broken-link", [issue["type"] for issue in report["issues"]])
        extra = self.vault / "30-conocimiento/otra.md"
        extra.write_text("# Otra\n\nUna nota nueva.\n", encoding="utf-8")
        self.assertIn("stale-index", [issue["type"] for issue in brain.lint(self.vault)["issues"]])

    def test_catalog_summaries_do_not_relocate_relative_links(self):
        self.publish(path="30-conocimiento/otra.md", title="Otra nota")
        self.body.write_text("Consulta [otra nota](otra.md) para continuar.\n", encoding="utf-8")
        self.publish()
        index = (self.vault / "index.md").read_text(encoding="utf-8")
        self.assertIn("— Consulta otra nota para continuar.", index)
        self.assertTrue(brain.lint(self.vault)["ok"])

    def test_concurrent_publications_do_not_lose_events_or_index_entries(self):
        processes = [subprocess.Popen([sys.executable, str(SCRIPT), "--vault", str(self.vault), "publish", "--path", f"30-conocimiento/nota-{i}.md", "--title", f"Nota {i}", "--body", str(self.body), "--source", "fixture"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8") for i in range(4)]
        for process in processes:
            out, err = process.communicate(timeout=20)
            self.assertEqual(process.returncode, 0, err or out)
        records = (self.vault / ".brain/events.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(records), 4)
        self.assertEqual(len(list(brain.notes(self.vault))), 4)
        self.assertEqual((self.vault / "index.md").read_text(encoding="utf-8"), brain.catalog(self.vault))

    def test_backup_contains_sources_notes_and_revision_history(self):
        self.publish()
        source = self.run_cli("capture-source", "--input", str(self.body), "--title", "Fuente", "--origin", "fixture")
        result = self.run_cli("backup")
        with zipfile.ZipFile(result["path"]) as archive:
            self.assertIn("30-conocimiento/idempotencia.md", archive.namelist())
            self.assertIn(source["path"], archive.namelist())
            self.assertNotIn(".brain/write.lock", archive.namelist())


if __name__ == "__main__":
    unittest.main()
