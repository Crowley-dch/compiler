import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.lexer.scanner import Scanner
from src.parser.parser import Parser
from src.semantic.analyzer import SemanticAnalyzer
from src.utils.error_handler import ErrorHandler

tests_dir = Path("tests/semantic/invalid")

# Список тестов, для которых нужно создать expected
test_files = [
    "argument_errors\\test_argument_count.src",
    "declaration_errors\\test_duplicate_function.src",
    "declaration_errors\\test_duplicate_var.src",
    "return_errors\\test_missing_return.src",
    "scope_errors\\test_out_of_scope.src",
    "scope_errors\\test_undeclared_variable.src",
    "type_errors\\test_binary_op_mismatch.src",
    "type_errors\\test_condition_not_bool.src",
]

for test_rel in test_files:
    test_file = tests_dir / test_rel
    print(f"\nProcessing: {test_file}")

    if not test_file.exists():
        print(f"  File not found, skipping")
        continue

    with open(test_file, 'r', encoding='utf-8') as f:
        source = f.read()

    error_handler = ErrorHandler()
    scanner = Scanner(source, error_handler)
    tokens = scanner.tokenize_all()

    if error_handler.has_errors():
        print(f"  Lexical errors, skipping")
        continue

    parser = Parser(tokens, error_handler)
    ast = parser.parse()

    if error_handler.has_errors():
        print(f"  Syntax errors, skipping")
        continue

    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)

    if analyzer.get_errors().has_errors():
        output = "\n".join(str(e) for e in analyzer.get_errors().errors)

        expected_file = Path("tests/semantic/expected/invalid") / test_rel.replace('.src', '.txt')
        expected_file.parent.mkdir(parents=True, exist_ok=True)

        with open(expected_file, 'w', encoding='utf-8') as f:
            f.write(output)

        print(f"  Created expected: {expected_file}")
    else:
        print(f"  No errors found, skipping")

print("\nDone! Now run tests again.")