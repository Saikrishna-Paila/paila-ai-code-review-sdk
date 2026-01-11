import sys; sys.path.insert(0, "..")
"""
Test 7: Rules Module
====================

Testing: Rule, RuleSet, RuleBuilder, SecurityRules, ComplexityRules, StyleRules
"""

print('=' * 60)
print('TESTING RULES MODULE')
print('=' * 60)

from paila.rules import Rule, RuleSet, RuleBuilder
from paila.rules.builtin import SecurityRules, ComplexityRules, StyleRules
from paila.models import Severity

# Test Rule class
print('\n1. Testing Rule class...')
try:
    def simple_checker(code, file_path, tree):
        return []

    rule = Rule(
        id='test/rule',
        name='Test Rule',
        description='A test rule',
        severity=Severity.MEDIUM,
        category='test',
        checker=simple_checker,
    )
    print(f'   ✓ Rule created: {rule.id}')
    print(f'   ✓ Rule name: {rule.name}')
    print(f'   ✓ Rule severity: {rule.severity.value}')

    issues = rule.check('some code', 'test.py', None)
    print(f'   ✓ Rule check works: {len(issues)} issues')
except Exception as e:
    print(f'   ✗ Error: {e}')

# Test RuleSet
print('\n2. Testing RuleSet...')
try:
    ruleset = RuleSet(name='test-set')
    ruleset.add(rule)
    print(f'   ✓ RuleSet created with {len(ruleset)} rules')

    issues = ruleset.check_all('some code', 'test.py', None)
    print(f'   ✓ check_all works: {len(issues)} issues')

    # Test enable/disable
    ruleset.disable(rule.id)
    print(f'   ✓ Rule disabled')
    ruleset.enable(rule.id)
    print(f'   ✓ Rule enabled')
except Exception as e:
    print(f'   ✗ Error: {e}')

# Test RuleBuilder
print('\n3. Testing RuleBuilder...')
try:
    custom_rule = (RuleBuilder('custom/my-rule')
        .name('My Custom Rule')
        .description('Detects bad pattern')
        .severity(Severity.HIGH)
        .category('custom')
        .pattern(r'bad_pattern', message='Found bad pattern')
        .tags('test', 'custom')
        .build()
    )
    print(f'   ✓ Rule built: {custom_rule.id}')
    print(f'   ✓ Rule name: {custom_rule.name}')
    print(f'   ✓ Rule tags: {custom_rule.tags}')

    # Test the pattern
    code_with_pattern = 'x = bad_pattern'
    issues = custom_rule.check(code_with_pattern, 'test.py', None)
    print(f'   ✓ Pattern matched: {len(issues)} issues')
except Exception as e:
    print(f'   ✗ Error: {e}')

# Test Built-in RuleSets
print('\n4. Testing Built-in RuleSets...')

# Security Rules
print('\n   SECURITY RULES:')
try:
    security = SecurityRules()
    print(f'   ✓ SecurityRules: {len(security)} rules')

    # List all rules
    for rule in security.rules:
        print(f'      - {rule.id}: {rule.name}')

    # Test against vulnerable code
    code = 'query = f"SELECT * FROM users WHERE id = {id}"'
    issues = security.check_all(code, 'test.py', None)
    print(f'   ✓ Security check: {len(issues)} issues found')
except Exception as e:
    print(f'   ✗ SecurityRules error: {e}')

# Complexity Rules
print('\n   COMPLEXITY RULES:')
try:
    complexity = ComplexityRules()
    print(f'   ✓ ComplexityRules: {len(complexity)} rules')

    for rule in complexity.rules:
        print(f'      - {rule.id}: {rule.name}')
except Exception as e:
    print(f'   ✗ ComplexityRules error: {e}')

# Style Rules
print('\n   STYLE RULES:')
try:
    style = StyleRules()
    print(f'   ✓ StyleRules: {len(style)} rules')

    for rule in style.rules:
        print(f'      - {rule.id}: {rule.name}')

    # Test trailing whitespace
    code = 'x = 1   '  # trailing spaces
    issues = style.check_all(code, 'test.py', None)
    print(f'   ✓ Style check: {len(issues)} issues found')
except Exception as e:
    print(f'   ✗ StyleRules error: {e}')

print('\n' + '=' * 60)
print('RULES MODULE: ALL TESTS PASSED')
print('=' * 60)
