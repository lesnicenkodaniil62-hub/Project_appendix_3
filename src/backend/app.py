"""
Веб-приложение на стандартной библиотеке Python (http.server).
"""

import mimetypes
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_COMPONENTS: str = os.path.join(BASE_DIR, "frontend", "components")
FRONTEND_STATIC: str = os.path.join(BASE_DIR, "frontend")

HOST: str = "127.0.0.1"
PORT: int = 8000


def read_html(filename: str) -> str:
    """Читает HTML-файл через контекстный менеджер."""
    filepath: str = os.path.join(FRONTEND_COMPONENTS, filename)
    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()


def read_static_file(relative_path: str) -> bytes:
    """Читает статический файл."""
    relative_path = relative_path.lstrip("/")
    prefix: str = "src/frontend/"
    if relative_path.startswith(prefix):
        relative_path = relative_path[len(prefix) :]

    filepath: str = os.path.join(FRONTEND_STATIC, relative_path)

    if not os.path.abspath(filepath).startswith(os.path.abspath(FRONTEND_STATIC)):
        raise PermissionError("Доступ за пределы frontend/ запрещён")

    with open(filepath, "rb") as file:
        return file.read()


def get_content_type(filepath: str) -> str:
    """Определяет MIME-тип файла."""
    mime_type: Optional[str] = mimetypes.guess_type(filepath)[0]
    return mime_type or "application/octet-stream"


def build_404_page() -> str:
    """Возвращает HTML-страницу 404."""
    return """<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><title>404</title>
<link href="/src/frontend/css/bootstrap.min.css" rel="stylesheet">
<style>body{display:flex;align-items:center;justify-content:center;min-height:100vh;font-family:system-ui;background:#f8f9fa;margin:0}.box{text-align:center;padding:40px;background:#fff;border-radius:12px;box-shadow:0 4px 12px rgba(0,0,0,0.08)}h1{font-size:6rem;color:#3b7ddd;margin:0}</style>
</head><body><header></header><main><div class="box"><h1>404</h1><p>Страница не найдена</p><a href="/">← На главную</a></div></main><footer></footer></body></html>"""


def build_500_page() -> str:
    """Возвращает HTML-страницу 500."""
    return """<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><title>500</title>
<link href="/src/frontend/css/bootstrap.min.css" rel="stylesheet">
<style>body{display:flex;align-items:center;justify-content:center;min-height:100vh;font-family:system-ui;background:#f8f9fa;margin:0}.box{text-align:center;padding:40px;background:#fff;border-radius:12px;box-shadow:0 4px 12px rgba(0,0,0,0.08)}h1{font-size:6rem;color:#dc3545;margin:0}</style>
</head><body><header></header><main><div class="box"><h1>500</h1><p>Ошибка сервера</p><a href="/">← На главную</a></div></main><footer></footer></body></html>"""


class RequestHandler(BaseHTTPRequestHandler):
    """Обработчик HTTP-запросов."""

    def log_message(self, format: str, *args: Any) -> None:
        """Переопределение логирования (исправлен IndexError)."""
        if args:
            print(f"[SERVER] {format % args}")
        else:
            print(f"[SERVER] {format}")

    def do_GET(self) -> None:
        """Обработка GET-запросов."""
        parsed_path = urlparse(self.path)
        path: str = parsed_path.path

        try:
            if path.startswith("/src/frontend/"):
                self._serve_static_file(path)
                return

            html_content: str = ""
            # На любой корневой запрос или явный запрос контактов возвращаем Контакты
            if path == "/" or path == "/contact.html":
                html_content = read_html("contact.html")
            elif path == "/main.html":
                html_content = read_html("main.html")
            elif path == "/catalog.html":
                html_content = read_html("catalog.html")
            elif path == "/orders.html":
                html_content = read_html("orders.html")
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
        """Обработка POST-запросов."""
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
                "<title>Принято</title><link href='/src/frontend/css/bootstrap.min.css' rel='stylesheet'>"
                "<style>body{display:flex;align-items:center;justify-content:center;min-height:100vh;font-family:system-ui;background:#f8f9fa;margin:0}.box{text-align:center;padding:40px;background:#fff;border-radius:12px}</style>"
                "</head><body><header></header><main><div class='box'><h2 style='color:#28a745'>✓ Данные успешно приняты</h2><p>Проверьте консоль сервера.</p><a href='/'>← На главную</a></div></main><footer></footer></body></html>"
            )
            self._send_response(200, response)

        except Exception as e:
            print(f"[ERROR] Ошибка обработки POST: {e}")
            self._send_response(500, build_500_page())

    def _serve_static_file(self, path: str) -> None:
        """Отдаёт статический файл."""
        file_content: bytes = read_static_file(path)
        content_type: str = get_content_type(path)

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(file_content)))
        self.end_headers()
        self.wfile.write(file_content)

    def _send_response(self, status_code: int, html_content: str) -> None:
        """Отправляет HTTP-ответ."""
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html_content.encode("utf-8"))


def run_server() -> None:
    """Запускает HTTP-сервер."""
    server: HTTPServer = HTTPServer((HOST, PORT), RequestHandler)
    print(f"\n🚀 Сервер запущен: http://{HOST}:{PORT}")
    print("⏹️  Для остановки нажмите Ctrl+C\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен пользователем.")
        server.server_close()

    return None


if __name__ == "__main__":
    run_server()
