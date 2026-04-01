#!/usr/bin/env python3
import sys
from pathlib import Path
from typing import Tuple

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.lexer.scanner import Scanner
from src.parser.parser import Parser
from src.semantic.analyzer import SemanticAnalyzer
from src.utils.error_handler import ErrorHandler


class SemanticTestRunner:
    def __init__(self, tests_dir: Path):
        self.tests_dir = tests_dir
        self.valid_dir = tests_dir / 'semantic' / 'valid'
        self.invalid_dir = tests_dir / 'semantic' / 'invalid'

    def run_test(self, test_file: Path) -> Tuple[bool, str]:
        print(f"[TEST] Running: {test_file}")  # Добавить эту строку
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                source = f.read()

            error_handler = ErrorHandler()
            scanner = Scanner(source, error_handler)
            tokens = scanner.tokenize_all()

            if error_handler.has_errors():
                return False, f"Lexical errors: {error_handler.errors}"

            parser = Parser(tokens, error_handler)
            ast = parser.parse()

            if error_handler.has_errors():
                return False, f"Syntax errors: {error_handler.errors}"

            analyzer = SemanticAnalyzer()
            analyzer.analyze(ast)

            # Определяем тип теста по расположению файла
            is_valid = self.valid_dir in test_file.parents

            has_errors = analyzer.get_errors().has_errors()
            error_count = len(analyzer.get_errors().errors)

            if is_valid:
                if has_errors:
                    errors = [str(e) for e in analyzer.get_errors().errors]
                    return False, f"Unexpected errors: {errors}"
                else:
                    return True, "OK"
            else:
                if has_errors:
                    return True, f"Found {error_count} errors (expected)"
                else:
                    return False, "Expected errors but none found"

        except Exception as e:
            return False, f"ERROR: {str(e)}"

    def run_all_tests(self) -> Tuple[int, int]:
        passed, total = 0, 0

        print("\n=== Running Semantic Tests ===\n")

        # Valid tests
        print("--- VALID TESTS ---")
        for test_file in sorted(self.valid_dir.rglob('*.src')):
            total += 1
            rel_path = test_file.relative_to(self.valid_dir)
            success, msg = self.run_test(test_file)
            if success:
                print(f"  ✅ {rel_path}: {msg}")
                passed += 1
            else:
                print(f"  ❌ {rel_path}: {msg}")

        # Invalid tests
        print("\n--- INVALID TESTS ---")
        for test_file in sorted(self.invalid_dir.rglob('*.src')):
            total += 1
            rel_path = test_file.relative_to(self.invalid_dir)
            success, msg = self.run_test(test_file)
            if success:
                print(f"  ✅ {rel_path}: {msg}")
                passed += 1
            else:
                print(f"  ❌ {rel_path}: {msg}")

        return passed, total


def main():
    print("Semantic Analyzer Test Runner")
    print("=" * 60)

    tests_dir = Path(__file__).parent.parent
    runner = SemanticTestRunner(tests_dir)

    passed, total = runner.run_all_tests()

    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} passed")
    print("=" * 60)

    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())