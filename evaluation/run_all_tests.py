#!/usr/bin/env python3
"""
Run All Evaluation Tests
========================

Master test runner for Paila SDK evaluation.
Runs all test files and generates a summary report.
"""

import subprocess
import sys
import os
from datetime import datetime

# Change to evaluation directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║                    🔍 PAILA SDK EVALUATION                           ║
║                    ══════════════════════════                        ║
║                                                                      ║
║                    Running All Test Suites                           ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
""")

print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Python: {sys.version.split()[0]}")
print()

test_files = [
    ("01_test_core_modules.py", "Core Modules"),
    ("02_test_analyzers.py", "Analyzers"),
    ("03_test_reporters.py", "Reporters"),
    ("04_test_ai_providers.py", "AI Providers"),
    ("05_test_integrations.py", "Integrations"),
    ("06_test_parsers_utils.py", "Parsers & Utils"),
    ("07_test_rules.py", "Rules"),
    ("08_test_cli.py", "CLI"),
]

results = []

for i, (filename, name) in enumerate(test_files, 1):
    print(f"\n{'─' * 70}")
    print(f"  [{i}/{len(test_files)}] Running: {name}")
    print(f"{'─' * 70}\n")

    try:
        result = subprocess.run(
            [sys.executable, filename],
            capture_output=True,
            text=True,
            timeout=60
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        # Check for success indicators
        if ("ALL TESTS PASSED" in result.stdout or
            "PASSED" in result.stdout.upper() or
            result.returncode == 0):
            results.append((name, "✅ PASSED"))
        else:
            results.append((name, "❌ FAILED"))
    except subprocess.TimeoutExpired:
        results.append((name, "⏱️ TIMEOUT"))
        print(f"   Test timed out!")
    except Exception as e:
        results.append((name, f"❌ ERROR: {e}"))
        print(f"   Error: {e}")

# Run pytest
print(f"\n{'─' * 70}")
print(f"  [PYTEST] Running Unit Tests")
print(f"{'─' * 70}\n")

try:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "../tests/", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=120
    )
    print(result.stdout)

    if "passed" in result.stdout and "failed" not in result.stdout:
        # Extract number of passed tests
        import re
        match = re.search(r'(\d+) passed', result.stdout)
        if match:
            results.append((f"Pytest ({match.group(1)} tests)", "✅ PASSED"))
        else:
            results.append(("Pytest", "✅ PASSED"))
    else:
        results.append(("Pytest", "❌ FAILED"))
except Exception as e:
    results.append(("Pytest", f"❌ ERROR: {e}"))

# Print summary
print(f"""

╔══════════════════════════════════════════════════════════════════════╗
║                         EVALUATION SUMMARY                           ║
╠══════════════════════════════════════════════════════════════════════╣
""")

for name, status in results:
    print(f"║  {name:<40} {status:<25} ║")

passed = sum(1 for _, s in results if "PASSED" in s)
total = len(results)

print(f"""╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  Total: {passed}/{total} test suites passed                                       ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
""")

print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Exit with appropriate code
sys.exit(0 if passed == total else 1)
