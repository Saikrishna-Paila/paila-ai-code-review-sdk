"""Tests for analyzers."""

import pytest
import ast
from paila.config import Config
from paila.analyzers import (
    ComplexityAnalyzer,
    SecurityAnalyzer,
    SmellAnalyzer,
)


class TestComplexityAnalyzer:
    """Test cases for ComplexityAnalyzer."""

    @pytest.fixture
    def analyzer(self):
        return ComplexityAnalyzer()

    def test_simple_function(self, analyzer):
        """Test a simple function with low complexity."""
        code = """
def simple():
    return 42
"""
        issues = analyzer.analyze(code, "test.py")
        high_complexity = [i for i in issues if i.type == "high_complexity"]
        assert len(high_complexity) == 0

    def test_complex_function(self, analyzer):
        """Test detection of high complexity."""
        code = """
def complex(a, b, c, d, e):
    if a:
        if b:
            if c:
                for x in d:
                    while e:
                        if x > 0:
                            pass
                        elif x < 0:
                            pass
                        else:
                            pass
"""
        config = Config(max_complexity=5)
        analyzer = ComplexityAnalyzer(config=config)
        issues = analyzer.analyze(code, "test.py")

        high_complexity = [i for i in issues if i.type == "high_complexity"]
        assert len(high_complexity) > 0

    def test_deep_nesting(self, analyzer):
        """Test detection of deep nesting."""
        code = """
def nested():
    if True:
        if True:
            if True:
                if True:
                    if True:
                        pass
"""
        config = Config(max_nesting_depth=3)
        analyzer = ComplexityAnalyzer(config=config)
        issues = analyzer.analyze(code, "test.py")

        nesting_issues = [i for i in issues if i.type == "deep_nesting"]
        assert len(nesting_issues) > 0

    def test_long_function(self, analyzer):
        """Test detection of long functions."""
        code = "def long_func():\n" + "    x = 1\n" * 60
        config = Config(max_function_lines=50)
        analyzer = ComplexityAnalyzer(config=config)
        issues = analyzer.analyze(code, "test.py")

        long_issues = [i for i in issues if i.type == "long_function"]
        assert len(long_issues) > 0

    def test_too_many_params(self, analyzer):
        """Test detection of too many parameters."""
        code = """
def many_params(a, b, c, d, e, f, g, h, i):
    pass
"""
        config = Config(max_parameters=5)
        analyzer = ComplexityAnalyzer(config=config)
        issues = analyzer.analyze(code, "test.py")

        param_issues = [i for i in issues if i.type == "too_many_params"]
        assert len(param_issues) > 0

    def test_calculate_metrics(self, analyzer):
        """Test metrics calculation."""
        code = """
# Comment
class MyClass:
    def method(self):
        if True:
            pass

def func():
    for i in range(10):
        if i > 5:
            break
"""
        metrics = analyzer.calculate_metrics(code)

        assert metrics["functions"] == 2
        assert metrics["classes"] == 1
        assert metrics["comment_lines"] >= 1


