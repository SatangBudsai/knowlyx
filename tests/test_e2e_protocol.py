from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
COMMAND_PATH = "agents/sage/commands/sage-e2e-test.md"


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


class E2EProtocolTests(unittest.TestCase):
    def test_workflow_is_autonomous_and_behavior_first(self) -> None:
        command = read(COMMAND_PATH)

        required = (
            "Plan, implement, run, debug, and validate",
            "without asking for routine confirmation",
            "Plan high-value journeys first",
            "Explore real behavior when possible",
            "Record expected behavior before each test",
            "Run continuously",
            "Continue autonomously until these criteria are met",
        )
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, command)

        self.assertNotIn("Ask before running", command)

    def test_browser_runner_and_failure_contracts_are_explicit(self) -> None:
        command = read(COMMAND_PATH)

        for phrase in (
            "interactive browser to discover or disambiguate behavior",
            "runner to encode repeatable regression coverage",
            "### A. Test issue",
            "### B. Application issue",
            "### C. Environment/infrastructure issue",
            "Never use arbitrary sleeps",
            "no meaningful browser, console, network, backend, or runner error was ignored",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, command)

    def test_model_routing_is_portable_with_optional_codex_mapping(self) -> None:
        command = read(COMMAND_PATH)

        self.assertIn("provider-, language-, and framework-neutral", command)
        self.assertIn("Optional Codex mapping", command)
        self.assertIn("Terra", command)
        self.assertIn("Luna", command)
        self.assertIn("Sol", command)
        self.assertIn("This mapping is an optimization, not a requirement", command)
        self.assertIn("Never exceed the session ceiling", command)
        self.assertIn("When delegation is unavailable", command)


if __name__ == "__main__":
    unittest.main()
