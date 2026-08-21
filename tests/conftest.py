"""
Фикстуры для тестирования веб-приложения.

Содержит фикстуры для:
    - Запуска тестового HTTP-сервера
    - Создания HTTP-клиента
    - Подготовки тестовых данных
"""

import threading
import time
from http.client import HTTPConnection
from http.server import HTTPServer
from pathlib import Path
from typing import Generator

import pytest

from src.backend.app import RequestHandler


@pytest.fixture(scope="session")
def test_server() -> Generator[HTTPServer, None, None]:
    """
    Фикстура для запуска тестового HTTP-сервера.

    Запускает сервер в отдельном потоке на порту 8765.

    Yields:
        HTTPServer: Экземпляр тестового сервера
    """
    host: str = "127.0.0.1"
    port: int = 8765

    server: HTTPServer = HTTPServer((host, port), RequestHandler)

    server_thread: threading.Thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )
    server_thread.start()

    time.sleep(0.5)

    yield server

    server.shutdown()
    server.server_close()


@pytest.fixture
def http_client() -> Generator[HTTPConnection, None, None]:
    """
    Фикстура для создания HTTP-клиента.

    Создаёт НОВОЕ соединение для каждого теста.

    Yields:
        HTTPConnection: HTTP-клиент для тестов
    """
    client: HTTPConnection = HTTPConnection("127.0.0.1", 8765)
    yield client
    client.close()


@pytest.fixture
def sample_form_data() -> dict[str, str]:
    """
    Фикстура с тестовыми данными формы.

    Returns:
        dict[str, str]: Тестовые данные формы
    """
    return {
        "name": "Иван Иванов",
        "email": "ivan@example.com",
        "message": "Тестовое сообщение",
    }


@pytest.fixture
def temp_html_file(tmp_path: Path) -> Path:
    """
    Фикстура для создания временного HTML-файла.

    Args:
        tmp_path: Временная директория pytest (pathlib.Path)

    Returns:
        Path: Путь к временному HTML-файлу
    """
    html_content: str = "<html><body>Тестовый файл</body></html>"
    file_path: Path = tmp_path / "test.html"
    file_path.write_text(html_content, encoding="utf-8")
    return file_path


@pytest.fixture
def temp_static_file(tmp_path: Path) -> Path:
    """
    Фикстура для создания временного статического файла.

    Args:
        tmp_path: Временная директория pytest (pathlib.Path)

    Returns:
        Path: Путь к временному файлу
    """
    file_content: str = "body { color: red; }"
    file_path: Path = tmp_path / "test.css"
    file_path.write_text(file_content, encoding="utf-8")
    return file_path
