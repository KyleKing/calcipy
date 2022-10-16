## Unreleased

### Feat

- sign commitizen tags
- add plantuml generation to mkdocs

### Fix

- remove version conflict with flake8-simplify and cl_bump

## 0.19.1 (2022-10-13)

### Fix

- don't auto-install types

## 0.19.0 (2022-10-06)

### Feat

- support optional logging of arguments

### Fix

- split mypy install from mypy run

## 0.18.0 (2022-09-27)

### Feat

- support Arrow in pydantic and mypy (ArrowType was causing errors)
- remove pdoc(s) from document task
- add gen_ref_nav!
- tried pybetter, but too focused on adding __all__
- **#102**: sort-of-replace pdocs, but pdoc only shows one function
- add mypy install argument
- expand flake8 and reduce tests

### Fix

- re-run prdc
- lower fail-under for diff. Raise for regular test
- standardize on a single doit task list
- Pathlib.absolute is not documented. Use .resolve

### Refactor

- add type hints and minor changes for mypy
- make python files non-executable (chmod -x)

## 0.17.1 (2022-09-22)

### Fix

- pytest cache assert circular reference

### Refactor

- move check_security from nox into doit

## 0.17.0 (2022-09-17)

### Feat

- add docformat
- make pyupgrade flag configurable based on minimum python version
- replace pendulum with arrow
- update to latest copier

### Fix

- move yamllint configuration to project-specific config
- naive datetimes can't be subtracted on Windows
- hack together a dictionary instead of punq
- drop safety because of false positives on Calcipy CalVer

### Refactor

- experiment with custom semgrep rules
- formalize solution from last commit
- try to fix punq by switching to functions
- fix one test, refactor a little, but punq is still not working
- begin replacing attrs with pydantic
- update semgrep nox task
- upgrade copier with linting fixes

## 0.16.0 (2022-08-04)

### Feat

- add flake8-simplify

### Fix

- show only date in coverage table

## 0.15.0 (2022-08-03)

### Fix

- resolve pyroma errors by installing poetry as a module

## 0.15.0rc0 (2022-07-24)

### Feat

- init update workflow and toml sorter
- create script to bump toml minimum requirements

### Fix

- properly handle missing datetime
- try to use separate sqlite files for pre-commit and doit
- correct safety arguments
- use the unversioned API for releases
- try to handle pypi response when no "releases"
- handle prefix of "*"
- improve error message when "releases" not present
- use sqlite3 for pre-commit concurrent doit access

## 0.14.5 (2022-03-05)

### Fix

- **#91**: prevent minified files from appearing in Code Tag Summary

## 0.14.4 (2022-03-01)

### Fix

- set upper limit to fix flake8-bandit compat

## 0.14.3 (2022-03-01)

### Fix

- suppress only known git blame errors
- use Github tables to prevent multi-line rows in Code Tag Summary

## 0.14.2 (2022-02-27)

### Fix

- don't allow multi-line tables

## 0.14.1 (2022-02-27)

### Fix

- lower pandas constraint for better 3.7 support
- drop generation of requirements.txt

## 0.14.0 (2022-02-27)

### Feat

- use next-gen attrs syntax
- improve code tag regex

### Fix

- correct type annotations
- undo silent nox step
- make coverage.json optional for task_doc

## 0.13.0 (2022-02-23)

### Feat

- drop AppVeyor and update with copier
- **#67**: initialize GH CI Action

### Fix

- drop appveyor from cz version files
- attempt to resolve UnicodeError on Windows action
- address more minor CI errors
- make yamllint more relaxed
- attempt to resolve CI issues
- remove diff-quality check until fixed for CI
- always use Interactive when using /dev/null
- run push hook stage and format subproject
- support Python 3.7.12
- don't suppress nox missing interpreter errors

### Refactor

- pre-commit can be run in one command
- resolve LGTM error

## 0.12.2 (2022-02-21)

### Fix

- skip cassette files

## 0.12.1 (2022-02-18)

### Fix

- always return 0 to complete format task
- use short paths when formatting Python code if available

## 0.12.0 (2022-02-18)

### Feat

- initialize calcipy pre-commit hook

## 0.11.0 (2022-02-18)

### Feat

