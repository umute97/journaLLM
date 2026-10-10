# api

[`openapi.json`](openapi.json) is the OpenAPI 3.1 description of the whole API 💖

It's **generated from the backend**, from the pydantic models and FastAPI routes in
[`backend/src/kritzellm/api`](../backend/src/kritzellm/api). Don't edit it by hand: change the code,
then regenerate it. It's committed so the web app and CLI can generate their clients from it, and a
backend test fails when it's out of date.

## Tools

```sh
just api-export    # regenerate openapi.json from the backend code
just api-install   # Redocly, Prism and Scalar (pinned in package.json)
just api-lint      # lint the spec (rules in redocly.yaml)
just api-mock      # mock server on http://localhost:4010 with random but valid data
just api-docs      # docs preview on http://localhost:4011, reloads on save
```

> Heads up: Prism can't parse repeated multipart fields, so `POST /journals/{journalId}/pages`
> always answers `422` in the mock. Try uploads against the real backend.

## Security overrides

Prism (the mock server) pins old, vulnerable versions of `lodash` and `uuid` deep in its
dependencies. `overrides` in [`package.json`](package.json) forces patched versions; drop them once
Prism updates. (Its old `@faker-js/faker` can't be overridden without breaking Prism. The
vulnerable code path isn't reachable here, since Prism only ever reads our own spec, locally.)

## Lint rules

[`redocly.yaml`](redocly.yaml) extends Redocly's `recommended-strict` and adds a few house rules:
camelCase for operation IDs, properties and parameters, and RFC 9457 problem details for every 4xx.
Deliberate exceptions live in [`.redocly.lint-ignore.yaml`](.redocly.lint-ignore.yaml), each with
a reason.

## Versioning

`info.version` follows the backend's version, which release-please bumps on every release. The spec
is attached to each GitHub Release.
