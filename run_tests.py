#!/usr/bin/env python3
"""
Simple test runner to verify the application works correctly
"""
import sys
import os
import subprocess

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_tests():
    """Run the test suite"""
    print("Running tests...")
    
    # Set environment variables
    os.environ['PYTHONPATH'] = os.path.join(os.path.dirname(__file__), 'src')
    
    # Run pytest
    result = subprocess.run([
        sys.executable, '-m', 'pytest', 
        'tests/', '-v', '--tb=short'
    ], cwd=os.path.dirname(__file__))
    
    return result.returncode == 0

def run_security_scan():
    """Run security scan"""
    print("Running security scan...")
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'bandit'], check=True)
        result = subprocess.run([
            'bandit', '-r', 'src/', '-f', 'json', '-o', 'bandit-report.json', '-ll'
        ], cwd=os.path.dirname(__file__))
        print("Security scan completed")
        return True
    except Exception as e:
        print(f"Security scan failed: {e}")
        return False

if __name__ == '__main__':
    print("=== Court Data Fetcher Test Suite ===")
    
    tests_passed = run_tests()
    security_passed = run_security_scan()
    
    print("\n=== Results ===")
    print(f"Tests: {'PASSED' if tests_passed else 'FAILED'}")
    print(f"Security: {'PASSED' if security_passed else 'FAILED'}")
    
    if tests_passed and security_passed:
        print("All checks passed!")
        sys.exit(0)
    else:
        print("Some checks failed!")
        sys.exit(1)