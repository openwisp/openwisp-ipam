#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Run the standard coverage suites or validate and run focused tests."""

import os
import sys

from openwisp_utils.test.runner import (
    InvalidTestArgument,
    compile_test_label_pattern,
    parse_test_arguments,
    validate_test_labels,
)

sys.path.insert(0, "tests")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openwisp2.settings")


def run_focused_tests(arguments):
    import django

    sample_modules = ("openwisp2.sample_ipam.tests", "openwisp2.sample_users.tests")
    pattern = compile_test_label_pattern(
        module_roots=("openwisp_ipam.tests",), exact_modules=sample_modules
    )
    try:
        labels, flags = parse_test_arguments(
            arguments, pattern, ("--failfast", "--noinput"), require_label=True
        )
        sample_labels = [
            label for label in labels if label.group("module") in sample_modules
        ]
        if sample_labels and len(sample_labels) != len(labels):
            raise InvalidTestArgument(
                "Unsupported test argument: run sample app tests separately"
            )
        if sample_labels:
            os.environ["SAMPLE_APP"] = "1"

        # The test settings look for the Django test subcommand in sys.argv.
        sys.argv[1:] = ["test", *(label.group(0) for label in labels), *flags]
        django.setup()
        validate_test_labels(labels)
    except InvalidTestArgument as error:
        print(error, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    if sys.argv[1:2] == ["--focused"]:
        run_focused_tests(sys.argv[2:])
        execute_from_command_line(sys.argv)
        sys.exit(0)

    args = sys.argv
    args.insert(1, "test")
    if not os.environ.get("SAMPLE_APP", False):
        args.insert(2, "openwisp_ipam")
    else:
        args.insert(2, "openwisp2")
    execute_from_command_line(args)
