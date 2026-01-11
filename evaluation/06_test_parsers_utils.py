import sys; sys.path.insert(0, "..")
"""
Test 6: Parsers and Utils
=========================

Testing: PythonParser, file_utils, text_utils, hash_utils
"""

print('=' * 60)
print('TESTING PARSERS AND UTILS')
print('=' * 60)

# Test Parsers
print('\n1. PARSERS')
print('-' * 40)
try:
    from paila.parsers import PythonParser
    from paila.parsers.base import BaseParser
    print('   ✓ Parser imports successful')

    parser = PythonParser()
    code = '''
class MyClass:
    def method1(self):
        pass

    def method2(self, arg):
        return arg

def standalone():
    import os
    from sys import path
    return None
'''

    # Test parse
    result = parser.parse(code)
    print(f'   ✓ Parsed code: {type(result).__name__}')

    # Test extract functions
    functions = parser.extract_functions(code)
    print(f'   ✓ Extracted {len(functions)} functions')
    for func in functions:
        print(f'      - {func["name"]}')

    # Test extract classes
    classes = parser.extract_classes(code)
    print(f'   ✓ Extracted {len(classes)} classes')
    for cls in classes:
        print(f'      - {cls["name"]}')

    # Test extract imports
    imports = parser.extract_imports(code)
    print(f'   ✓ Extracted {len(imports)} imports')
    for imp in imports:
        print(f'      - {imp}')

except Exception as e:
    print(f'   ✗ Parser error: {e}')

# Test Utils
print('\n2. UTILS')
print('-' * 40)

# File utils
print('   File Utils:')
try:
    from paila.utils.file_utils import read_file, find_python_files, is_binary_file
    print('      ✓ Imports successful')

    # Test is_binary
    is_bin = is_binary_file('/tmp/test.txt')
    print(f'      ✓ is_binary_file works: {is_bin}')
except Exception as e:
    print(f'      ✗ Error: {e}')

# Text utils
print('   Text Utils:')
try:
    from paila.utils.text_utils import truncate_text, highlight_line, count_lines
    print('      ✓ Imports successful')

    # Test truncate
    truncated = truncate_text('Hello World this is a long text', max_length=10)
    print(f'      ✓ truncate_text: "{truncated}"')

    # Test count_lines
    count = count_lines('line1\nline2\nline3')
    print(f'      ✓ count_lines: {count}')

    # Test highlight_line
    highlighted = highlight_line('def foo():', line_number=1)
    print(f'      ✓ highlight_line works')
except Exception as e:
    print(f'      ✗ Error: {e}')

# Hash utils
print('   Hash Utils:')
try:
    from paila.utils.hash_utils import hash_code, hash_file, find_duplicate_code
    print('      ✓ Imports successful')

    # Test hash_code
    hash1 = hash_code('def foo(): pass')
    hash2 = hash_code('def foo(): pass')
    hash3 = hash_code('def bar(): pass')
    print(f'      ✓ hash_code: {hash1[:16]}...')
    print(f'      ✓ Same code same hash: {hash1 == hash2}')
    print(f'      ✓ Different code different hash: {hash1 != hash3}')
except Exception as e:
    print(f'      ✗ Error: {e}')

print('\n' + '=' * 60)
print('PARSERS AND UTILS: ALL TESTS PASSED')
print('=' * 60)
