# `.github` README

The `ci_pipline.yml` Github Action is based on these excellent examples

- <https://github.com/executablebooks/mdformat/blob/4752321bb444b51f120d8a6933583129a6ecaabb/.github/workflows/tests.yaml>
- <https://github.com/codefellows/data-structures-and-algorithms/blob/7a1670b1475fc57a5f851c7685040c11bc41ec8d/.github/workflows/python-tests.yml>
- [Re-engineering the SciPy Pipelines](https://labs.quansight.org/blog/2021/10/re-engineering-cicd-pipelines-for-scipy/) and [Example](https://github.com/scipy/scipy/blob/c4829bddb859ffe5716a88f6abd5e0d2dc1d9045/.github/workflows/linux_meson.yml)
- <https://github.com/MrThearMan/savestate/blob/fb299e220ef366727857b1df0631300a027840fc/.github/workflows/main.yml>

Additional Resources

- `act`, a local GHA runner: <https://github.com/nektos/act>
- [actions/checkout](https://github.com/actions/checkout)
- [actions/setup-python](https://github.com/actions/setup-python)
- [abatilo/actions-poetry](https://github.com/abatilo/actions-poetry)
- [actions/cache](https://github.com/marketplace/actions/cache)
- [pre-commit/action](https://github.com/pre-commit/action)
- [Github Action Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

## In Progress

- Great article on AWS integration, screenshot artifacts, etc.
  - <https://posthog.com/blog/automating-a-software-company-with-github-actions>
- General Advice: <https://www.datree.io/resources/github-actions-best-practices>
  - <https://docs.github.com/en/actions/security-guides/encrypted-secrets>
  - <https://docs.github.com/en/billing/managing-billing-for-github-actions/viewing-your-github-actions-usage>
  - <https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows>
  - <https://docs.github.com/en/actions/managing-workflow-runs/manually-running-a-workflow>
- "docker" example building Docker image with layer caching
  - <https://github.com/scipy/scipy/blob/c4829bddb859ffe5716a88f6abd5e0d2dc1d9045/.github/workflows/docker.yml>
  - <https://github.com/scipy/scipy/blob/c4829bddb859ffe5716a88f6abd5e0d2dc1d9045/.github/workflows/gitpod.yml>
- "document" calcipy should be released locally, but useful for recipes and personal portfolio
  - <https://github.com/opinionated-code/opinionated-fastapi/blob/9d237237a986604aacf296548619b126b848af0e/.github/workflows/publish-docs.yml>
- "Awesome": <https://github.com/sdras/awesome-actions>
- "services" Can create PG or other services in workflows!
  - <https://github.com/Nike-Inc/knockoff-factory/blob/1567a46e5eaa3fe1bdf989ef5253f9ee0dbd69b3/.github/workflows/python-test.yaml>
- "artifact" optionally upload the report.zip from successful builds
  - <https://github.com/marketplace/actions/upload-a-build-artifact>
