import sys
import argparse
from pathlib import Path
from lexer.scanner import Scanner
from utils.error_handler import ErrorHandler

def main():
    parser = argparse.ArgumentParser(description='MiniCompiler - Lexical Analyzer')
    parser.add_argument('--input', '-i', type=str, required=True, help='Input source file')
    parser.add_argument('--output', '-o', type=str, help='Output token file')

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File '{args.input}' not found")
        sys.exit(1)

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            source = f.read()

        error_handler = ErrorHandler()
        scanner = Scanner(source, error_handler)

        tokens = scanner.tokenize_all()

        if error_handler.has_errors():
            error_handler.print_all()
            sys.exit(1)

        output_lines = [str(token) for token in tokens]
        output = '\n'.join(output_lines)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Tokens saved to {args.output}")
        else:
            print(output)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()