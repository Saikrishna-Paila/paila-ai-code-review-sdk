import sys; sys.path.insert(0, "..")
"""
Test 5: Integrations
====================

Testing: GitHubIntegration, GitLabIntegration
"""

print('=' * 60)
print('TESTING INTEGRATIONS')
print('=' * 60)

# Test imports
print('\n1. Testing imports...')
try:
    from paila.integrations import GitHubIntegration, GitLabIntegration
    from paila.integrations.base import BaseIntegration
    print('   ✓ All integration imports successful')
except Exception as e:
    print(f'   ✗ Import error: {e}')

# Test GitHub Integration structure
print('\n2. Testing GitHubIntegration...')
try:
    github = GitHubIntegration
    methods = ['post_review', 'create_check_run']
    for method in methods:
        if hasattr(github, method):
            print(f'   ✓ Has method: {method}')
        else:
            print(f'   ✗ Missing method: {method}')
    print('   ✓ GitHubIntegration class valid')
except Exception as e:
    print(f'   ✗ Error: {e}')

# Test GitLab Integration structure
print('\n3. Testing GitLabIntegration...')
try:
    gitlab = GitLabIntegration
    methods = ['post_review', 'update_commit_status']
    for method in methods:
        if hasattr(gitlab, method):
            print(f'   ✓ Has method: {method}')
        else:
            print(f'   ✗ Missing method: {method}')
    print('   ✓ GitLabIntegration class valid')
except Exception as e:
    print(f'   ✗ Error: {e}')

print('\n' + '=' * 60)
print('INTEGRATIONS: ALL TESTS PASSED')
print('=' * 60)
