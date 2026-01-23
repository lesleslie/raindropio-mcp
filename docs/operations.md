# Operations & Deployment

## Configuration

Set `RAINDROP_TOKEN` for all environments. Optional variables control timeouts,
connection pools, and HTTP transport. See the project README for the full table.

Use `.env` during development:

```
RAINDROP_TOKEN=your-token-here
RAINDROP_ENABLE_HTTP_TRANSPORT=true
RAINDROP_HTTP_PORT=3034
```

### Configuration Decision Tree

![Decision tree for selecting optional environment variables based on deployment needs](https://mermaid.ink/svg/pako:eNpVkV1PwjAUhu_9FU28lfgBxmgcZh8FBluLXUHJQhYcBZaMVddOY5j_3a2bUHfRnPY9T9_3rJuUf8W7VS4Bdc5A9ZkhYmwNJAcBk8Dm2SbZPi1Bp9MH1oGwjyLJK7k9_1GIVavlgokS2GFNEdNFDsHTiOIJRI9v-WXfN5FjUkwWSw1BvATOQfnZhZB8X3vKJNuK9mZb-TbBnCMCw5lgwGGbVZFKoa5_57k0ulfd3gWQyZ7xot6JpQaqeIPDyy6Jd382rctANYwonQKfr1kJhuFxAohMy4NRLUaUmCiYYkINmRdsqbFt-mmVogSjE60wRcSqQ2dok7ME7qmfwOcZDGhEXR_iGTUEi3m2Fv-seJaxWCY8q-YZn1DffI1sjBC0qYtRYMS8yKQOeny7rWYuweQEYSuAZG5arufSReThYeTBOfQMB1qzYQOrZajewQtJkVX_Lv9keSOOmnNVu1o91uqJVkOtVouQ3ymrnnmTpOnDObzvWd1bTfBa4Q463ZvrX2fBwng)

## Transport Modes

- **STDIO** (default) – ideal for local MCP clients such as desktops and CLI
  assistants.

![Sequence diagram showing stdio communication between MCP client, server, and Raindrop API](https://mermaid.ink/svg/pako:eNplkcFqwzAMhu97Ch07aNZuxzACm0sgg7bB7guoiSgCz85sZ4M9_ewkkHQxRgf9vz7JsqevnkxDB8abw88HiKdDF7jhDk0AAejhKGoQmsmEla6Srsh9k4ONDy3bx5WnTJ4SfYiclSiTKJFN62y3aDKEkw0ENrHFVuWgLofqDEfb0qCKrChStsMfA7WzDXn_enW7Is1hdjHafoSp6CxzqAwHRs2_Y30ZszIH4Qhjm0XvCfyhzqdM1gJkWpK_Q12s1SBQ6yXpra7mnMxGpyTf6zDZZnDKd9Z4mqhRETmMM99r3DUBHC3K25e9vstTPfpedz2_13FWd655VTE1qCenzIYhn8aCsm0f74ZlO8)

- **Streamable HTTP** – enable with `--http` or `RAINDROP_ENABLE_HTTP_TRANSPORT`.
  The server listens on the configured host/port/path and exposes the FastMCP
  streamable endpoint.

![Sequence diagram showing HTTP/SSE communication between web client, reverse proxy, server, and Raindrop API](https://mermaid.ink/svg/pako:eNplkEFqwzAQRfc9xSxbSOq0S1MMRY1xCkmM5AvI9jQIHEkdySn09JVkQ91aiFnMf_pfMw4_R9Qdvil5IXm9g3CsJK86ZaX2wEA6OLIa2KBQ-5VeRb1qmhoE0g1pBZQRKKXzweSlpaxI8NH0uEJ5RLlUuidjF3mpnIxHMCEB2KbKp8iGpHbWkP_1Y9uiCHJ9Fg1k186mSCH2IDzhPF8VmDKHg1ZeyUF9Ty_L0OU5sICFpEX8bNkYMwCP63J-acPNGPioLm1e6wMwOUw9vp1RdOPgZ2xyfRfnU-xbox3OtkFhOcRP729_dkDYeaBLK-93G3jehRLv49NDUv9viU9byqLRhyH4wha6NJZLPOr-B1IOkQw)

## Logging

`configure_logging()` reads `settings.observability`:

- Structured JSON logging by default.
- Switch to classic log format by setting
  `RAINDROP_OBSERVABILITY_STRUCTURED_LOGGING=false`.
- Log level is controlled through `RAINDROP_OBSERVABILITY_LOG_LEVEL`.

## Shutdown Handling

The FastMCP app registers an `on_shutdown` handler to close the shared
`RaindropClient`. This prevents hanging sockets when assistants disconnect or
HTTP servers redeploy.

### Shutdown Lifecycle

![Sequence diagram showing shutdown process from disconnect through client.close() to httpx resource cleanup](https://mermaid.ink/svg/pako:eNplkDFPwzAQhXd-xY0g0bJHKBJyqLKAooQhGzLuKbWS3hmfU8q_x3FSESkePPh9997zCX6PSAYLqzuvz3cQj9M-WGOdpgAKtMCbqkANFik8f_mnvLBimAhNkA3fTPxBS5hmGvQX9BumnBimTzmN4cg_BCVzv6HqFF1rS0fPbo7fWrUTdArBXfcv8ktmxaVL7fK8yeC_MjS2Iz0ksYlimcGHt12HHpqlT9LKqNUqA5MM92ZgwfuHJNWTadlmoNevZbtbRtScZJni1iJwvE3NcWpATaOL2NkNGHCJm4veOkDBhEvJqETXyrNBEXi92tX_3jkgcNxy9H-cOlUeL7GwgLDpMUAM6-UPJZyW0g)

## Testing & Quality Gates

- Run `uv run pytest` before releases (coverage threshold 80%).
- `uv run crackerjack` bundles Ruff, mypy, pytest, and Bandit scans.
- Coverage HTML is written to `htmlcov/` for review.

## Deployment Architecture

![Deployment architecture showing stdio mode for local clients and HTTP mode with reverse proxy for web clients](https://mermaid.ink/svg/pako:eNp9kVFrgzAQx9_3KY7u2bVqYbSMghplhZZKFfYgfYg1a8PUSJKOFfrhF5N2SifNS8j97-5398-B4-YIqf8E6ohTftDvUZKi5QbWrCBgwYrtcQlBSUktxUhntsezs6DEJ5WCiPiSrNl1kpMFqyV4QlAhsarqSW62kUfCYR3Et55GJXWh77tROKZ1wVlDmVXtG0gI_ya8m8K3swgL2XYz0lvOxwshC8qgUvN3ZN_JttdehvsQ-56m8c2ALamYJP8dCOzsg-TgNU1J91hSVvcWDRTO1N3b8IiYclyLhnHZUdDghjq7XVC_5u7EnXZs1LJVpiAQc_Zz1jnpKoGU8IrWetSBWTwbLGtx0eZdlLMm6AwF3YGgr8uVz-al6yD8M_1F_YgXL3cdLzC8dpVxkoQXNbeJO8NxZFoig0MGFw3-amTgPZ_luSTtiJ-0LOfPU282CZ2egm7KbGK7UdhXnKvyGiLXsX8BYerc9A)

## Deployment Tips

- For container deployments, forward the MCP protocol over stdio or run the
  HTTP transport behind a reverse proxy that terminates TLS.
- Avoid sharing tokens between assistants; generate dedicated Raindrop tokens
  with least privilege where possible.
- Rotate tokens periodically and keep them outside version control.
