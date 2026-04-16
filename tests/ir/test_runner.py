import sys
from pathlib import Path
from typing import Tuple

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.lexer.scanner import Scanner
from src.parser.parser import Parser
from src.semantic.analyzer import SemanticAnalyzer
from src.utils.error_handler import ErrorHandler
from src.ir.ir_generator import IRGenerator


class IRTestRunner:
    def __init__(self, tests_dir: Path):
        self.tests_dir = tests_dir
        self.generation_dir = tests_dir / 'ir' / 'generation'
        self.expected_dir = tests_dir / 'ir' / 'expected'

    def run_test(self, test_file: Path, expected_file: Path) -> Tuple[bool, str]:
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

            if analyzer.get_errors().has_errors():
                return False, f"Semantic errors: {analyzer.get_errors().errors}"

            ir_gen = IRGenerator(analyzer.get_symbol_table())
            functions = ir_gen.generate(ast)

            output = []
            for name, cfg in functions.items():
                output.append(f"function {name}:")
                for block in cfg.blocks:
                    output.append(f"  {block.name}:")
                    for inst in block.instructions:
                        output.append(f"    {inst}")
                output.append("")

            actual_output = "\n".join(output).strip()

            if expected_file.exists():
                with open(expected_file, 'r', encoding='utf-8') as f:
                    expected_output = f.read().strip()
                if actual_output == expected_output:
                    return True, "OK"
                else:
                    return False, f"Output mismatch"
            else:
                expected_file.parent.mkdir(parents=True, exist_ok=True)
                with open(expected_file, 'w', encoding='utf-8') as f:
                    f.write(actual_output)
                return True, f"Created expected: {expected_file.name}"

        except Exception as e:
            return False, f"ERROR: {str(e)}"

    def run_all_tests(self) -> Tuple[int, int]:
        passed, total = 0, 0

        print("\n=== Running IR Generation Tests ===\n")

        for category in ['expressions', 'control_flow', 'functions', 'integration']:
            test_dir = self.generation_dir / category
            if not test_dir.exists():
                continue

            print(f"--- {category.upper()} ---")
            for test_file in sorted(test_dir.glob('*.src')):
                total += 1
                expected = self.expected_dir / category / f"{test_file.stem}.txt"
                success, msg = self.run_test(test_file, expected)
                if success:
                    print(f"   {test_file.name}: {msg}")
                    passed += 1
                else:
                    print(f"   {test_file.name}: {msg}")

        return passed, total


def main():
    print("IR Generator Test Runner")
    print("=" * 60)

    tests_dir = Path(__file__).parent.parent
    runner = IRTestRunner(tests_dir)

    passed, total = runner.run_all_tests()

    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} passed")
    print("=" * 60)

    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())
