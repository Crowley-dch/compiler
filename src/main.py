import sys
import argparse
import json
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).parent))

from lexer.scanner import Scanner
from lexer.token import Token
from utils.error_handler import ErrorHandler
from parser.parser import Parser
from parser import (
    ASTNode, ProgramNode, DebugVisitor,
    ExpressionNode,
    FunctionDeclNode, StructDeclNode, VarDeclStmtNode,
    ParamNode, TypeNode, BlockStmtNode, IfStmtNode,
    WhileStmtNode, ForStmtNode, ReturnStmtNode, ExprStmtNode,
    BinaryExprNode, UnaryExprNode, LiteralExprNode,
    IdentifierExprNode, CallExprNode, AssignmentExprNode
)
from semantic.analyzer import SemanticAnalyzer


class ASTPrinter:

    @staticmethod
    def print_text(node: ASTNode, indent: int = 0) -> str:
        if node is None:
            return ""

        indent_str = "  " * indent
        result = []

        node_type = node.__class__.__name__

        if node_type == 'ProgramNode':
            result.append(f"Program [line {node.line}]:")
            for decl in node.declarations:
                result.append(ASTPrinter.print_text(decl, indent + 1))

        elif node_type == 'FunctionDeclNode':
            params = ", ".join(str(p) for p in node.parameters)
            result.append(f"{indent_str}FunctionDecl: {node.name}({params}) -> {node.return_type} [line {node.line}]:")
            result.append(ASTPrinter.print_text(node.body, indent + 1))

        elif node_type == 'StructDeclNode':
            result.append(f"{indent_str}StructDecl: {node.name} [line {node.line}]:")
            for field in node.fields:
                result.append(ASTPrinter.print_text(field, indent + 1))

        elif node_type == 'BlockStmtNode':
            result.append(f"{indent_str}Block [line {node.line}]:")
            for stmt in node.statements:
                result.append(ASTPrinter.print_text(stmt, indent + 1))

        elif node_type == 'IfStmtNode':
            result.append(f"{indent_str}IfStmt [line {node.line}]:")
            result.append(f"{indent_str}  Condition:")
            result.append(ASTPrinter.print_text(node.condition, indent + 2))
            result.append(f"{indent_str}  Then:")
            result.append(ASTPrinter.print_text(node.then_branch, indent + 2))
            if node.else_branch:
                result.append(f"{indent_str}  Else:")
                result.append(ASTPrinter.print_text(node.else_branch, indent + 2))

        elif node_type == 'WhileStmtNode':
            result.append(f"{indent_str}WhileStmt [line {node.line}]:")
            result.append(f"{indent_str}  Condition:")
            result.append(ASTPrinter.print_text(node.condition, indent + 2))
            result.append(f"{indent_str}  Body:")
            result.append(ASTPrinter.print_text(node.body, indent + 2))

        elif node_type == 'ForStmtNode':
            result.append(f"{indent_str}ForStmt [line {node.line}]:")
            if node.init:
                result.append(f"{indent_str}  Init:")
                result.append(ASTPrinter.print_text(node.init, indent + 2))
            if node.condition:
                result.append(f"{indent_str}  Condition:")
                result.append(ASTPrinter.print_text(node.condition, indent + 2))
            if node.update:
                result.append(f"{indent_str}  Update:")
                result.append(ASTPrinter.print_text(node.update, indent + 2))
            result.append(f"{indent_str}  Body:")
            result.append(ASTPrinter.print_text(node.body, indent + 2))

        elif node_type == 'ReturnStmtNode':
            if node.value:
                result.append(f"{indent_str}Return: {ASTPrinter._expr_to_str(node.value)} [line {node.line}]")
            else:
                result.append(f"{indent_str}Return [line {node.line}]")

        elif node_type == 'ExprStmtNode':
            expr_str = ASTPrinter._expr_to_str(node.expression)
            result.append(f"{indent_str}{expr_str};")

        elif node_type == 'VarDeclStmtNode':
            if node.initializer:
                init_str = ASTPrinter._expr_to_str(node.initializer)
                result.append(f"{indent_str}VarDecl: {node.var_type} {node.name} = {init_str} [line {node.line}]")
            else:
                result.append(f"{indent_str}VarDecl: {node.var_type} {node.name} [line {node.line}]")

        elif node_type == 'ParamNode':
            result.append(f"{indent_str}Param: {node.param_type} {node.name} [line {node.line}]")

        elif node_type == 'BinaryExprNode':
            left = ASTPrinter._expr_to_str(node.left)
            right = ASTPrinter._expr_to_str(node.right)
            result.append(f"{indent_str}{left} {node.operator} {right}")

        elif node_type == 'UnaryExprNode':
            operand = ASTPrinter._expr_to_str(node.operand)
            result.append(f"{indent_str}{node.operator}{operand}")

        elif node_type == 'LiteralExprNode':
            if isinstance(node.value, str):
                result.append(f'{indent_str}"{node.value}"')
            else:
                result.append(f"{indent_str}{node.value}")

        elif node_type == 'IdentifierExprNode':
            result.append(f"{indent_str}{node.name}")

        elif node_type == 'CallExprNode':
            args = ", ".join(ASTPrinter._expr_to_str(arg) for arg in node.arguments)
            callee = ASTPrinter._expr_to_str(node.callee)
            result.append(f"{indent_str}{callee}({args})")

        elif node_type == 'AssignmentExprNode':
            target = ASTPrinter._expr_to_str(node.target)
            value = ASTPrinter._expr_to_str(node.value)
            result.append(f"{indent_str}{target} {node.operator} {value}")

        elif node_type == 'TypeNode':
            result.append(f"{indent_str}{node.name}")

        else:
            node_str = str(node).split("\n")
            for i, line in enumerate(node_str):
                if i == 0:
                    result.append(f"{indent_str}{line}")
                else:
                    result.append(f"{indent_str}{line}")

        return "\n".join(result)

    @staticmethod
    def _expr_to_str(expr) -> str:
        if expr is None:
            return ""

        expr_type = expr.__class__.__name__

        if expr_type == 'LiteralExprNode':
            if isinstance(expr.value, str):
                return f'"{expr.value}"'
            return str(expr.value)
        elif expr_type == 'IdentifierExprNode':
            return expr.name
        elif expr_type == 'BinaryExprNode':
            left = ASTPrinter._expr_to_str(expr.left)
            right = ASTPrinter._expr_to_str(expr.right)
            return f"({left} {expr.operator} {right})"
        elif expr_type == 'UnaryExprNode':
            operand = ASTPrinter._expr_to_str(expr.operand)
            return f"({expr.operator}{operand})"
        elif expr_type == 'CallExprNode':
            args = ", ".join(ASTPrinter._expr_to_str(arg) for arg in expr.arguments)
            callee = ASTPrinter._expr_to_str(expr.callee)
            return f"{callee}({args})"
        elif expr_type == 'AssignmentExprNode':
            target = ASTPrinter._expr_to_str(expr.target)
            value = ASTPrinter._expr_to_str(expr.value)
            return f"{target} {expr.operator} {value}"
        else:
            return str(expr)

    @staticmethod
    def print_dot(node: ASTNode) -> str:
        lines = []
        lines.append("digraph AST {")
        lines.append("  node [shape=box, style=filled, fillcolor=lightblue];")

        node_counter = 0
        node_ids = {}

        def visit(node: ASTNode) -> int:
            nonlocal node_counter
            node_id = node_counter
            node_ids[node] = node_id
            node_counter += 1

            label = node.__class__.__name__
            if hasattr(node, 'name'):
                label += f"\\n{node.name}"
            elif hasattr(node, 'operator'):
                label += f"\\n{node.operator}"
            elif hasattr(node, 'value'):
                label += f"\\n{node.value}"

            lines.append(f'  node{node_id} [label="{label}"];')

            if hasattr(node, 'declarations') and node.declarations:
                for child in node.declarations:
                    child_id = visit(child)
                    lines.append(f"  node{node_id} -> node{child_id};")
            if hasattr(node, 'body') and node.body:
                child_id = visit(node.body)
                lines.append(f"  node{node_id} -> node{child_id};")
            if hasattr(node, 'then_branch') and node.then_branch:
                child_id = visit(node.then_branch)
                lines.append(f"  node{node_id} -> node{child_id} [label=\"then\"];")
            if hasattr(node, 'else_branch') and node.else_branch:
                child_id = visit(node.else_branch)
                lines.append(f"  node{node_id} -> node{child_id} [label=\"else\"];")
            if hasattr(node, 'condition') and node.condition:
                child_id = visit(node.condition)
                lines.append(f"  node{node_id} -> node{child_id} [label=\"cond\"];")
            if hasattr(node, 'left') and node.left:
                child_id = visit(node.left)
                lines.append(f"  node{node_id} -> node{child_id} [label=\"left\"];")
            if hasattr(node, 'right') and node.right:
                child_id = visit(node.right)
                lines.append(f"  node{node_id} -> node{child_id} [label=\"right\"];")
            if hasattr(node, 'operand') and node.operand:
                child_id = visit(node.operand)
                lines.append(f"  node{node_id} -> node{child_id};")
            if hasattr(node, 'callee') and node.callee:
                child_id = visit(node.callee)
                lines.append(f"  node{node_id} -> node{child_id} [label=\"callee\"];")
            if hasattr(node, 'arguments') and node.arguments:
                for arg in node.arguments:
                    child_id = visit(arg)
                    lines.append(f"  node{node_id} -> node{child_id} [label=\"arg\"];")
            if hasattr(node, 'target') and node.target:
                child_id = visit(node.target)
                lines.append(f"  node{node_id} -> node{child_id} [label=\"target\"];")
            if hasattr(node, 'value') and isinstance(node.value, ASTNode):
                child_id = visit(node.value)
                lines.append(f"  node{node_id} -> node{child_id} [label=\"value\"];")
            if hasattr(node, 'parameters') and node.parameters:
                for param in node.parameters:
                    child_id = visit(param)
                    lines.append(f"  node{node_id} -> node{child_id} [label=\"param\"];")
            if hasattr(node, 'fields') and node.fields:
                for field in node.fields:
                    child_id = visit(field)
                    lines.append(f"  node{node_id} -> node{child_id} [label=\"field\"];")
            if hasattr(node, 'statements') and node.statements:
                for stmt in node.statements:
                    child_id = visit(stmt)
                    lines.append(f"  node{node_id} -> node{child_id};")
            if hasattr(node, 'init') and node.init:
                child_id = visit(node.init)
                lines.append(f"  node{node_id} -> node{child_id} [label=\"init\"];")
            if hasattr(node, 'update') and node.update:
                child_id = visit(node.update)
                lines.append(f"  node{node_id} -> node{child_id} [label=\"update\"];")

            return node_id

        visit(node)
        lines.append("}")
        return "\n".join(lines)

    @staticmethod
    def print_json(node: ASTNode) -> str:
        def to_dict(node: ASTNode):
            if node is None:
                return None

            result = {
                "type": node.__class__.__name__,
                "line": node.line,
                "column": node.column
            }

            if hasattr(node, 'name'):
                result["name"] = node.name
            if hasattr(node, 'operator'):
                result["operator"] = node.operator
            if hasattr(node, 'value') and not isinstance(node.value, ASTNode):
                result["value"] = node.value
            if hasattr(node, 'declarations') and node.declarations:
                result["declarations"] = [to_dict(d) for d in node.declarations]
            if hasattr(node, 'body') and node.body:
                result["body"] = to_dict(node.body)
            if hasattr(node, 'then_branch') and node.then_branch:
                result["then_branch"] = to_dict(node.then_branch)
            if hasattr(node, 'else_branch') and node.else_branch:
                result["else_branch"] = to_dict(node.else_branch)
            if hasattr(node, 'condition') and node.condition:
                result["condition"] = to_dict(node.condition)
            if hasattr(node, 'left') and node.left:
                result["left"] = to_dict(node.left)
            if hasattr(node, 'right') and node.right:
                result["right"] = to_dict(node.right)
            if hasattr(node, 'operand') and node.operand:
                result["operand"] = to_dict(node.operand)
            if hasattr(node, 'callee') and node.callee:
                result["callee"] = to_dict(node.callee)
            if hasattr(node, 'arguments') and node.arguments:
                result["arguments"] = [to_dict(a) for a in node.arguments]
            if hasattr(node, 'target') and node.target:
                result["target"] = to_dict(node.target)
            if hasattr(node, 'value') and isinstance(node.value, ASTNode):
                result["value"] = to_dict(node.value)
            if hasattr(node, 'parameters') and node.parameters:
                result["parameters"] = [to_dict(p) for p in node.parameters]
            if hasattr(node, 'var_type') and node.var_type:
                result["var_type"] = to_dict(node.var_type)
            if hasattr(node, 'return_type') and node.return_type:
                result["return_type"] = to_dict(node.return_type)
            if hasattr(node, 'fields') and node.fields:
                result["fields"] = [to_dict(f) for f in node.fields]
            if hasattr(node, 'statements') and node.statements:
                result["statements"] = [to_dict(s) for s in node.statements]
            if hasattr(node, 'init') and node.init:
                result["init"] = to_dict(node.init)
            if hasattr(node, 'update') and node.update:
                result["update"] = to_dict(node.update)
            if hasattr(node, 'param_type') and node.param_type:
                result["param_type"] = to_dict(node.param_type)

            return result

        return json.dumps(to_dict(node), indent=2, ensure_ascii=False)


