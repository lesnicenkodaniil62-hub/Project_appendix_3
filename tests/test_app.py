"""
Юнит-тесты для функций и методов модуля app.py.

Тестирует:
    - Вспомогательные функции (read_html, read_static_file, ...)
    - RequestHandler.do_GET()
    - RequestHandler.do_POST()
    - RequestHandler._serve_static_file()
    - RequestHandler._send_response()
    - run_server()
"""

import io
import socket
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.backend.app import (
    RequestHandler,
    build_404_page,
    build_500_page,
    get_content_type,
    read_html,
    read_static_file,
    run_server,
)


def create_mock_handler() -> RequestHandler:
    """
    Создаёт экземпляр RequestHandler с мокированными зависимостями.

    Returns:
        RequestHandler: Мокированный обработчик запросов
    """
    request = MagicMock(spec=socket.socket)
    client_address = ("127.0.0.1", 12345)
    server = MagicMock()

    with patch.object(RequestHandler, "handle_one_request"):
        handler = RequestHandler(request, client_address, server)

    # Заменяем методы экземпляра на MagicMock.
    # type: ignore[assignment] необходим для намеренной подмены методов
    handler._send_response = MagicMock()  # type: ignore[assignment]
    handler._serve_static_file = MagicMock()  # type: ignore[assignment]
    handler.wfile = MagicMock(spec=io.BytesIO)
    handler.send_response = MagicMock()  # type: ignore[assignment]
    handler.send_header = MagicMock()  # type: ignore[assignment]
    handler.end_headers = MagicMock()  # type: ignore[assignment]
    handler.headers = {}  # type: ignore[assignment]

    # Явно создаём rfile как MagicMock с вложенным read
    mock_rfile = MagicMock()
    mock_rfile.read.return_value = b""
    handler.rfile = mock_rfile  # type: ignore[assignment]

    return handler


# ===========================================================================
# Тесты вспомогательных функций
# ===========================================================================
class TestReadHtml:
    """Тесты функции read_html()."""

    def test_read_html_success(self) -> None:
        """Тест успешного чтения HTML файла."""
        content = read_html("contact.html")
        assert isinstance(content, str)
        assert "Контакты" in content

    def test_read_html_file_not_found(self) -> None:
        """Тест чтения несуществующего файла."""
        with pytest.raises(FileNotFoundError):
            read_html("nonexistent.html")


