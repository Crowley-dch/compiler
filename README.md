# compiler

# MCompiler - Спринт 1: Лексический анализатор

## 📋 Описание проекта
Реализован лексический анализатор, который преобразует исходный код в последовательность токенов с полной информацией о позиции и значениях литералов.

---

## 📁 Структура проекта
```text
compiler
├── src/ # Исходный код
│ ├── lexer/ # Лексический анализатор (Спринт 1)
│ │ ├── scanner.py # Сканер
│ │ ├── token.py # Структура токена
│ │ └── token_types.py # Типы токенов (Enum)
│ ├── parser/ # Синтаксический анализатор (Спринт 2)
│ │ ├── ast.py # Классы AST
│ │ ├── grammar.txt # Формальная грамматика (краткая)
│ │ └── parser.py # Парсер методом рекурсивного спуска
│ ├── utils/ # Вспомогательные модули
│ │ └── error_handler.py # Обработка ошибок
│ └── main.py # Точка входа (CLI)
├── tests/ # Тесты
│ ├── lexer/ # Тесты лексера
│ │ ├── valid/ # Корректные тесты
│ │ ├── invalid/ # Тесты с ошибками
│ │ └── expected/ # Ожидаемые результаты
│ ├── parser/ # Тесты парсера
│ │ ├── valid/ # Корректные тесты
│ │ │ ├── expressions/ # Тесты выражений
│ │ │ ├── statements/ # Тесты инструкций
│ │ │ ├── declarations/ # Тесты объявлений
│ │ │ └── full_programs/ # Полные программы
│ │ ├── invalid/ # Синтаксические ошибки
│ │ │ └── syntax_errors/ # Тесты ошибок
│ │ ├── expected/ # Ожидаемые AST
│ │ └── test_runner.py # Раннер тестов парсера
│ └── test_runner.py # Общий раннер тестов
├── examples/ # Примеры программ
├── docs/ # Документация
│ └── grammar.md # Формальная грамматика 
├── README.md
├── pyproject.toml
├── setup.py
└── requirements.txt

```
---
##  Установка и запуск

### Требования
- Python 3.8 или выше
- pip (менеджер пакетов Python)

### Установка

```bash
# Клонировать репозиторий
git clone <repository-url>
cd compiler-project
```
```bash
# Создать виртуальное окружение (рекомендуется)
python -m venv .venv
```
```bash
# Активировать виртуальное окружение
# Для Windows:
.venv\Scripts\activate
# Для Linux/Mac:
source .venv/bin/activate
```
```bash
# Установить зависимости для разработки
pip install -r requirements.txt
```
```bash
# Установить проект в режиме разработки
pip install -e .
```

### Использование
## Лексический анализ (токенизация)
```bash
# Запуск лексера
compiler lex --input examples/hello.src

# Сохранить токены в файл
compiler lex --input examples/hello.src --output tokens.txt

# Подробный вывод с предупреждениями
compiler lex --input examples/hello.src --verbose
```

## Синтаксический анализ
```bash
# Текстовый вывод AST (по умолчанию)
compiler parse --input examples/hello.src

# Сохранить AST в файл
compiler parse --input examples/hello.src --output ast.txt

# Визуализация в формате DOT (для Graphviz)
compiler parse --input examples/factorial.src --format dot --output ast.dot
dot -Tpng ast.dot -o ast.png  # требует установки Graphviz

# JSON вывод для машинной обработки
compiler parse --input examples/hello.src --format json

# Подробный вывод с отладкой
compiler parse --input examples/hello.src --verbose
``` 

## Семантический анализ 
```bash
# Семантическая проверка программы
compiler check --input examples/hello.src

# Вывод таблицы символов
compiler check --input examples/hello.src --dump-symbols

# Вывод AST с типами
compiler check --input examples/hello.src --show-types
```

## Тестирование 

```bash

# Запустить  тесты лексера
python tests/lexer/test_runner.py

# Запустить тесты парсера
python tests/parser/test_runner.py

# Запуск через pytest
pytest tests/

```