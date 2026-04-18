---
name: git-release
description: Create releases with hybrid major.minor.calver versioning and bee-genus naming
version: "2.0"
author: software-engineer
audience: software-engineer
workflow: release-management
---

# Git Release

Create a tagged GitHub release after the PO accepts the feature (Step 5).

## Version Format

`v{major}.{minor}.{YYYYMMDD}`

- **Major**: breaking changes (API changes, removed features)
- **Minor**: new features; also incremented if two releases happen on the same day
- **Date**: today in YYYYMMDD format

Examples:
```
v1.2.20260302  →  v1.3.20260415   (new feature, new day)
v1.2.20260302  →  v2.0.20260415   (breaking change)
v1.2.20260415  →  v1.3.20260415   (same-day second release)
```

## Release Naming

Each release gets a unique name: **`{adjective}-{bee-genus}`**

The adjective reflects what this release does or its character. The bee genus is chosen from the curated pool below, matched thematically to the release (e.g. a release about test orchestration might use *Bombus* — the highly-organized bumblebee; a release about precise detection might use *Osmia* — the meticulous mason bee).

**Constraints:**
1. **Thematic fit**: adjective and genus should together evoke the release character
2. **No repetition**: neither the adjective nor the genus may appear in any previous release name

Check previous names to avoid repetition:
```bash
gh release list --limit 100
```

### Curated Bee Genus Pool

Choose from this pool for intentional, memorable names. Each genus has a character note to guide thematic matching.

| Genus | Common name | Character / theme |
|---|---|---|
| *Apis* | Honey bee | Collaboration, industry, the gold standard |
| *Bombus* | Bumblebee | Robustness, persistence, surprising capability |
| *Osmia* | Mason bee | Precision, craftsmanship, careful construction |
| *Megachile* | Leafcutter bee | Clever tooling, cutting to shape |
| *Xylocopa* | Carpenter bee | Structural work, building into solid foundations |
| *Halictus* | Sweat bee | Small but essential, invisible infrastructure |
| *Lasioglossum* | Small sweat bee | Ubiquity, the most common; baseline correctness |
| *Nomada* | Nomad bee | Migration, discovery, exploratory behavior |
| *Andrena* | Mining bee | Digging deep, uncovering hidden things |
| *Colletes* | Plasterer bee | Sealing, finishing, waterproofing |
| *Hylaeus* | Masked bee | Hidden internals, minimal exterior |
| *Eulaema* | Orchid bee | Exotic, specialized, high-value collection |
| *Eufriesea* | Orchid bee | Rare, distinctive, one-of-a-kind |
| *Agapostemon* | Metallic sweat bee | Brilliance, sheen, polish |
| *Augochlora* | Green sweat bee | Fresh, new, verdant growth |
| *Augochlorella* | Sweat bee | Emerging, small-scale refinement |
| *Augochloropsis* | Sweat bee | Variation on a theme, extension |
| *Panurgus* | Mining bee | Collective effort, many small contributions |
| *Perdita* | Mining bee | Smallest US bee; economy, minimalism |
| *Melitturga* | Mining bee | Clarity, straight lines |
| *Dasypoda* | Pantaloon bee | Deep foundations, load-bearing |
| *Macropis* | Oil bee | Specialized extraction, targeted collection |
| *Melitta* | Melitta bee | Sweetness, reward, delight |
| *Anthidium* | Wool-carder bee | Gathering, tidying, organization |
| *Coelioxys* | Sharp-tailed bee | Edge cases, pointed precision |
| *Stelis* | Cleptoparasitic bee | Detection, catching what doesn't belong |
| *Dioxys* | Cleptoparasitic bee | Finding impostors, validation |
| *Sphecodes* | Blood bee | Ruthless removal of what shouldn't be there |
| *Ceratina* | Small carpenter bee | Incremental progress, small but persistent |
| *Exomalopsis* | Bee | Quiet correctness, unassuming reliability |
| *Emphorella* | Bee | Niche specialization |
| *Peponapis* | Squash bee | Domain-specific excellence |
| *Xenoglossa* | Squash bee | Specialized vocabulary, domain language |
| *Ptilothrix* | Mallow bee | Softness of interface, gentle handling |
| *Melissodes* | Long-horned bee | Signal detection, communication |
| *Svastra* | Long-horned bee | Season-aware, time-sensitive behavior |
| *Eucera* | Long-horned bee | Patient waiting, timing |
| *Tetralonia* | Long-horned bee | Systematic coverage |
| *Anthophora* | Digger bee | Fast, energetic execution |
| *Habropoda* | Digger bee | Buzz-pollination; resonance, vibration |
| *Amegilla* | Blue-banded bee | Vibrant, high-frequency operation |
| *Xylocopinae* | Carpenter bee subfamily | Load-bearing architecture |
| *Euglossa* | Orchid bee | Precision collection, perfume of quality |
| *Eulaema* | Orchid bee | Valuable, coveted output |
| *Trigona* | Stingless bee | Safe, no sharp edges, user-friendly |
| *Tetragonula* | Stingless bee | Compact, structured, geometric |
| *Meliponula* | Stingless bee | African precision; warm-climate reliability |
| *Frieseomelitta* | Stingless bee | Abundant output, productivity |
| *Scaptotrigona* | Stingless bee | Aggressive defense of quality |
| *Plebeia* | Stingless bee | Humble, small, widely deployed |
| *Schwarziana* | Stingless bee | Named for a scientist; rigorous methodology |
| *Ctenocolletes* | Stenotritid bee | Ancient, foundational, rarely changed |
| *Stenotritus* | Stenotritid bee | Narrow, focused, specialized interface |

