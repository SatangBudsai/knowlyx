from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
COMMAND = "agents/sage/commands/sage-refactoring-code.md"


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


class RefactoringCodeSkillTests(unittest.TestCase):
    def test_command_prioritizes_readability_without_weakening_safety(self) -> None:
        command = read(COMMAND)

        required_guidance = (
            "Preserve correctness, security, data integrity",
            "as evidence, not as an excuse",
            "frequency alone does not make",
            "more than roughly two levels of nesting as a review signal",
            "Group primarily by feature/domain ownership",
            "Prefer explicit typed columns for stable core fields",
            "Avoid a universal schema intended to represent every future entity",
            "This skill cannot lower a gate",
            "Do not claim readability from line count alone",
        )
        for guidance in required_guidance:
            with self.subTest(guidance=guidance):
                self.assertIn(guidance, command)

    def test_all_thin_adapters_point_to_the_canonical_command(self) -> None:
        adapters = (
            "integrations/.claude/commands/sage-refactoring-code.md",
            "integrations/.clinerules/sage-refactoring-code.md",
            "integrations/.codex/prompts/sage-refactoring-code.md",
            "integrations/.cursor/rules/sage-refactoring-code.mdc",
            "integrations/.github/instructions/sage-refactoring-code.instructions.md",
            "integrations/.windsurf/rules/sage-refactoring-code.md",
            "integrations/.gemini/commands/sage-refactoring-code.toml",
            "integrations/.codex/skills/sage-refactoring-code/SKILL.md",
        )

        for adapter in adapters:
            with self.subTest(adapter=adapter):
                self.assertTrue((ROOT / adapter).is_file())
                self.assertIn(COMMAND, read(adapter))

        manifest = read("agents/sage/adapter-manifest.txt").splitlines()
        self.assertIn("sage-refactoring-code", manifest)

    def test_codex_skill_has_discovery_metadata(self) -> None:
        skill = read("integrations/.codex/skills/sage-refactoring-code/SKILL.md")
        metadata = read(
            "integrations/.codex/skills/sage-refactoring-code/agents/openai.yaml"
        )

        self.assertIn("name: sage-refactoring-code", skill)
        self.assertIn("database schemas", skill)
        self.assertIn("$sage-refactoring-code", metadata)
        self.assertNotIn("TODO", skill)


if __name__ == "__main__":
    unittest.main()
