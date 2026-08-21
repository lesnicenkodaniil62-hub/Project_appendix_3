"""
Веб-приложение на стандартной библиотеке Python (http.server).

Основной функционал:
  - GET-запросы возвращают HTML-страницы из components/
  - Отдаёт статические файлы (CSS, JS, изображения)
  - POST-запрос принимает данные формы и выводит их в консоль
  - Обработка ошибок 404 и 500

Запуск:
    python main.py
"""

import mimetypes
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict, List, NoReturn, Optional
from urllib.parse import parse_qs, urlparse

# ---------------------------------------------------------------------------
# Пути к файлам
# ---------------------------------------------------------------------------
BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT: str = os.path.dirname(BASE_DIR)
FRONTEND_COMPONENTS: str = os.path.join(BASE_DIR, "frontend", "components")
FRONTEND_STATIC: str = os.path.join(BASE_DIR, "frontend")

HOST: str = "127.0.0.1"
PORT: int = 8000


# ---------------------------------------------------------------------------
# Вспомогательные функции
# ---------------------------------------------------------------------------
def read_html(filename: str) -> str:
    """
    Читает HTML-файл через контекстный менеджер.

    Args:
        filename: Имя файла в папке components

    Returns:
        Содержимое файла в виде строки

    Raises:
        FileNotFoundError: Если файл не найден
    """
    filepath: str = os.path.join(FRONTEND_COMPONENTS, filename)
    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()


def read_static_file(relative_path: str) -> bytes:
    """
    Читает статический файл (CSS, JS, изображения).

    Args:
        relative_path: Относительный путь к файлу

    Returns:
        Содержимое файла в виде байтов

    Raises:
        FileNotFoundError: Если файл не найден
        PermissionError: Если путь выходит за пределы frontend/
    """
    relative_path = relative_path.lstrip("/")
    filepath: str = os.path.join(FRONTEND_STATIC, relative_path)

    # Проверка безопасности
    if not os.path.abspath(filepath).startswith(os.path.abspath(FRONTEND_STATIC)):
        raise PermissionError("Доступ за пределы frontend/ запрещён")

    with open(filepath, "rb") as file:
        return file.read()


def get_content_type(filepath: str) -> str:
    """
    Определяет MIME-тип файла.

    Args:
        filepath: Путь к файлу

    Returns:
        MIME-тип файла
    """
    mime_type: Optional[str] = mimetypes.guess_type(filepath)[0]
    return mime_type or "application/octet-stream"


def build_404_page() -> str:
    """
    Возвращает HTML-страницу 404.

    Returns:
        HTML-строка страницы 404
    """
    return """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 — Страница не найдена</title>
    <link href="/src/frontend/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { display: flex; align-items: center; justify-content: center;
               min-height: 100vh; font-family: system-ui, sans-serif; background: #f8f9fa; margin: 0; }
        .box { text-align: center; padding: 40px; background: #fff;
               border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
        .box h1 { font-size: 6rem; color: #3b7ddd; margin: 0; }
        .box p  { color: #6c757d; font-size: 1.1rem; }
        .box a  { color: #3b7ddd; text-decoration: none; }
    </style>
</head>
<body>
    <header></header>
    <main>
        <div class="box">
            <h1>404</h1>
            <p>Страница не найдена</p>
            <a href="/">← Вернуться на главную</a>
        </div>
    </main>
    <footer></footer>
</body>
</html>"""


