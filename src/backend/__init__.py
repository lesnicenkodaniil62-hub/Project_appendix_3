"""
Backend-пакет приложения.

Содержит:
    - HTTP-сервер для обработки запросов
    - Логику работы с HTML-шаблонами
    - Обработку форм и данных пользователя
"""

from typing import List

from .app import RequestHandler, run_server

__all__: List[str] = ["run_server", "RequestHandler"]
__version__: str = "0.A.1"
