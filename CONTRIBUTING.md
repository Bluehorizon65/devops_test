# Contributing Guide

## Branching Model

- `main`: production-ready code only
- `develop`: integration branch for features
- `feature/<ticket>-<short-name>`: new features
- `bugfix/<ticket>-<short-name>`: bug fixes
- `hotfix/<ticket>-<short-name>`: urgent production fixes

## Commit Convention

Use conventional commits:

- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation change
- `ci:` pipeline or automation updates
- `infra:` infrastructure updates
- `test:` testing changes
- `refactor:` code restructure without behavior changes

Example:

`feat(frontend): add API base URL environment support`

## Pull Request Process

1. Rebase on latest `develop`.
2. Ensure local checks pass:
   - `npm test` in `backend`
   - `npm run build` in `frontend`
   - `pytest -q` in `AI`
3. Open PR against `develop` using the project PR template.
4. Require at least one reviewer approval and passing CI before merge.
5. Use squash merge unless there is a clear reason to preserve commit history.

## Release Process

1. Merge `develop` into `main` via release PR.
2. CI/CD workflow on `main` builds, tests, containerizes, and deploys.
3. Tag release using semantic versioning (`v1.0.0`, `v1.1.0`, etc.).