def run_lexer(input_file: Path, output_file: Optional[Path], verbose: bool) -> int:
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            source = f.read()

        error_handler = ErrorHandler()
        scanner = Scanner(source, error_handler)

        tokens = scanner.tokenize_all()

        if verbose and error_handler.has_warnings():
            print("\n=== Warnings ===")
            error_handler.print_all()
            print()

        if error_handler.has_errors():
            print("\n=== Errors ===")
            error_handler.print_all()
            return 1

        output_lines = []
        for token in tokens:
            if token.literal_value is not None:
                if token.type.name == 'STRING_LITERAL':
                    output_lines.append(
                        f"{token.line}:{token.column} {token.type.name} \"{token.lexeme}\" \"{token.literal_value}\"")
                else:
                    output_lines.append(
                        f"{token.line}:{token.column} {token.type.name} \"{token.lexeme}\" {token.literal_value}")
            else:
                output_lines.append(f"{token.line}:{token.column} {token.type.name} \"{token.lexeme}\"")

        output = '\n'.join(output_lines)

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Tokens saved to {output_file}")
        else:
            print(output)

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


def run_parser(input_file: Path, output_file: Optional[Path],
               format: str, verbose: bool) -> int:
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            source = f.read()

        error_handler = ErrorHandler()
        scanner = Scanner(source, error_handler)
        tokens = scanner.tokenize_all()

        if error_handler.has_errors():
            print("\n=== Lexical Errors ===")
            error_handler.print_all()
            return 1

        if verbose:
            print(f"Tokenized {len(tokens)} tokens")
            if error_handler.has_warnings():
                print("\n=== Lexical Warnings ===")
                error_handler.print_all()
                print()

        parser = Parser(tokens, error_handler)
        ast = parser.parse()

        if error_handler.has_errors():
            print("\n=== Syntax Errors ===")
            error_handler.print_all()
            return 1

        if verbose:
            print("\n=== AST Debug ===")
            debug_visitor = DebugVisitor()
            ast.accept(debug_visitor)
            print()

        if format == "text":
            output = ASTPrinter.print_text(ast)
        elif format == "dot":
            output = ASTPrinter.print_dot(ast)
        elif format == "json":
            output = ASTPrinter.print_json(ast)
        else:
            print(f"Unknown format: {format}")
            return 1

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"AST saved to {output_file}")
        else:
            print(output)

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


