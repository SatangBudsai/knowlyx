import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def manifest_entries(name: str) -> list[str]:
    entries: list[str] = []
    for raw in read(f"agents/sage/{name}").splitlines():
        value = raw.rstrip("\r")
        if value and not value.startswith("#"):
            entries.append(value)
    return entries


def shell_executable() -> str | None:
    if os.name == "nt":
        candidates = [
            r"C:\Program Files\Git\bin\sh.exe",
            r"C:\Program Files\Git\bin\bash.exe",
            shutil.which("sh"),
        ]
    else:
        candidates = [shutil.which("sh"), shutil.which("bash")]
    return next((value for value in candidates if value and Path(value).is_file()), None)


class InstallerDistributionTests(unittest.TestCase):
    def run_installer(
        self,
        platform: str,
        target: Path,
        source: Path = ROOT,
        expect_success: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["SAGE_TOOLS"] = "codex"
        env["SAGE_INSTALL_SOURCE"] = (
            source.as_posix() if platform == "shell" else str(source)
        )

        if platform == "shell":
            executable = shell_executable()
            if not executable:
                self.skipTest("No POSIX shell available")
            command = [executable, str(ROOT / "install.sh")]
        else:
            executable = shutil.which("powershell") or shutil.which("pwsh")
            if not executable:
                self.skipTest("No PowerShell available")
            command = [
                executable,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ROOT / "install.ps1"),
            ]

        result = subprocess.run(
            command,
            cwd=target,
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if expect_success:
            self.assertEqual(
                result.returncode,
                0,
                f"{platform} installer failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
            )
        else:
            self.assertNotEqual(
                result.returncode,
                0,
                f"{platform} installer unexpectedly succeeded\n{result.stdout}",
            )
        return result

    def assert_fresh_install(self, target: Path, output: str) -> None:
        self.assertEqual(
            (target / "AGENTS.md").read_text(encoding="utf-8"),
            read("AGENTS.md"),
        )
        for relative_path in manifest_entries("install-manifest.txt"):
            with self.subTest(relative_path=relative_path):
                self.assertEqual(
                    (target / relative_path).read_text(encoding="utf-8"),
                    read(relative_path),
                )

        source_commands = {
            path.name for path in (ROOT / "agents/sage/commands").glob("*.md")
        }
        target_commands = {
            path.name for path in (target / "agents/sage/commands").glob("*.md")
        }
        self.assertEqual(target_commands, source_commands)
        self.assertTrue((target / "agents/sage/index.md").is_file())
        self.assertTrue((target / "agents/sage/roles/role-architect.md").is_file())
        self.assertEqual(
            (target / ".codex/prompts/sage.md").read_text(encoding="utf-8"),
            read("integrations/.codex/prompts/sage.md"),
        )
        self.assertIn("preflight passed", output)
        self.assertIn(
            "Project DNA spec: agents/sage/flows/project-dna-flow.md",
            output,
        )

    def assert_safe_upgrade(self, platform: str) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            first = self.run_installer(platform, target)
            self.assert_fresh_install(target, first.stdout)

            sentinels = {
                "agents/sage/index.md": "custom index\n",
                "agents/sage/roles/role-architect.md": "custom role\n",
                "agents/sage/acme/rules.md": "custom domain\n",
                "agents/sage/flows/custom-flow.md": "custom flow\n",
                "agents/sage/sage-product/custom.md": "custom sage product note\n",
                "docs/custom.md": "custom docs\n",
                ".sage-local.json": '{"custom": true}\n',
                ".codex/prompts/sage-custom.md": "custom adapter\n",
            }
            for relative_path, content in sentinels.items():
                path = target / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")

            (target / "agents/sage/flows/project-dna-flow.md").write_text(
                "stale managed spec\n",
                encoding="utf-8",
            )
            (target / "agents/sage/commands/retired.md").write_text(
                "retired command\n",
                encoding="utf-8",
            )
            (target / ".codex/prompts/sage.md").write_text(
                "stale managed adapter\n",
                encoding="utf-8",
            )

            second = self.run_installer(platform, target)
            self.assert_fresh_install(target, second.stdout)
            self.assertFalse((target / "agents/sage/commands/retired.md").exists())
            for relative_path, content in sentinels.items():
                with self.subTest(platform=platform, sentinel=relative_path):
                    self.assertEqual(
                        (target / relative_path).read_text(encoding="utf-8"),
                        content,
                    )

    def source_fixture(self, destination: Path) -> Path:
        source = destination / "source"
        source.mkdir()
        shutil.copy2(ROOT / "AGENTS.md", source / "AGENTS.md")
        shutil.copytree(ROOT / "agents", source / "agents")
        shutil.copytree(ROOT / "integrations", source / "integrations")
        return source

    def malformed_source(self, destination: Path) -> Path:
        source = self.source_fixture(destination)
        manifest = source / "agents/sage/install-manifest.txt"
        manifest.write_text(
            manifest.read_text(encoding="utf-8") + "../escape.md\n",
            encoding="utf-8",
        )
        return source

    def assert_traversal_rejected_before_write(self, platform: str) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.malformed_source(root)
            target = root / "target"
            target.mkdir()
            sentinel = target / "sentinel.txt"
            sentinel.write_text("keep\n", encoding="utf-8")

            result = self.run_installer(
                platform,
                target,
                source=source,
                expect_success=False,
            )

            self.assertIn("unsafe install manifest path", result.stdout + result.stderr)
            self.assertFalse((target / "AGENTS.md").exists())
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep\n")
            self.assertFalse((root / "escape.md").exists())

    def assert_same_source_and_target_rejected(self, platform: str) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.source_fixture(root)
            sentinel = source / "sentinel.txt"
            sentinel.write_text("keep\n", encoding="utf-8")

            result = self.run_installer(
                platform,
                source,
                source=source,
                expect_success=False,
            )

            self.assertIn(
                "SAGE_INSTALL_SOURCE must not be the target repository",
                result.stdout + result.stderr,
            )
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep\n")

    def test_manifests_are_exact_complete_and_source_backed(self) -> None:
        install_entries = manifest_entries("install-manifest.txt")
        adapter_entries = manifest_entries("adapter-manifest.txt")

        self.assertEqual(len(install_entries), len(set(install_entries)))
        self.assertEqual(len(adapter_entries), len(set(adapter_entries)))
        self.assertIn("agents/sage/flows/project-dna-flow.md", install_entries)
        self.assertIn(
            "agents/sage/flows/installer-managed-assets-flow.md",
            install_entries,
        )
        self.assertIn("agents/sage/protocol/index.md", install_entries)
        self.assertIn("agents/sage/sage-product/index.md", install_entries)
        self.assertNotIn("docs/project-dna.md", install_entries)

        for relative_path in install_entries:
            with self.subTest(relative_path=relative_path):
                self.assertFalse(Path(relative_path).is_absolute())
                self.assertNotIn("..", Path(relative_path).parts)
                self.assertTrue((ROOT / relative_path).is_file())

        for basename in adapter_entries:
            with self.subTest(basename=basename):
                self.assertRegex(basename, r"^[a-z0-9][a-z0-9-]*$")

        adapter_sources = {
            path.stem
            for pattern in (
                "integrations/.claude/commands/*.md",
                "integrations/.codex/prompts/*.md",
                "integrations/.cursor/rules/*.mdc",
                "integrations/.windsurf/rules/*.md",
                "integrations/.clinerules/*.md",
            )
            for path in ROOT.glob(pattern)
        }
        adapter_sources.update(
            path.name.removesuffix(".instructions.md")
            for path in ROOT.glob("integrations/.github/instructions/*.instructions.md")
        )
        self.assertTrue(adapter_sources)
        self.assertTrue(adapter_sources.issubset(set(adapter_entries)))

    def test_installers_share_manifests_and_avoid_broad_adapter_deletion(self) -> None:
        shell = read("install.sh")
        powershell = read("install.ps1")

        for content in (shell, powershell):
            self.assertIn("install-manifest.txt", content)
            self.assertIn("adapter-manifest.txt", content)
            self.assertIn("SAGE_INSTALL_SOURCE", content)
            self.assertIn("preflight passed", content)

        self.assertNotIn("find \"$src\" -name 'sage*'", shell)
        self.assertNotIn("-Filter 'sage*'", powershell)

    def test_shell_fresh_install_upgrade_and_preservation(self) -> None:
        self.assert_safe_upgrade("shell")

    def test_powershell_fresh_install_upgrade_and_preservation(self) -> None:
        self.assert_safe_upgrade("powershell")

    def test_shell_rejects_manifest_traversal_before_write(self) -> None:
        self.assert_traversal_rejected_before_write("shell")

    def test_powershell_rejects_manifest_traversal_before_write(self) -> None:
        self.assert_traversal_rejected_before_write("powershell")

    def test_shell_rejects_local_source_equal_to_target(self) -> None:
        self.assert_same_source_and_target_rejected("shell")

    def test_powershell_rejects_local_source_equal_to_target(self) -> None:
        self.assert_same_source_and_target_rejected("powershell")


if __name__ == "__main__":
    unittest.main()
