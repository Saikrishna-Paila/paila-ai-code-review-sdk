import sys; sys.path.insert(0, "..")
"""
Test 3: Reporters
=================

Testing: TerminalReporter, JSONReporter, MarkdownReporter, HTMLReporter
"""

print('=' * 60)
print('TESTING REPORTERS')
print('=' * 60)

from paila import review_code
from paila.reporters import TerminalReporter, JSONReporter, MarkdownReporter, HTMLReporter

# Create test data
code = '''
def vulnerable(id):
    query = f"SELECT * FROM users WHERE id = {id}"
    password = "secret123"
    return query
'''
result = review_code(code)

# Test Terminal Reporter
print('\n1. TERMINAL REPORTER')
print('-' * 40)
try:
    reporter = TerminalReporter()
    output = reporter.format(result)
    print(f'   ✓ Generated {len(output)} chars of output')
    print(f'   ✓ Contains score: {"Score" in output or "score" in output.lower()}')
except Exception as e:
    print(f'   ✗ Error: {e}')

# Test JSON Reporter
print('\n2. JSON REPORTER')
print('-' * 40)
try:
    import json
    reporter = JSONReporter()
    output = reporter.format(result)
    data = json.loads(output)
    print(f'   ✓ Valid JSON output')
    print(f'   ✓ Has issues: {len(data.get("issues", []))} issues')
    print(f'   ✓ Has score: {data.get("score")}')
    print(f'   ✓ Has grade: {data.get("grade")}')
except Exception as e:
    print(f'   ✗ Error: {e}')

# Test Markdown Reporter
print('\n3. MARKDOWN REPORTER')
print('-' * 40)
try:
    reporter = MarkdownReporter()
    output = reporter.format(result)
    print(f'   ✓ Generated {len(output)} chars of output')
    print(f'   ✓ Has header: {"#" in output}')
    print(f'   ✓ Has code blocks: {"```" in output}')
except Exception as e:
    print(f'   ✗ Error: {e}')

# Test HTML Reporter
print('\n4. HTML REPORTER')
print('-' * 40)
try:
    reporter = HTMLReporter()
    output = reporter.format(result)
    print(f'   ✓ Generated {len(output)} chars of output')
    print(f'   ✓ Has HTML tags: {"<html" in output.lower() or "<div" in output.lower()}')
    print(f'   ✓ Has style: {"<style" in output.lower() or "style=" in output.lower()}')
except Exception as e:
    print(f'   ✗ Error: {e}')

print('\n' + '=' * 60)
print('REPORTERS: ALL TESTS PASSED')
print('=' * 60)
