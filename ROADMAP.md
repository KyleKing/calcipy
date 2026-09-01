# Roadmap

Outstanding work for calcipy, ordered by what blocks the most other things.
This file
replaces the scratch notes that used to sit at the repo root and under
`docs/superpowers/plans/`.
The planning detail worth keeping from them is in the
appendices.

Reaching a downstream project takes a calcipy release to PyPI, then a
[calcipy_template](https://github.com/KyleKing/calcipy_template) release, then a
`copier update` in each child.
That chain is why the release below sits at the top.

## Now

### Cut 6.1.0 final

`6.1.0rc0` was tagged 2026-07-29 and no release has followed.
Stuck behind it:

- the Zensical docs migration (`2bddcef2`)
- the CLI staying usable when an optional extra is missing (`b03d9654`)
- the vale prose linting task (`e41d2e5f`)
- the ruff ceiling on the `lint` extra (`dc985234`)

None of it reaches a child repo until the version is on PyPI.

Regenerate `uv.lock` before committing the bump.
`pre_bump_hooks = ["uv lock"]` already
does this, so the check is that the hook actually ran and the lockfile is in the bump
commit.

### Finish ADR-0009 in the template

[ADR-0009](docs/docs/adr/0009-pin-ruff-versions-for-the-lint-fix-hook.md) rests on
`required-version` under `[tool.ruff]` in each child's `pyproject.toml`, and that line
does not exist yet.
calcipy carries its half (`ruff >=0.16.0,<0.17.0` on the `lint`
extra), but calcipy_template's `package_template/pyproject.toml.jinja` only sets
`required-version` under `[tool.uv]`, which constrains uv rather than ruff.

Until the template writes that line, a hook/lockfile ruff mismatch stays silent, so the
fix loop can stop converging again.
That is the exact failure the ADR exists to prevent,
and the ceiling on the `lint` extra makes it look already handled.

### Make `lint.prose` work in a template child

vale exits with a runtime error when no `.vale.ini` is present, and calcipy packages
none, so `lint.prose` only runs in repos that hand-wrote the config.
calcipy's own
`.vale.ini` is the only reason the task works here.
Either pass `--config` pointing at a
packaged default (`StylesPath` wants a cache dir rather than a path inside
site-packages), or distribute the file from calcipy_template.
Recorded under
Consequences in
[ADR-0008](docs/docs/adr/0008-adopt-vale-ai-tells-for-prose-linting.md).

## Next

### Track the ruff ceiling as a doneram hold

`# TODO` at `pyproject.toml:77`. `.doneram.pkl` now exists and tracks the workflow and
`mkdocs.yml` pins, so this is a matter of adding the `Hold` entry rather than
bootstrapping the file.
calcipy_template's config is the worked example: the hold keeps
taking updates below `max` and carries the reason, so a stale pin fails the run instead
of rotting unnoticed.

### Judge `lint.slop-export` before it leaves beta

calcipy's own docs export to 33 documents and 33,182 words, which is thin for the n-gram
fingerprinting slop-forensics does.
The open question is whether a corpus this size
yields a stable word list at all.
Run it against a release cycle's worth of prose, then
promote the task, widen the corpus, or drop it.

### Close out the Zensical migration

Loose ends from the move off MkDocs + Material:

- `docs/gen_ref_nav.py` is a standalone script because Zensical does not support
    `mkdocs-gen-files`
    ([zensical/backlog#8](https://github.com/zensical/backlog/issues/8)).
    Restore the two
    `mkdocs_gen_files` lines once the plugin is supported natively
- The `doc` extra still pulls five `mkdocs-*` plugins plus `mkdocstrings`.
    Audit which
    ones Zensical actually consumes through its module mapping and drop the rest, so
    children stop installing dead dependencies

## Scope reduction

The largest body of work, and the one with the least agreement between the plans that
fed it.
It serves [#136](https://github.com/KyleKing/calcipy/issues/136), which argues
calcipy should run as a tool (`uvx`, `pipx`) rather than as a project dependency.
The
end state is calcipy keeping only first-party tooling (code tag collection, the
duplicate-test check, the griffe-based bump, the pyproject sync) and handing the
wrappers to calcipy_template.

### Decide how nox goes away

The approaches written up so far contradict each other.
Appendix B carries both in
enough detail to execute either.

- A `test.multi` calcipy task that shells out to `uv run --python <ver> pytest`,
    soft-deprecating `nox.noxfile` and deleting the template's `noxfile.py` boilerplate.
    Specified down to the code that would be written, and it keeps the logic in calcipy
- `mise.toml` tasks, which already define `test:310` through `test:312` and `test:all`,
    with the noxfile itself moving to the template.
    Less written down, and it matches the
    scope-reduction goal above

Pick one before writing code. The mise route fits the stated goal of shrinking calcipy's
surface area, and `mise.toml` already has working parity for the tests it would take
over, so the uv-task plan is a step sideways unless mise turns out not to cover CI.

Open either way: whether a minimal noxfile module stays for backwards compatibility, how
per-Python-version pytest configuration is handled, and when the `calcipy[nox]` extra is
deprecated.

### Move the wrapper tasks to mise

Appendix A inventories all 20 invoke tasks: 14 are pure shell (`lint.check`, `lint.fix`,
`types.mypy`, `types.pyright`, `test.pytest`, `doc.watch`, and the rest) against 6 that
need Python (`pack.bump_tag`, `pack.sync_pyproject_versions`, `tags.collect_code_tags`,
`doc.build`, `cl.write`, `test.check`).
Appendix C carries the mise usage syntax the
translation needs, so what remains is the rollout rather than the design.

The sequencing question left open is whether mise becomes the sole entry point (calling
calcipy for the six complex tasks) or whether both interfaces stay.
One entry point is
worth more than the migration costs, though it breaks every child's muscle memory and
every CI file at once, so it wants its own ADR.

### Write the `select = ['ALL']` ADR

[ADR-0009](docs/docs/adr/0009-pin-ruff-versions-for-the-lint-fix-hook.md) names this as
the deeper cause it deliberately did not address: `select = ['ALL']` with
`preview = true` enrolls the whole fleet in every preview rule on the day it is
released, and ruff's versioning policy allows preview rules to appear and change
behavior in a patch release.
Narrowing to explicit rule families removes the
auto-enrollment, at the cost of every rule nobody thought to list.

Revisit when `required-version` proves to be a bandage on a wound that keeps reopening,
or after two ruff minors pass cleanly and the question can be closed.

## Cleanup

### Fix the code tag summary's signal-to-noise

`docs/docs/CODE_TAG_SUMMARY.md` lists 11 tags and 8 of them are test fixtures from
`tests/tasks/test_tags.py` (`# TODO: root task`, `# TODO: include`, and friends).
Two
real tags are buried in the noise. Exclude `tests/` from the default collection, or
teach the collector to skip string literals.

### Drop `tomli`

`PLANNED` at `pyproject.toml:69`. `requires-python` is `>=3.10.11` today, so the
conditional dependency goes away when the floor moves to 3.11.
Python 3.10 reaches end
of life in October 2026, which sets the earliest reasonable date.

### Refresh the stale docs

- `docs/README.md:218` still documents `nox.noxfile` as the multi-version story, and
    `docs/README.md:9` compares calcipy to pyscaffold on a tox-versus-nox axis.
    Both need
    rewriting once the nox decision is made
- `docs/docs/MIGRATION.md` documents the v6 Poetry-to-uv move in emoji checkmarks.
    It
    reads as a release announcement rather than a migration guide, and it will not age
    well past v7

### Triage the two old link-dump issues

[#42](https://github.com/KyleKing/calcipy/issues/42) (ADRs) and
[#38](https://github.com/KyleKing/calcipy/issues/38) (README and documentation) are both
long unchecked reading lists.
#42 is substantially done, because nine ADRs exist in MADR
format under `docs/docs/adr/` with a README index.
What is left there is whether to
auto-generate the table of contents and whether Y-statements are worth adding for small
decisions.
Close it with those two carved out, or close it outright.
#38 has been open
since 2025 with no checked boxes, which is the signal to close it and open something
scoped.

## Appendix A: invoke task inventory

Which of the 20 tasks can become a mise task directly, and which need to keep calling
calcipy.

| Task                             | Shell command                                          | Miseable | Notes                                             |
| -------------------------------- | ------------------------------------------------------ | -------- | ------------------------------------------------- |
| **cl.bump**                      | `cz bump && git push && gh release`                    | Y        | Chain, optional suffix                            |
| **cl.write**                     | `cz changelog` plus a file move                        | N        | Post-command file operations                      |
| **doc.build**                    | Python preprocessing, then `zensical build`            | N        | Requires `write_template_formatted_md_sections()` |
| **doc.deploy**                   | `prek uninstall`, publish, `prek install`              | Y        | Multi-command                                     |
| **doc.watch**                    | `zensical serve`                                       | Y        | Simple                                            |
| **lint.check**                   | `python -m ruff check <target>`                        | Y        | Supports file args                                |
| **lint.fix**                     | `python -m ruff check --fix [--unsafe-fixes] <target>` | Y        | Optional flag                                     |
| **lint.pre_commit**              | `prek install && prek autoupdate && prek run ...`      | Y        | Multi-command chain                               |
| **lint.watch**                   | `python -m ruff check --watch <target>`                | Y        | Simple                                            |
| **nox.noxfile**                  | `python -m nox [--session <s>]`                        | Y        | Optional arg                                      |
| **pack.bump_tag**                | Python, griffe API analysis                            | N        | Semver logic                                      |
| **pack.lock**                    | `uv lock`                                              | Y        | Simple, no args                                   |
| **pack.sync_pyproject_versions** | Python, parses the lock and rewrites pyproject         | N        | File manipulation                                 |
| **tags.collect_code_tags**       | Python, regex parse and markdown generation            | N        | Code analysis                                     |
| **test.check**                   | Python, AST parse for duplicates                       | N        | Code analysis                                     |
| **test.coverage**                | `coverage run && report && html && json`               | Y        | Multi-command                                     |
| **test.pytest**                  | `python -m pytest ./tests --cov=<pkg> ...`             | Y        | Many optional args                                |
| **test.watch**                   | `ptw . --now ./tests ...`                              | Y        | Optional filters                                  |
| **types.mypy**                   | `python -m mypy`                                       | Y        | No args                                           |
| **types.pyright**                | `pyright`                                              | Y        | No args                                           |

Every task marked N stays in calcipy under either plan, called from mise as
`uv run calcipy <task>`.

## Appendix B: the two nox replacements

### Option 1, a `test.multi` calcipy task

Reads Python versions from `get_tool_versions()` (already used by the noxfile) and runs
pytest per version, with `UV_PROJECT_ENVIRONMENT` giving each version a persistent env
that mirrors nox's `reuse_venv=True`.

```python
@task()
def multi(ctx: Context) -> None:
    """Run pytest against all configured Python versions using uv."""
    for ver in dict.fromkeys(get_tool_versions()['python']):
        major_minor = '.'.join(str(ver).split('.')[:2])
        run(ctx, f'uv run --python {ver} pytest ./tests', env={'UV_PROJECT_ENVIRONMENT': f'.uv-tests/py{major_minor}'})
```

The env slug drops the patch so `3.13.11` maps to `py3.13` and the cache path survives
patch upgrades.
`dict.fromkeys()` deduplicates while preserving order, matching the
noxfile's set-dedup.

Everything else that changes:

- `_OTHER_TASKS` swaps `nox.noxfile.with_kwargs(session='tests')` for `test.multi`
- `calcipy/tasks/nox.py` and `calcipy/noxfile/_noxfile.py` get deprecation notes rather
    than deletion, so `calcipy[nox]` users keep working
- The `recommended` extra drops `nox` while the `nox` extra itself stays
- `.gitignore` gains `.uv-tests/`
- calcipy_template deletes `package_template/noxfile.py` and `.ctt/default/noxfile.py`

### Option 2, mise tasks

`mise.toml` already defines `test`, `test:310`, `test:311`, `test:312`, `test:all`, and
`test:all-verbose`, each running `uv run --group ci pytest tests/` against a Python
version from `[tools]`.
The work is confirming parity with the nox session, switching CI
to mise, then moving the noxfile to calcipy_template for projects that still want it.

Against option 1, mise declares versions in config where the noxfile discovers them
programmatically.
It also creates no venv per session, so it runs faster with one tool
fewer, and it moves the multi-version story out of calcipy entirely.

## Appendix C: mise usage syntax

Reference for translating invoke's flags and arguments when the tasks in Appendix A move
over.

| Type                | Syntax                                     | Description                 |
| ------------------- | ------------------------------------------ | --------------------------- |
| Required positional | `arg "<name>"`                             | Must be provided            |
| Optional positional | `arg "[name]"`                             | Can be omitted              |
| Variadic            | `arg "<name>" var=#true`                   | Captures all remaining args |
| Flag (boolean)      | `flag "-s --long"`                         | True if present             |
| Option (with value) | `flag "-o --option <value>"`               | Requires a value            |
| Default value       | `arg "<name>" default="value"`             | Fallback if not provided    |
| Choices             | `flag "-t --type <t>" { choices "a" "b" }` | Constrained values          |

In `run`, `${usage_name}` is the raw value (empty when unset), `${usage_name?}` errors
when unset, and `${usage_name:-default}` falls back.

Argument passing is the part that bites.
With multiple `run` commands, args reach the
last command only.
Args are not forwarded to `depends`, `pre`, or `post` tasks.
Use an
explicit `:::` to pass them to each task separately.

```toml
[tasks.lock]
description = "Update uv lock file"
run = "uv lock"

[tasks."lint:fix"]
description = "Run ruff with fixes"
usage = 'flag "-u --unsafe" help="Apply unsafe fixes"'
run = '''
#!/usr/bin/env bash
unsafe_flag=""
if [ "${usage_unsafe:-false}" = "true" ]; then
  unsafe_flag="--unsafe-fixes"
fi
uv run ruff check --fix $unsafe_flag ./calcipy ./tests
'''

[tasks."tags:collect"]
description = "Collect code tags (via calcipy)"
usage = 'arg "[args]" var=#true'
run = "uv run calcipy tags.collect-code-tags ${usage_args:-}"
```
