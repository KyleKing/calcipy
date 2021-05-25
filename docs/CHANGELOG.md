## Unreleased

### Feat

- rename DIG to DG because doit is one word
- move changelog into doc_dir
- retrieve doc_dir from copier
- add log-setup fun for doit
- make (source) doc_dir configurable
- add sanitizer
- add pytype
- **#36**: start WIP ReadMeMachine
- **#36**: merge logic of markdown auto-formatters
- make code tag partially configurable
- move check_types into calcipy
- import templates from pdocs

### Fix

- remaining non-PEP585 Dict/Tuple
- import the loguru Logger class safely
- revert PEP585 changes, which are not available in 3.8
- type errors identified by mypy
- correct type annotation for DoitTask & start beartyping
- collect python files non-redundantly
- correct isort configuration
- restore ReadMeMachine
- repair small bugs found in tests
- make transitions optional

### Refactor

- make additional mypy fixes
- apply the pep585 pre-commit hook
- apply PEP585 for stdlib typing
- fix capitalization for doit (one word, all lowercase)
- improve activate_debug_logging
- try to replace Any with BaseAction
- apply 0.0.2 minor fixes
- apply 0.0.1 version of calcipy_template
- minor renaming for _MarkdownMachine
- fix lock file and line length
- run more pre-commit checks on commit
- standardize on code tags and cleanup

## 2021.0.2.0a0 (2021-02-11)

### Feat

- push tags with no pre-commit hooks on pre
- use Interactive instead of —yes for cl_bump*
- remove tag create/remove tasks
- new task cl_bump_pre
- replace MIT license with Unlicense
- use cz_legacy to generate changelogs
- remove task in anticipation of copier #26
- improve git pre-commit hooks
- new add-trailing-comma and pyupgrade hooks
- new mkdocs tasks and improvements
- new optional preconvert to serialize logs
- move logger configuration to log_helpers
- new cl_bump task. Closes #21

### Fix

- do not pass filenames to pre-commit
- **#43**: add year to version for pseudo-calver
- prevent legacy types for new commits
- prevent circular import in doit_tasks
- extras need to be defined as optional
- rollback hook changes as they are not working
- install hooks for push
- LongRunning passed tasks that should fail
- yesqa removed necessary noqa (H303, etc)
- incorrect output paths
- reduce false tags found (WIP). Fix #24
- regression in lint_project tasks
- unincremented version in toml

### Refactor

- **#22**: restore MIT license
- copy+paste unmodified labels workflow
- update local TODO notes
- make toml an optional import
- rename path_source to path_project
- rename DIG_CWD as PATH_TEST_PROJECT
- rename test file
- doit is lowercase (CC looks like Dolt)
- replace sh with subprocess-tee
- reduce excess logging
- move DOIT_CONFIG to import
- move dig test to dig test file

## 0.1.0 (2020-12-19)

### Feat

- new write_cl task utilizing comittizen
- new task, pre_commit_hooks

### Refactor

- show STDOUT formatting in DoIt task
- remove archived code

### New (Old)

- initialize new DIG for #7 (@WIP)
- last version with dash_dev package name (#22)
- use the climate strike license (#22)
- ADR template and notes

### Change (Old)

- try skipcq above the line
- suppress LGTM warnings
- skip all DeepSource checks of wildcard import
- make dev-dep an “Extra” Fix #19
- test wildcard imports
- remove temp files used to test DeepSource
- rename doit_helpers folder to doit_tasks
- register tasks in __init__ with __all__
- WIP remove old DIG
- restore documentation tasks from archive
- remove pdoc3 documentation tasks
- final changes to intialize calcipy. Fixes #22
- move notes on typeguard to #28
- rename folder to calcipy #22
- rename source to calcipy for #22
- remove pdoc3 & archive documentation tasks
- remove sh for Windows support @WIP
- try long running for pytest

### Fix (Old)

- remaining DS wilcard issue
- try one more time to fix DeepSource * issues
- attempt to resolve deepsource issues
- circular import for tag_collector
- breaking changes from DIG changes (#7)
- refactor the missing keyword argument logic
- bury attr exceptions for coverage table
- make creating the log directory optional

## 0.0.2 (2020-11-14)

### New (Old)

- separate task_git_add_docs
- archive watchcode task
- move DIG to separate file
- move tasks to use a wildcard import
- add logging. Fixes #5
- intialized tag-finding logic @WIP
- use a new DoItTask type for annotations
- add type annotations
- Loguru configuration for init @WIP
- activate DeepSource
- allow user-content in __init__. Fixes #1
- indicate private functions. Fixes #4
- add loguru!
- add watchcode task for arbitrary files
- flake8-ann & drop pur
- show README contents in __init__
- dump isort & flake8 settings in source path
- improve linting & test tasks
- vastly expanded test coverage
- add ptw as a DoIt LongRunning task
- initialize index.html as redirect
- implement source code from dash_charts
- initialize poetry project

### Change (Old)

- add skipcq & update version
- update documentation
- improve how tags are located
- update documentation @WIP
- minor type annotation fixes
- improve logging. Addresses #5
- improve logger context manager
- add task to summarize tags. Fixes #2
- move watchcode to separate file
- mark additional globals as private
- sync local changes for branch and TODOs
- loosen dependencies requirements
- add WIP type checker configs
- drop dash dependency
- remove unused packages
- drop interrogate
- try to improve interrogate table
- add interrogate to README
- implement linting tasks in package
- push local changes for linting
- add DIG.test_path
- incremental changes from local
- apply and cleanup local changes
- create the index.html with redirect
- add the HTML documentation to git control
- move gitchangelog to package
- sync local improvements to coverage & linting
- update dependencies and documentation
- further improved commit_docs task
- call out issues with task_commit_docs @wip
- set Dash version & update whitelist

### Fix (Old)

- replace subprocess with sh
- problems found by DeepSource
- path to the .flake8 should be in source_path
- remove DIG.gh_pages_dir & task_commit_docs
- changelog creation
- commit_docs task
- add missing pystache dep for gitchangelog
- document dash extras in README
