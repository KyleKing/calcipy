# Zensical Migration Guide (MkDocs + Material → Zensical)

> **AI context**: This guide is written for an AI agent assisting with migration. It covers the full surface area: what changes are required, what is compatible as-is, what needs verification, and what is not yet supported. Source: https://zensical.org/compatibility/ (fetched 2026-03-24).
>
> Zensical is built by the creators of Material for MkDocs and is designed as a drop-in replacement consolidating MkDocs, Material theming, and plugins into a single package.

---

## TL;DR

For most projects the migration is:

1. Replace `mkdocs` + `mkdocs-material` (and most plugins) with `zensical` in dependencies
1. Run `zensical build` or `zensical serve` — your existing `mkdocs.yml` works as-is
1. Fix any Jinja2 → MiniJinja template syntax if you have custom overrides
1. Replace `gh-deploy` CI step with the Zensical publishing workflow

---

## 1. Dependency Changes

### Remove

```
mkdocs
mkdocs-material
mkdocs-material-extensions   # bundled in zensical
```

### Add

```
zensical
```

### Plugins — check each one

Zensical natively supports 27 plugins via its module system. When listed in `mkdocs.yml`, they are automatically mapped to Zensical modules with no config changes needed.

#### Tier 1 — highest priority, expected to work

| Plugin                                 | Notes                  |
| -------------------------------------- | ---------------------- |
| `mkdocs-autorefs`                      | Supported              |
| `mkdocs-awesome-nav`                   | Supported              |
| `mkdocs-exclude`                       | Supported              |
| `mkdocs-glightbox`                     | Supported              |
| `mkdocs-literate-nav`                  | Supported              |
| `mkdocs-macros-plugin`                 | Supported              |
| `mkdocs-meta-plugin`                   | Supported              |
| `mike`                                 | Supported (versioning) |
| `mkdocs-minify-plugin`                 | Supported              |
| `mkdocstrings` / `mkdocstrings-python` | Supported              |
| `mkdocs-offline-plugin`                | Supported              |
| `mkdocs-redirects`                     | Supported              |
| `mkdocs-search`                        | Supported (built-in)   |
| `mkdocs-tags-plugin`                   | Supported              |

#### Tier 2 — secondary priority, may have partial support

| Plugin                                      | Notes   |
| ------------------------------------------- | ------- |
| `mkdocs-audio`                              | Planned |
| `mkdocs-blog`                               | Planned |
| `mkdocs-gen-files`                          | Planned |
| `mkdocs-git-authors-plugin`                 | Planned |
| `mkdocs-git-committers-plugin`              | Planned |
| `mkdocs-git-revision-date-localized-plugin` | Planned |
| `mkdocs-optimize-plugin`                    | Planned |
| `mkdocs-privacy-plugin`                     | Planned |
| `mkdocs-rss-plugin`                         | Planned |
| `mkdocs-social`                             | Planned |
| `mkdocs-static-i18n`                        | Planned |
| `mkdocs-table-reader-plugin`                | Planned |
| `mkdocs-video`                              | Planned |

#### Unknown / not in the supported list

Any plugin **not listed above** has no stated compatibility. Before removing it, verify:

- Does Zensical have a built-in equivalent feature?
- Is the plugin maintained and likely to add Zensical support?
- Can the plugin functionality be replicated in content or configuration?

---

## 2. Configuration (`mkdocs.yml`)

**No changes required.** Zensical reads `mkdocs.yml` directly. Plugin entries are automatically mapped to Zensical modules.

### Known incompatibilities to verify

| Setting                                        | Status                                                                                                                     |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `theme: name: material`                        | Supported — Zensical ships the Material theme                                                                              |
| `theme: features: [...]`                       | Supported — full Material feature parity claimed                                                                           |
| `pymdownx.*` extensions                        | Supported                                                                                                                  |
| `!!python/name:` YAML tags (e.g., emoji index) | **Verify** — these call Python callables at build time; confirm Zensical handles them or replace with built-in equivalents |
| `extra_css` / `extra_javascript`               | Supported                                                                                                                  |
| `watch:`                                       | Supported                                                                                                                  |
| `edit_uri:`                                    | Supported                                                                                                                  |

### This project's `mkdocs.yml.jinja` — items to verify

The template uses:

- `pymdownx.emoji` with `!!python/name:material.extensions.emoji.twemoji` — the callable references `material.*`; confirm Zensical bundles this or provides a replacement path
- `codehilite` + `pymdownx.highlight` — both are listed; this is redundant in MkDocs too, but confirm Zensical does not error on duplicate highlighters
- `gen-files` (Tier 2) — used to generate API reference nav; verify this works before removing it
- `mkdocstrings` (Tier 1) — should work, but test Python handler options (`docstring_section_style`, `separate_signature`, etc.)

---

## 3. CLI Changes

### Commands that work

```bash
zensical build       # replaces: mkdocs build
zensical serve       # replaces: mkdocs serve
```

### Flags removed or changed

| MkDocs flag                                    | Zensical behavior                                                         |
| ---------------------------------------------- | ------------------------------------------------------------------------- |
| `--theme` / `-t`                               | Not supported — single theme only                                         |
| `--use-directory-urls` / `--no-directory-urls` | Not supported as flags — set `use_directory_urls` in `mkdocs.yml` instead |
| `--site-dir`                                   | Not supported as flag — set `site_dir` in config                          |
| `--strict`                                     | Currently ignored — validation planned for future                         |
| `serve --dirty`                                | Unnecessary — Zensical caches by default                                  |

