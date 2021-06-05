## Unreleased

### Feat

- move lock into doit tasks with file-dependency
- **#38**: re-implement coverage and write source
- drop subprocess-tee
- **#36**: WIP implementation of doc formatting
- implement publish tasks
- add pip outdated to stale check
- implement check for stale packages
- begin implementing stale package check
- smart default tasks for CI vs. local
- make nox imports optional
- try doit rather than CWD for initial path
- move noxfile into calcipy
- integrate nox to doit tasks
- WIP check for stale dep & placeholder publish
- add additional configuration options
- add nox tasks
- add detect-secrets as pre-commit
- lint non-Python files
- read doc_dir from copier file
- make most settings configurable
- added dotted-dict wrapper of Box
- delete old files rather than full directory
- filter with glob-like ignore_patterns (2/2)
- add security check task
- add skip_phrase for code tag skipping
- beartype - roar!
- optionally clear log directory. Move file_helpers from base
- new tail-like reverse read_lines
- rename DIG to DG because doit is one word
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

- repair failing test
- packaging needed keyword argument
- import and nox syntax errors
- run push pre-commit hooks with doit
- show log warning instead of error for stale dep
- improve output from check_stale
- errors caught in testing
- suppress beartype warnings for now
- drop logger middleware
- catch most calcipy section typos in toml
- remove check-secrets but keep snippets
- errors in ignore patterns
- import doit and expand nox test file
- skip tags must be at bottom
- reset Lint paths instead of extend
- use find_files for code tag summary
- don't manually add the package source dir
- lint typing and improve tests
- create separate file_search file to fix imports
- **#51**: replace glob with git-based file identification
- **#53**: Use Interact instead of LongRunning
- undo PEP585 for runtime beartype
- resolve file explosion from _find_files
- import the loguru Logger class safely
- additional problems found with mypy
- fix Doit Types and start beartype
- add no-verify to cl_bump
- correct isort configuration
- restore ReadMeMachine
- repair small bugs found in tests
- make transitions optional

### Refactor

- fix some type issues
- minor fixes from AppVeyor testing
- **#38**: reduce complexity
- minor cleanup to docs
- apply pre-commit autoformat
- auto-drop skipcq comment
- format with VSCode
- fix lint errors in YAML files
- move find file paths to DG.meta
- move if_found_unlink to file_helpers
- fix formatting with pre-commit
- fix attribute names for path types (1/2)
- use calcipy:skip-tags
- fix minor code tags
- move __temp_chdir and improve fix_dg
- narrow type ignore use
- use path_file of file_path
- apply auto-fixes from pre-commit
- replace all glob-search with find_files
- remove find_files from code_tag script
- update isort for trailing-comma
- move excluded lint rules to DG
- apply PEP585 and add pre-commit hook
- fix capitalization for doit (one word, all lowercase)
- improve activate_debug_logging
- try to replace Any with BaseAction
- apply 0.0.2 minor fixes
- apply 0.0.1 version of calcipy_template
- minor renaming for _MarkdownMachine
- fix lock file and line length
- run more pre-commit checks on commit
- standardize on code tags and cleanup

### Perf

- combine autopep8 paths into single command
- combine files for linting in one command

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

### Fix (Old)

- remaining DS wilcard issue
- try one more time to fix DeepSource * issues
- attempt to resolve deepsource issues
- circular import for tag_collector
- breaking changes from DIG changes (#7)
- refactor the missing keyword argument logic
- bury attr exceptions for coverage table

## 0.0.3 (2020-12-10)

### New (Old)

- use the climate strike license (#22)
- ADR template and notes

### Change (Old)

- remove sh for Windows support @WIP
- try long running for pytest

### Fix (Old)

- make creating the log directory optional

## 0.0.2 (2020-11-14)

### New (Old)

- separate task_git_add_docs
- archive watchcode task
- move DIG to separate file
- move tasks to use a wildcard import

### Change (Old)

- add skipcq & update version
- update documentation
- improve how tags are located
- update documentation @WIP
- minor type annotation fixes

## 0.0.1 (2020-11-14)

### New (Old)

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
