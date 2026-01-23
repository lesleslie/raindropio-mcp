# HTTP Clients

The `raindropio_mcp.clients` package contains two layers:

1. `BaseHTTPClient` – async helper that wraps `httpx.AsyncClient` with retry
   logic, error mapping, JSON parsing, and rate-limit awareness.
1. `RaindropClient` – typed facade over the Raindrop REST API, returning
   Pydantic models for each call.

## BaseHTTPClient

- Configured via `RaindropSettings.http_client_config()` which injects
  `httpx.Limits`, timeout, and authenticated headers.
- Retries network errors and selected response codes (408, 425, 429, 5xx).
- `_map_error` converts HTTP responses to domain exceptions (`NotFoundError`,
  `RateLimitError`, `APIError`).
- `get_json` ensures payloads are valid JSON and raises `APIError` when parsing
  fails.

Unit tests in `tests/unit/test_base_client.py` cover success paths, retries, and
error handling.

### Retry Logic Flow

![Flowchart showing HTTP request retry logic with exponential backoff for retryable status codes and error type mapping](https://mermaid.ink/svg/pako:eNptkdlugkAUhu_7FCfprabI0pbGaFBx30JJmoZYM-oQicjY4dBipO9eGCBiUy7OxXz_Mmdwffa93ROOYPfuIP0MZ2jbS7DoZ0RDXEG93oLOxaLhiQUhhcWk_SN0nYwk7zQEOY4T6DoWxYgHUCpXFdWcJdBLM5Cfycan7eaGP7RU6bkGqqxlQxcnmiTVQJPkbCjZUPOqXlmVgOmYcRpPA_SIDx2yPTDXFWaXbJFx-ACCSI8nzPtNcf_-xcgPQ2jCjMTFCv1r7sB5Ix6Wgbl3ILxGRZrtMXQs4qUPYSxHJueMrypXzPjIWR_JaU2vbCRyxhfxrq9IMArz_rEwqZKawKRInTPssyjYVaJLVSOB6Z9usfgo-CK-twObHWhwY5H1BGaFxSJIp97Rw6tR_I-64SK9aVrgnvIE5v_uKUaIZz8F4Hq-_3KvGrpkyhXQLcCT2VPkRgUMC2DqakfRKmBSgL5mPMpKBcxuwC86j8Zl)

## RaindropClient

- Accepts a `RaindropSettings` instance (defaulting to `get_settings()`).
- Implements account (`get_me`), collection CRUD, bookmark operations, tag
  management, and search helpers.
- Paginated endpoints return the `PaginatedBookmarks` dataclass so callers retain
  page information, counts, and collection context.
- Exceptions bubble as `APIError` (or subclasses) making downstream handling
  straightforward inside FastMCP tools.

### Client Class Hierarchy

![Class diagram showing BaseHTTPClient with retry logic inherited by RaindropClient with typed API methods](https://mermaid.ink/svg/pako:eNp9kstOwzAQRfd8xShbmh9AbHgsgAVUbZeVosEeUrd-aewIRcC_40Qpbd0aLyzlnvH4jnOFxhAeFbaM5grSEoMA9xjoabWaP2hFNsLXiIZ1jaG3AlqKzTY4m-vehQLoLuuSNEU6RXVj0DfE7PhICxvXadkwRe5H-Wfcj0wvUFnJzp-bDhSjsm24-atZTsqlwQzlqlZpLOG0JhGVsxdPHXBOBROmGcsFnZf_F0yvVC4YDb47tzPIuzN7gZDFpswH-3tYMF_Ck_USnoyX8Gg74vlvYLJoaECFjntyFIIss7ffdZ1F4lBrXST4cJwfqhZDvEC7VokZjBGEFEafojJb25fl2yt45DB8AqfBa62MirBBK3USq9PmWSCrVe9Jwt38GT45NSVe23RfxzbAvJdooxJgXJowVL-AKxx6)

Tests in `tests/unit/test_raindrop_client.py` focus on payload validation and the
JSON envelope expectations used by the Raindrop API.
