"""Фикстуры для тестирования."""
import os
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def sample_form_data() -> dict[str, str]:
    return {"name": "Иван", "email": "ivan@example.com", "message": "Привет"}


@pytest.fixture
def temp_html_file(tmp_path: Path) -> Path:
    file_path: Path = tmp_path / "test.html"
    file_path.write_text("<html><body>Тест</body></html>", encoding="utf-8")
    return file_path


@pytest.fixture
def temp_static_file(tmp_path: Path) -> Path:
    file_path: Path = tmp_path / "test.css"
    file_path.write_text("body { color: red; }", encoding="utf-8")
    return file_path
