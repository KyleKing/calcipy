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

Other useful poetry snippets

```sh
# Specify a Pre-Release ({alpha,beta,rc})
poetry run cz bump --prerelease rc --changelog
poetry run cz bump --changelog --dry-run
poetry run cz bump --changelog
git push --tags
```