### Commands not implemented

| MkDocs command     | Alternative                                          |
| ------------------ | ---------------------------------------------------- |
| `mkdocs gh-deploy` | Use Zensical publishing guide; update CI/CD workflow |
| `mkdocs get-deps`  | Declare deps in `pyproject.toml` directly            |

---

## 4. Template Overrides

Zensical uses **MiniJinja** instead of Jinja2. HTML structure is preserved, but syntax differences require adjustments.

### Known MiniJinja vs Jinja2 differences to audit

- `{% set ns = namespace(x=0) %}` — `namespace()` may not exist; use direct variable reassignment patterns supported by MiniJinja
- Filters: most standard Jinja2 filters work; custom filters registered via MkDocs hooks will not
- `{% call(arg) macro_name() %}` — block calls with arguments differ; verify any custom macros
- `loop.cycle()` — verify availability
- `{% trans %}` i18n blocks — verify if used
- `{{ super() }}` in block overrides — should work but confirm

### Audit steps

1. Find all template overrides: `find docs/ -name "*.html" -path "*/overrides/*"`
1. Search for Python-specific Jinja2 constructs: `grep -r "namespace\|import\|from.*import" docs/`
1. Run `zensical build` and inspect any template rendering errors

---

## 5. CI/CD Changes

### GitHub Actions

Replace the deploy step:

```yaml
# Before
  - run: mkdocs gh-deploy --force

# After — consult https://zensical.org/docs/ for current publishing guide
# Likely: build with zensical, then deploy the site_dir artifact
  - run: zensical build
  - uses: peaceiris/actions-gh-pages@v3
    with:
      github_token: ${{ secrets.GITHUB_TOKEN }}
      publish_dir: ./releases/site
```

Update any pinned dependency installs:

```yaml
# Before
pip install mkdocs mkdocs-material

# After
pip install zensical
# or with uv:
uv add --dev zensical
```

---

## 6. Migration Checklist

Work through these in order. Each item should pass before moving to the next.

### Phase A — Dependency swap

- [ ] Remove `mkdocs`, `mkdocs-material`, `mkdocs-material-extensions` from `pyproject.toml`
- [ ] Add `zensical` as a dev dependency
- [ ] Run `zensical build` — confirm no errors
- [ ] Confirm output in `releases/site/` matches prior build visually

### Phase B — Plugin verification

- [ ] Audit every plugin in `mkdocs.yml` against the Tier 1/2 lists above
- [ ] For Tier 2 plugins, test each feature (gen-files API nav, git dates, etc.)
- [ ] For unlisted plugins, evaluate replacement or removal
- [ ] Remove plugin packages that are now bundled in Zensical

### Phase C — Template overrides

- [ ] Locate any custom `overrides/` HTML files
- [ ] Audit for Jinja2 constructs incompatible with MiniJinja (see Section 4)
- [ ] Fix syntax issues and re-run `zensical build`

### Phase D — CLI and CI

- [ ] Update `Makefile` / `noxfile.py` / `run` scripts: `mkdocs` → `zensical`
- [ ] Remove `--dirty`, `--strict`, `--site-dir` flags from build commands if used
- [ ] Replace `mkdocs gh-deploy` in CI with Zensical-compatible deploy step
- [ ] Update `pyproject.toml` dependency groups and lock file

### Phase E — Validation

- [ ] Full `zensical build --strict` equivalent (when available) with zero warnings
- [ ] Check rendered site: navigation, search, code blocks, diagrams, API reference
- [ ] Verify `pymdownx.emoji` renders correctly (callable path may need updating)
- [ ] Verify link validation (if previously using `--strict`)
- [ ] Deploy to staging and confirm URLs are unchanged

---

## 7. Known Risks

| Risk                                                  | Severity   | Mitigation                                                        |
| ----------------------------------------------------- | ---------- | ----------------------------------------------------------------- |
| `!!python/name:material.extensions.emoji.*` callables | Medium     | Test early; Zensical may remap these or require a config update   |
| `gen-files` (Tier 2) for API nav generation           | Medium     | Test before committing to migration; have a fallback nav strategy |
| Unlisted plugins with no Zensical equivalent          | High       | Inventory all plugins first; find alternatives before starting    |
| MiniJinja template incompatibilities                  | Low–Medium | Only affects projects with custom `overrides/` HTML               |
| `gh-deploy` removal                                   | Low        | Well-documented alternatives exist                                |
| Zensical Tier 2 plugins incomplete                    | Medium     | Zensical is early-stage; check GitHub issues for current status   |

---

## 8. Rollback Plan

Zensical reads `mkdocs.yml` unchanged, so rollback is straightforward:

1. Reinstall `mkdocs` + `mkdocs-material` + original plugins
1. Run `mkdocs build` — no config changes needed to revert

Keep the original `pyproject.toml` lockfile committed on a branch until migration is fully validated in production.

---

## References

- Zensical compatibility overview: https://zensical.org/compatibility/
- Configuration compatibility: https://zensical.org/compatibility/configuration/
- Feature parity: https://zensical.org/compatibility/features/
- Plugin compatibility: https://zensical.org/compatibility/plugins/
- CLI compatibility: https://zensical.org/compatibility/cli/
- Getting started / install: https://zensical.org/docs/get-started/
