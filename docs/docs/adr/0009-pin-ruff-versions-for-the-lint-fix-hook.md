# Pin Ruff Versions for the Lint-Fix Hook

- Status: accepted
- Date: 2026-07-27
- Deciders: KyleKing
- Consulted: calcipy_template child repositories
- Informed: calcipy users

## Context and Problem Statement

calcipy ships `.pre-commit-hooks.yaml`, and every repo generated from `calcipy_template` runs its `lint-fix` hook. The hook resolves ruff through calcipy's `lint` extra with a floor and no ceiling, and the template's hook invocation resolves calcipy the same way (`uvx --from 'calcipy[recommended]>=6.0.1'`), so the hook always installs whatever ruff is newest at the moment it runs. Meanwhile each child's lockfile pins ruff to a specific 0.15.x. On 2026-07-27 that gap opened: the hook picked up a ruff new enough to have RUF105, calcipy selects `ALL` rules with `preview = true`, so RUF105 activated the day it shipped and rewrote `# noqa: X` comments into `# ruff: ignore[X]`. The children's older pinned ruff could not parse what the hook had written, and the fix loop stopped converging. The interim patch (add `RUF105` to the template's ignore list, raise the `lint` extra floor to `ruff >=0.16.0`) closed this one hole and made it worse in a small way, because on ruff 0.15.7 and 0.15.8 an unrecognized selector in the ignore list is a hard startup failure rather than a warning. The decision here is what to change structurally so that the next preview rule Astral ships does not reopen the same hole.

The cost of getting this wrong is high and slow to undo. Any change to the hook needs a calcipy release, then a calcipy_template release, then a copier update rolled out across every child. A per-child configuration lever can move without that chain; a lever baked into the hook cannot.

## Decision Drivers

- The hook binary and the child's pinned binary must never disagree silently; if they disagree, the run must fail loudly and immediately
- Failures must be legible, so a message naming the version mismatch beats a diff that will not converge
- Whatever is chosen applies to every calcipy_template child, so the blast radius of a bad choice is the whole fleet
- A child should be able to move at its own pace without waiting on a calcipy release
- calcipy deliberately runs `select = ['ALL']` with `preview = true`, which auto-enrolls the project in every new preview rule on the day it lands
- ruff's own policy permits preview rules to appear and to change behavior in a patch release, so there is no version range that makes preview churn go away
- Maintenance must stay low; a scheme requiring a hand-edit on every ruff release will rot

## Verified Facts

Primary sources, checked on 2026-07-27:

- ruff's [versioning policy](https://docs.astral.sh/ruff/versioning/) puts "A rule is added in preview", "The scope of a rule is increased in preview", and "The behavior of a preview rule is changed" under **patch** releases. Only stable-rule behavior changes and stable promotions require a minor bump. Pinning `>=0.16,<0.17` therefore constrains stable behavior and does nothing at all for preview behavior
- [`required-version`](https://docs.astral.sh/ruff/settings/#required-version) is a `[tool.ruff]` string that accepts a PEP 440 specifier ("like `==0.3.1` or `>=0.3.1`"). If the running ruff does not satisfy it, "Ruff will exit with an error." calcipy does not currently set it; the `required-version` at `pyproject.toml:250` is under `[tool.uv]` and constrains uv, not ruff
- RUF105 is [`noqa-comments`](https://docs.astral.sh/ruff/rules/noqa-comments/), in preview since **0.15.22** (2026-07-16), not 0.16. Its siblings RUF106 (`rule-codes-in-suppression-comments`) and RUF201 (`rule-codes-in-selectors`) shipped in the same patch release. The rule docs call it "opinionated, stylistic", state that `noqa` comments remain fully supported, and say you are "free to disable this rule if you simply prefer `noqa` comments"
- ruff [0.15.20](https://github.com/astral-sh/ruff/releases/tag/0.15.20) (2026-06-25) changed unknown rule selectors to "Emit a warning instead of an error". This is the release boundary that explains why the severity varied across the fleet
- ruff [0.16.0](https://github.com/astral-sh/ruff/releases/tag/0.16.0) (2026-07-23) expanded the default rule set from 59 to 413 rules, made `ruff: ignore` valid at end of line, and under Rule changes shipped "Insert a space after the colon in Ruff suppression comments", which is itself a rewrite of already-rewritten comments
- The [0.16 blog post](https://astral.sh/blog/ruff-v0.16.0) presents `ruff: ignore` as complementary to `noqa` and keeps human-readable rule names behind `--preview`. There is no announcement that codes-to-names becomes the default
- [ruff-pre-commit](https://github.com/astral-sh/ruff-pre-commit) and ruff's [pre-commit integration docs](https://docs.astral.sh/ruff/integrations/) both use a concrete `rev: v0.16.0` in every example and offer no guidance on syncing the hook version against the project's pinned ruff
- pre-commit's [docs](https://pre-commit.com/) require `rev` to be an immutable ref: "pre-commit assumes that the value of `rev` is an immutable ref (such as a tag or SHA) and will cache based on that", and using a branch name "is not supported". Upgrades happen through `pre-commit autoupdate`, which moves to the latest tag. The framework has no "always latest" mode by design
- black's [stability policy](https://black.readthedocs.io/en/stable/the_black_code_style/index.html) guarantees identical output across a calendar year, so `black ~= 26.0` is safe, and its `--required-version` (also settable in `pyproject.toml`) accepts a bare major/year. `--preview` output carries "no guarantees around the stability of the output"
- [prettier](https://prettier.io/docs/install) tells users to install an exact version with `--save-exact`, because "Even a patch release of Prettier can result in slightly different formatting"
- [golangci-lint](https://golangci-lint.run/docs/welcome/install/ci/) recommends installing a specific released version, calling out that adding a linter or upgrading an upstream one can "start to fail all builds at the same time"

Not verified from primary sources, flagged so a future reader does not treat these as settled:

- That 0.15.7 and 0.15.8 surface an unknown selector specifically as a **TOML parse** error. The 0.15.20 changelog confirms the error-to-warning switch, and the exact error class on the older versions comes from observing the fleet
- Whether Astral intends `ruff: ignore` and human-readable names to become the default. Nothing in the docs, the rule pages, or the 0.16 post says so; the current signal points the other way
- That Astral publishes any recommendation on pinning ruff at all. Nothing was found across the settings, versioning, and integrations pages or the 0.16 post, so the absence is inferred from having looked, not from a statement

## Considered Options

- Pin an exact ruff version in the hook (`ruff ==0.16.3`)
- Pin a compatible range in the hook (`ruff >=0.16,<0.17`)
- Set `[tool.ruff] required-version` in the template so config and binary cannot drift
- Keep the hook unpinned and absorb the churn (status quo)
- Disable `preview = true`

| Option | What breaks | Who acts on a ruff release | Blast radius across children | Maintenance cost |
| --- | --- | --- | --- | --- |
| Exact pin in hook (`==0.16.3`) | Nothing drifts, but the hook and a child's own lockfile still pin independently, so they can still disagree, just deterministically | KyleKing, on every release worth taking; children get nothing until calcipy plus template plus copier lands | Uniform. Every child moves at once or not at all | High. A three-repo release chain for each bump |
| Compatible range in hook (`>=0.16,<0.17`) | Stable-rule churn is contained. Preview rules and preview behavior changes still land freely, because ruff allows both in a patch | KyleKing, once per ruff minor. Nobody acts on patches, which is where the RUF105 class of break lives | Uniform, and the failure mode is exactly the one already seen | Medium, and it does not solve the reported problem |
| `required-version` in the template | The mismatch itself breaks, on purpose. A hook binary outside the child's declared window refuses to start with a version message instead of rewriting files | The child, when its own bound goes stale. calcipy is not in the loop | Per child. Each repo fails independently and recovers independently | Low for calcipy, small and recurring for each child, and it rides the existing copier and lockfile bump flow |
| Unpinned (status quo) | Any preview rule with a fix can rewrite files a pinned ruff cannot parse. Non-convergent fix loops, fleet-wide, with no warning | Nobody until it breaks, then KyleKing under time pressure | Fleet-wide and simultaneous, which is exactly what happened | Low until an incident, then very high |
| Disable `preview = true` | Loses preview rules and preview fixes across calcipy and every child. Does not stop stable-rule churn, and 0.16 shows a minor release can move 354 rules into the default set | KyleKing, on minor releases only | Uniform, and it is a behavior regression everyone notices | Low, at a real cost in coverage |

## Decision Outcome

Chosen option: **set `[tool.ruff] required-version` in the template**, paired with keeping a compatible range on calcipy's `lint` extra, because it is the only lever that converts a silent divergence into a loud failure and the only one that lets a child move without a three-repo release chain.

The concrete shape:

- calcipy's `lint` extra carries `ruff >=0.16.0,<0.17.0`. This bounds what the hook can pull without pretending it solves preview churn
- calcipy_template writes `required-version = ">=0.16.0,<0.17.0"` under `[tool.ruff]` in each child's `pyproject.toml`, alongside the existing lockfile pin. The child owns this line and can widen or narrow it on its own schedule
- The two are allowed to disagree, and that is the point. When the hook resolves a ruff outside the child's window, ruff exits with a version error before it edits a single file

The reasoning is that no version range can prevent this class of break. ruff's policy explicitly permits a preview rule to be added or to change behavior in a **patch** release, and calcipy opts into every one of them through `select = ['ALL']` with `preview = true`. Chasing the range is chasing a moving target. What is actually needed is a guarantee that the binary doing the rewriting is the same binary that will later read the result, and `required-version` is the mechanism ruff itself provides for that. It is also the same shape black settled on with `--required-version`, and the same instinct behind prettier's exact pin and golangci-lint's warning about all builds failing at once.

The per-child ownership matters as much as the mechanism. A ceiling living only in calcipy's `lint` extra means every adjustment costs a calcipy release, a template release, and a fleet rollout. A `required-version` line in the child's own `pyproject.toml` costs one line in one repo, and a child that is ready to move to 0.17 does not have to wait for the slowest child in the fleet.

Preview mode stays on. Turning it off would trade a narrow, now-understood failure for a broad loss of coverage, and 0.16 (59 default rules to 413 in a single minor) shows that stable releases move plenty on their own.

### Consequences

- Good, because a hook/lockfile mismatch fails in the first second with a message naming the versions, rather than producing a fix loop that never converges
- Good, because the failure is per child, so one stale repo does not block the fleet and a fleet-wide incident becomes a fleet-wide set of independent, individually fixable errors
- Good, because children set their own bound and can upgrade without a calcipy or template release
- Good, because `required-version` is ruff's own supported mechanism, so it needs no wrapper logic in calcipy and cannot be bypassed by a different invocation path
- Good, because it composes with the compatible range instead of replacing it; the range narrows the window, `required-version` enforces it
- Bad, because a child whose bound has gone stale sees a hard hook failure and must act, which is more visible friction than today's silent drift
- Bad, because the bound is one more thing to keep current in each child, and a fleet of repos with stale bounds is a real possibility
- Bad, because it does not stop a preview rule from changing behavior *within* the allowed window; two ruff versions that both satisfy `>=0.16,<0.17` can still disagree about RUF105-style rewrites
- Neutral, because the interim RUF105 ignore stays. The rule is stylistic by its own docs, `noqa` remains supported, and cross-tool compatibility is worth keeping
- Neutral, because rolling this out is one template change plus a copier update, roughly the cost of any other template field

### Not chosen, and why

`select = ['ALL']` with `preview = true` is the deeper cause; it enrolls the fleet in every preview rule the day it ships. Narrowing to explicit rule families would remove the auto-enrollment, and it was left out of this decision because it is a much larger change to calcipy's linting identity and deserves its own ADR. It should be revisited if `required-version` proves to be a bandage on a wound that keeps reopening.

## Validation

This decision holds if, over the next two ruff minor releases:

- No child produces a non-convergent fix loop
- Any hook/lockfile mismatch surfaces as a ruff version error and nothing else
- Children that fall behind their bound are individually recoverable, without a calcipy release

We will revisit this decision if:

- ruff changes `required-version` semantics or removes it
- Stale bounds across the fleet become a bigger operational burden than the drift they prevent
- ruff stabilizes `ruff: ignore` as the default suppression form, which would make the RUF105 ignore a migration to schedule rather than a preference to hold
- Preview rules keep causing incidents inside an allowed window, which would point at `select = ['ALL']` with `preview = true` as the thing to change instead

## More Information

- ruff versioning policy: https://docs.astral.sh/ruff/versioning/
- ruff `required-version`: https://docs.astral.sh/ruff/settings/#required-version
- ruff `preview`: https://docs.astral.sh/ruff/preview/
- RUF105 `noqa-comments`: https://docs.astral.sh/ruff/rules/noqa-comments/
- ruff 0.15.20 release (unknown selectors become warnings): https://github.com/astral-sh/ruff/releases/tag/0.15.20
- ruff 0.15.22 release (RUF105, RUF106, RUF201): https://github.com/astral-sh/ruff/releases/tag/0.15.22
- ruff 0.16.0 release: https://github.com/astral-sh/ruff/releases/tag/0.16.0
- ruff 0.16 blog post: https://astral.sh/blog/ruff-v0.16.0
- ruff-pre-commit: https://github.com/astral-sh/ruff-pre-commit
- pre-commit `rev` and `autoupdate`: https://pre-commit.com/
- black stability policy: https://black.readthedocs.io/en/stable/the_black_code_style/index.html
- prettier install guidance: https://prettier.io/docs/install
- golangci-lint CI install guidance: https://golangci-lint.run/docs/welcome/install/ci/
- Related: [ADR-0003](0003-use-ruff-for-linting-and-formatting.md) - Use Ruff for Linting and Formatting
