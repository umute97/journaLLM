"""Interactive API docs (Scalar), served next to the generated `openapi.json`."""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(include_in_schema=False)

# Pinned, with Subresource Integrity, so the CDN can't swap the script.
SCALAR_URL = "https://cdn.jsdelivr.net/npm/@scalar/api-reference@1.72.4/dist/browser/standalone.js"
SCALAR_INTEGRITY = "sha384-omTRdD9MbjA1vm12DqRUVvqJlr3VzSixvAdF1Jruu9AJOiJKyTKraIB6DyX+m10M"

DOCS_HTML = f"""\
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>kritzeLLM API</title>
  </head>
  <body>
    <script id="api-reference" data-url="openapi.json"></script>
    <script src="{SCALAR_URL}" integrity="{SCALAR_INTEGRITY}" crossorigin="anonymous"></script>
  </body>
</html>
"""


@router.get("/docs")
async def get_docs() -> HTMLResponse:
    return HTMLResponse(DOCS_HTML)
