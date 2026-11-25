import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "install_global.py"
spec = importlib.util.spec_from_file_location("install_global", SCRIPT)
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="second-brain-install-test-")
        self.base = Path(self.temporary.name).resolve()
        self.root = self.base / "workspace"
        self.root.mkdir()
        self.user = self.base / "user"
        self.user.mkdir()
        self.config = self.user / "config.toml"
        self.config.write_text('# Configuracion previa\nmodel = "existing-model"\n[mcp_servers.existing]\ncommand = "existing.exe"\n', encoding="utf-8")
        self.instructions = self.user / "AGENTS.md"
        self.instructions.write_text("# Preferencias previas\n\nContenido personal.\n", encoding="utf-8")
        self.skill = self.root / "skill-source"
        self.skill.mkdir()
        (self.skill / "SKILL.md").write_text("Una skill de prueba", encoding="utf-8")
        self.target = self.user / "skills" / "second-brain"
        self.patch = patch.multiple(installer, ROOT=self.root, VAULT=self.root / "second-brain", SOURCE_SKILL=self.skill, CODEX_HOME=self.user, TARGET_SKILL=self.target, CONFIG=self.config, INSTRUCTIONS=self.instructions, MANIFEST=self.root / ".runtime" / "installed.json")
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self.temporary.cleanup()

    def test_install_preserves_other_configuration_and_is_repeatable(self):
        self.assertTrue(installer.apply()["ok"])
        self.assertTrue(installer.apply()["ok"])
        import tomlkit
        text = self.config.read_text(encoding="utf-8")
        document = tomlkit.parse(text)
        self.assertIn("# Configuracion previa", text)
        self.assertEqual(document["model"], "existing-model")
        self.assertEqual(document["mcp_servers"]["existing"]["command"], "existing.exe")
        self.assertEqual(len(document["sandbox_workspace_write"]["writable_roots"]), 2)
        instructions = self.instructions.read_text(encoding="utf-8")
        self.assertIn("Contenido personal.", instructions)
        self.assertEqual(instructions.count(installer.START), 1)
        self.assertTrue(list((self.root / "second-brain-backups").rglob("config.toml")))

    def test_unrelated_existing_skill_is_not_overwritten(self):
        self.target.mkdir(parents=True)
        (self.target / "SKILL.md").write_text("Otra skill", encoding="utf-8")
        previous = self.config.read_bytes()
        with self.assertRaises(ValueError):
            installer.apply()
        self.assertEqual(self.config.read_bytes(), previous)
        self.assertEqual((self.target / "SKILL.md").read_text(encoding="utf-8"), "Otra skill")

    def test_skill_template_resolves_checkout_paths_without_changing_source(self):
        template = "Vault: {{SECOND_BRAIN_VAULT}}\nHelper: {{SECOND_BRAIN_HELPER}}\n"
        (self.skill / "SKILL.md").write_text(template, encoding="utf-8")
        self.assertTrue(installer.apply()["ok"])
        installed = (self.target / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn((self.root / "second-brain").as_posix(), installed)
        self.assertIn((self.root / "second-brain-tools" / "brain.py").as_posix(), installed)
        self.assertNotIn("{{SECOND_BRAIN_", installed)
        self.assertEqual((self.skill / "SKILL.md").read_text(encoding="utf-8"), template)

    def test_incomplete_global_block_is_rejected(self):
        previous = self.config.read_bytes()
        self.instructions.write_text(installer.START + "\nEdicion incompleta", encoding="utf-8")
        with self.assertRaises(ValueError):
            installer.apply()
        self.assertEqual(self.config.read_bytes(), previous)


if __name__ == "__main__":
    unittest.main()
