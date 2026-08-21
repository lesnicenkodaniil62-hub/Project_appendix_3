"""Юнит-тесты для модуля app.py."""

import io
import socket
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.backend.app import (RequestHandler, build_404_page, build_500_page, get_content_type, read_html,
                             read_static_file, run_server)


def create_mock_handler() -> RequestHandler:
    """Создаёт экземпляр RequestHandler с мокированными зависимостями."""
    request = MagicMock(spec=socket.socket)
    client_address = ("127.0.0.1", 12345)
    server = MagicMock()

    with patch.object(RequestHandler, "handle_one_request"):
        handler = RequestHandler(request, client_address, server)

    # type: ignore необходим для намеренной подмены методов экземпляра на MagicMock
    handler._send_response = MagicMock()  # type: ignore[assignment]
    handler._serve_static_file = MagicMock()  # type: ignore[assignment]
    handler.wfile = MagicMock(spec=io.BytesIO)
    handler.send_response = MagicMock()  # type: ignore[assignment]
    handler.send_header = MagicMock()  # type: ignore[assignment]
    handler.end_headers = MagicMock()  # type: ignore[assignment]
    handler.headers = {}  # type: ignore[assignment]
    handler.rfile = MagicMock()

    return handler


class TestReadHtml:
    def test_read_html_success(self) -> None:
        content = read_html("contact.html")
        assert isinstance(content, str) and "Контакты" in content

    def test_read_html_file_not_found(self) -> None:
        with pytest.raises(FileNotFoundError):
            read_html("nonexistent.html")


class TestReadStaticFile:
    def test_read_static_file_success(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        test_file = tmp_path / "test.css"
        test_file.write_text("body { color: red; }", encoding="utf-8")

        import src.backend.app as app_module

        monkeypatch.setattr(app_module, "FRONTEND_STATIC", str(tmp_path))

        content = read_static_file("test.css")
        assert b"color: red" in content

    def test_read_static_file_security(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        import src.backend.app as app_module

        monkeypatch.setattr(app_module, "FRONTEND_STATIC", str(tmp_path))
        with pytest.raises(PermissionError):
            read_static_file("../../etc/passwd")


class TestGetContentType:
    @pytest.mark.parametrize(
        "filepath,expected_type",
        [("test.html", "text/html"), ("test.css", "text/css"), ("test.js", "application/javascript")],
    )
    def test_get_content_type_known_types(self, filepath: str, expected_type: str) -> None:
        assert get_content_type(filepath) == expected_type

    def test_get_content_type_unknown(self) -> None:
        assert get_content_type("test.xyz123") == "application/octet-stream"


class TestBuildPages:
    def test_build_404_page(self) -> None:
        assert "404" in build_404_page() and "<!DOCTYPE html>" in build_404_page()

    def test_build_500_page(self) -> None:
        assert "500" in build_500_page() and "<!DOCTYPE html>" in build_500_page()


class TestDoGet:
    @patch("src.backend.app.read_html")
    def test_do_get_root_returns_contacts(self, mock_read: MagicMock) -> None:
        handler = create_mock_handler()
        handler.path = "/"
        mock_read.return_value = "<html>Контакты</html>"
        handler.do_GET()
        mock_read.assert_called_once_with("contact.html")
        handler._send_response.assert_called_once_with(200, "<html>Контакты</html>")  # type: ignore[attr-defined]

    @patch("src.backend.app.build_404_page")
    def test_do_get_unknown_path_returns_404(self, mock_404: MagicMock) -> None:
        handler = create_mock_handler()
        handler.path = "/unknown.html"
        mock_404.return_value = "<html>404</html>"
        handler.do_GET()
        handler._send_response.assert_called_once_with(404, "<html>404</html>")  # type: ignore[attr-defined]

    @patch("src.backend.app.read_html", side_effect=Exception("Test error"))
    @patch("src.backend.app.build_500_page")
    def test_do_get_internal_error(self, mock_500: MagicMock, mock_read: MagicMock) -> None:
        handler = create_mock_handler()
        handler.path = "/contact.html"
        mock_500.return_value = "<html>500</html>"
        handler.do_GET()
        handler._send_response.assert_called_once_with(500, "<html>500</html>")  # type: ignore[attr-defined]


class TestDoPost:
    def test_do_post_success(self, capsys: pytest.CaptureFixture[str]) -> None:
        handler = create_mock_handler()
        handler.path = "/contact.html"
        handler.headers = {"Content-Length": "30"}  # type: ignore[assignment]
        handler.rfile.read.return_value = b"name=Ivan&email=ivan@example.com&message=Hello"

        handler.do_POST()

        captured = capsys.readouterr()
        assert "[POST] Получены данные от пользователя:" in captured.out
        assert handler._send_response.called  # type: ignore[attr-defined]

    @patch("src.backend.app.build_500_page")
    def test_do_post_exception(self, mock_500: MagicMock) -> None:
        handler = create_mock_handler()
        handler.path = "/contact.html"
        handler.headers = MagicMock()
        handler.headers.get.side_effect = Exception("Test error")
        mock_500.return_value = "<html>500</html>"

        handler.do_POST()
        handler._send_response.assert_called_once_with(500, "<html>500</html>")  # type: ignore[attr-defined]


class TestRunServer:
    @patch("src.backend.app.HTTPServer")
    def test_run_server_creates_and_starts(
        self, mock_server_class: MagicMock, capsys: pytest.CaptureFixture[str]
    ) -> None:
        mock_server_instance = MagicMock()
        mock_server_class.return_value = mock_server_instance
        mock_server_instance.serve_forever.side_effect = KeyboardInterrupt

        run_server()

        mock_server_class.assert_called_once_with(("127.0.0.1", 8000), RequestHandler)
        mock_server_instance.server_close.assert_called_once()
        captured = capsys.readouterr()
        assert "Сервер запущен" in captured.out


class TestLogMessage:
    def test_log_message_with_args(self, capsys: pytest.CaptureFixture[str]) -> None:
        handler = create_mock_handler()
        handler.log_message("GET %s HTTP/1.1", "/")
        assert "[SERVER] GET / HTTP/1.1" in capsys.readouterr().out

    def test_log_message_without_args(self, capsys: pytest.CaptureFixture[str]) -> None:
        handler = create_mock_handler()
        handler.log_message("Simple message")
        assert "[SERVER] Simple message" in capsys.readouterr().out
