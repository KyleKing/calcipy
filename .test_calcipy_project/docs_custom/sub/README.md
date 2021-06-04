# Test Project

This is a test project for use in testing `calcipy` and indirectly testing `calcipy_template`

For `calcipy` testing, ensure that the below commands are manually run:

<!-- FIXME: convert this to a submodule (on an orphan branch of calcipy?) so that checkouts work on other computers - otherwise, may fail in AppVeyor -->

```sh
# A git instance is required for finding files
git init
git add .
git commit -m "test: check-in files"
# These files are managed by the "calcipy_template" and should be updated when the template changes
copier update
```
