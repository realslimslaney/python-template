"""Verify that complete client instructions remain synchronized and usable."""

import importlib.util
import shutil
import tempfile
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("agent_sync", ROOT / "scripts/sync_agent_instructions.py")
agent_sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(agent_sync)


class AgentInstructionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        shutil.copyfile(ROOT / "AGENTS.md", self.root / "AGENTS.md")
        shutil.copytree(ROOT / ".agents/skills", self.root / ".agents/skills")
        agent_sync.sync(self.root)

    def test_native_agents_contain_full_skill_procedures(self):
        for role in agent_sync.ROLES:
            source = (self.root / f".agents/skills/{role}/SKILL.md").read_text(encoding="utf-8")
            body = source.split("---", 2)[2].strip()
            claude = (self.root / f".claude/agents/{role}.md").read_text(encoding="utf-8")
            codex = tomllib.loads((self.root / f".codex/agents/{role}.toml").read_text(encoding="utf-8"))
            self.assertEqual(claude.split("---", 2)[2].strip(), body)
            self.assertEqual(codex["developer_instructions"].strip(), body)
            self.assertEqual(codex["name"], role.replace("-", "_"))

    def test_missing_or_stale_client_files_fail_until_synchronized(self):
        for relative, content in agent_sync.outputs(self.root).items():
            with self.subTest(file=str(relative)):
                path = self.root / relative
                path.unlink()
                self.assertTrue(agent_sync.check(self.root))
                self.assertFalse(path.exists(), "Checking must not silently regenerate files.")
                agent_sync.sync(self.root)
                path.write_text("stale instructions\n", encoding="utf-8")
                self.assertTrue(agent_sync.check(self.root))
                agent_sync.sync(self.root)
                self.assertEqual(path.read_text(encoding="utf-8"), content)
                self.assertEqual(agent_sync.check(self.root), [])

    def test_source_edits_propagate_and_unmanaged_files_survive(self):
        policy = self.root / "AGENTS.md"
        policy.write_text(
            policy.read_text(encoding="utf-8") + "\nUse the project's café fixture.\n", encoding="utf-8"
        )
        skill = self.root / ".agents/skills/committer/SKILL.md"
        skill.write_text(
            skill.read_text(encoding="utf-8") + '\nExplain "quoted" paths and C:\\work.\n', encoding="utf-8"
        )
        extra = self.root / ".claude/agents/custom.md"
        extra.write_text("project-specific agent\n", encoding="utf-8")
        self.assertTrue(agent_sync.check(self.root))
        agent_sync.sync(self.root)
        self.assertEqual(agent_sync.check(self.root), [])
        self.assertEqual(
            (self.root / "CLAUDE.md").read_text(encoding="utf-8"), policy.read_text(encoding="utf-8")
        )
        config = tomllib.loads((self.root / ".codex/agents/committer.toml").read_text(encoding="utf-8"))
        self.assertIn('Explain "quoted" paths and C:\\work.', config["developer_instructions"])
        self.assertEqual(extra.read_text(encoding="utf-8"), "project-specific agent\n")

    def test_invalid_skill_source_is_reported(self):
        (self.root / ".agents/skills/committer/SKILL.md").write_text("No frontmatter\n", encoding="utf-8")
        self.assertTrue(any("frontmatter" in error for error in agent_sync.check(self.root)))


if __name__ == "__main__":
    unittest.main()
