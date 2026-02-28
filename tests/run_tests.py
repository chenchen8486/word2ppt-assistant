#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统一测试入口脚本
提供便捷的方式来运行不同类型的测试
"""

import os
import sys
import subprocess
from pathlib import Path

def run_unit_tests():
    """运行单元测试"""
    print("Running unit tests...")
    unit_tests_dir = Path(__file__).parent / "unit_tests"
    result = subprocess.run([
        sys.executable, "-m", "pytest", str(unit_tests_dir),
        "-v", "--tb=short"
    ])
    return result.returncode == 0

def run_integration_tests():
    """运行集成测试"""
    print("Running integration tests...")
    integration_tests_dir = Path(__file__).parent / "integration_tests"
    result = subprocess.run([
        sys.executable, "-m", "pytest", str(integration_tests_dir),
        "-v", "--tb=short"
    ])
    return result.returncode == 0

def run_all_tests():
    """运行所有测试"""
    print("Running all tests...")
    tests_dir = Path(__file__).parent
    result = subprocess.run([
        sys.executable, "-m", "pytest", str(tests_dir),
        "-v", "--tb=short"
    ])
    return result.returncode == 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py [unit|integration|all]")
        print("  unit: Run unit tests only")
        print("  integration: Run integration tests only")
        print("  all: Run all tests")
        return

    test_type = sys.argv[1].lower()

    if test_type == "unit":
        success = run_unit_tests()
    elif test_type == "integration":
        success = run_integration_tests()
    elif test_type == "all":
        success = run_all_tests()
    else:
        print(f"Unknown test type: {test_type}")
        print("Usage: python run_tests.py [unit|integration|all]")
        return

    if success:
        print("Tests completed successfully!")
    else:
        print("Some tests failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()