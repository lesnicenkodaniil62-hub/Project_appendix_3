"""
Backend-пакет приложения.
"""

from typing import List

from .app import RequestHandler, run_server

__all__: List[str] = ["run_server", "RequestHandler"]
__version__: str = "1.0.0"
