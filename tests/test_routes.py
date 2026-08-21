"""
Интеграционные тесты для HTTP-маршрутов.

Тестирует:
    - GET запросы ко всем страницам
    - POST запросы с формой
    - Обработку ошибок 404
    - Возврат правильного Content-Type
"""

from http.client import HTTPConnection
from typing import Optional
from urllib.parse import urlencode

import pytest


class TestGetRoutes:
    """Тесты GET-маршрутов."""

    @pytest.mark.parametrize(
        "path,expected_status",
        [
            ("/", 200),
            ("/main.html", 200),
            ("/catalog.html", 200),
            ("/orders.html", 200),
            ("/contact.html", 200),
        ],
    )
    def test_get_routes_success(
        self,
        path: str,
        expected_status: int,
    ) -> None:
        """Тест успешного GET-запроса к страницам."""
        client: HTTPConnection = HTTPConnection("127.0.0.1", 8765)
        try:
            client.request("GET", path)
            response = client.getresponse()

            assert response.status == expected_status
            assert response.getheader("Content-Type") == "text/html; charset=utf-8"

            body: bytes = response.read()
            assert len(body) > 0
            assert b"<!DOCTYPE html>" in body
        finally:
            client.close()

    def test_get_root_returns_contacts(self) -> None:
        """Тест что корневой путь возвращает страницу контактов."""
        client: HTTPConnection = HTTPConnection("127.0.0.1", 8765)
        try:
            client.request("GET", "/")
            response = client.getresponse()

            assert response.status == 200

            body: bytes = response.read()
            assert b"Контакты" in body
        finally:
            client.close()

    def test_get_main_page(self) -> None:
        """Тест главной страницы."""
        client: HTTPConnection = HTTPConnection("127.0.0.1", 8765)
        try:
            client.request("GET", "/main.html")
            response = client.getresponse()

            assert response.status == 200

            body: bytes = response.read()
            assert b"Главная" in body
        finally:
            client.close()

    def test_get_catalog_page(self) -> None:
        """Тест страницы каталога."""
        client: HTTPConnection = HTTPConnection("127.0.0.1", 8765)
        try:
            client.request("GET", "/catalog.html")
            response = client.getresponse()

            assert response.status == 200

            body: bytes = response.read()
            assert b"Каталог" in body
        finally:
            client.close()

    def test_get_orders_page(self) -> None:
        """Тест страницы заказов."""
        client: HTTPConnection = HTTPConnection("127.0.0.1", 8765)
        try:
            client.request("GET", "/orders.html")
            response = client.getresponse()

            assert response.status == 200

            body: bytes = response.read()
            assert b"Категория 1" in body or b"Заказы" in body
        finally:
            client.close()

    def test_get_contact_page(self) -> None:
        """Тест страницы контактов."""
        client: HTTPConnection = HTTPConnection("127.0.0.1", 8765)
        try:
            client.request("GET", "/contact.html")
            response = client.getresponse()

            assert response.status == 200

            body: bytes = response.read()
            assert b"Контакты" in body
        finally:
            client.close()

    def test_get_nonexistent_page(self) -> None:
        """Тест несуществующей страницы (404)."""
        client: HTTPConnection = HTTPConnection("127.0.0.1", 8765)
        try:
            client.request("GET", "/nonexistent.html")
            response = client.getresponse()

            assert response.status == 404

            body: bytes = response.read()
            assert b"404" in body
        finally:
            client.close()

    def test_get_page_contains_header(self) -> None:
        """Тест наличия тега header в странице."""
        client: HTTPConnection = HTTPConnection("127.0.0.1", 8765)
        try:
            client.request("GET", "/contact.html")
            response = client.getresponse()

            body: bytes = response.read()
            assert b"<header>" in body
        finally:
            client.close()

    def test_get_page_contains_main(self) -> None:
        """Тест наличия тега main в странице."""
        client: HTTPConnection = HTTPConnection("127.0.0.1", 8765)
        try:
            client.request("GET", "/contact.html")
            response = client.getresponse()

            body: bytes = response.read()
            assert b"<main>" in body
        finally:
            client.close()

    def test_get_page_contains_footer(self) -> None:
        """Тест наличия тега footer в странице."""
        client: HTTPConnection = HTTPConnection("127.0.0.1", 8765)
        try:
            client.request("GET", "/contact.html")
            response = client.getresponse()

            body: bytes = response.read()
            assert b"<footer>" in body
        finally:
            client.close()

    def test_get_page_contains_bootstrap(self) -> None:
        """Тест подключения Bootstrap."""
        client: HTTPConnection = HTTPConnection("127.0.0.1", 8765)
        try:
            client.request("GET", "/contact.html")
            response = client.getresponse()

            body: bytes = response.read()
            assert b"bootstrap.min.css" in body
        finally:
            client.close()


