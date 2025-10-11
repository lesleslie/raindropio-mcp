"""Process entrypoint for the Raindrop.io MCP server."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from typing import Any

from raindropio_mcp.config import get_settings
from raindropio_mcp.server import create_app

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    settings = get_settings()
    level = getattr(logging, settings.observability.log_level.upper(), logging.INFO)

    if settings.observability.structured_logging:

        class JSONFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
                payload: dict[str, Any] = {
                    "timestamp": self.formatTime(record),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                }
                if record.exc_info:
                    payload["exception"] = self.formatException(record.exc_info)
                return json.dumps(payload)

        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logging.basicConfig(level=level, handlers=[handler])
    else:
        logging.basicConfig(
            level=level,
            format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Raindrop.io MCP Server")
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    parser.add_argument(
        "--http", action="store_true", help="Run using streamable HTTP transport"
    )
    parser.add_argument("--http-host", type=str, help="HTTP bind host override")
    parser.add_argument("--http-port", type=int, help="HTTP port override")
    parser.add_argument("--http-path", type=str, help="HTTP path override")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)  # noqa

    if args.version:
        import sys

        sys.exit(0)

    configure_logging()
    settings = get_settings()
    app = create_app()

    use_http = args.http or settings.enable_http_transport
    if use_http:
        host = args.http_host or settings.http_host
        port = args.http_port or settings.http_port
        path = args.http_path or settings.http_path
        logger.info(
            "Starting Raindrop.io MCP server (HTTP)",
            extra={"host": host, "port": port, "path": path},
        )
        asyncio.run(
            app.run(  # type: ignore[func-returns-value]
                transport="streamable-http",
                host=host,
                port=port,
                streamable_http_path=path,
            )
        )
        return

    logger.info("Starting Raindrop.io MCP server (stdio)")
    asyncio.run(app.run())  # type: ignore[func-returns-value]


if __name__ == "__main__":
    main()
