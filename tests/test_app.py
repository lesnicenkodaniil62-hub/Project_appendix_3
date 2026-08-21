"""
Юнит-тесты для функций модуля app.py.

Тестирует:
    - read_html() - чтение HTML файлов
    - read_static_file() - чтение статических файлов
    - get_content_type() - определение MIME-типа
    - build_404_page() - генерация страницы 404
    - build_500_page() - генерация страницы 500
"""

from pathlib import Path

import pytest

from src.backend.app import (
    build_404_page,
    build_500_page,
    get_content_type,
    read_html,
    read_static_file,
)


class TestReadHtml:
    """Тесты функции read_html()."""

    def test_read_html_success(self) -> None:
        """Тест успешного чтения HTML файла."""
        content: str = read_html("contact.html")
        assert isinstance(content, str)
        assert len(content) > 0
        assert "Контакты" in content

    def test_read_html_file_not_found(self) -> None:
        """Тест чтения несуществующего файла."""
        with pytest.raises(FileNotFoundError):
            read_html("nonexistent.html")

    def test_read_html_returns_string(self) -> None:
        """Тест типа возвращаемого значения."""
        content: str = read_html("main.html")
        assert isinstance(content, str)

    def test_read_html_contains_doctype(self) -> None:
        """Тест наличия DOCTYPE в файле."""
        content: str = read_html("main.html")
        assert "<!DOCTYPE html>" in content

    def test_read_html_all_pages(self) -> None:
        """Тест чтения всех HTML страниц."""
        pages: list[str] = ["main.html", "catalog.html", "orders.html", "contact.html"]
        for page in pages:
            content: str = read_html(page)
            assert len(content) > 0
            assert "<html" in content


class TestReadStaticFile:
    """Тесты функции read_static_file()."""

    def test_read_static_file_success(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Тест успешного чтения статического файла."""
        # Создаём тестовый файл во временной директории
        test_file: Path = tmp_path / "test.css"
        test_file.write_text("body { color: red; }", encoding="utf-8")

        # Подменяем FRONTEND_STATIC на tmp_path
        import src.backend.app as app_module
        monkeypatch.setattr(app_module, "FRONTEND_STATIC", str(tmp_path))

        # Читаем файл по относительному пути
        content: bytes = read_static_file("test.css")
        assert isinstance(content, bytes)
        assert b"color: red" in content

    def test_read_static_file_with_prefix(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Тест чтения файла с префиксом src/frontend/."""
        # Создаём структуру src/frontend/css/test.css
        css_dir: Path = tmp_path / "src" / "frontend" / "css"
        css_dir.mkdir(parents=True)
        test_file: Path = css_dir / "test.css"
        test_file.write_text("body { color: blue; }", encoding="utf-8")

        # FRONTEND_STATIC = tmp_path/src/frontend
        frontend_static: str = str(tmp_path / "src" / "frontend")
        import src.backend.app as app_module
        monkeypatch.setattr(app_module, "FRONTEND_STATIC", frontend_static)

        # Путь с префиксом src/frontend/
        content: bytes = read_static_file("src/frontend/css/test.css")
        assert b"color: blue" in content

    def test_read_static_file_not_found(self) -> None:
        """Тест чтения несуществующего файла."""
        with pytest.raises(FileNotFoundError):
            read_static_file("nonexistent.css")

    def test_read_static_file_returns_bytes(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Тест типа возвращаемого значения."""
        test_file: Path = tmp_path / "test.js"
        test_file.write_text("console.log('test');", encoding="utf-8")

        import src.backend.app as app_module
        monkeypatch.setattr(app_module, "FRONTEND_STATIC", str(tmp_path))

        content: bytes = read_static_file("test.js")
        assert isinstance(content, bytes)

    def test_read_static_file_security(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Тест защиты от выхода за пределы директории."""
        import src.backend.app as app_module
        monkeypatch.setattr(app_module, "FRONTEND_STATIC", str(tmp_path))

        # Попытка выйти за пределы через ..
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
            ("test.json", "application/json"),
            ("test.png", "image/png"),
            ("test.jpg", "image/jpeg"),
            ("test.gif", "image/gif"),
            ("test.svg", "image/svg+xml"),
            ("test.pdf", "application/pdf"),
            ("test.xml", "text/xml"),  # mimetypes возвращает text/xml
        ],
    )
    def test_get_content_type_known_types(
        self, filepath: str, expected_type: str
    ) -> None:
        """Тест определения MIME-типа для известных расширений."""
        content_type: str = get_content_type(filepath)
        assert content_type == expected_type

    def test_get_content_type_unknown(self) -> None:
        """Тест определения MIME-типа для неизвестного расширения."""
        content_type: str = get_content_type("test.xyz123")
        assert content_type == "application/octet-stream"

    def test_get_content_type_returns_string(self) -> None:
        """Тест типа возвращаемого значения."""
        content_type: str = get_content_type("test.html")
        assert isinstance(content_type, str)


class TestBuild404Page:
    """Тесты функции build_404_page()."""

    def test_build_404_page_returns_string(self) -> None:
        """Тест типа возвращаемого значения."""
        page: str = build_404_page()
        assert isinstance(page, str)

    def test_build_404_page_contains_404(self) -> None:
        """Тест наличия кода 404 в странице."""
        page: str = build_404_page()
        assert "404" in page

    def test_build_404_page_contains_doctype(self) -> None:
        """Тест наличия DOCTYPE."""
        page: str = build_404_page()
        assert "<!DOCTYPE html>" in page

    def test_build_404_page_contains_header(self) -> None:
        """Тест наличия тега header."""
        page: str = build_404_page()
        assert "<header>" in page

    def test_build_404_page_contains_main(self) -> None:
        """Тест наличия тега main."""
        page: str = build_404_page()
        assert "<main>" in page

    def test_build_404_page_contains_footer(self) -> None:
        """Тест наличия тега footer."""
        page: str = build_404_page()
        assert "<footer>" in page

    def test_build_404_page_contains_bootstrap(self) -> None:
        """Тест подключения Bootstrap."""
        page: str = build_404_page()
        assert "bootstrap.min.css" in page


class TestBuild500Page:
    """Тесты функции build_500_page()."""

    def test_build_500_page_returns_string(self) -> None:
        """Тест типа возвращаемого значения."""
        page: str = build_500_page()
        assert isinstance(page, str)

    def test_build_500_page_contains_500(self) -> None:
        """Тест наличия кода 500 в странице."""
        page: str = build_500_page()
        assert "500" in page

    def test_build_500_page_contains_doctype(self) -> None:
        """Тест наличия DOCTYPE."""
        page: str = build_500_page()
        assert "<!DOCTYPE html>" in page

    def test_build_500_page_contains_header(self) -> None:
        """Тест наличия тега header."""
        page: str = build_500_page()
        assert "<header>" in page

    def test_build_500_page_contains_main(self) -> None:
        """Тест наличия тега main."""
        page: str = build_500_page()
        assert "<main>" in page

    def test_build_500_page_contains_footer(self) -> None:
        """Тест наличия тега footer."""
        page: str = build_500_page()
        assert "<footer>" in page

    def test_build_500_page_contains_bootstrap(self) -> None:
        """Тест подключения Bootstrap."""
        page: str = build_500_page()
        assert "bootstrap.min.css" in page
