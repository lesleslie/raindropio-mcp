"""
Raindrop.io MCP Server.

A FastMCP-based Model Context Protocol server for Raindrop.io APIs,
providing AI agents with seamless access to bookmark management functions.
"""

from importlib.metadata import version as _importlib_version

__version__ = _importlib_version("raindropio-mcp")
__author__ = "Raindrop.io MCP Team"
__description__ = "MCP Server for the Raindrop.io API"

__all__ = [
    "__author__",
    "__description__",
    "__version__",
]