class TestPostRoutes:
    """Тесты POST-маршрутов."""

    def test_post_contact_form(
        self,
        sample_form_data: dict[str, str],
    ) -> None:
        """Тест отправки формы контактов."""
        client: HTTPConnection = HTTPConnection("127.0.0.1", 8765)
        try:
            data: str = urlencode(sample_form_data)
            headers: dict[str, str] = {
                "Content-Type": "application/x-www-form-urlencoded"
            }

            client.request("POST", "/contact.html", body=data, headers=headers)
            response = client.getresponse()

            assert response.status == 200

            body: bytes = response.read()
            assert b"Данные успешно приняты" in body
        finally:
            client.close()

    def test_post_form_with_empty_data(self) -> None:
        """Тест отправки пустой формы."""
        client: HTTPConnection = HTTPConnection("127.0.0.1", 8765)
        try:
            data: str = urlencode({"name": "", "email": "", "message": ""})
            headers: dict[str, str] = {
                "Content-Type": "application/x-www-form-urlencoded"
            }

            client.request("POST", "/contact.html", body=data, headers=headers)
            response = client.getresponse()

            assert response.status == 200
            response.read()
        finally:
            client.close()

    def test_post_form_with_special_characters(self) -> None:
        """Тест отправки формы со специальными символами."""
        client: HTTPConnection = HTTPConnection("127.0.0.1", 8765)
        try:
            data: str = urlencode({
                "name": "Иван & Мария",
                "email": "test@example.com",
                "message": "Привет! <script>alert('test')</script>",
            })
            headers: dict[str, str] = {
                "Content-Type": "application/x-www-form-urlencoded"
            }

            client.request("POST", "/contact.html", body=data, headers=headers)
            response = client.getresponse()

            assert response.status == 200
            response.read()
        finally:
            client.close()

    def test_post_form_content_type(
        self,
        sample_form_data: dict[str, str],
    ) -> None:
        """Тест Content-Type ответа на POST-запрос."""
        client: HTTPConnection = HTTPConnection("127.0.0.1", 8765)
        try:
            data: str = urlencode(sample_form_data)
            headers: dict[str, str] = {
                "Content-Type": "application/x-www-form-urlencoded"
            }

            client.request("POST", "/contact.html", body=data, headers=headers)
            response = client.getresponse()

            content_type: Optional[str] = response.getheader("Content-Type")
            assert content_type == "text/html; charset=utf-8"
            response.read()
        finally:
            client.close()

    def test_post_form_data_printed_to_console(
        self,
        sample_form_data: dict[str, str],
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Тест что данные формы выводятся в консоль."""
        client: HTTPConnection = HTTPConnection("127.0.0.1", 8765)
        try:
            data: str = urlencode(sample_form_data)
            headers: dict[str, str] = {
                "Content-Type": "application/x-www-form-urlencoded"
            }

            client.request("POST", "/contact.html", body=data, headers=headers)
            response = client.getresponse()
            response.read()

            captured = capsys.readouterr()
            assert "[POST] Получены данные от пользователя:" in captured.out
            assert sample_form_data["name"] in captured.out
        finally:
            client.close()
