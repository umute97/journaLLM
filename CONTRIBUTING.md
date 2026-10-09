# Contributing

## Setup

```sh
uv tool install pre-commit   # or: brew install pre-commit
pre-commit install
```

Hooks cover whitespace, file validity, workflow linting ([actionlint](https://github.com/rhysd/actionlint),
[zizmor](https://github.com/zizmorcore/zizmor)), and stop direct commits to `main`.

## Personal data

This repository is public. **Never commit real journal pages, scans, exports, database dumps or `.env` files.**
Images and PDFs are rejected by a pre-commit hook unless they live under a `tests/fixtures/` directory
(synthetic samples only) or `web/public/`. Local data belongs in `data/`, `scans/` and `exports/`, which are git-ignored.

## Workflow

1. Branch off `main`: `<type>/<short-slug>`, e.g. `feat/page-upload`, `fix/band-offset`.
2. Open a PR. One PR per issue where practical; put `Closes #<issue>` in the body.
3. PRs are **squash-merged**. The PR title becomes the commit on `main`, so it must follow
   [Conventional Commits](https://www.conventionalcommits.org/):

   ```
   <type>(<optional scope>)!: <lowercase summary>
   ```

   | Types | `feat` `fix` `perf` `refactor` `docs` `test` `build` `ci` `chore` `revert` |
   |---|---|
   | Scopes | `api` `backend` `web` `cli` `infra` `docs` `deps` `release` |

   Add `!` (or a `BREAKING CHANGE:` line in the body) for breaking changes. Commit messages on the
   branch itself are free-form.

4. `main` is protected: changes go through PRs, and the `ci-ok` and `pr-title` checks must pass.

## Labels

Labels are defined in [`.github/labels.yml`](.github/labels.yml) and mostly applied automatically:

- **Kind** (`feature`, `bug`, `performance`, `refactor`, `documentation`, `test`, `build`, `ci`,
  `chore`, `revert`, plus `breaking`) comes from the PR title.
- **Area** (`api`, `backend`, `web`, `cli`, `infra`, `ci`, `documentation`) comes from the changed paths
  ([`.github/labeler.yml`](.github/labeler.yml)).
- `blocked` and `needs-review` are set by hand; `deps` marks Dependabot PRs.

## Releases

Versioning follows [SemVer](https://semver.org/) (pre-1.0: breaking changes bump the minor version)
and is automated with [release-please](https://github.com/googleapis/release-please):

1. Every `feat`/`fix`/`perf`/... merged to `main` updates an open **release PR**
   (`chore(main): release X.Y.Z`) with the version bump and `CHANGELOG.md`.
2. Merging the release PR tags `vX.Y.Z`, creates the GitHub Release, publishes the Docker images to
   `ghcr.io/umute97/kritzellm-{api,web}` (amd64 + arm64, with provenance attestations) and attaches
   `api/openapi.yaml` to the release.

Release PRs are opened by `GITHUB_TOKEN`, which doesn't trigger CI. They only touch the changelog
and version strings, so a maintainer merges them using the ruleset bypass.

## Adding a new component

When a new top-level component (e.g. `backend/`, `web/`, `cli/`) or file type lands, wire it in
within the same PR:

1. **CI job** in [`.github/workflows/ci.yml`](.github/workflows/ci.yml), gated on its path filter,
   and add it to `ci-ok`'s `needs`:

   ```yaml
   backend:
     name: Backend
     needs: changes
     if: needs.changes.outputs.backend == 'true'
     runs-on: ubuntu-latest
     timeout-minutes: 20
     permissions:
       contents: read
     steps:
       - uses: actions/checkout@<sha> # vX
         with:
           persist-credentials: false
       # lint, typecheck, test ...
   ```

2. **Path filter** entry in the `changes` job (if not already there).
3. **Labeler** glob in [`.github/labeler.yml`](.github/labeler.yml).
4. **Dependabot** ecosystem in [`.github/dependabot.yml`](.github/dependabot.yml) (`uv`, `npm`, `docker`).
5. **Version stamp** in [`release-please-config.json`](release-please-config.json) `extra-files`, e.g.
   `{ "type": "toml", "path": "backend/pyproject.toml", "jsonpath": "$.project.version" }`.
6. **Image publishing**: if it ships a Dockerfile, make sure it's in the `publish-images` matrix in
   [`.github/workflows/release-please.yml`](.github/workflows/release-please.yml).
7. **CodeQL** language in [`.github/workflows/codeql.yml`](.github/workflows/codeql.yml)
   (`python`, `javascript-typescript`).
8. **pre-commit** hooks for the component's formatters/linters.

Pin every third-party action to a full commit SHA with a version comment; Dependabot keeps them current.

## Repository settings

Repository settings and rulesets are applied with [`scripts/setup-github.sh`](scripts/setup-github.sh)
(requires admin rights and an authenticated `gh`). It is idempotent; re-run it after changing it.
