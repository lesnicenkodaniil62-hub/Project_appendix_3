"""
Тесты для статических файлов (CSS, JS).

Тестирует:
    - Отдачу CSS файлов
    - Отдачу JS файлов
    - Правильные MIME-типы
    - Обработку несуществующих файлов
"""

from http.client import HTTPConnection
from typing import Optional

import pytest


class TestStaticFiles:
    """Тесты статических файлов."""

    def test_get_css_file(self, http_client: HTTPConnection) -> None:
        """Тест получения CSS файла."""
        http_client.request("GET", "/src/frontend/css/bootstrap.min.css")
        response = http_client.getresponse()

        assert response.status == 200

        content_type: Optional[str] = response.getheader("Content-Type")
        assert content_type == "text/css"

        body: bytes = response.read()
        assert len(body) > 0

    def test_get_js_file(self, http_client: HTTPConnection) -> None:
        """Тест получения JS файла."""
        http_client.request("GET", "/src/frontend/js/bootstrap.bundle.min.js")
        response = http_client.getresponse()

        assert response.status == 200

        content_type: Optional[str] = response.getheader("Content-Type")
        assert content_type is not None
        assert "javascript" in content_type

        body: bytes = response.read()
        assert len(body) > 0

    def test_get_nonexistent_static_file(self, http_client: HTTPConnection) -> None:
        """Тест получения несуществующего статического файла."""
        http_client.request("GET", "/src/frontend/css/nonexistent.css")
        response = http_client.getresponse()

        assert response.status == 404

    def test_static_file_content_length(
        self, http_client: HTTPConnection
    ) -> None:
        """Тест наличия Content-Length в ответе."""
        http_client.request("GET", "/src/frontend/css/bootstrap.min.css")
        response = http_client.getresponse()

        content_length: Optional[str] = response.getheader("Content-Length")
        assert content_length is not None
        assert int(content_length) > 0

        response.read()

    def test_static_file_not_empty(self, http_client: HTTPConnection) -> None:
        """Тест что статический файл не пустой."""
        http_client.request("GET", "/src/frontend/css/bootstrap.min.css")
        response = http_client.getresponse()

        body: bytes = response.read()
        assert len(body) > 0
