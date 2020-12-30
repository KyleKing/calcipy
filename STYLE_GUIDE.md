# Personal Style Guides

## Git

Use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) and [Commitizen](https://github.com/commitizen-tools/commitizen)

The [Changelog](https://keepachangelog.com/en/1.0.0/) is an important part of a project (built with `commitizen`). Use [semver](https://semver.org/)

### Conventional Commits

- `type(scope): description / body`
- The type feat MUST be used when a commit adds a new feature to your application or library.
- The type fix MUST be used when a commit represents a bug fix for your application.
- A scope MUST consist of a noun describing a section of the codebase surrounded by parenthesis, e.g., `fix(parser):` or issue number `fix(#32):`
- A `!` can be used to indicate a breaking change, e.g. `refactor!: drop support for Node 6`
- What if a commit fits multiple types?
    - Go back and make multiple commits whenever possible. Part of the benefit of Conventional Commits is its ability to drive us to make more organized commits and PRs.
    - It discourages moving fast in a disorganized way. It helps you be able to move fast long term across multiple projects with varied contributors.
- `semver`: `fix : PATCH / feat : MINOR / BREAKING CHANGE : MAJOR`
    - Use `git rebase -i` to fix commit names prior to merging if incorrect types/scopes are used

### Commitizen

- Types
    - fix: A bug fix
    - feat: A new feature
    - docs: Documentation-only changes (code comments, separate docs)
    - style: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons)
    - perf: A code change that improves performance
    - refactor: A change to production code that is not fix, feat, or perf
    - test: Adding missing or correcting existing tests
    - build: Changes that affect the build system or external dependencies (example scopes: pip, docker, npm)
    - ci: Changes to our CI configuration files and scripts (example scopes: GitLabCI)
- Scopes
    - Class, File name, Issue Number, other approved noun

### Guidelines

- [Commit message guidelines](https://writingfordevelopers.substack.com/p/how-to-write-a-commit-message)
    - Full sentence with verb (*lowercase*) and concise description. Below are modified examples for Conventional Commits
        - `fix(roles): bug in admin role permissions`
        - `feat(ui): implement new button design`
        - `build(pip): upgrade package to remove vulnerabilities`
        - `refactor: file structure to improve code readability`
        - `perf(cli): rewrite methods`
        - `feat(api): endpoints to implement new customer dashboard`
- [How to write a good commit message](https://chris.beams.io/posts/git-commit/)
    - A diff will tell you what changed, but only the commit message can properly tell you why.
    - Keep in mind: [This](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html) [has](https://www.git-scm.com/book/en/v2/Distributed-Git-Contributing-to-a-Project#_commit_guidelines) [all](https://github.com/torvalds/subsurface-for-dirk/blob/master/README.md#contributing) [been](http://who-t.blogspot.co.at/2009/12/on-commit-messages.html) [said](https://github.com/erlang/otp/wiki/writing-good-commit-messages) [before](https://github.com/spring-projects/spring-framework/blob/30bce7/CONTRIBUTING.md#format-commit-messages).
    - The seven rules of a great Git commit message
        - 2. [Try for 50 characters, but consider 72 the hard limit](https://chris.beams.io/posts/git-commit/#limit-50)
        - 7. [Use the body to explain what and why vs. how](https://chris.beams.io/posts/git-commit/#why-not-how)

### Github Labels

Personal Guide

- Labels
    - Type: (Bug, Maintenance, Idea, Feature)
- Milestones
    - Main Milestone (Currently Active Tasks) - name could change based on a specific project or month
    - Next Tasks
    - Blue Sky
- Search
    - `is:open is:issue assignee:KyleKing archived:false milestone:"blue sky"` or `no:milestone` etc.

#### Research

- [Sane Github Labels](https://medium.com/@dave_lunny/sane-github-labels-c5d2e6004b63) and see [sensible-github-labels](https://github.com/Relequestual/sensible-github-labels) for full descriptions of each
    - “it is much more helpful to see the status and type of all issues at a glance.”
    - One of each:
        - Status: …
            - Abandoned, Accepted, Available, Blocked, Completed, In Progress, On Hold, Pending, Review Needed, Revision Needed
        - Type: …
            - Bug, Maintenance, Question, Enhancement
        - Priority: …
            - Critical, High, Medium, Low
- [Britecharts](https://britecharts.github.io/britecharts/github-labels.html)
    - Status: …
        - On Review – Request that we are pondering if including or not
        - Needs Reproducing – For bugs that need to be reproduced in order to get fixed
        - Needs Design – Feature that needs a design
        - Ready to Go – Issue that has been defined and is ready to get started with
        - In Progress – Issue that is being worked on right now.
        - Completed – Finished feature or fix
    - Type: …
        - Bug – An unexpected problem or unintended behavior
        - Feature – A new feature request
        - Maintenance – A regular maintenance chore or task, including refactors, build system, CI, performance improvements
        - Documentation – A documentation improvement task
        - Question – An issue or PR that needs more information or a user question
    - Not Included
        - Priority: They would add complexity and overhead due to the discussions, but could help with the roadmap
        - Technology Labels: It can create too much overhead, as properly tag with technologies all the issues could be time consuming
- [Ian Bicking Blog](https://www.ianbicking.org/blog/2014/03/use-github-issues-to-organize-a-project.html)
    - Milestone Overview
        - What are we doing right now?
        - What aren’t we doing right now?
            - 2a. Stuff we’ll probably do soon
            - 2b. Stuff we probably won’t do soon
        - What aren’t we sure about?
    - Milestone Descriptions
        - Stuff we are doing right now: this is the “main” milestone. We give it a name (like Alpha 2 or Strawberry Rhubarb Pie) and we write down what we are trying to accomplish with the milestone. We create a new milestone when we are ready for the next iteration.
        - Stuff we’ll probably do soon: this is a standing “**Next Tasks**” milestone. We never change or rename this milestone.
            - We use a permanent “Next Tasks” milestone (as opposed to renaming it to “Alpha 3” or actual-next-iteration milestone) because we don’t want to presume or default to including something in the real next iteration. When we’re ready to start planning the next iteration we’ll create a new milestone, and only deliberately move things into that milestone.
        - Stuff we probably won’t do soon: this is a standing “**Blue Sky**” milestone. We refer to these tickets and sometimes look through them, but they are easy to ignore, somewhat intentionally ignored.
        - What aren’t we sure about?: issues with no milestone.
    - Label: “Needs Discussion” - (addressed in a triage meeting) - use liberally for either big or small tickets
    - “It’s better to give people more power: it’s actually helpful if people can overreach because it is an opportunity to establish where the limits really are and what purpose those limits have”

### External Links

**TODO: Revisit**

- [Git: The Simple Guide][1]
- [Commit Messages][2] and [why use the present tense](https://news.ycombinator.com/item?id=8874177)
- [Github's Advice on Github](https://github.com/erlang/otp/wiki/Writing-good-commit-messages)
- [Most Comprehensive Guide](https://chris.beams.io/posts/git-commit/)
- [Git Pro Book (free)](https://git-scm.com/book/en/v2)
    - [Bash Tab-Completion Snippet](https://git-scm.com/book/en/v2/Appendix-A%3A-Git-in-Other-Environments-Git-in-Bash)

[1]: http://rogerdudler.github.io/git-guide/
[2]: https://github.com/atom/atom/blob/master/CONTRIBUTING.md#styleguides

## Python

**TODO: Revisit**

- Python Style Guides
    - https://gist.github.com/sloria/7001839
    - http://www.nilunder.com/blog/2013/08/03/pythonic-sensibilities/
    - https://innoq.github.io/cards42org_en/

## ADRs

**TODO: Revisit**

- Examples
    - https://github.com/pawamoy/mkdocstrings/issues/28
