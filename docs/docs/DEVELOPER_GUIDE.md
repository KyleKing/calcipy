# Developer Notes

## Local Development

```sh
git clone https://github.com/kyleking/calcipy.git
cd calcipy
poetry install -E dev -E lint -E test -E commitizen_legacy

# See the available tasks
poetry run doit list

# Run the default task list (lint, auto-format, test coverage, etc.)
poetry run doit --continue

# Make code changes and run specific tasks as needed:
poetry run doit run test
```

## Publishing

For testing, create an account on [TestPyPi](https://test.pypi.org/legacy/)

```sh
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry config pypi-token.testpypi ...

poetry run doit run publish_test_pypi
# If you didn't configure a token, you will need to provide your username and password to publish
```

To publish to the real PyPi

```sh
poetry config pypi-token.pypi ...
poetry run doit run publish

# For a full release, increment the version, the documentation, and publish
poetry run doit run --continue
poetry run doit run cl_bump document deploy_docs publish
# Note: cl_bump_pre is helpful for pre-releases rather than full increments
```

> Replace "..." with the API token generated on TestPyPi/PyPi respectively

### Checklist

- [ ] Run doit tasks (test) `poetry run doit`
- [ ] Commit and push all local changes
- [ ] Increment version: `poetry run doit run cl_bump`
- [ ] Check that the README and other Markdown files are up-to-date
- [ ] Publish (see above)
