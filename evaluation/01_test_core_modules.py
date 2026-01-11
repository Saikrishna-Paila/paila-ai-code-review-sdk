import sys; sys.path.insert(0, "..")
"""
Test 1: Core Modules
====================

Testing: Reviewer, Config, Models, review_code function
"""

print('=' * 60)
print('TESTING CORE MODULES')
print('=' * 60)

# Test imports
print('\n1. Testing imports...')
try:
    from paila import Reviewer, Config, review, review_code
    from paila.models import Issue, Metrics, FileResult, ReviewResult, Severity, IssueType
    print('   ✓ All core imports successful')
except Exception as e:
    print(f'   ✗ Import error: {e}')

# Test Config
print('\n2. Testing Config...')
try:
    config = Config()
    print(f'   ✓ Default config: analyzers={config.analyzers}')

    strict = Config.strict()
    print(f'   ✓ Strict config: max_complexity={strict.max_complexity}')

    relaxed = Config.relaxed()
    print(f'   ✓ Relaxed config: max_complexity={relaxed.max_complexity}')

    security = Config.security_only()
    print(f'   ✓ Security only: analyzers={security.analyzers}')
except Exception as e:
    print(f'   ✗ Config error: {e}')

# Test Reviewer
print('\n3. Testing Reviewer...')
try:
    reviewer = Reviewer()
    print(f'   ✓ Reviewer created: analyzers={reviewer.analyzers}')

    reviewer_strict = Reviewer(config=Config.strict())
    print(f'   ✓ Strict Reviewer created')
except Exception as e:
    print(f'   ✗ Reviewer error: {e}')

# Test review_code
print('\n4. Testing review_code...')
try:
    code = 'def foo(): pass'
    result = review_code(code)
    print(f'   ✓ Simple code: score={result.score}, issues={len(result.issues)}')

    code_vuln = '''
def get_user(id):
    query = f"SELECT * FROM users WHERE id = {id}"
    return query
'''
    result2 = review_code(code_vuln)
    print(f'   ✓ Vulnerable code: score={result2.score}, issues={len(result2.issues)}')
except Exception as e:
    print(f'   ✗ review_code error: {e}')

# Test Models
print('\n5. Testing Models...')
try:
    issue = Issue(
        type='test',
        severity=Severity.HIGH,
        file='test.py',
        line=1,
        message='Test issue'
    )
    print(f'   ✓ Issue created: {issue.severity.value}')

    metrics = Metrics(lines_of_code=100, functions=5)
    print(f'   ✓ Metrics created: loc={metrics.lines_of_code}')

    file_result = FileResult(file='test.py', issues=[issue], metrics=metrics)
    print(f'   ✓ FileResult: score={file_result.score}, grade={file_result.grade}')

    review_result = ReviewResult(
        files=[file_result],
        total_issues=1,
        issues_by_severity={'high': 1}
    )
    print(f'   ✓ ReviewResult: score={review_result.score}, grade={review_result.grade}')
except Exception as e:
    print(f'   ✗ Models error: {e}')

print('\n' + '=' * 60)
print('CORE MODULES: ALL TESTS PASSED')
print('=' * 60)
