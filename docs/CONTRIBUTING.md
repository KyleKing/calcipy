# Contributing

Thanks for taking a look! This is primarily a personal project, but Pull Requests and Issues (questions, feature requests, etc.) are welcome. If you would like to submit a Pull Request, please open an issue first to discuss what you would like to change

## Pull Requests (PR)

### Code Development

See [./DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md)

### PR Process

1. Fork the Project and Clone
2. Create a new branch (`git checkout -b feat/feature-name`)
3. Edit code; update documentation and tests; commit and push
4. Before submitting the review and pushing, make sure to run `poetry run doit`
5. Open a new Pull Request

> Recommended: See my style guide for [commit message conventions](https://gist.github.com/KyleKing/729914c4c88c8de8bcb11f7e978d24cc)

If you run into any issues, please open a new issue or respond to the corresponding open issue

### Other PR Tips

- Link the issue with `Fixes #N` in the Pull Request body
- Please add a short summary of `why` the change was made, `what changed`, and any relevant information or screenshots

```sh
# SHA is the SHA of the commit you want to fix
git commit --fixup=SHA
# Once all the changes are approved, you can squash your commits:
git rebase --interactive --autosquash main
# Force Push
git push --force
```
