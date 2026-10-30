#!/usr/bin/env python3
"""
Test runner for respysive-slide test suite.

This script provides a convenient way to run tests with various options
and configurations.
"""

import argparse
import importlib.util
import os
import subprocess
import sys
from pathlib import Path


def find_project_root():
    """Find the project root directory."""
    current = Path(__file__).parent
    while current != current.parent:
        if (current / "respysive").exists():
            return current
        current = current.parent
    raise FileNotFoundError("Could not find project root")


def run_tests(args):
    """Run the test suite with specified arguments."""
    project_root = find_project_root()

    # Change to project root directory
    os.chdir(project_root)

    # Add project root to Python path
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Build pytest command
    cmd = ["python", "-m", "pytest"]

    # Add test directories
    if args.unit_only:
        cmd.append("tests/unit/")
    elif args.integration_only:
        cmd.append("tests/integration/")
    else:
        cmd.append("tests/")

    # Add verbosity
    if args.verbose:
        cmd.extend(["-v", "-s"])
    elif args.quiet:
        cmd.append("-q")

    # Add coverage if requested
    if args.coverage:
        cmd.extend(["--cov=respysive", "--cov-report=html", "--cov-report=term-missing"])

    # Add specific test markers
    if args.markers:
        cmd.extend(["-m", args.markers])

    # Add specific test file or function
    if args.test:
        cmd.append(args.test)

    # Add parallel execution if requested
    if args.parallel:
        if importlib.util.find_spec("xdist"):
            cmd.extend(["-n", "auto"])
        else:
            print("Warning: pytest-xdist not installed, running tests sequentially")

    # Add additional pytest arguments
    if args.pytest_args:
        cmd.extend(args.pytest_args.split())

    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd)


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="Test runner for respysive-slide",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_runner.py                     # Run all tests
  python test_runner.py --unit-only         # Run only unit tests
  python test_runner.py --verbose           # Run with verbose output
  python test_runner.py --coverage          # Run with coverage report
  python test_runner.py --test test_slide   # Run specific test file
  python test_runner.py -m maplibre         # Run tests marked with 'maplibre'
  python test_runner.py --parallel          # Run tests in parallel
        """,
    )

    # Test selection options
    test_group = parser.add_mutually_exclusive_group()
    test_group.add_argument("--unit-only", action="store_true", help="Run only unit tests")
    test_group.add_argument("--integration-only", action="store_true", help="Run only integration tests")

    # Output options
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    output_group.add_argument("--quiet", "-q", action="store_true", help="Quiet output")

    # Coverage options
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage analysis")

    # Test filtering options
    parser.add_argument(
        "--markers", "-m", help='Run tests matching given mark expression (e.g., "maplibre", "not slow")'
    )

    parser.add_argument("--test", "-t", help="Run specific test file or test function")

    # Performance options
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel (requires pytest-xdist)")

    # Additional pytest arguments
    parser.add_argument("--pytest-args", help="Additional arguments to pass to pytest")

    # Information options
    parser.add_argument("--list-markers", action="store_true", help="List available test markers")

    args = parser.parse_args()

    if args.list_markers:
        print("Available test markers:")
        markers = [
            "unit - Unit tests",
            "integration - Integration tests",
            "slow - Slow running tests",
            "maplibre - MapLibre related tests",
            "handlers - Handler system tests",
            "presentation - Presentation class tests",
            "slide - Slide class tests",
            "utilities - Utility function tests",
            "requires_matplotlib - Tests requiring matplotlib",
            "requires_plotly - Tests requiring plotly",
            "requires_network - Tests requiring network access",
        ]
        for marker in markers:
            print(f"  {marker}")
        return 0

    # Run the tests
    result = run_tests(args)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
