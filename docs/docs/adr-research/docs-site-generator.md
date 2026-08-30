# Successor to MkDocs for package docs

Research from 2026-08-16 on what should build the per-package docs sites (calcipy, corallium, diacea, tail-jsonl, and the rest of the copier-template family). Two spikes back the conclusions.

## How the sites are used today

Each site is a README, a few Markdown pages (changelog, developer guide, ADRs), an auto-generated API reference, client-side search, and a `gh-pages` deploy from a calcipy task. Content is Python-Markdown with pymdownx (admonitions, superfences, tabbed), which is also the dialect the `mdformat-mkdocs` and `mdformat-admon` plugins target. As of July 2026 the build runs on Zensical reading the unchanged `mkdocs.yml`, with `docs/gen_ref_nav.py` writing mkdocstrings stubs before the build.

## Where the ecosystem is (August 2026)

- MkDocs is unmaintained (1.6.1 from 2024-08, last commit 2025-10). Tom Christie's "MkDocs 2.0" drops the plugin system and has not shipped to PyPI ([discussion 4077](https://github.com/mkdocs/mkdocs/discussions/4077), [chronicle](https://fpgmaas.com/blog/collapse-of-mkdocs/))
- Material for MkDocs is in maintenance mode, EOL 2026-11-05 ([issue 8523](https://github.com/squidfunk/mkdocs-material/issues/8523))
- Zensical is at 0.0.55, weekly releases, "alpha" per its [roadmap](https://zensical.org/about/roadmap/), no 1.0 ETA. It reads `mkdocs.yml` indefinitely and maps `plugins:` onto built-in modules. Supported: mkdocstrings, autorefs, section-index, macros, mike, glightbox, markdown-exec. Not supported and dropped without a warning: gen-files, git-revision-date-localized, llmstxt, minify, redirects, tags ([compatibility table](https://zensical.org/compatibility/plugins/)). The third-party module API is held back and iterated inside the paid Spark tier first ([backlog 41](https://github.com/zensical/backlog/issues/41))
- ProperDocs is oprypin's drop-in MkDocs 1.x continuation (1.6.7, 2026-03), the zero-change fallback ([release notes](https://properdocs.org/about/release-notes/))
- mkdocstrings-python 2.0.6 and griffe 2.2.0 are current. pawamoy joined the Zensical core team and said he would keep mkdocstrings going for roughly a year while Zensical rethinks API docs ([post](https://pawamoy.github.io/posts/sunsetting-the-sponsorware-strategy/)). [griffe2md](https://github.com/mkdocs/griffe2md) 1.5.0 renders the same griffe model to plain Markdown with the same Jinja-template approach
- Outside Python: Astro Starlight 0.41 (Pagefind search, best default UX), VitePress 1.x, mdBook 0.5, Hugo Book/Hextra, Sphinx 9 (needs Python 3.12+) with furo or shibuya, Rspress 2 (every page also served as Markdown plus llms.txt). None generates Python API pages. Each needs Markdown handed to it

## Options

| Option                       | UX                      | Longevity                            | Moving parts                    | Cost to move                                   |
| ---------------------------- | ----------------------- | ------------------------------------ | ------------------------------- | ---------------------------------------------- |
| Zensical (stay)              | Material                | Alpha, funded team, plugin API gated | Python only                     | Zero                                           |
| ProperDocs                   | Material (EOL Nov 2026) | Small team, frozen design            | Python only                     | Zero                                           |
| Sphinx + shibuya/furo + MyST | Good                    | Boring and durable                   | Python 3.12+, `conf.py`         | Rewrite `!!!` to MyST directives in every repo |
| Astro Starlight              | Best                    | Astro-backed, stable                 | Node in every repo's doc build  | Rewrite admonitions to `:::` asides            |
| Own generator                | Whatever I build        | Mine to maintain                     | markdown-it-py, Jinja, Pagefind | Weeks, then theme, nav, and search forever     |

## Spikes

**Spike 1, what Zensical drops.** A clean `zensical build` of calcipy takes 8.5s and finishes with "No issues found" while `mkdocs-llmstxt` and `git-revision-date-localized` produce nothing. The silent drop is confirmed. The build also copies `gen_ref_nav.py` and `Calcipy.sketch` into the site because they live under `docs_dir`.

**Spike 2, API reference as plain Markdown without mkdocstrings.** A 30-line script loads the package with griffe, walks public modules, and calls `griffe2md`'s `render_object_docs` per module into `docs/reference/<module>.md`. It runs in 1.6s (including griffe load), yields 19 pages, and Zensical renders them with the mkdocstrings plugin removed in the same 8s. Two gaps showed up:

- griffe2md's summary lists link to `#calcipy.tasks.lint.check` but Python-Markdown slugifies headings differently. Appending `{ #calcipy.tasks.lint.check }` to each heading fixed 88 of 120 warnings
- The other 32 are cross-page links (`#calcipy.cli` from the package index) and external types (`#pathlib.Path`, `#str`). This is the resolver work `mkdocs-autorefs` and `objects.inv` do. It is a map from object path to page plus anchor, with unresolved externals downgraded to plain text, on the order of 30 lines

Rendered side by side, mkdocstrings gives collapsible source blocks, annotated signatures, and short headings. griffe2md gives fully qualified headings, summary bullets, and no source links. The gap is templates, not data: griffe already holds source spans, annotations, and inherited members.

The spike script (kept out of the repo, reproduced here for the record):

```python
import re, shutil, sys
from pathlib import Path
import griffe
from griffe2md._internal.main import render_object_docs

pkg, out = sys.argv[1], Path(sys.argv[2])
loader = griffe.GriffeLoader(docstring_parser=griffe.Parser.google)
root = loader.load(pkg)
loader.resolve_aliases(external=True)
config = {"heading_level": 1, "show_submodules": False, "members_order": "alphabetical", "line_length": 120}

def walk(mod):
    yield mod
    for m in mod.members.values():
        if not m.is_alias and m.is_module:
            yield from walk(m)

for mod in walk(root):
    if not mod.is_public or not any(m.is_public and not m.is_alias and not m.is_module for m in mod.members.values()):
        continue
    parts = mod.path.split(".")[1:]
    dest = out.joinpath(*parts, "index.md") if mod.is_package else out.joinpath(*parts).with_suffix(".md")
    dest.parent.mkdir(parents=True, exist_ok=True)
    md = render_object_docs(mod, config)
    dest.write_text(re.sub(r"^(#+ `([\w.]+)`)$", r"\1 { #\2 }", md, flags=re.M))
```

## Decision

Keep Zensical as the site generator and move the API reference off mkdocstrings onto a griffe-based Markdown emitter.

The site generator is a commodity for this content. What ranks first is look and feel, and Material is the look technical users already know. Zensical keeps it, keeps the pymdownx dialect the mdformat plugins target, needs no Node, and costs nothing to keep. Its risks are real (alpha, plugin API behind a paid tier, a planned parser change) but they are risks to a layer that is cheap to swap as long as the content stays plain Markdown. Starlight is the exit if Zensical stalls, at the price of Node in ten repos and an admonition rewrite. Sphinx is the exit if I want the most boring option and accept MyST directives.

The API reference is where the value and the coupling live. mkdocstrings has about a year of committed maintenance and only renders inside a MkDocs-shaped build. Emitting real Markdown from griffe (griffe2md today, own templates when the output matters more) removes that coupling, restores the llms.txt output Zensical dropped by concatenating the same files, and produces the artifact I want for reviewing code at different levels of abstraction (a module summary, then signatures, then bodies) from nvim or a review agent. Owning that emitter is worth it. Owning a site generator is not: the weeks go into theme, nav, and search, which Zensical and Starlight already do better than a first version would.

## Next steps

- [ ] Replace `docs/gen_ref_nav.py` with the griffe emitter, add the link resolver, and drop `mkdocstrings[python]` from the `doc` extra
- [ ] Add a `docs/llms-full.md` (or `llms.txt`) built by concatenating the emitted pages
- [ ] Move `gen_ref_nav.py` and `Calcipy.sketch` out of `docs_dir` so they stop shipping in the site
- [ ] Revisit the generator choice when Zensical publishes its API-docs design or opens the module API, whichever comes first