- don't verify on cz_bump

### Refactor

- format fixes
- reduce noise on matched vulnerabilities
- make run_cmd public
- remove jsonlint action
- use beartype typing
- move pre-commit hooks into doit

## 0.10.0 (2022-01-19)

### Feat

- create Github release if gh CLI is installed

## 0.9.1 (2022-01-17)

### Fix

- correct code-tag-collector for CLI use
- use target file's directory for git info

### Refactor

- drop template echo command

## 0.9.0 (2022-01-17)

### Feat

- show code tag summary as a table
- add date of last blame to code tag summary
- only link code tag from line number
- use revision-specific commit hashes
- add git links to code tag summary
- add python format pre-commit hook
- add support for TOML formatting with taplo

### Fix

- handle "0000.." hash by using branch name
- handle non-git directories
- use correct line number for pinned hash
- handle git dependencies when checking stale packages
- use positional arguments for pre-commit commands
- correct syntax error in pre-commit command

### Refactor

- make slow python pre-commit push-only
- apply auto-format tools to test project

## 0.8.2 (2022-01-16)

### Fix

- drop all references to CalVer

## 0.8.1 (2022-01-16)

### Refactor

- drop tag_format and use semver-only

## 0.8.0 (2022-01-16)

### Feat

- add pip-check for prettier outdated
- add cct command
- initialize the cement CLI application
- replace toml with tomli (#74)
- move wily to nox to reduce version conflicts
- add pip-audit
- add attrs_strict
- trim trailing whitespace from doc output

### Fix

- bump year to 2022
- code_tag_collector must return doit-compliant value (None)
- only run pre-commit once
- Code Tag Collector cannot return a Path for DoIt tasks
- cct was not being created as an alias. Use full command
- wily
- properly exclude auto-generated doc files from code tag collector
- run ptw on whole directory, not just test files
- drop FYI and NOTE from Code Tags

### Refactor

- fix PY-W2000 by using __all__
- move file_search to top-level
- just run pre-commit install
- replace pass with ... to keep it from being removed

## 0.6.0rc2 (2022-08-04)

### Feat

- drop pytest-cov and run coverage directly

### Fix

- swap pytest-watch(er) and other version bumps
- pin min-version (xenon) & drop preconvert and flake8-mock

## 0.6.0rc1 (2022-08-04)

### Fix

- bug in noxfile and code tags reading doc output files

## 0.6.0rc0 (2022-08-04)

### Feat

- implement pylint rules
- add xenon (wraps radon)
- condense doit output in show_cmd
- initial semgrep implementation
- add code diagrams to doc-site
- add notes on wily and pylint
- add vulture
- diff-quality (lint)
- add it
- add output if no stale packages found
- add autoflake

### Fix

- try to fix issues found with pytest_cache_assert
- drop unused Python2 demjson
- error in noxfile with poetry install

### Refactor

- decouple code tag collector from DG
- improve lint_py and the return type check is working
- zip release task
- cleanup a few minor errors
- use Interactive instead of Chrome
- apply fixes found from semgrep
- rename "wrappers" to "dot_dict"
- prevent mutation in DG.set_paths

## 0.3.1rc0 (2022-08-04)

### Feat

- add task to zip artifacts from testing
- implement pandas.to_markdown for cov table
- **#58**: implement doc task and merge serve_docs
- make loading YAML files more generic
- create doit summary report
- add task to check license compliance
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

- install full dev-dep as temporary nox workaround
- prevent committing changelog at base dir
- remove type_name from docstring for Google-style
- run pytest as a module for nox
- resolve doc_dir and style errors
- **#58**: remove None from pdocs output
- deconflict doit/nox
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

- see if only one space is okay for skipcq
- fix anti-pattern with nox session decorator and arg
- improve code quality
- try to suppress deepsource errors
- address DeepSource issues
- split up set_paths from DG
- fix formatting error from pre-push
- rename doc_dir to doc_sub_dir for clarity
- apply 0.0.10 template
- move markdown to subdirectory for mkdocs
- move isort back to toml
- fix edge case in diff-cov failing and lint errors
- relicense with MIT for better compliance
- create generic doit-runner for noxfile
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

## 0.2.0a0 (2022-08-04)

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
