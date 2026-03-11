# compiler

# MCompiler - Спринт 1: Лексический анализатор

## 📋 Описание проекта
Реализован лексический анализатор, который преобразует исходный код в последовательность токенов с полной информацией о позиции и значениях литералов.

---

## 📁 Структура проекта
```text
compiler-project/
├── src/ # Исходный код
│ ├── lexer/ # Лексический анализатор (Спринт 1)
│ │ ├── scanner.py # Сканер
│ │ ├── token.py # Структура токена
│ │ └── token_types.py # Типы токенов
│ ├── parser/ # Синтаксический анализатор (Спринт 2)
│ │ ├── ast.py # Классы AST
│ │ ├── grammar.txt # Формальная грамматика
│ │ └── parser.py # Парсер
│ ├── utils/ # Вспомогательные модули
│ │ └── error_handler.py # Обработка ошибок
│ └── main.py # Точка входа
├── tests/ # Тесты
│ ├── lexer/ # Тесты лексера
│ │ ├── valid/ # Корректные тесты
│ │ ├── invalid/ # Тесты с ошибками
│ │ └── expected/ # Ожидаемые результаты
│ ├── parser/ # Тесты парсера
│ │ ├── valid/ # Корректные программы
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

## Установка и запуск

### Требования
- Python 3.8 или выше
- pip

### Установка

```bash
# Клонировать репозиторий
git clone <repository-url>
cd compiler-project
```
```bash
# Создать виртуальное окружение
python -m venv .venv
.venv\Scripts\activate  # для Windows
```
```bash
# Установить зависимости
pip install -r requirements.txt
```
```bash
# Установить проект в режиме разработки
pip install -e .
```

## Лексический анализ
```bash
# Запуск лексера
compiler lex --input examples/hello.src
```
```bash
# Или через python -m
python -m src.main lex --input examples/hello.src
```
```bash
# Сохранить токены в файл
compiler lex --input examples/hello.src --output tokens.txt
```
