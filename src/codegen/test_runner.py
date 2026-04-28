import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.lexer.scanner import Scanner
from src.parser.parser import Parser
from src.semantic.analyzer import SemanticAnalyzer
from src.ir.ir_generator import IRGenerator
from src.codegen.x86_generator import X86Generator
from src.utils.error_handler import ErrorHandler


class CodegenTestRunner:
    def __init__(self, tests_dir: Path):
        self.tests_dir = tests_dir
        self.valid_dir = tests_dir / 'codegen' / 'valid'
        self.nasm_path = "C:\\Users\\dimad\\nasm-3.02rc7-win64\\nasm-3.02rc7\\nasm.exe"

    def compile_and_run(self, source: str) -> tuple:
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

        asm_gen = X86Generator()
        asm = asm_gen.generate(functions)

        return True, asm

    def assemble_and_run(self, asm: str, test_file: Path) -> tuple:
        asm_file = test_file.with_suffix('.asm')
        obj_file = test_file.with_suffix('.obj')
        exe_file = test_file.with_suffix('.exe')

        with open(asm_file, 'w') as f:
            f.write(asm)

        result = subprocess.run([self.nasm_path, '-f', 'win64', str(asm_file), '-o', str(obj_file)],
                                capture_output=True)
        if result.returncode != 0:
            return False, f"NASM failed: {result.stderr.decode()}"

        result = subprocess.run(['gcc', '-o', str(exe_file), str(obj_file)], capture_output=True)
        if result.returncode != 0:
            return False, f"GCC failed: {result.stderr.decode()}"

        result = subprocess.run([str(exe_file)], capture_output=True)
        return True, result.returncode

    def run_test(self, test_file: Path) -> tuple:
        try:
            with open(test_file, 'r') as f:
                source = f.read()

            success, result = self.compile_and_run(source)
            if not success:
                return False, result

            success, result = self.assemble_and_run(result, test_file)
            if not success:
                return False, result

            return True, result

        except Exception as e:
            return False, str(e)

    def run_all_tests(self):
        passed, total = 0, 0
        print("\n=== Code Generation Tests ===\n")

        for test_file in sorted(self.valid_dir.glob('*.src')):
            total += 1
            success, result = self.run_test(test_file)

            if success:
                print(f"   {test_file.name}: returned {result}")
                passed += 1
            else:
                print(f"   {test_file.name}: {result}")

        return passed, total


def main():
    print("Code Generator Test Runner")

    tests_dir = Path(__file__).parent.parent
    runner = CodegenTestRunner(tests_dir)

    passed, total = runner.run_all_tests()

    print(f"TEST RESULTS: {passed}/{total} passed")


if __name__ == '__main__':
    sys.exit(main())