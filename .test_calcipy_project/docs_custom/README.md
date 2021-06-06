# Test Project

This is a test project for use in testing `calcipy` and indirectly testing `calcipy_template`

When new template releases are available, make sure to rerun these snippets

```sh
# Update local files
cd .test_calcipy_project
copier update
rm -rf .git
# > Manually review and accept diffs

# Then test changes
cd ..
poetry run doit --continue
```
