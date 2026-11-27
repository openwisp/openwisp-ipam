"""Verify that the focused CI entry point only accepts test arguments."""

import subprocess
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


if __name__ == "__main__":
    unittest.main()
