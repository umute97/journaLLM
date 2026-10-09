# kritzeLLM 📓✨

Turn a handwritten journal into something you can search and chat with.
(*kritzeln* is German for "to scribble" 🖍️)

Snap photos of your pages, and kritzeLLM reads the handwriting, remembers *where* on each page things are,
and lets you ask questions. Every answer comes with sources that point to the exact page and spot 💖

> Very much a work in progress. Everything runs locally with docker compose; only page images and text
> are sent to the OpenAI API. Maybe I'll switch that up in the future so you can use self-hosted LLMs.

## Quickstart

You'll need [Docker](https://www.docker.com/) and [just](https://just.systems) (`brew install just`).

```sh
cp .env.example .env   # then fill in your values
just up                # start the local stack
just db-check          # → postgres 18.x, pgvector 0.8.x
```

`just` lists every recipe.

## What's where

| Path | What lives there |
|---|---|
| [`api/`](api/) | The OpenAPI contract, the source of truth for everything else |
| [`backend/`](backend/) | Python / FastAPI service |
| [`web/`](web/) | Vue 3 web app |
| [`cli/`](cli/) | Command-line client |
| [`docs/`](docs/) | Longer-form docs |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) 🌸