If the release theme doesn't match any entry above, choose any other real bee genus and add it to this list with a character note.

## Release Process

### 1. Analyze changes since last release

```bash
last_tag=$(git describe --tags --abbrev=0)
git log ${last_tag}..HEAD --oneline
```

### 2. Calculate new version

```bash
current_date=$(date +%Y%m%d)
# Determine major.minor based on change type, then:
# new_version="v{major}.{minor}.${current_date}"
```

### 3. Choose release name

1. Read the commits and accepted features since the last release
2. Identify the theme (what did this release fundamentally accomplish?)
3. Choose an adjective that captures the theme
4. Choose a bee genus from the pool above that matches the theme
5. Verify neither the adjective nor the genus appear in previous release names:
   ```bash
   gh release list --limit 100
   ```

### 4. Update version in pyproject.toml

```bash
# Update the version field in pyproject.toml
# e.g.: version = "0.2.20260418"
```

No `__version__` in `__init__.py` — version is read at runtime via `importlib.metadata`.

### 5. Update CHANGELOG.md

Add at the top of the changelog (below the `# Changelog` heading):

```markdown
## [v{version}] — {Adjective Genus} — {YYYY-MM-DD}

### Added
- feat({feature-name}): description of what was added

### Fixed
- fix({feature-name}): description of what was fixed

### Changed
- refactor/chore: description of structural changes
```

Reference feature names (from `feat(<feature-name>): ...` commits), not PR numbers — this project uses direct commits rather than PRs.

### 6. Regenerate lockfile and commit version bump

After updating `pyproject.toml`, regenerate the lockfile — CI runs `uv sync --locked` and will fail if it is stale:

```bash
uv lock
git add pyproject.toml CHANGELOG.md uv.lock
git commit -m "chore(release): bump version to v{version} — {Adjective Genus}"
```

### 7. Create GitHub release

```bash
SHA=$(git rev-parse --short HEAD)
gh release create "v{version}" \
  --title "v{version} — {Adjective Genus}" \
  --notes "# v{version} — {Adjective Genus}

> *\"{one-line tagline matching the release theme}\"*

## Changelog

### Added
- feat({feature-name}): description

### Fixed
- fix({feature-name}): description

### Changed
- refactor/chore: description

## Summary

2-3 sentences describing what this release accomplishes and why the genus name fits.

---
**SHA**: \`${SHA}\`"
```

### 8. If a hotfix commit follows the release tag

If CI fails after the release (e.g. a stale lockfile) and a hotfix commit is pushed, reassign the tag and GitHub release to that commit:

```bash
# Delete the old tag locally and on remote
git tag -d "v{version}"
git push origin ":refs/tags/v{version}"

# Recreate the tag on the hotfix commit
git tag "v{version}" {hotfix-sha}
git push origin "v{version}"

# Update the GitHub release to point to the new tag
gh release edit "v{version}" --target {hotfix-sha}
```

The release notes and title do not need to change — only the target commit moves.

## Quality Checklist

- [ ] `task test` passes
- [ ] `task lint` passes
- [ ] `task static-check` passes
- [ ] `pyproject.toml` version updated
- [ ] `uv lock` run after version bump — lockfile must be up to date
- [ ] CHANGELOG.md updated with only beehave-specific changes (no template history)
- [ ] Release name: adjective not used before, genus not used before
- [ ] Genus chosen from curated pool (or new entry added to pool with character note)
- [ ] Release notes follow the template format
- [ ] If a hotfix was pushed after the tag: tag reassigned to hotfix commit
