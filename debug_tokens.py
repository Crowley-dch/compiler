import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))

from src.lexer.scanner import Scanner
from src.utils.error_handler import ErrorHandler

# Используем правильный путь
file_path = Path(__file__).parent / 'examples' / 'hello.src'
print(f"Reading file: {file_path}")

with open(file_path, 'r', encoding='utf-8') as f:
    source = f.read()

scanner = Scanner(source, ErrorHandler())
tokens = scanner.tokenize_all()

print("\nTokens from lexer:")
print("-" * 50)
for token in tokens:
    print(f"{token.line}:{token.column} {token.type.name:15} '{token.lexeme}'")
print("-" * 50)