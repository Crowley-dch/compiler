import sys
import os
from pathlib import Path
from typing import Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.lexer.scanner import Scanner
from src.utils.error_handler import ErrorHandler


class TestRunner:
    def __init__(self, tests_dir: Path):
        self.tests_dir = tests_dir
        self.valid_dir = tests_dir / 'lexer' / 'valid'
        self.invalid_dir = tests_dir / 'lexer' / 'invalid'
        self.expected_dir = tests_dir / 'lexer' / 'expected'

        self.valid_dir.mkdir(parents=True, exist_ok=True)
        self.invalid_dir.mkdir(parents=True, exist_ok=True)
        self.expected_dir.mkdir(parents=True, exist_ok=True)

    def run_test(self, test_file: Path, expected_file: Path) -> Tuple[bool, str]:
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                source = f.read()

            scanner = Scanner(source, ErrorHandler())

            tokens = []
            while True:
                token = scanner.next_token()
                tokens.append(token)
                if token.type.name == 'END_OF_FILE':
                    break

            actual_lines = []
            for token in tokens:
                if token.literal_value is not None:
                    actual_lines.append(
                        f"{token.line}:{token.column} {token.type.name} \"{token.lexeme}\" {token.literal_value}")
                else:
                    actual_lines.append(f"{token.line}:{token.column} {token.type.name} \"{token.lexeme}\"")

            actual_output = '\n'.join(actual_lines)

            if expected_file.exists():
                with open(expected_file, 'r', encoding='utf-8') as f:
                    expected_output = f.read().strip()
            else:
                with open(expected_file, 'w', encoding='utf-8') as f:
                    f.write(actual_output)
                return True, f"Created expected file: {expected_file.name}"

            if actual_output.strip() == expected_output.strip():
                return True, "OK"
            else:
                return False, "FAIL"

        except Exception as e:
            return False, f"ERROR: {str(e)}"

    def run_all_valid_tests(self) -> Tuple[int, int]:
        print("\n=== Running Valid Tests ===\n")

        passed = 0
        total = 0

        for test_file in sorted(self.valid_dir.glob('*.src')):
            total += 1
            expected_file = self.expected_dir / f"{test_file.stem}.txt"

            success, message = self.run_test(test_file, expected_file)

            if success:
                print(f"PASS {test_file.name}: {message}")
                passed += 1
            else:
                print(f"FAIL {test_file.name}: {message}")

        return passed, total

    def run_all_invalid_tests(self) -> Tuple[int, int]:
        print("\n=== Running Invalid Tests ===\n")

        passed = 0
        total = 0

        for test_file in sorted(self.invalid_dir.glob('*.src')):
            total += 1
            expected_file = self.expected_dir / f"{test_file.stem}.txt"

            success, message = self.run_test(test_file, expected_file)

            if success:
                print(f"PASS {test_file.name}: {message}")
                passed += 1
            else:
                print(f"FAIL {test_file.name}: {message}")

        return passed, total

    def create_sample_tests(self):
        valid_tests = {
            'test_identifiers.src': 'x\ncounter1\n_private\ncamelCase\nPascalCase',
            'test_numbers.src': '42\n0\n2147483647\n-2147483648\n3.14\n0.5',
            'test_keywords.src': 'if else while for int float bool return true false void struct fn',
            'test_operators.src': '+ - * / % = == != < <= > >= && || ! += -= *= /= ( ) { } [ ] ; , :',
            'test_comments.src': '// comment\nint x = 42; // comment\n/* multi\nline */',
            'test_mixed.src': 'fn main() {\n    int x = 42;\n    return x;\n}',
            'test_strings.src': '"hello" "world" ""'
        }

        invalid_tests = {
            'test_invalid_char.src': '@invalid',
            'test_unterminated_string.src': '"unterminated\n',
            'test_unterminated_comment.src': '/* unclosed',
            'test_malformed_number.src': '123.456.789\n..42'
        }

        for name, content in valid_tests.items():
            test_file = self.valid_dir / name
            if not test_file.exists():
                with open(test_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Created test: {name}")

        for name, content in invalid_tests.items():
            test_file = self.invalid_dir / name
            if not test_file.exists():
                with open(test_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Created test: {name}")


def main():
    print("MiniCompiler Test Runner")
    print("=" * 50)

    tests_dir = Path(__file__).parent
    runner = TestRunner(tests_dir)

    print("\nChecking test files...")
    runner.create_sample_tests()

    valid_passed, valid_total = runner.run_all_valid_tests()
    invalid_passed, invalid_total = runner.run_all_invalid_tests()

    total_passed = valid_passed + invalid_passed
    total_tests = valid_total + invalid_total

    print("\n" + "=" * 50)
    print("TEST RESULTS:")
    print(f"  Valid tests: {valid_passed}/{valid_total}")
    print(f"  Invalid tests: {invalid_passed}/{invalid_total}")
    print(f"  TOTAL: {total_passed}/{total_tests} passed")
    print("=" * 50)

    if total_tests == 0:
        print("\nNo tests found!")
        return 1
    elif total_passed == total_tests:
        print("\nAll tests passed!")
        return 0
    else:
        print(f"\nFailed {total_tests - total_passed} tests")
        return 1


if __name__ == '__main__':
    sys.exit(main())