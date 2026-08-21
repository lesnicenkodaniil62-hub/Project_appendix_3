"""
Точка входа в веб-приложение.

Запуск:
    python main.py
"""

from typing import NoReturn

from src.backend.app import run_server


def main() -> NoReturn:
    """Запускает веб-приложение."""
    run_server()


if __name__ == "__main__":
    main()