class TestSecurityAnalyzer:
    """Test cases for SecurityAnalyzer."""

    @pytest.fixture
    def analyzer(self):
        return SecurityAnalyzer()

    def test_sql_injection_concat(self, analyzer):
        """Test SQL injection via concatenation."""
        code = '''
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    return query
'''
        issues = analyzer.analyze(code, "test.py")

        sql_issues = [i for i in issues if "sql" in i.type.lower()]
        assert len(sql_issues) > 0

    def test_sql_injection_fstring(self, analyzer):
        """Test SQL injection via f-string."""
        code = '''
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return query
'''
        issues = analyzer.analyze(code, "test.py")

        sql_issues = [i for i in issues if "sql" in i.type.lower()]
        assert len(sql_issues) > 0

    def test_command_injection(self, analyzer):
        """Test command injection detection."""
        code = '''
import os

def run_command(user_input):
    os.system("ls " + user_input)
'''
        issues = analyzer.analyze(code, "test.py")

        cmd_issues = [i for i in issues if "command" in i.type.lower()]
        assert len(cmd_issues) > 0

    def test_hardcoded_password(self, analyzer):
        """Test hardcoded password detection."""
        code = '''
password = "secret123"
api_key = "sk-1234567890abcdef"
'''
        issues = analyzer.analyze(code, "test.py")

        secret_issues = [i for i in issues if "secret" in i.type.lower() or "hardcoded" in i.type.lower()]
        assert len(secret_issues) > 0

    def test_eval_usage(self, analyzer):
        """Test eval usage detection."""
        code = '''
def dangerous(user_input):
    result = eval(user_input)
    return result
'''
        issues = analyzer.analyze(code, "test.py")

        eval_issues = [i for i in issues if "eval" in i.type.lower()]
        assert len(eval_issues) > 0

    def test_pickle_usage(self, analyzer):
        """Test pickle usage detection."""
        code = '''
import pickle

def load_data(data):
    return pickle.loads(data)
'''
        issues = analyzer.analyze(code, "test.py")

        pickle_issues = [i for i in issues if "pickle" in i.type.lower()]
        assert len(pickle_issues) > 0

    def test_safe_code(self, analyzer):
        """Test that safe code has no security issues."""
        code = '''
def safe_function(x):
    return x * 2
'''
        issues = analyzer.analyze(code, "test.py")

        # Filter out non-security issues
        security_types = ["sql_injection", "command_injection", "hardcoded_secret", "eval_usage"]
        security_issues = [i for i in issues if i.type in security_types]
        assert len(security_issues) == 0


class TestSmellAnalyzer:
    """Test cases for SmellAnalyzer."""

    @pytest.fixture
    def analyzer(self):
        return SmellAnalyzer()

    def test_missing_docstring(self, analyzer):
        """Test detection of missing docstring."""
        code = '''
def public_function():
    pass

class PublicClass:
    pass
'''
        issues = analyzer.analyze(code, "test.py")

        docstring_issues = [i for i in issues if "docstring" in i.type.lower()]
        assert len(docstring_issues) >= 2

    def test_with_docstring(self, analyzer):
        """Test that docstrings are not flagged."""
        code = '''
def documented():
    """This function is documented."""
    pass

class Documented:
    """This class is documented."""
    pass
'''
        issues = analyzer.analyze(code, "test.py")

        docstring_issues = [i for i in issues if "docstring" in i.type.lower()]
        assert len(docstring_issues) == 0

    def test_magic_numbers(self, analyzer):
        """Test detection of magic numbers."""
        code = '''
def calculate(x):
    return x * 3.14159 + 42
'''
        issues = analyzer.analyze(code, "test.py")

        magic_issues = [i for i in issues if "magic" in i.type.lower()]
        assert len(magic_issues) > 0

    def test_empty_except(self, analyzer):
        """Test detection of empty except blocks."""
        code = '''
try:
    risky()
except:
    pass
'''
        issues = analyzer.analyze(code, "test.py")

        except_issues = [i for i in issues if "except" in i.type.lower()]
        assert len(except_issues) >= 1

    def test_bare_except(self, analyzer):
        """Test detection of bare except."""
        code = '''
try:
    risky()
except:
    print("error")
'''
        issues = analyzer.analyze(code, "test.py")

        bare_issues = [i for i in issues if i.type == "bare_except"]
        assert len(bare_issues) > 0

    def test_star_import(self, analyzer):
        """Test detection of star imports."""
        code = '''
from os import *
from sys import *
'''
        issues = analyzer.analyze(code, "test.py")

        star_issues = [i for i in issues if "star" in i.type.lower()]
        assert len(star_issues) >= 2

    def test_mutable_default(self, analyzer):
        """Test detection of mutable default arguments."""
        code = '''
def bad_default(items=[]):
    items.append(1)
    return items

def also_bad(config={}):
    return config
'''
        issues = analyzer.analyze(code, "test.py")

        mutable_issues = [i for i in issues if "mutable" in i.type.lower()]
        assert len(mutable_issues) >= 2

    def test_todo_comment(self, analyzer):
        """Test detection of TODO comments."""
        code = '''
# TODO: fix this later
# FIXME: this is broken
def func():
    pass
'''
        issues = analyzer.analyze(code, "test.py")

        todo_issues = [i for i in issues if "todo" in i.type.lower()]
        assert len(todo_issues) >= 2