def run_check(input_file: Path, output_file: Optional[Path],
              show_types: bool, dump_symbols: bool, verbose: bool) -> int:
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            source = f.read()

        error_handler = ErrorHandler()
        scanner = Scanner(source, error_handler)
        tokens = scanner.tokenize_all()

        if error_handler.has_errors():
            print("\n=== Lexical Errors ===")
            error_handler.print_all()
            return 1

        if verbose:
            print(f"Tokenized {len(tokens)} tokens")

        parser = Parser(tokens, error_handler)
        ast = parser.parse()

        if error_handler.has_errors():
            print("\n=== Syntax Errors ===")
            error_handler.print_all()
            return 1

        if verbose:
            print("\n=== Parsing completed, starting semantic analysis ===")

        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)

        if analyzer.get_errors().has_errors():
            print("\n=== Semantic Errors ===")
            analyzer.get_errors().print_all()
            return 1

        print("\n=== Semantic Analysis Successful ===")

        if dump_symbols:
            print("\n=== Symbol Table ===")
            print(analyzer.get_symbol_table().print_table())

        if show_types:
            print("\n=== Type Annotated AST ===")
            print(ASTPrinter.print_text(ast))

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(ASTPrinter.print_text(ast))
            print(f"Decorated AST saved to {output_file}")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description='MiniCompiler - Lexical, Syntax and Semantic Analyzer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Lexical analysis (Sprint 1)
  compiler lex --input examples/hello.src
  compiler lex --input examples/hello.src --output tokens.txt
  compiler lex --input examples/hello.src --verbose

  # Syntax analysis (Sprint 2)
  compiler parse --input examples/factorial.src
  compiler parse --input examples/factorial.src --format dot --output ast.dot
  compiler parse --input examples/factorial.src --format json
  compiler parse --input examples/factorial.src --verbose

  # Semantic analysis (Sprint 3)
  compiler check --input examples/hello.src
  compiler check --input examples/hello.src --dump-symbols
  compiler check --input examples/hello.src --show-types
  compiler check --input examples/hello.src --verbose

  # Visualize AST with Graphviz
  compiler parse --input examples/factorial.src --format dot --output ast.dot
  dot -Tpng ast.dot -o ast.png
        """
    )

    parser.add_argument(
        'command',
        choices=['lex', 'parse', 'check'],
        help='Command to execute: lex (tokenize), parse (build AST), check (semantic analysis)'
    )

    parser.add_argument(
        '--input', '-i',
        type=str,
        required=True,
        help='Input source file'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file (for tokens, AST or decorated AST)'
    )

    parser.add_argument(
        '--format', '-f',
        choices=['text', 'dot', 'json'],
        default='text',
        help='Output format for AST (default: text)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output with warnings and debug info'
    )

    parser.add_argument(
        '--show-types',
        action='store_true',
        help='Show type-annotated AST (for check command)'
    )

    parser.add_argument(
        '--dump-symbols',
        action='store_true',
        help='Dump symbol table (for check command)'
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File '{args.input}' not found")
        return 1

    output_path = Path(args.output) if args.output else None

    if args.command == 'lex':
        return run_lexer(input_path, output_path, args.verbose)
    elif args.command == 'parse':
        return run_parser(input_path, output_path, args.format, args.verbose)
    else:
        return run_check(input_path, output_path, args.show_types, args.dump_symbols, args.verbose)


if __name__ == '__main__':
    sys.exit(main())