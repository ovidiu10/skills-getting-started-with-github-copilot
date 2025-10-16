#!/usr/bin/env python3
"""
Test runner script for the Mergington High School API.
Usage: python run_tests.py [options]
"""
import subprocess
import sys
from pathlib import Path


def run_tests(with_coverage: bool = True, verbose: bool = True) -> int:
    """Run the test suite with optional coverage and verbosity."""
    project_root = Path(__file__).parent
    
    cmd = [sys.executable, "-m", "pytest", "tests/"]
    
    if verbose:
        cmd.append("-v")
    
    if with_coverage:
        cmd.extend([
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-report=html"
        ])
    
    print(f"Running tests from: {project_root}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, cwd=project_root)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run the test suite")
    parser.add_argument("--no-coverage", action="store_true", 
                       help="Run tests without coverage report")
    parser.add_argument("--quiet", action="store_true",
                       help="Run tests with minimal output")
    
    args = parser.parse_args()
    
    exit_code = run_tests(
        with_coverage=not args.no_coverage,
        verbose=not args.quiet
    )
    
    sys.exit(exit_code)