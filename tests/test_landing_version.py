from pathlib import Path
import re
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class LandingVersionTests(unittest.TestCase):
    def test_landing_version_matches_latest_git_tag(self) -> None:
        latest_tag = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        landing = (ROOT / "landing/index.html").read_text(encoding="utf-8")

        meta = re.search(
            r'<meta\s+name="sage-version"\s+content="([^"]+)"\s*/>',
            landing,
        )
        self.assertIsNotNone(meta)
        self.assertEqual(meta.group(1), latest_tag)
        self.assertEqual(landing.count(f">{latest_tag}</span"), 2)
        self.assertEqual(
            landing.count(f'aria-label="Current Sage version {latest_tag}"'),
            2,
        )


if __name__ == "__main__":
    unittest.main()