def build_500_page() -> str:
    """
    Возвращает HTML-страницу 500.

    Returns:
        HTML-строка страницы 500
    """
    return """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>500 — Ошибка сервера</title>
    <link href="/src/frontend/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { display: flex; align-items: center; justify-content: center;
               min-height: 100vh; font-family: system-ui, sans-serif; background: #f8f9fa; margin: 0; }
        .box { text-align: center; padding: 40px; background: #fff;
               border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
        .box h1 { font-size: 6rem; color: #dc3545; margin: 0; }
        .box p  { color: #6c757d; font-size: 1.1rem; }
        .box a  { color: #3b7ddd; text-decoration: none; }
    </style>
</head>
<body>
    <header></header>
    <main>
        <div class="box">
            <h1>500</h1>
            <p>Внутренняя ошибка сервера</p>
            <a href="/">← Вернуться на главную</a>
        </div>
    </main>
    <footer></footer>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Обработчик HTTP-запросов
# ---------------------------------------------------------------------------
class RequestHandler(BaseHTTPRequestHandler):
    """Обработчик HTTP-запросов."""

    def log_message(self, format: str, *args: object) -> None:
        """
        Переопределение логирования.

        Args:
            format: Формат сообщения
            *args: Аргументы для форматирования
        """
        print(f"[SERVER] {args[0]}")

    def do_GET(self) -> None:
        """
        Обработка GET-запросов.

        Маршруты:
            - / или /main.html → главная страница
            - /catalog.html → каталог
            - /orders.html → заказы
            - /contact.html → контакты
            - /src/frontend/* → статические файлы
        """
        parsed_path = urlparse(self.path)
        path: str = parsed_path.path

        try:
            # Статические файлы (CSS, JS, изображения)
            if path.startswith("/src/frontend/"):
                self._serve_static_file(path)
                return

            # Маршрутизация HTML-страниц
            html_content: str = ""
            if path == "/" or path == "/main.html":
                html_content = read_html("main.html")
            elif path == "/catalog.html":
                html_content = read_html("catalog.html")
            elif path == "/orders.html":
                html_content = read_html("orders.html")
            elif path == "/contact.html":
                html_content = read_html("contact.html")
            else:
                self._send_response(404, build_404_page())
                return

            self._send_response(200, html_content)

        except FileNotFoundError:
            self._send_response(404, build_404_page())
        except PermissionError as e:
            print(f"[SECURITY] {e}")
            self._send_response(403, "<h1>403 Forbidden</h1>")
        except Exception as e:
            print(f"[ERROR] Ошибка при обработке GET: {e}")
            self._send_response(500, build_500_page())

    def do_POST(self) -> None:
        """
        Обработка POST-запросов.

        Принимает данные формы и выводит их в консоль.
        """
        try:
            content_length: int = int(self.headers.get("Content-Length", 0))
            post_data: str = self.rfile.read(content_length).decode("utf-8")
            parsed: Dict[str, List[str]] = parse_qs(post_data)

            print("\n" + "=" * 50)
            print("[POST] Получены данные от пользователя:")
            print(f"  URL:          {self.path}")
            print(f"  Content-Type: {self.headers.get('Content-Type')}")
            print(f"  Тело запроса: {post_data}")
            print(f"  Распарсенные: {parsed}")
            print("=" * 50 + "\n")

            response: str = (
                "<!DOCTYPE html><html><head><meta charset='UTF-8'>"
                "<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
                "<title>Данные приняты</title>"
                "<link href='/src/frontend/css/bootstrap.min.css' rel='stylesheet'>"
                "<style>"
                "body { display: flex; align-items: center; justify-content: center;"
                "min-height: 100vh; font-family: system-ui; background: #f8f9fa; margin: 0; }"
                ".box { text-align: center; padding: 40px; background: #fff;"
                "border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }"
                ".box h2 { color: #28a745; margin: 0 0 16px 0; }"
                ".box a { color: #3b7ddd; text-decoration: none; }"
                "</style></head><body>"
                "<header></header>"
                "<main><div class='box'>"
                "<h2>✓ Данные успешно приняты</h2>"
                "<p>Проверьте консоль сервера.</p>"
                "<a href='/'>← На главную</a>"
                "</div></main>"
                "<footer></footer>"
                "</body></html>"
            )
            self._send_response(200, response)

        except Exception as e:
            print(f"[ERROR] Ошибка обработки POST: {e}")
            self._send_response(500, build_500_page())

    def _serve_static_file(self, path: str) -> None:
        """
        Отдаёт статический файл.

        Args:
            path: Путь к файлу
        """
        file_content: bytes = read_static_file(path)
        content_type: str = get_content_type(path)

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(file_content)))
        self.end_headers()
        self.wfile.write(file_content)

    def _send_response(self, status_code: int, html_content: str) -> None:
        """
        Отправляет HTTP-ответ.

        Args:
            status_code: HTTP статус код
            html_content: HTML содержимое ответа
        """
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html_content.encode("utf-8"))


# ---------------------------------------------------------------------------
# Точка входа
# ---------------------------------------------------------------------------
def run_server() -> NoReturn:
    """
    Запускает HTTP-сервер.

    Функция не возвращает управление (serve_forever).
    """
    server: HTTPServer = HTTPServer((HOST, PORT), RequestHandler)
    print(f"\n Сервер запущен: http://{HOST}:{PORT}")
    print(f" HTML-файлы: {FRONTEND_COMPONENTS}")
    print(f" Статика:    {FRONTEND_STATIC}")
    print("️  Для остановки нажмите Ctrl+C\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n Сервер остановлен пользователем.")
        server.server_close()


if __name__ == "__main__":
    run_server()
