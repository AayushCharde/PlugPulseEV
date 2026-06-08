# Contributing to PlugPulse

Thanks for helping build an open trust layer for EV charging! This guide covers the
workflow so your contribution sails through review.

## Ground rules

- **Keep the core open.** No proprietary or paid-only services in the core path
  (the app must run with free, open tools — see the stack in the README).
- **Preserve attribution.** Open Charge Map and OpenFreeMap/OpenStreetMap attribution
  is a license condition. See `ATTRIBUTION.md`.
- **Mind the budgets.** This is a map app used across the web — keep changes within the
  performance budgets in `PERFORMANCE.md`, or call out the trade-off in your PR.
- Be kind. We follow the [Code of Conduct](./CODE_OF_CONDUCT.md).

## Workflow

1. **Find or open an issue** describing the change. For anything non-trivial, comment
   that you're taking it so work isn't duplicated.
2. **Fork** the repo (or branch, if you're a maintainer).
3. **Create a branch** off `main`:
   ```
   git checkout -b feat/reliability-decay
   ```
   Use prefixes: `feat/`, `fix/`, `docs/`, `chore/`, `ci/`, `refactor/`.
4. **Make your change** with tests where it makes sense.
5. **Run the checks locally** (these are exactly what CI runs):
   ```
   # backend
   cd backend && ruff check . && ruff format --check . && mypy app && pytest
   # frontend
   cd frontend && npm run lint && npm run test && npm run build
   ```
6. **Commit** using [Conventional Commits](https://www.conventionalcommits.org/):
   ```
   feat(scoring): add half-life decay to reliability score
   fix(map): correct marker clustering at low zoom
   ```
7. **Open a PR** against `main`, fill out the template, and link the issue
   (`Closes #123`). Keep PRs focused — one logical change each.

## What CI checks (all must pass to merge)

- **`CI`** — backend lint (ruff) + format + types (mypy) + tests (pytest with coverage);
  frontend lint (eslint) + tests (vitest) + build.
- **`CodeQL`** — security analysis for Python and JS/TS.
- **`Docker`** — images build cleanly (publish only happens on `main` / tags).

## Recommended branch protection (for maintainers)

On GitHub: **Settings → Branches → Add rule** for `main`:

- Require a pull request before merging (no direct pushes to `main`).
- Require status checks to pass: select `CI` jobs and `CodeQL`.
- Require branches to be up to date before merging.
- Require at least 1 approving review (CODEOWNERS auto-requests review).
- Optionally require signed commits and a linear history.

## Local pre-commit hooks (optional but nice)

```
pip install pre-commit
pre-commit install
```

This runs ruff and basic hygiene checks before each commit (see
`.pre-commit-config.yaml`).
