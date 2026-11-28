"""Test IPAM-specific focused test dispatch."""

import os
import sys
from unittest import TestCase
from unittest.mock import patch

import runtests


class TestFocusedRunner(TestCase):
    def test_sample_label_enables_sample_mode_before_django_setup(self):
        with (
            patch.dict(os.environ),
            patch.object(sys, "argv", ["runtests.py"]),
            patch("django.setup") as setup,
            patch("runtests.validate_test_labels"),
        ):
            os.environ.pop("SAMPLE_APP", None)
            setup.side_effect = lambda: self.assertEqual(
                os.environ.get("SAMPLE_APP"), "1"
            )
            runtests.run_focused_tests(["openwisp2.sample_ipam.tests.TestModels"])
            setup.assert_called_once()
