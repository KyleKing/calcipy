# Contributing to calcipy

We welcome contributions to calcipy! This guide will help you get started.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Review Process](#code-review-process)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Testing Guidelines](#testing-guidelines)
- [Code Style](#code-style)
- [Documentation](#documentation)
- [Debugging](#debugging)
- [Opening Issues](#opening-issues)
- [Pull Request Guidelines](#pull-request-guidelines)

## Getting Started

1. **Fork and Clone**: Fork the repository and clone your fork locally
   ```sh
   git clone https://github.com/YOUR_USERNAME/calcipy.git
   cd calcipy
   ```

2. **Set Up Development Environment**:
   ```sh
   uv sync --all-extras
   ./run
   ```

3. **Verify Setup**: Run the test suite to ensure everything works
   ```sh
   ./run test
   ```

For detailed setup instructions, see our [Developer Guide](docs/docs/DEVELOPER_GUIDE.md).

## Development Workflow

1. **Create a Branch**: Use descriptive branch names
   ```sh
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. **Make Changes**: Write code, add tests, update documentation

3. **Test Your Changes**:
   ```sh
   ./run lint.fix test  # Run linting and tests
   ./run types          # Run type checking
   ```

4. **Commit Your Changes**: Follow our [commit message guidelines](#commit-message-guidelines)

5. **Push and Create PR**: Push your branch and open a pull request

## Code Review Process

### For Contributors

When submitting code for review:

- **Keep PRs Focused**: Each PR should address a single concern
- **Write Clear Descriptions**: Explain *what* changed and *why*
- **Add Tests**: Include tests that validate your changes
- **Update Documentation**: Keep docs in sync with code changes
- **Respond to Feedback**: Address reviewer comments promptly and professionally

### For Reviewers

When reviewing code:

- **Be Constructive**: Focus on the code, not the person
- **Ask Questions**: Seek to understand before suggesting changes
- **Explain Reasoning**: Help contributors learn by explaining *why*
- **Acknowledge Good Work**: Recognize well-written code and thoughtful solutions
- **Review Thoroughly**: Check for correctness, maintainability, and edge cases
- **Be Timely**: Respond to PRs within a reasonable timeframe

### Code Review Checklist

- [ ] Does the code solve the stated problem?
- [ ] Are there adequate tests with good coverage?
- [ ] Is the code readable and maintainable?
- [ ] Are there potential bugs or edge cases?
- [ ] Is error handling appropriate?
- [ ] Are there security concerns?
- [ ] Is the documentation updated?
- [ ] Do commit messages follow conventions?

**References:**
- [Code Review Best Practices](https://www.kevinlondon.com/2015/05/05/code-review-best-practices.html)
- [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments) (principles apply to Python)

## Commit Message Guidelines

We use [Conventional Commits](https://www.conventionalcommits.org/) with [Commitizen](https://github.com/commitizen-tools/commitizen) for automated changelog generation and semantic versioning.

### Format

```
type(scope): description

[optional body]

[optional footer]
```

### Types

- **feat**: A new feature (MINOR version bump)
- **fix**: A bug fix (PATCH version bump)
- **docs**: Documentation-only changes
- **style**: Code style changes (formatting, missing semi-colons, etc.)
- **refactor**: Code refactoring (neither fixes a bug nor adds a feature)
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **build**: Changes to build system or dependencies
- **ci**: Changes to CI configuration
- **BREAKING CHANGE**: Breaking changes (MAJOR version bump)
  - Use `!` after type/scope: `feat!:` or `refactor(core)!:`

### Scopes

Use appropriate scopes like module names, file names, or issue numbers:
- `build(uv): bump requests to v3`
- `style(#32): add missing type annotations`
- `fix(cli): correct argument parsing`

### Examples

```
feat(lint): add support for custom ruff rules

fix(test): handle edge case in dot_dict tests

docs: update installation instructions

refactor!: restructure task module API

BREAKING CHANGE: TaskCollection.add() now requires name parameter
```

### Tips

- Use present tense: "add feature" not "added feature"
- Be concise but descriptive (aim for 50 characters, max 72)
- Use the body to explain *what* and *why*, not *how*
- Reference issues: "fixes #123" or "relates to #456"
- Use `git rebase -i` to fix commit messages before merging

**References:**
- [How to Write a Git Commit Message](https://chris.beams.io/posts/git-commit/)
- [Commit Message Guide](https://writingfordevelopers.substack.com/p/how-to-write-a-commit-message)

## Testing Guidelines

### Writing Tests

- **Test Behavior, Not Implementation**: Focus on what the code does, not how
- **Use Descriptive Names**: Test names should describe the scenario
- **Follow AAA Pattern**: Arrange, Act, Assert
- **Test Edge Cases**: Don't just test the happy path
- **Keep Tests Independent**: Tests should not depend on each other

### Test Organization

```python
def test_function_name_expected_behavior():
    """Test that function_name does X when given Y."""
    # Arrange: Set up test data
    input_data = create_test_data()
    
    # Act: Execute the code being tested
    result = function_name(input_data)
    
    # Assert: Verify the outcome
    assert result.status == "success"
    assert result.value == expected_value
```

### Mocking and Stubbing

- **Stubs**: Provide predetermined responses (for queries)
- **Mocks**: Verify behavior and interactions (for commands)

Use mocks sparingly - prefer real objects when possible:

```python
from unittest.mock import Mock, patch

def test_api_call_with_mock():
    """Test API handling with mocked HTTP client."""
    # Use mocks to avoid external dependencies
    with patch('module.http_client') as mock_client:
        mock_client.get.return_value = Mock(status=200, data='test')
        
        result = fetch_data()
        
        assert result == 'test'
        mock_client.get.assert_called_once()
```

### Running Tests

```sh
./run test              # Run all tests
./run test path/to/test # Run specific test
./run test.watch        # Run tests in watch mode
./run test.coverage     # Generate coverage report
```

**References:**
- [Testing Concepts: Stubbing vs Mocking](https://outsidein.dev/testing-concepts.html#stubbing-and-mocking)
- [Python Testing Style Guide](https://blog.thea.codes/my-python-testing-style-guide/)
- [Testing the Diff](https://www.vinta.com.br/blog/2021/testing-the-diff/)

## Code Style

We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting. Run it before committing:

```sh
./run lint.fix  # Auto-fix style issues
./run lint      # Check without fixing
```

### Python Style Guidelines

- Follow [PEP 8](https://pep8.org/) (enforced by Ruff)
- Use type hints for function signatures
- Write docstrings for public APIs
- Prefer functions over classes when appropriate
- Keep functions focused and small
- Use meaningful variable names
- Avoid premature optimization

**References:**
- [Python Style Guide](https://docs.python-guide.org/writing/style/)
- [Add list of advice of regular function over class](https://sobolevn.me/2018/03/mediocre-developer)

## Documentation

### When to Update Docs

- Adding a new feature → Update relevant docs
- Changing behavior → Update affected docs
- Fixing a bug → Consider if docs need clarification
- Adding configuration → Document new options

### Documentation Types

1. **Code Comments**: Explain *why*, not *what*
2. **Docstrings**: Document public APIs (modules, classes, functions)
3. **README**: Project overview and quick start
4. **Developer Guide**: Development workflow and setup
5. **Style Guide**: Project conventions
6. **ADRs**: Significant architectural decisions

### Building Documentation

```sh
./run doc.build  # Build documentation
./run doc.watch  # Serve docs locally with auto-reload
```

## Debugging

### General Debugging Workflow

1. **Reproduce the Issue**: Create a minimal test case
2. **Gather Information**: Read error messages, check logs, review stack traces
3. **Form a Hypothesis**: What could be causing the issue?
4. **Test Your Hypothesis**: Add print statements, use a debugger, write a test
5. **Fix and Verify**: Make the change and ensure it works
6. **Prevent Recurrence**: Add tests to catch similar issues

### Debugging Tools

- **Print/Log Debugging**: Quick and effective for many issues
  ```python
  import logging
  logger = logging.getLogger(__name__)
  logger.debug(f"Variable value: {value}")
  ```

- **Python Debugger (pdb)**: Interactive debugging
  ```python
  import pdb; pdb.set_trace()  # Add breakpoint
  ```

- **Pytest with pdb**: Drop into debugger on test failure
  ```sh
  pytest --pdb
  ```

### Logging Best Practices

When adding logging to code:

- **ERROR**: Something failed, needs immediate attention
- **WARNING**: Something unexpected but recoverable happened
- **INFO**: Important business logic milestones
- **DEBUG**: Detailed information for diagnosing issues

**Avoid over-logging:**
- Don't log every function entry/exit
- Don't log sensitive data
- Don't log in tight loops
- Don't use logging for control flow

**References:**
- [Logging Levels: The Wrong Abstraction](https://labs.ig.com/logging-level-wrong-abstraction)
- [What Should You Log in an Application](https://cloudncode.blog/2016/12/30/what-should-you-log-in-an-application-and-how-to-avoid-having-24x7-support-looking-at-them/)
- [How to Log in Python Like a Pro](https://guicommits.com/how-to-log-in-python-like-a-pro/)
- [Debugging Series 2021](https://thoughtbot.com/blog/debugging-series-2021-welcome-to-the-jungle)
- [Geo-Python Debugging Guide](https://geo-python.github.io/2017/lessons/L6/debugging-scripts.html)

**Bug Fixing Reference:**
- [How to Fix a Bug](https://sobolevn.me/2019/01/how-to-fix-a-bug)

## Opening Issues

### Before Opening an Issue

1. **Search Existing Issues**: Check if it's already reported
2. **Verify It's a Bug**: Make sure it's not expected behavior
3. **Create Minimal Reproduction**: Reduce to simplest example
4. **Gather Information**: Version numbers, error messages, environment

### Issue Template

```markdown
## Description
[Clear description of the issue]

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Environment
- calcipy version: [e.g., 1.2.3]
- Python version: [e.g., 3.11]
- Operating System: [e.g., Ubuntu 22.04]

## Additional Context
[Any other relevant information]
```

## Pull Request Guidelines

### Before Submitting

- [ ] Code follows the project style guide
- [ ] All tests pass locally
- [ ] New tests cover your changes
- [ ] Documentation is updated
- [ ] Commit messages follow conventions
- [ ] Branch is up to date with main

### PR Description Template

```markdown
## Description
[Describe the changes and their purpose]

## Related Issue
Fixes #[issue number]

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing Done
- [ ] Unit tests pass
- [ ] Manual testing completed
- [ ] Edge cases considered

## Screenshots (if applicable)
[Add screenshots for UI changes]

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added/updated
```

### After Submitting

1. **Monitor CI**: Ensure all checks pass
2. **Respond to Reviews**: Address feedback promptly
3. **Keep PR Updated**: Rebase if main branch advances
4. **Be Patient**: Reviews take time

**References:**
- [PR Guidelines](https://gist.github.com/mherrmann/5ce21814789152c17abd91c0b3eaadca)
- [Using GitHub Professionally](https://petabridge.com/blog/use-github-professionally/)

## Additional Resources

### General Development
- [Every Programmer Should Know](https://github.com/mtdvio/every-programmer-should-know)
- [Software Quality Metrics](https://hub.codebeat.co/docs/software-quality-metrics)

### Regex Tips
- [Regex Visualization Tool](https://regexper.com/)

### Python-Specific
- [Real Python Refactoring Guide](https://realpython.com/python-refactoring/)

## Questions?

If you have questions:
1. Check the [Developer Guide](docs/docs/DEVELOPER_GUIDE.md)
2. Search [existing issues](https://github.com/KyleKing/calcipy/issues)
3. Open a new issue with the "question" label

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

---

Thank you for contributing to calcipy! 🎉
