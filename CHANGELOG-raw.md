# Changelog


## 0.0.2 (2020-11-14)

### New

* Separate task_git_add_docs. [Kyle King]

* Archive watchcode task. [Kyle King]

* Move DIG to separate file. [Kyle King]

* Move tasks to use a wildcard import. [Kyle King]

  - Breaking changes, but a huge improvement!

### Changes

* Add skipcq & update version. [Kyle King]

* Update documentation. [Kyle King]

* Improve how tags are located. [Kyle King]

* Chg: update documentation @WIP. [Kyle King]

* Minor type annotation fixes. [Kyle King]

  - Note: making the paths clickable in TAG_SUMMARY would appear to require the full local path, which isn’t worth tracking in git

### Other

* Merge branch 'main' into dev/development. [Kyle King]


## 0.0.1 (2020-11-14)

### New

* Add logging. Fixes #5. [Kyle King]

* New: intialized tag-finding logic @WIP. [Kyle King]

* Use a new DoItTask type for annotations. [Kyle King]

* Add type annotations. [Kyle King]

* New: Loguru configuration for init @WIP. [Kyle King]

* Activate DeepSource. [Kyle King]

* Allow user-content in __init__. Fixes #1. [Kyle King]

* Indicate private functions. Fixes #4. [Kyle King]

* Add loguru! [Kyle King]

* Add watchcode task for arbitrary files. [Kyle King]

* Flake8-ann & drop pur. [Kyle King]

* Show README contents in __init__ [Kyle King]

* Dump isort & flake8 settings in source path. [Kyle King]

* Improve linting & test tasks. [Kyle King]

* Vastly expanded test coverage. [Kyle King]

* Add ptw as a DoIt LongRunning task. [Kyle King]

* Initialize index.html as redirect. [Kyle King]

  - Based on https://github.com/pdoc3/pdoc/issues/55#issuecomment-614247015

* Implement source code from dash_charts. [Kyle King]

* Initialize poetry project. [Kyle King]

### Changes

* Improve logging. Addresses #5. [Kyle King]

* Improve logger context manager. [Kyle King]

* Add task to summarize tags. Fixes #2. [Kyle King]

* Move watchcode to separate file. [Kyle King]

* Mark additional globals as private. [Kyle King]

* Sync local changes for branch and TODOs. [Kyle King]

* Loosen dependencies requirements. [Kyle King]

* Add WIP type checker configs. [Kyle King]

* Drop dash dependency. [Kyle King]

* Remove unused packages. [Kyle King]

* Drop interrogate. [Kyle King]

* Try to improve interrogate table. [Kyle King]

* Add interrogate to README. [Kyle King]

* Implement linting tasks in package. [Kyle King]

* Push local changes for linting. [Kyle King]

* Add DIG.test_path. [Kyle King]

* Incremental changes from local. [Kyle King]

* Apply and cleanup local changes. [Kyle King]

* Create the index.html with redirect. [Kyle King]

* Add the HTML documentation to git control. [Kyle King]

* Move gitchangelog to package. [Kyle King]

* Sync local improvements to coverage & linting. [Kyle King]

* Update dependencies and documentation. [Kyle King]

* Further improved commit_docs task. [Kyle King]

* Set Dash version & update whitelist. [Kyle King]

### Fix

* Replace subprocess with sh. [Kyle King]

* Problems found by DeepSource. [Kyle King]

* Path to the .flake8 should be in source_path. [Kyle King]

* Remove DIG.gh_pages_dir & task_commit_docs. [Kyle King]

* Changelog creation. [Kyle King]

* Commit_docs task. [Kyle King]

* Add missing pystache dep for gitchangelog. [Kyle King]

* Document dash extras in README. [Kyle King]

### Other

* Merge pull request #12 from KyleKing/dev/development. [Kyle King]

  Improve Logging

* Merge pull request #11 from KyleKing/dev/development. [Kyle King]

  Add summary of TODO, FIXME, etc.

* Merge pull request #10 from KyleKing/dev/development. [Kyle King]

  Add Loger Configuration and Type Annotations

* Merge pull request #8 from KyleKing/dev/development. [Kyle King]

  - Merge code privacy changes and Deep Source fixes

* Initial commit. [Kyle King]


