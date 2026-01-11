"""
Basic Usage Examples for Paila SDK
==================================

This file demonstrates basic usage of the Paila SDK.
"""

from paila import Reviewer, Config, review_code


def example_review_code():
    """Example: Review a code string."""
    print("=" * 50)
    print("Example 1: Review Code String")
    print("=" * 50)

    code = '''
def calculate_price(quantity, discount):
    base_price = quantity * 19.99
    if discount:
        final = base_price * 0.85
    else:
        final = base_price
    return final
'''

    reviewer = Reviewer()
    result = reviewer.review_code(code, "pricing.py")

    print(f"File: {result.file}")
    print(f"Issues found: {len(result.issues)}")
    print(f"Lines of code: {result.metrics.lines_of_code}")
    print(f"Functions: {result.metrics.functions}")
    print()

    for issue in result.issues:
        print(f"[{issue.severity.value.upper()}] {issue.message}")
        print(f"  Line {issue.line}: {issue.code}")
        if issue.suggestion:
            print(f"  💡 {issue.suggestion}")
        print()


def example_quick_review():
    """Example: Quick one-liner review."""
    print("=" * 50)
    print("Example 2: Quick One-Liner")
    print("=" * 50)

    result = review_code("def foo(): pass")

    print(f"Functions: {result.metrics.functions}")
    print(f"Issues: {len(result.issues)}")
    print()


def example_security_scan():
    """Example: Security-focused scan."""
    print("=" * 50)
    print("Example 3: Security Scan")
    print("=" * 50)

    dangerous_code = '''
import os

def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return execute(query)

def run_command(cmd):
    os.system("ls " + cmd)

password = "secret123"
'''

    config = Config.security_only()
    reviewer = Reviewer(config=config)
    result = reviewer.review_code(dangerous_code, "vulnerable.py")

    print(f"Security issues found: {len(result.issues)}")
    print()

    for issue in result.issues:
        print(f"🔒 [{issue.severity.value.upper()}] {issue.message}")
        print(f"   Rule: {issue.rule}")
        print()


def example_complexity_check():
    """Example: Complexity analysis."""
    print("=" * 50)
    print("Example 4: Complexity Check")
    print("=" * 50)

    complex_code = '''
def process_order(order, user, payment, shipping, discounts, taxes, fees):
    if order:
        if user:
            if payment:
                for discount in discounts:
                    if discount.applies(order):
                        for item in order.items:
                            if item.eligible:
                                while item.quantity > 0:
                                    process_item(item)
                                    item.quantity -= 1
'''

    config = Config(analyzers=["complexity"], max_complexity=5, max_nesting_depth=3)
    reviewer = Reviewer(config=config)
    result = reviewer.review_code(complex_code, "orders.py")

    print(f"Complexity issues: {len(result.issues)}")
    print(f"Avg complexity: {result.metrics.avg_complexity}")
    print()

    for issue in result.issues:
        print(f"📊 {issue.message}")
        if issue.suggestion:
            print(f"   💡 {issue.suggestion}")
        print()


def example_custom_config():
    """Example: Custom configuration."""
    print("=" * 50)
    print("Example 5: Custom Configuration")
    print("=" * 50)

    config = Config(
        analyzers=["smells"],
        max_line_length=80,
        max_function_lines=30,
        ignore_patterns=["test_"],
    )

    code = '''
# TODO: refactor this later
def process():
    magic = 42
    items = []

def bad_default(data=[]):
    data.append(1)
    return data
'''

    reviewer = Reviewer(config=config)
    result = reviewer.review_code(code)

    print(f"Code smells found: {len(result.issues)}")
    print()

    for issue in result.issues:
        print(f"🦨 [{issue.type}] {issue.message}")
        print()


if __name__ == "__main__":
    example_review_code()
    example_quick_review()
    example_security_scan()
    example_complexity_check()
    example_custom_config()

    print("=" * 50)
    print("All examples completed!")
    print("=" * 50)
