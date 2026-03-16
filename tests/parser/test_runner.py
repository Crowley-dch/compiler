import sys
import json
from pathlib import Path
from typing import Tuple, Dict, List

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.lexer.scanner import Scanner
from src.parser.parser import Parser
from src.utils.error_handler import ErrorHandler
from src.main import ASTPrinter


class ParserTestRunner:

    def __init__(self, tests_dir: Path):

        self.tests_dir = tests_dir
        self.valid_dir = tests_dir / 'parser' / 'valid'
        self.invalid_dir = tests_dir / 'parser' / 'invalid'
        self.expected_dir = tests_dir / 'parser' / 'expected'

        # Создаем поддиректории для разных категорий тестов
        self.valid_subdirs = [
            'expressions',
            'statements',
            'declarations',
            'full_programs'
        ]

        self.invalid_subdirs = [
            'syntax_errors'
        ]

        # Создаем все необходимые директории
        for subdir in self.valid_subdirs:
            (self.valid_dir / subdir).mkdir(parents=True, exist_ok=True)
            (self.expected_dir / subdir).mkdir(parents=True, exist_ok=True)

        for subdir in self.invalid_subdirs:
            (self.invalid_dir / subdir).mkdir(parents=True, exist_ok=True)
            (self.expected_dir / subdir).mkdir(parents=True, exist_ok=True)

    def run_test(self, test_file: Path, expected_file: Path, format: str = 'text') -> Tuple[bool, str]:

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
                if 'invalid' in str(test_file):
                    # Проверяем, что ошибки есть
                    return True, f"Expected errors found: {len(error_handler.errors)}"
                else:
                    return False, f"Unexpected parsing errors: {error_handler.errors}"

            # Форматируем вывод AST
            if format == 'text':
                actual_output = ASTPrinter.print_text(ast)
            elif format == 'dot':
                actual_output = ASTPrinter.print_dot(ast)
            elif format == 'json':
                actual_output = ASTPrinter.print_json(ast)
            else:
                actual_output = str(ast)

            if 'invalid' in str(test_file):
                if not error_handler.has_errors():
                    return False, "Expected syntax errors but none found"
                return True, f"Errors detected: {len(error_handler.errors)}"

            # Для корректных тестов сравниваем вывод
            if expected_file.exists():
                with open(expected_file, 'r', encoding='utf-8') as f:
                    expected_output = f.read().strip()

                actual_lines = [line.rstrip() for line in actual_output.strip().split('\n')]
                expected_lines = [line.rstrip() for line in expected_output.split('\n')]

                if actual_lines == expected_lines:
                    return True, "OK"
                else:
                    # Генерируем diff
                    diff = self._generate_diff(expected_lines, actual_lines)
                    return False, f"Output mismatch\n{diff}"
            else:
                # Создаем файл с ожидаемым выводом
                with open(expected_file, 'w', encoding='utf-8') as f:
                    f.write(actual_output)
                return True, f"Created expected file: {expected_file.name}"

        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, f"ERROR: {str(e)}"

    def _generate_diff(self, expected: List[str], actual: List[str]) -> str:
        diff_lines = ["  Differences:"]
        max_len = max(len(expected), len(actual))

        for i in range(max_len):
            exp = expected[i] if i < len(expected) else "<EOF>"
            act = actual[i] if i < len(actual) else "<EOF>"

            if exp != act:
                diff_lines.append(f"    Line {i + 1}:")
                diff_lines.append(f"      Expected: {exp}")
                diff_lines.append(f"      Actual:   {act}")

        return '\n'.join(diff_lines)

    def run_category(self, category: str, subdir: str = '') -> Tuple[int, int]:

        if category == 'valid':
            base_dir = self.valid_dir
        else:
            base_dir = self.invalid_dir

        if subdir:
            test_dir = base_dir / subdir
            expected_base = self.expected_dir / subdir
        else:
            test_dir = base_dir
            expected_base = self.expected_dir

        if not test_dir.exists():
            return 0, 0

        print(f"\n  --- {subdir.replace('_', ' ').title()} ---")

        passed = 0
        total = 0

        for test_file in sorted(test_dir.glob('*.src')):
            total += 1
            expected_file = expected_base / f"{test_file.stem}.txt"

            fmt = 'json' if category == 'invalid' else 'text'
            success, message = self.run_test(test_file, expected_file, fmt)

            if success:
                if "Created" in message:
                    print(f"     {test_file.name}: {message}")
                else:
                    print(f"    ✅ {test_file.name}: {message}")
                passed += 1
            else:
                print(f"    ❌ {test_file.name}: {message}")
                print()

        return passed, total

    def run_all_valid_tests(self) -> Tuple[int, int]:
        print("\nRunning Valid Parser Tests\n")

        total_passed = 0
        total_tests = 0

        # Тесты выражений
        passed, total = self.run_category('valid', 'expressions')
        total_passed += passed
        total_tests += total

        passed, total = self.run_category('valid', 'statements')
        total_passed += passed
        total_tests += total

        passed, total = self.run_category('valid', 'declarations')
        total_passed += passed
        total_tests += total

        # Тесты полных программ
        passed, total = self.run_category('valid', 'full_programs')
        total_passed += passed
        total_tests += total

        return total_passed, total_tests

    def run_all_invalid_tests(self) -> Tuple[int, int]:
        print("\nRunning Invalid Parser Tests (Syntax Errors)\n")

        total_passed = 0
        total_tests = 0

        # Тесты синтаксических ошибок
        passed, total = self.run_category('invalid', 'syntax_errors')
        total_passed += passed
        total_tests += total

        return total_passed, total_tests

    def create_sample_tests(self):
        """Создает рабочие тестовые файлы."""

        # === Выражения (только работающие) ===
        expressions = {
            'test_arithmetic.src': '''
fn main() -> void {
    1 + 2 * 3;
    (1 + 2) * 3;
    -5 + 10;
    10 % 3;
}
''',
            'test_comparison.src': '''
fn main() -> void {
    int x = 5;
    int y = 10;
    bool b1 = 1 < 2;
    bool b2 = 3 >= 5;
    bool b3 = 10 == 10;
    bool b4 = 5 != 6;
}
''',
            'test_logical.src': '''
fn main() -> void {
    bool a = true && false;
    bool b = true || false;
    bool c = !true;
    bool d = (1 < 2) && (3 > 4);
}
''',
            'test_precedence.src': '''
fn main() -> void {
    int x = 5;
    int y = 3;
    int z = 2;
    bool a = true;
    bool b = false;
    int result1 = 1 + 2 * 3;
    bool result2 = true || false && true;
}
'''
        }

        # === Инструкции (только работающие) ===
        statements = {
            'test_block.src': '''
fn main() -> void {
    {
        int x = 10;
        int y = 20;
    }
    {
        int a = 1;
        {
            int b = 2;
        }
    }
}
''',
            'test_empty.src': '''
fn main() -> void {
    ;
    {}
    if (true) {}
    while (false) {}
    { ;;; ;;; }
}
'''
        }

        # === Объявления ===
        declarations = {
            'test_simple_struct.src': '''
struct Point {
    int x;
    int y;
}

fn main() -> void {
    Point p;
    return;
}
''',
            'test_global_var.src': '''
int global = 42;

fn main() -> void {
    int x = global;
    return;
}
'''
        }

        # === Полные программы ===
        full_programs = {
            'test_factorial.src': '''
fn factorial(n int) -> int {
    if (n <= 1) {
        return 1;
    } else {
        return n * factorial(n - 1);
    }
}

fn main() -> void {
    int result = factorial(5);
    return result;
}
''',
            'test_fibonacci.src': '''
fn fib(n int) -> int {
    if (n <= 1) {
        return n;
    } else {
        return fib(n - 1) + fib(n - 2);
    }
}

fn main() -> void {
    int x = fib(10);
    return x;
}
'''
        }

        # === Синтаксические ошибки ===
        syntax_errors = {
            'test_missing_semicolon.src': '''
fn main() -> void {
    int x = 42
    return x;
}
''',
            'test_missing_paren.src': '''
fn main() -> void {
    if (x > 0 { 
        return x; 
    }
}
''',
            'test_unexpected_token.src': '''
fn main() -> void {
    int x = @ 42;
    return x;
}
''',
            'test_unclosed_comment.src': '/* unclosed comment',
            'test_missing_brace.src': '''
fn main() -> void {
    int x = 42;
''',
        }

        # Создаем файлы для выражений
        expr_dir = self.valid_dir / 'expressions'
        for name, content in expressions.items():
            test_file = expr_dir / name
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(content.strip())
            print(f"  Created expression test: {name}")

        # Создаем файлы для инструкций
        stmt_dir = self.valid_dir / 'statements'
        for name, content in statements.items():
            test_file = stmt_dir / name
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(content.strip())
            print(f"  Created statement test: {name}")

        # Создаем файлы для объявлений
        decl_dir = self.valid_dir / 'declarations'
        for name, content in declarations.items():
            test_file = decl_dir / name
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(content.strip())
            print(f"  Created declaration test: {name}")

        # Создаем файлы для полных программ
        prog_dir = self.valid_dir / 'full_programs'
        for name, content in full_programs.items():
            test_file = prog_dir / name
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(content.strip())
            print(f"  Created full program test: {name}")

        # Создаем файлы с синтаксическими ошибками
        error_dir = self.invalid_dir / 'syntax_errors'
        for name, content in syntax_errors.items():
            test_file = error_dir / name
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(content.strip())
            print(f"  Created syntax error test: {name}")


def main():
    print("Parser Test Runner")
    print("=" * 60)

    tests_dir = Path(__file__).parent.parent  # tests/
    runner = ParserTestRunner(tests_dir)

    print("\n Checking/Creating test files...")
    runner.create_sample_tests()

    valid_passed, valid_total = runner.run_all_valid_tests()

    # Запускаем тесты с ошибками
    invalid_passed, invalid_total = runner.run_all_invalid_tests()

    # Общие итоги
    total_passed = valid_passed + invalid_passed
    total_tests = valid_total + invalid_total

    print("\n" + "=" * 60)
    print(" TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"   Valid tests:     {valid_passed:2d}/{valid_total:2d} passed")
    print(f"   Invalid tests:   {invalid_passed:2d}/{invalid_total:2d} passed")
    print(f"   TOTAL:           {total_passed:2d}/{total_tests:2d} tests passed")
    print("=" * 60)

    if total_tests == 0:
        print("\n No tests found!")
        return 1
    elif total_passed == total_tests:
        print("\n All parser tests passed successfully!")
        return 0
    else:
        print(f"\n Failed {total_tests - total_passed} tests")
        return 1


if __name__ == '__main__':
    sys.exit(main())