class TestReadStaticFile:
    """Тесты функции read_static_file()."""

    def test_read_static_file_success(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Тест успешного чтения статического файла."""
        test_file = tmp_path / "test.css"
        test_file.write_text("body { color: red; }", encoding="utf-8")

        import src.backend.app as app_module

        monkeypatch.setattr(app_module, "FRONTEND_STATIC", str(tmp_path))

        content = read_static_file("test.css")
        assert b"color: red" in content

    def test_read_static_file_security(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Тест защиты от выхода за пределы директории."""
        import src.backend.app as app_module

        monkeypatch.setattr(app_module, "FRONTEND_STATIC", str(tmp_path))

        with pytest.raises(PermissionError):
            read_static_file("../../etc/passwd")


class TestGetContentType:
    """Тесты функции get_content_type()."""

    @pytest.mark.parametrize(
        "filepath,expected_type",
        [
            ("test.html", "text/html"),
            ("test.css", "text/css"),
            ("test.js", "application/javascript"),
        ],
    )
    def test_get_content_type_known_types(
        self, filepath: str, expected_type: str
    ) -> None:
        """Тест определения MIME-типа для известных расширений."""
        assert get_content_type(filepath) == expected_type

    def test_get_content_type_unknown(self) -> None:
        """Тест определения MIME-типа для неизвестного расширения."""
        assert (
            get_content_type("test.xyz123") == "application/octet-stream"
        )


class TestBuildPages:
    """Тесты функций build_*_page()."""

    def test_build_404_page(self) -> None:
        """Тест страницы 404."""
        page = build_404_page()
        assert "404" in page
        assert "<!DOCTYPE html>" in page

    def test_build_500_page(self) -> None:
        """Тест страницы 500."""
        page = build_500_page()
        assert "500" in page
        assert "<!DOCTYPE html>" in page


# ===========================================================================
# Тесты RequestHandler.do_GET()
# ===========================================================================
class TestDoGet:
    """Тесты метода do_GET()."""

    @patch("src.backend.app.read_html")
    def test_do_get_root_returns_contacts(
        self, mock_read: MagicMock
    ) -> None:
        """Тест GET / возвращает страницу контактов."""
        handler = create_mock_handler()
        handler.path = "/"
        mock_read.return_value = "<html>Контакты</html>"

        handler.do_GET()

        mock_read.assert_called_once_with("contact.html")
        handler._send_response.assert_called_once_with(
            200, "<html>Контакты</html>"
        )  # type: ignore[attr-defined]

    @patch("src.backend.app.build_404_page")
    def test_do_get_unknown_path_returns_404(
        self, mock_404: MagicMock
    ) -> None:
        """Тест GET неизвестного пути возвращает 404."""
        handler = create_mock_handler()
        handler.path = "/unknown.html"
        mock_404.return_value = "<html>404</html>"

        handler.do_GET()

        handler._send_response.assert_called_once_with(
            404, "<html>404</html>"
        )  # type: ignore[attr-defined]

    @patch("src.backend.app.read_html", side_effect=Exception("Test"))
    @patch("src.backend.app.build_500_page")
    def test_do_get_internal_error(
        self, mock_500: MagicMock, mock_read: MagicMock
    ) -> None:
        """Тест обработки внутренней ошибки."""
        handler = create_mock_handler()
        handler.path = "/contact.html"
        mock_500.return_value = "<html>500</html>"

        handler.do_GET()

        handler._send_response.assert_called_once_with(
            500, "<html>500</html>"
        )  # type: ignore[attr-defined]


# ===========================================================================
# Тесты RequestHandler.do_POST()
# ===========================================================================
class TestDoPost:
    """Тесты метода do_POST()."""

    def test_do_post_success(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Тест успешного POST-запроса."""
        handler = create_mock_handler()
        handler.path = "/contact.html"
        handler.headers = {"Content-Length": "30"}  # type: ignore[assignment]

        form_data = "name=Ivan&email=ivan@example.com&message=Hello"
        handler.rfile.read.return_value = form_data.encode("utf-8")

        handler.do_POST()

        captured = capsys.readouterr()
        assert "[POST] Получены данные от пользователя:" in captured.out
        assert "name=Ivan" in captured.out
        assert handler._send_response.called  # type: ignore[attr-defined]

    @patch("src.backend.app.build_500_page")
    def test_do_post_exception(
        self, mock_500: MagicMock
    ) -> None:
        """Тест обработки исключения в POST."""
        handler = create_mock_handler()
        handler.path = "/contact.html"

        mock_headers = MagicMock()
        mock_headers.get.side_effect = Exception("Test error")
        handler.headers = mock_headers  # type: ignore[assignment]

        mock_500.return_value = "<html>500</html>"

        handler.do_POST()

        handler._send_response.assert_called_once_with(
            500, "<html>500</html>"
        )  # type: ignore[attr-defined]


# ===========================================================================
# Тесты run_server()
# ===========================================================================
class TestRunServer:
    """Тесты функции run_server()."""

    @patch("src.backend.app.HTTPServer")
    def test_run_server_creates_and_starts(
        self,
        mock_server_class: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Тест создания и запуска сервера."""
        mock_server_instance = MagicMock()
        mock_server_class.return_value = mock_server_instance
        mock_server_instance.serve_forever.side_effect = KeyboardInterrupt

        run_server()

        mock_server_class.assert_called_once_with(
            ("127.0.0.1", 8000), RequestHandler
        )
        mock_server_instance.server_close.assert_called_once()

        captured = capsys.readouterr()
        assert "Сервер запущен" in captured.out


# ===========================================================================
# Тесты log_message()
# ===========================================================================
class TestLogMessage:
    """Тесты метода log_message()."""

    def test_log_message_with_args(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Тест вывода лога с аргументами."""
        handler = create_mock_handler()
        handler.log_message("GET %s HTTP/1.1", "/")

        captured = capsys.readouterr()
        assert "[SERVER] GET / HTTP/1.1" in captured.out

    def test_log_message_without_args(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Тест вывода лога без аргументов."""
        handler = create_mock_handler()
        handler.log_message("Simple message")

        captured = capsys.readouterr()
        assert "[SERVER] Simple message" in captured.out