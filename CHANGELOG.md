## Unreleased

### Refactor

- rename DIG_CWD as PATH_TEST_PROJECT
- rename test file
- doit is lowercase (CC looks like Dolt)
- replace sh with subprocess-tee
- reduce excess logging
- move DOIT_CONFIG to import
- move dig test to dig test file

### Fix

- LongRunning passed tasks that should fail
- yesqa removed necessary noqa (H303, etc)
- incorrect output paths
- reduce false tags found (WIP). Fix #24
- regression in lint_project tasks
- unincremented version in toml

### Feat

- new add-trailing-comma and pyupgrade hooks
- new mkdocs tasks and improvements
- new optional preconvert to serialize logs
- move logger configuration to log_helpers
- new cl_bump task. Closes #21

## 0.1.0 (2020-12-19)

### Feat

- new write_cl task utilizing comittizen
- new task, pre_commit_hooks

### Refactor

- show STDOUT formatting in DoIt task
- remove archived code
