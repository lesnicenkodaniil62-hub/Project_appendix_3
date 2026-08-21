"""
Точка входа в веб-приложение.

Запуск:
    python main.py
"""

from src.backend.app import run_server


def main() -> None:
    """Запускает веб-приложение."""
    run_server()
    return None


if __name__ == "__main__":
    main()
