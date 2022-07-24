Create formatting plugin for toml with tomlikt
- Deterministic, alphabetical sort (for sections and (dev-)dependencies)
- Prevent leading and trailing whitespace
- Line length? Wrap long comments? (Maybe not?)

Actually might already be implemented: https://github.com/macisamuele/language-formatters-pre-commit-hooks/blob/8d75b37c878398217c5d194ca46e9fcbe4f0dcdb/language_formatters_pre_commit_hooks/pretty_format_toml.py

---

Switch to using the unversioned API to get "releases"
https://warehouse.pypa.io/api-reference/json.html#release

---

For stale packages, could also include a metric of packages that have low download counts for flagging niche packages?
https://pypistats.org/api/

---

Switching to pdm. Requires removal of "allow-prereleases" and updates to .gitignore
https://github.com/frostming/python-cfonts/commit/3af9a45b0dbd53c1b549dca17b98da598dc762aa
