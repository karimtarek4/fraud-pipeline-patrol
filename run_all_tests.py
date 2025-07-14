#!/usr/bin/env python3
"""
Simple Test Runner for Fraud Pipeline Patrol

This script runs all tests in the project sequentially using the same pattern
that works manually: PYTHONPATH=. pytest <test_file>

Usage:
    python run_all_tests.py [options]

Options:
    --verbose, -v     : Run tests with verbose output
    --quiet, -q       : Run tests with minimal output
    --help, -h        : Show this help message
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

class SimpleTestRunner:
    """Simple test runner that executes pytest commands sequentially."""
    
    def __init__(self, verbose=False, quiet=False):
        self.verbose = verbose
        self.quiet = quiet
        self.project_root = Path(__file__).parent
        
        # Detect the right pytest to use
        self.pytest_cmd = self.find_pytest()
        
        # List of all test files
        self.test_files = [
            "tests/test_postgres_helper.py",
            "tests/test_actualdata_postgres_helper.py", 
            "tests/test_generate_synthetic_fraud_data.py",
            "tests/test_dag_parsing_and_validation.py",
            "tests/test_dag_structure_and_datasets.py"
        ]
        
        self.results = []
        
    def find_pytest(self):
        """Find the right pytest executable to use."""
        # Try different pytest locations in order of preference
        pytest_candidates = [
            "pytest",  # System pytest (what works manually)
            ".venv/bin/pytest",  # Virtual environment pytest
            "/opt/anaconda3/bin/pytest",  # Anaconda pytest
        ]
        
        for pytest_path in pytest_candidates:
            try:
                # Test if this pytest can import airflow successfully
                env = os.environ.copy()
                env['PYTHONPATH'] = '.'
                
                result = subprocess.run(
                    [pytest_path, "--version"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                    env=env
                )
                
                if result.returncode == 0:
                    # Test if this pytest environment has airflow
                    airflow_test = subprocess.run(
                        [pytest_path.replace("pytest", "python"), "-c", "from airflow.models import DagBag"],
                        capture_output=True,
                        text=True,
                        cwd=self.project_root,
                        env=env
                    )
                    
                    if airflow_test.returncode == 0:
                        if not self.quiet:
                            print(f"✅ Using pytest: {pytest_path} (with Airflow support)")
                        return pytest_path
                    else:
                        if not self.quiet:
                            print(f"⚠️  {pytest_path} available but no Airflow support")
                        
            except Exception:
                continue
        
        # Fallback to system pytest
        if not self.quiet:
            print("⚠️  Using fallback pytest (DAG tests may fail)")
        return "pytest"
        
    def run_single_test(self, test_file):
        """Run a single test file using PYTHONPATH=. pytest pattern."""
        if not (self.project_root / test_file).exists():
            if not self.quiet:
                print(f"⚠️  Warning: {test_file} not found, skipping...")
            return True  # Skip missing files
        
        # Build command exactly like you run it manually
        cmd = [self.pytest_cmd, test_file]
        
        if self.verbose:
            cmd.append("-v")
        elif self.quiet:
            cmd.append("-q")
        
        if not self.quiet:
            print(f"🚀 Running: PYTHONPATH=. {' '.join(cmd)}")
        
        try:
            # Set environment exactly like your manual command
            env = os.environ.copy()
            env['PYTHONPATH'] = '.'
            
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                env=env,
                capture_output=self.quiet,
                text=True
            )
            
            success = result.returncode == 0
            self.results.append({
                "file": test_file,
                "success": success,
                "return_code": result.returncode
            })
            
            if self.quiet and result.stdout:
                # Show summary line in quiet mode
                lines = result.stdout.strip().split('\n')
                summary_lines = [line for line in lines if 'passed' in line or 'failed' in line or 'error' in line]
                if summary_lines:
                    print(f"{test_file}: {summary_lines[-1]}")
            
            if not self.quiet:
                if success:
                    print(f"✅ {test_file} - PASSED")
                else:
                    print(f"❌ {test_file} - FAILED (exit code: {result.returncode})")
                print()
            
            return success
            
        except Exception as e:
            if not self.quiet:
                print(f"❌ Error running {test_file}: {e}")
            self.results.append({
                "file": test_file,
                "success": False,
                "error": str(e)
            })
            return False
    
    def print_summary(self):
        """Print test summary."""
        if not self.results:
            print("No tests were run.")
            return False
        
        passed = sum(1 for r in self.results if r.get("success", False))
        total = len(self.results)
        failed = total - passed
        
        if self.quiet and failed == 0:
            print(f"✅ All {total} test files passed!")
            return True
        
        print("\n" + "="*50)
        print("📊 TEST SUMMARY")
        print("="*50)
        print(f"Total test files: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print()
        
        for result in self.results:
            status = "✅ PASSED" if result.get("success", False) else "❌ FAILED"
            print(f"{status} - {result['file']}")
        
        print("="*50)
        
        if failed == 0:
            print("🎉 All tests passed!")
            return True
        else:
            print(f"❌ {failed} test file(s) failed.")
            return False
    
    def run_all_tests(self):
        """Run all test files sequentially."""
        start_time = datetime.now()
        
        if not self.quiet:
            print("🧪 Fraud Pipeline Patrol - Simple Test Runner")
            print("=" * 50)
            print(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Running {len(self.test_files)} test files...")
            print()
        
        all_success = True
        for test_file in self.test_files:
            success = self.run_single_test(test_file)
            all_success = all_success and success
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        if not self.quiet:
            print(f"⏱️  Total execution time: {duration}")
        
        summary_success = self.print_summary()
        
        return all_success and summary_success

def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="Run all tests for the Fraud Pipeline Patrol project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_all_tests.py                    # Run all tests
    python run_all_tests.py -v                 # Run with verbose output  
    python run_all_tests.py -q                 # Run quietly
        """
    )
    
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="Run tests with verbose output")
    parser.add_argument("-q", "--quiet", action="store_true",
                       help="Run tests with minimal output")
    
    args = parser.parse_args()
    
    # Create and run test runner
    runner = SimpleTestRunner(
        verbose=args.verbose,
        quiet=args.quiet
    )
    
    try:
        success = runner.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
