#!/bin/bash
# Скрипты для работы с Ruff линтером

# Проверка кода (без исправлений)
echo "=== Проверка кода с Ruff ==="
poetry run ruff check .

# Проверка форматирования
echo ""
echo "=== Проверка форматирования ==="
poetry run ruff format --check .

# Автоматическое исправление проблем
echo ""
echo "=== Автоматическое исправление ==="
poetry run ruff check --fix .

# Форматирование кода
echo ""
echo "=== Форматирование кода ==="
poetry run ruff format .

echo ""
echo "✅ Готово!"

