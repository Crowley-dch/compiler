import sys
sys.path.insert(0, 'src')
from lexer.scanner import Scanner
from parser.parser import Parser
from semantic.analyzer import SemanticAnalyzer
from utils.error_handler import ErrorHandler

with open('tests/semantic/invalid/scope_errors/test_parameter_scope.src') as f:
    source = f.read()

print('=== ИСХОДНЫЙ КОД ===')
print(source)
print()

error_handler = ErrorHandler()
scanner = Scanner(source, error_handler)
tokens = scanner.tokenize_all()

print('=== ТОКЕНЫ ===')
for t in tokens:
    print(f'  {t.type.name:15} {t.lexeme:10} {t.literal_value}')
print()

parser = Parser(tokens, error_handler)
ast = parser.parse()

print('=== СЕМАНТИЧЕСКИЙ АНАЛИЗ ===')
analyzer = SemanticAnalyzer()
analyzer.analyze(ast)

print()
print(f'Найдено ошибок: {len(analyzer.get_errors().errors)}')
for e in analyzer.get_errors().errors:
    print(e)