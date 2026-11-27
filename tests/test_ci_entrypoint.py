"""Verify that the focused CI entry point only accepts test arguments."""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestCiEntrypoint(unittest.TestCase):
    def test_rejects_unsupported_arguments(self):
        for arguments in (
            ("--settings=other",),
            ("--testrunner=other.Runner",),
            ("--noinput",),
            ("openwisp_ipam.tests.test_missing",),
            ("openwisp_ipam.tests.test_models", "openwisp2.sample_ipam.tests"),
        ):
            with self.subTest(arguments=arguments):
                result = subprocess.run(
                    ["./runtests", *arguments],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("Unsupported test argument", result.stderr)

    def test_focused_labels_select_their_configuration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copy2(ROOT / "runtests", root / "runtests")
            shutil.copy2(ROOT / "runtests.py", root / "runtests.py")
            (root / "django" / "core").mkdir(parents=True)
            (root / "openwisp_ipam" / "tests").mkdir(parents=True)
            (root / "tests" / "openwisp2" / "sample_ipam").mkdir(parents=True)
            for package in (
                root / "django",
                root / "django" / "core",
                root / "openwisp_ipam",
                root / "openwisp_ipam" / "tests",
                root / "tests" / "openwisp2",
                root / "tests" / "openwisp2" / "sample_ipam",
            ):
                (package / "__init__.py").touch()
            (root / "django" / "__init__.py").write_text("def setup(): pass\n")
            (root / "django" / "core" / "management.py").write_text(
                "import json, os\n"
                "def execute_from_command_line(args):\n"
                '    print(json.dumps({"sample": os.environ.get("SAMPLE_APP"), '
                '"args": args[1:]}))\n'
            )
            for module in (
                root / "openwisp_ipam" / "tests" / "test_probe.py",
                root / "tests" / "openwisp2" / "sample_ipam" / "tests.py",
            ):
                module.write_text(
                    "import unittest\n"
                    "class TestProbe(unittest.TestCase):\n"
                    "    def test_ok(self): pass\n"
                )
            for label, sample in (
                ("openwisp_ipam.tests.test_probe.TestProbe.test_ok", None),
                ("openwisp2.sample_ipam.tests.TestProbe.test_ok", "1"),
            ):
                with self.subTest(label=label):
                    result = subprocess.run(
                        [str(root / "runtests"), label, "--noinput"],
                        cwd=root,
                        env={**os.environ, "SAMPLE_APP": ""},
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(
                        json.loads(result.stdout),
                        {"sample": sample or "", "args": ["test", label, "--noinput"]},
                    )


if __name__ == "__main__":
    unittest.main()
