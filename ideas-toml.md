Switch to using the unversioned API to get "releases"
https://warehouse.pypa.io/api-reference/json.html#release

---

For stale packages, could also include a metric of packages that have low download counts for flagging niche packages?
https://pypistats.org/api/

---

Switching to pdm. Requires removal of "allow-prereleases" and updates to .gitignore
https://github.com/frostming/python-cfonts/commit/3af9a45b0dbd53c1b549dca17b98da598dc762aa
