"""Tests for the Reviewer class."""

import pytest
from paila import Reviewer, Config, review_code


class TestReviewer:
    """Test cases for Reviewer class."""

    def test_init_default(self):
        """Test default initialization."""
        reviewer = Reviewer()
        assert reviewer.config is not None
        assert len(reviewer.analyzers) == 3

    def test_init_with_config(self):
        """Test initialization with custom config."""
        config = Config(analyzers=["security"])
        reviewer = Reviewer(config=config)
        assert "security" in reviewer.analyzers
        assert len(reviewer.analyzers) == 1

    def test_review_code_simple(self):
        """Test reviewing simple code."""
        code = """
def hello():
    print("Hello, World!")
"""
        reviewer = Reviewer()
        result = reviewer.review_code(code)

        assert result.file == "<string>"
        assert result.metrics is not None
        assert result.metrics.functions == 1

    def test_review_code_with_issues(self):
        """Test code with known issues."""
        code = """
def calculate(x):
    result = x * 3.14159
    return result
"""
        reviewer = Reviewer()
        result = reviewer.review_code(code)

        # Should find missing docstring and possibly magic number
        assert result.metrics.functions == 1

    def test_review_code_sql_injection(self):
        """Test detection of SQL injection."""
        code = '''
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    cursor.execute(query)
'''
        config = Config(analyzers=["security"])
        reviewer = Reviewer(config=config)
        result = reviewer.review_code(code)

        # Should detect SQL injection
        sql_issues = [i for i in result.issues if "sql" in i.type.lower()]
        assert len(sql_issues) > 0

    def test_review_code_complexity(self):
        """Test complexity detection."""
        code = """
def complex_function(a, b, c, d, e, f, g):
    if a:
        if b:
            if c:
                if d:
                    for i in e:
                        while f:
                            if g:
                                pass
"""
        config = Config(analyzers=["complexity"], max_nesting_depth=3)
        reviewer = Reviewer(config=config)
        result = reviewer.review_code(code)

        # Should detect deep nesting
        nesting_issues = [i for i in result.issues if "nesting" in i.type.lower()]
        assert len(nesting_issues) > 0

    def test_review_code_empty_except(self):
        """Test detection of empty except blocks."""
        code = """
def risky():
    try:
        do_something()
    except:
        pass
"""
        config = Config(analyzers=["smells"])
        reviewer = Reviewer(config=config)
        result = reviewer.review_code(code)

        except_issues = [i for i in result.issues if "except" in i.type.lower()]
        assert len(except_issues) > 0

    def test_review_code_metrics(self):
        """Test that metrics are calculated correctly."""
        code = """
# This is a comment

class MyClass:
    def method1(self):
        pass

    def method2(self):
        pass

def standalone():
    pass
"""
        reviewer = Reviewer()
        result = reviewer.review_code(code)

        assert result.metrics.classes == 1
        assert result.metrics.functions == 3  # 2 methods + 1 standalone
        assert result.metrics.comment_lines >= 1


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_review_code_function(self):
        """Test the review_code convenience function."""
        result = review_code("def foo(): pass")
        assert result is not None
        assert result.metrics.functions == 1


class TestConfig:
    """Test configuration options."""

    def test_config_strict(self):
        """Test strict configuration."""
        config = Config.strict()
        assert config.max_complexity < 10
        assert config.max_nesting_depth < 4

    def test_config_relaxed(self):
        """Test relaxed configuration."""
        config = Config.relaxed()
        assert config.max_complexity > 10
        assert config.max_nesting_depth > 4

    def test_config_security_only(self):
        """Test security-only configuration."""
        config = Config.security_only()
        assert config.analyzers == ["security"]
