# Developer Notes

## Local Development

```sh
git clone https://github.com/KyleKing/calcipy.git
cd calcipy
poetry install -E development -E serializers -E commitizen_legacy

# See the available tasks
poetry run doit list

# Run the default task list (lint, auto-format, test coverage, etc.)
poetry run doit

# Make code changes and run specific tasks as needed:
poetry run doit run test
```

## Publishing

For testing, create an account on [TestPyPi](https://test.pypi.org/legacy/)

```sh
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry config pypi-token.testpypi ...

poetry build
poetry publish --repository testpypi
# If you didn't configure a token, you will need to provide your username and password to publish
```

To publish to the real PyPi

```sh
poetry config pypi-token.pypi ...
poetry build
poetry publish

# Combine build and publish
poetry publish --build
```

> Replace "..." with the API token generated on TestPyPi/PyPi respectively

### Changelog Snippets

Typically `poetry run doit run cl_bump` and `cl_bump_pre alpha` is sufficient for most cases. If additional changelog options are needed, see below:

<!-- TODO: make `cl_bump_pre alpha` and remove this section -->

```sh
# Specify a Pre-Release ({alpha,beta,rc})
poetry run cz bump --changelog --prerelease rc
poetry run cz bump --changelog --dry-run
poetry run cz bump --changelog
git push --tags
```

### Checklist

- [ ] Run doit tasks (test) `poetry run doit`
- [ ] Commit and push all local changes
- [ ] Increment version: `poetry run doit run cl_bump`
- [ ] Check that the README and other Markdown files are up-to-date
- [ ] Publish (see above)
