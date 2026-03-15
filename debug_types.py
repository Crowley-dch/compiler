import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.lexer.token_types import TokenType
from src.lexer.scanner import Scanner
from src.utils.error_handler import ErrorHandler

# Проверим значение KW_FN
print(f"TokenType.KW_FN = {TokenType.KW_FN}")
print(f"TokenType.KW_FN name = {TokenType.KW_FN.name}")
print(f"TokenType.KW_FN value = {TokenType.KW_FN.value}")

# Проверим маппинг ключевых слов
from src.lexer.token_types import KEYWORDS_MAP
print(f"\nKEYWORDS_MAP['fn'] = {KEYWORDS_MAP.get('fn')}")

# Просканируем файл и посмотрим типы
with open('examples/hello.src', 'r', encoding='utf-8') as f:
    source = f.read()

scanner = Scanner(source, ErrorHandler())
tokens = scanner.tokenize_all()

print(f"\nТип первого токена: {tokens[0].type}")
print(f"Сравнение: tokens[0].type == TokenType.KW_FN? {tokens[0].type == TokenType.KW_FN}")