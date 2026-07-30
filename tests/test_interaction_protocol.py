from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def compact(value: str) -> str:
    return " ".join(value.split())


class InteractionProtocolTests(unittest.TestCase):
    def test_version_3_separates_checklist_and_interaction_policy(self) -> None:
        for path in (
            "AGENTS.md",
            "agents/sage/commands/sage.md",
            "agents/sage/commands/sage-setting.md",
        ):
            content = read(path)
            with self.subTest(path=path):
                self.assertIn('"version": 3', content)
                self.assertIn('"mode": "auto"', content)
                self.assertIn('"runPolicy": "until-gate"', content)
                self.assertIn('"questionPolicy": "batch-independent"', content)
                self.assertIn('"maxQuestionsPerCheckpoint": 3', content)
                self.assertIn('"autoDecideReversible": true', content)
                self.assertIn('"continueAfterHandoff": true', content)

    def test_picker_is_capability_aware_and_auto_never_prompts(self) -> None:
        agents = compact(read("AGENTS.md"))
        sage = compact(read("agents/sage/commands/sage.md"))

        for content in (agents, sage):
            self.assertIn("Native multi-select", content)
            self.assertIn("Structured single-select", content)
            self.assertIn("Run recommended", content)
            self.assertIn("Use saved defaults", content)
            self.assertIn("-e2e +security", content)
            self.assertIn("provider name", content)

        self.assertIn("mode:auto` never opens any of these pickers", agents)
        self.assertIn("do not open any picker", sage)
        self.assertNotIn(
            "Preferred structured picker, else Markdown fallback (numbers",
            sage,
        )

        public_docs = compact(
            "\n".join(
                (
                    read("README.md"),
                    read("docs/run-until-gate.md"),
                    read("landing/index.html"),
                )
            )
        )
        self.assertIn("native multi-select", public_docs.lower())
        self.assertIn("Recommended/Defaults/Customize", public_docs)
        self.assertNotIn("once you confirm", public_docs)

    def test_run_until_gate_continues_across_child_handoffs(self) -> None:
        agents = compact(read("AGENTS.md"))
        sage = compact(read("agents/sage/commands/sage.md"))

        for marker in (
            "Run-until-gate loop",
            "Closing a ticket, command, handoff, checkpoint, or phase",
            "continueAfterHandoff",
            "true completion",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, agents)

        self.assertIn("run until gate", sage.lower())
        self.assertIn("requirements-clear", sage)
        self.assertIn("spec-ready", sage)
        self.assertIn("design-clear", sage)

        child_markers = {
            "agents/sage/commands/sage-grill.md": "return `requirements-clear`",
            "agents/sage/commands/sage-flow.md": "return `design-clear`",
            "agents/sage/commands/sage-wayfinder.md": "return `spec-ready`",
            "agents/sage/commands/sage-unit-test.md": "return the test evidence",
            "agents/sage/commands/sage-e2e-test.md": "return the E2E evidence",
            "agents/sage/commands/sage-security-review.md": "return findings/control evidence",
        }
        for path, marker in child_markers.items():
            with self.subTest(path=path):
                self.assertIn(marker, read(path))

    def test_wayfinder_uses_frontier_waves_not_one_ticket_sessions(self) -> None:
        surfaces = "\n".join(
            (
                read("agents/sage/commands/sage-wayfinder.md"),
                read("agents/sage/flows/request-routing-wayfinder-flow.md"),
                read("docs/request-routing-wayfinder.md"),
            )
        )

        for marker in (
            "Work frontier waves",
            "recompute the frontier",
            "multiple independent tickets",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker.lower(), surfaces.lower())

        for stale in (
            "One session resolves at most one non-research ticket",
            "Resolve exactly one non-research ticket",
            "หนึ่ง session ปิดไม่เกินหนึ่ง non-research ticket",
            "one-ticket-per-session",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale.lower(), surfaces.lower())

    def test_question_policy_batches_only_independent_decisions(self) -> None:
        surfaces = "\n".join(
            (
                read("AGENTS.md"),
                read("agents/sage/commands/sage-grill.md"),
                read("agents/sage/commands/sage-flow.md"),
            )
        )

        self.assertIn("batch-independent", surfaces)
        self.assertIn("maxQuestionsPerCheckpoint", surfaces)
        self.assertIn("independent decisions", surfaces)
        self.assertIn("dependent", surfaces)

    def test_plan_flow_trigger_is_not_file_count_or_routine_bug(self) -> None:
        agents = compact(read("AGENTS.md"))
        sage = compact(read("agents/sage/commands/sage.md"))

        self.assertIn(
            "Multi-file size, an ordinary bug, or a dependency change alone is not enough",
            agents,
        )
        self.assertIn(
            "Do not recommend it merely because a task is `logic`, `multi-file`, a routine bug fix, or a dependency change",
            sage,
        )
        self.assertNotIn(
            "recommend for `logic`, `multi-file`, `backend-api`",
            sage,
        )

    def test_roles_are_compact_approved_lenses_without_local_gates(self) -> None:
        role_paths = sorted((ROOT / "agents/sage/roles").glob("role-*.md"))
        self.assertTrue(role_paths)

        forbidden = re.compile(r"\b(ask|wait|stop|approval)\b", re.IGNORECASE)
        for path in role_paths:
            content = path.read_text(encoding="utf-8")
            body_words = re.findall(r"\b[\w'-]+\b", content.split("---", 2)[-1])
            with self.subTest(path=path.name):
                self.assertIn("status: approved", content)
                self.assertIn("## Expertise", content)
                self.assertIn("## Pitfalls", content)
                self.assertIn("## How I work", content)
                self.assertIsNone(forbidden.search(content))
                self.assertGreaterEqual(len(body_words), 80)
                self.assertLessEqual(len(body_words), 170)

    def test_interaction_preferences_cannot_disable_safety_gates(self) -> None:
        agents = compact(read("AGENTS.md"))
        flow = compact(read("agents/sage/flows/run-until-gate-flow.md"))

        for marker in (
            "Interaction settings never weaken the risk gates",
            "HIGH or destructive/irreversible work",
            "auth/payment/PII",
            "failed critical control",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, agents)

        self.assertIn("Safety gates", flow)
        self.assertIn("ทำให้ gate อ่อนลงไม่ได้", flow)


if __name__ == "__main__":
    unittest.main()
