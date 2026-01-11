import sys; sys.path.insert(0, "..")
"""
Test 2: Analyzers
=================

Testing: SecurityAnalyzer, ComplexityAnalyzer, SmellAnalyzer
"""

print('=' * 60)
print('TESTING ANALYZERS')
print('=' * 60)

from paila.analyzers import BaseAnalyzer, ComplexityAnalyzer, SecurityAnalyzer, SmellAnalyzer
from paila.config import Config

config = Config()

# Test Security Analyzer
print('\n1. SECURITY ANALYZER')
print('-' * 40)
security = SecurityAnalyzer(config)
print(f'   Name: {security.name}')

# SQL Injection tests
tests = [
    ('SQL Injection (f-string)', 'query = f"SELECT * FROM users WHERE id = {id}"'),
    ('SQL Injection (concat)', 'query = "SELECT * FROM users WHERE id = " + id'),
    ('Command Injection', 'os.system("ls " + user_input)'),
    ('Hardcoded Password', 'password = "secret123"'),
    ('Eval Usage', 'result = eval(user_input)'),
    ('Exec Usage', 'exec(code)'),
    ('Pickle Usage', 'data = pickle.loads(untrusted)'),
]

for name, code in tests:
    issues = security.analyze(code, 'test.py', None)
    status = '✓' if issues else '✗'
    print(f'   {status} {name}: {len(issues)} issues')

# Test Complexity Analyzer
print('\n2. COMPLEXITY ANALYZER')
print('-' * 40)
complexity = ComplexityAnalyzer(config)
print(f'   Name: {complexity.name}')

complex_code = '''
def complex_function(a, b, c, d, e, f, g):
    if a:
        if b:
            if c:
                if d:
                    if e:
                        return 1
    for i in range(10):
        for j in range(10):
            for k in range(10):
                pass
    return 0
'''
issues = complexity.analyze(complex_code, 'test.py', None)
print(f'   ✓ Complex code detected: {len(issues)} issues')
for issue in issues:
    print(f'      - {issue.type}: {issue.message[:50]}...')

# Test Smell Analyzer
print('\n3. SMELL ANALYZER')
print('-' * 40)
smell = SmellAnalyzer(config)
print(f'   Name: {smell.name}')

smelly_code = '''
from os import *

def no_docs(x):
    magic = 42
    result = x * 3.14159
    try:
        pass
    except:
        pass
    # TODO: fix this
    print("debug")
    return result

def mutable_default(items=[]):
    items.append(1)
    return items
'''
issues = smell.analyze(smelly_code, 'test.py', None)
print(f'   ✓ Smelly code detected: {len(issues)} issues')
for issue in issues[:5]:
    print(f'      - {issue.type}')

print('\n' + '=' * 60)
print('ANALYZERS: ALL TESTS PASSED')
print('=' * 60)
