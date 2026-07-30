from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def compact(value: str) -> str:
    return " ".join(value.split())


class ProjectDNASpecContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.flow = read("agents/sage/flows/project-dna-flow.md")
        self.docs = read("docs/project-dna.md")
        self.surfaces = "\n".join((self.flow, self.docs))

    def test_public_docs_are_honest_about_runtime_status(self) -> None:
        readme = read("README.md")
        changelog = read("CHANGELOG.md")

        self.assertIn("specified, not shipped", readme)
        self.assertIn("specification only", changelog.lower())
        self.assertIn("specification only", compact(self.docs))
        self.assertIn("ยังไม่ shipped", compact(self.docs))

        for stale_claim in (
            "Project DNA is now available",
            "Project DNA runtime is available",
            "Project DNA runtime is shipped",
        ):
            with self.subTest(stale_claim=stale_claim):
                self.assertNotIn(stale_claim, "\n".join((readme, changelog, self.docs)))

    def test_spec_defines_all_dna_facets_and_progressive_levels(self) -> None:
        for facet in (
            "Project Identity",
            "Business DNA",
            "Architecture DNA",
            "Workflow DNA",
            "Design DNA",
            "Critical Flow DNA",
            "Reusable Assets",
            "Convention Graph",
            "Impact Graph",
            "Risk Signals",
        ):
            with self.subTest(facet=facet):
                self.assertIn(facet, self.surfaces)

        for level in ("L0", "L1", "L2", "L3", "L4"):
            with self.subTest(level=level):
                self.assertIn(level, self.surfaces)

        self.assertIn("100–300 tokens", self.surfaces)
        self.assertIn("safety kernel", self.surfaces)

    def test_claims_cannot_hide_provenance_or_approval_state(self) -> None:
        for marker in (
            "observed",
            "declared",
            "inferred",
            "approved",
            "provenance",
            "confidence",
            "freshness",
            "conflicts",
            "non-binding staging",
            "authenticated human",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker.lower(), self.surfaces.lower())

        decision = read(
            "agents/sage/sage-product/decisions/"
            "separate-observations-from-approved-knowledge.md"
        )
        self.assertIn("never become binding", decision)
        self.assertIn(
            "cannot lower a safety gate",
            read("agents/sage/sage-product/context.md"),
        )

    def test_tool_contract_is_provider_neutral_and_complete(self) -> None:
        for tool in (
            "getSageCapabilities",
            "prepareProjectDNA",
            "refreshProjectDNA",
            "getProjectDNAStatus",
            "getProjectDNA",
            "getBusinessContext",
            "getArchitectureDNA",
            "getWorkflowDNA",
            "getDesignDNA",
            "getImpact",
            "getRisks",
            "getReusableAssets",
            "getConventions",
            "proposeKnowledge",
            "reviewKnowledgeProposal",
        ):
            with self.subTest(tool=tool):
                self.assertIn(tool, self.flow)

        for field in (
            '"schemaVersion"',
            '"snapshotId"',
            '"scope"',
            '"freshness"',
            '"confidence"',
            '"provenance"',
            '"conflicts"',
            '"continuation"',
            '"warnings"',
        ):
            with self.subTest(field=field):
                self.assertIn(field, self.flow)

        self.assertIn("provider-neutral", self.flow)
        self.assertIn("ไม่เดาจากชื่อ provider", self.flow)

    def test_freshness_and_refresh_are_evidence_based_and_atomic(self) -> None:
        for marker in (
            "source fingerprint",
            "detector versions",
            "fingerprint reconciliation",
            "atomic activate",
            "last complete snapshot",
            "one writer per scope",
            "hard-coded domain cascade ห้ามนับเป็น proof",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker.lower(), self.surfaces.lower())

        context = read("agents/sage/sage-product/context.md")
        self.assertIn("A timestamp alone never proves freshness", context)

    def test_spec_has_migration_quality_and_failure_gates(self) -> None:
        for marker in (
            "Quality evaluation",
            "Compatibility and migration",
            "false-confidence",
            "precision",
            "recall",
            "rollback",
            "Tool unavailable",
            "SCOPE_FORBIDDEN",
            "DNA_CONFLICT",
            "current Markdown fallback",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker.lower(), self.flow.lower())


if __name__ == "__main__":
    unittest.main()
