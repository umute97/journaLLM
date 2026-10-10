# backend

The Python (FastAPI) service: uploads, transcription, search and the chat agent ✨

It also *defines* the API: [`api/openapi.json`](../api/openapi.json) is generated from the
models and routes in [`src/kritzellm/api`](src/kritzellm/api).

```sh
uv sync                  # install (Python 3.14)
uv run pytest            # tests, incl. the "is api/openapi.json up to date?" check
just api-export          # regenerate api/openapi.json after changing the API
```
