## Unreleased

### Fix

- incorrect output paths
- reduce false tags found (WIP). Fix #24
- regression in lint_project tasks
- unincremented version in toml

### Refactor

- reduce excess logging
- move DOIT_CONFIG to import
- move dig test to dig test file

### Feat

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
