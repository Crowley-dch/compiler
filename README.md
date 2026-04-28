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
│ ├── semantic/ # Семантический анализатор (Спринт 3)
│ │ ├── analyzer.py # Семантический анализатор
│ │ ├── symbol_table.py # Таблица символов
│ │ ├── type_system.py # Система типов
│ │ └── errors.py # Семантические ошибки
│ ├── ir/ # Генерация IR (Спринт 4)
│ │ ├── ir_generator.py # Генератор IR
│ │ ├── ir_instructions.py # Инструкции IR
│ │ ├── basic_block.py # Базовые блоки
│ │ └── control_flow.py # Control Flow Graph
│ ├── codegen/ # Генерация кода (Спринт 5)
│ │ ├── x86_generator.py # Генератор x86-64
│ │ └── stack_frame.py # Управление стеком
│ ├── runtime/ # Рантайм библиотека
│ │ └── runtime.asm
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
## Генерация IR (промежуточного кода)

```bash
# Генерация IR в текстовом формате
compiler ir --input examples/arithmetic.src

# Сохранить IR в файл
compiler ir --input examples/factorial.src --output factorial.ir

# Визуализация Control Flow Graph
compiler ir --input examples/if.src --format dot --output cfg.dot
dot -Tpng cfg.dot -o cfg.png

# Статистика IR
compiler ir --input examples/factorial.src --stats
```

## Генерация ассемблерного кода
```bash
compiler compile --input examples/simple_return.src --output output.asm

nasm -f win64 output.asm -o output.obj
gcc -m64 -mconsole -no-pie -o output.exe output.obj
output.exe
echo %errorlevel%
```

## Тестирование 

```bash

# Запустить  тесты лексера
python tests/lexer/test_runner.py

# Запустить тесты лексера
python tests/lexer/test_runner.py

# Запустить тесты парсера
python tests/parser/test_runner.py

# Запустить тесты семантического анализатора
python tests/semantic/test_runner.py

# Запустить тесты генерации IR
python tests/ir/test_runner.py

# Запустить тесты генерации кода
python tests/codegen/test_runner.py

# Запуск всех тестов через pytest
pytest tests/

```