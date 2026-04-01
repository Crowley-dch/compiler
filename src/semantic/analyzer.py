from typing import Optional, List, Dict, Any
from src.parser.ast import (
    ASTNode, ProgramNode, FunctionDeclNode, StructDeclNode, VarDeclStmtNode,
    BlockStmtNode, IfStmtNode, WhileStmtNode, ForStmtNode, ReturnStmtNode,
    ExprStmtNode, LiteralExprNode, IdentifierExprNode, BinaryExprNode,
    UnaryExprNode, CallExprNode, AssignmentExprNode, TypeNode, ParamNode
)
from src.semantic.type_system import (
    Type, INT_TYPE, FLOAT_TYPE, BOOL_TYPE, VOID_TYPE, STRING_TYPE,
    StructType, FunctionType, TypeChecker, PrimitiveType
)
from src.semantic.symbol_table import SymbolTable, Symbol, SymbolKind
from src.semantic.errors import SemanticErrorCollector, SemanticErrorCode


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = SemanticErrorCollector()
        self.current_function: Optional[FunctionDeclNode] = None
        self.current_return_type: Optional[Type] = None
        self.in_loop = False

    def analyze(self, ast: ProgramNode) -> ProgramNode:
        self._visit_program(ast)
        return ast

    def get_errors(self):
        return self.errors

    def get_symbol_table(self):
        return self.symbol_table

    def _visit_program(self, node: ProgramNode) -> None:
        for decl in node.declarations:
            self._visit_declaration(decl)

    def _visit_declaration(self, node: ASTNode) -> None:
        if isinstance(node, FunctionDeclNode):
            self._visit_function_decl(node)
        elif isinstance(node, StructDeclNode):
            self._visit_struct_decl(node)
        elif isinstance(node, VarDeclStmtNode):
            self._visit_var_decl(node, is_global=True)

    def _visit_function_decl(self, node: FunctionDeclNode) -> None:
        func_type = self._get_type_from_node(node.return_type)

        existing = self.symbol_table.lookup_global(node.name)
        if existing:
            self.errors.add_error(
                SemanticErrorCode.DUPLICATE_DECLARATION,
                f"duplicate declaration of function '{node.name}'",
                node.line, node.column,
                context=f"previous declaration at line {existing.line}",
                suggestion="rename the function or remove the duplicate"
            )
            return

        param_types = []
        param_names = set()

        for param in node.parameters:
            if param.name in param_names:
                self.errors.add_error(
                    SemanticErrorCode.DUPLICATE_DECLARATION,
                    f"duplicate parameter '{param.name}' in function '{node.name}'",
                    param.line, param.column,
                    suggestion="rename the parameter"
                )
            else:
                param_names.add(param.name)

            param_type = self._get_type_from_node(param.param_type)
            param_types.append(param_type)

        symbol = Symbol(
            name=node.name,
            kind=SymbolKind.FUNCTION,
            type=func_type,
            line=node.line,
            column=node.column,
            param_types=param_types
        )
        self.symbol_table.insert(symbol)

        # Создаем ОДНУ область для функции (параметры + тело)
        self.symbol_table.enter_scope(f"function {node.name}")
        self.symbol_table.reset_offsets()

        for param in node.parameters:
            param_type = self._get_type_from_node(param.param_type)
            param_symbol = Symbol(
                name=param.name,
                kind=SymbolKind.PARAMETER,
                type=param_type,
                line=param.line,
                column=param.column
            )
            self.symbol_table.insert(param_symbol)

        old_function = self.current_function
        old_return_type = self.current_return_type
        self.current_function = node
        self.current_return_type = func_type

        # Обрабатываем тело функции В ТОЙ ЖЕ ОБЛАСТИ, а не создаем новую
        self._visit_statements_in_current_scope(node.body)

        if func_type != VOID_TYPE and not self._function_has_return(node.body):
            self.errors.add_error(
                SemanticErrorCode.MISSING_RETURN,
                f"function '{node.name}' must return a value",
                node.line, node.column,
                context=f"expected return type: {func_type}",
                suggestion="add a return statement with a value"
            )

        self.current_function = old_function
        self.current_return_type = old_return_type
        self.symbol_table.exit_scope()

    def _visit_statements_in_current_scope(self, node: BlockStmtNode) -> None:
        """Обрабатывает инструкции блока без создания новой области видимости."""
        for stmt in node.statements:
            self._visit_statement(stmt)

    def _function_has_return(self, node: ASTNode) -> bool:
        """Проверяет, содержит ли узел инструкцию return."""
        if isinstance(node, ReturnStmtNode):
            return True

        if isinstance(node, BlockStmtNode):
            for stmt in node.statements:
                if self._function_has_return(stmt):
                    return True
            return False

        if isinstance(node, IfStmtNode):
            has_return_then = self._function_has_return(node.then_branch)
            if node.else_branch:
                has_return_else = self._function_has_return(node.else_branch)
                # Если есть return в обеих ветках, то функция всегда возвращает значение
                return has_return_then and has_return_else
            return False

        if isinstance(node, WhileStmtNode) or isinstance(node, ForStmtNode):
            # В цикле return не гарантирует возврат из функции
            return False

        return False

    def _visit_struct_decl(self, node: StructDeclNode) -> None:
        existing = self.symbol_table.lookup_global(node.name)
        if existing:
            self.errors.add_error(
                SemanticErrorCode.DUPLICATE_DECLARATION,
                f"duplicate declaration of struct '{node.name}'",
                node.line, node.column,
                context=f"previous declaration at line {existing.line}",
                suggestion="rename the struct or remove the duplicate"
            )
            return

        fields = {}
        for field in node.fields:
            field_type = self._get_type_from_node(field.var_type)
            if field.name in fields:
                self.errors.add_error(
                    SemanticErrorCode.DUPLICATE_DECLARATION,
                    f"duplicate field '{field.name}' in struct '{node.name}'",
                    field.line, field.column,
                    suggestion="rename the field"
                )
            else:
                fields[field.name] = field_type

        struct_type = StructType(node.name, fields)

        symbol = Symbol(
            name=node.name,
            kind=SymbolKind.STRUCT,
            type=struct_type,
            line=node.line,
            column=node.column,
            fields=fields
        )
        self.symbol_table.insert(symbol)

    def _visit_var_decl(self, node: VarDeclStmtNode, is_global: bool = False) -> None:
        print(f"[DEBUG] _visit_var_decl: {node.name} at depth {self.symbol_table.current_depth()}")
        print(f"[DEBUG] All symbols in current scope: {[s.name for s in self.symbol_table.get_symbols_in_scope()]}")
        var_type = self._get_type_from_node(node.var_type)

        existing_local = self.symbol_table.lookup_local(node.name)

        if existing_local and existing_local.kind == SymbolKind.PARAMETER:
            self.errors.add_error(
                SemanticErrorCode.DUPLICATE_DECLARATION,
                f"cannot redeclare parameter '{node.name}' as variable",
                node.line, node.column,
                context=f"parameter '{node.name}' declared at line {existing_local.line}",
                suggestion="rename the variable"
            )
            return

        if self.symbol_table.is_defined_in_current_scope(node.name):
            existing = self.symbol_table.lookup_local(node.name)
            self.errors.add_error(
                SemanticErrorCode.DUPLICATE_DECLARATION,
                f"duplicate declaration of variable '{node.name}'",
                node.line, node.column,
                context=f"previous declaration at line {existing.line}",
                suggestion="rename the variable or remove the duplicate"
            )
            return

        symbol = Symbol(
            name=node.name,
            kind=SymbolKind.VARIABLE,
            type=var_type,
            line=node.line,
            column=node.column,
            is_initialized=node.initializer is not None
        )

        if not is_global:
            symbol.stack_offset = self.symbol_table.allocate_offset(var_type.size())

        self.symbol_table.insert(symbol)

        if node.initializer:
            init_type = self._visit_expression(node.initializer)
            if init_type and not var_type.is_compatible_with(init_type, implicit_conversion=True):
                self.errors.add_error(
                    SemanticErrorCode.TYPE_MISMATCH,
                    f"type mismatch in variable initialization",
                    node.line, node.column,
                    expected=str(var_type),
                    found=str(init_type),
                    suggestion=f"use value of type {var_type} or convert"
                )

    def _visit_block(self, node: BlockStmtNode) -> None:
        # Блок создает новую область видимости
        self.symbol_table.enter_scope("block")
        for stmt in node.statements:
            self._visit_statement(stmt)
        self.symbol_table.exit_scope()
    def _visit_statement(self, node: ASTNode) -> None:
        if isinstance(node, BlockStmtNode):
            self._visit_block(node)
        elif isinstance(node, IfStmtNode):
            self._visit_if(node)
        elif isinstance(node, WhileStmtNode):
            self._visit_while(node)
        elif isinstance(node, ForStmtNode):
            self._visit_for(node)
        elif isinstance(node, ReturnStmtNode):
            self._visit_return(node)
        elif isinstance(node, ExprStmtNode):
            self._visit_expression_stmt(node)
        elif isinstance(node, VarDeclStmtNode):
            self._visit_var_decl(node)

    def _visit_if(self, node: IfStmtNode) -> None:
        cond_type = self._visit_expression(node.condition)
        if cond_type and not cond_type.is_compatible_with(BOOL_TYPE):
            self.errors.add_error(
                SemanticErrorCode.INVALID_CONDITION_TYPE,
                "if condition must be boolean",
                node.condition.line, node.condition.column,
                expected="bool",
                found=str(cond_type),
                suggestion="use a boolean expression"
            )

        self._visit_statement(node.then_branch)
        if node.else_branch:
            self._visit_statement(node.else_branch)

    def _visit_while(self, node: WhileStmtNode) -> None:
        cond_type = self._visit_expression(node.condition)
        if cond_type and not cond_type.is_compatible_with(BOOL_TYPE):
            self.errors.add_error(
                SemanticErrorCode.INVALID_CONDITION_TYPE,
                "while condition must be boolean",
                node.condition.line, node.condition.column,
                expected="bool",
                found=str(cond_type),
                suggestion="use a boolean expression"
            )

        old_in_loop = self.in_loop
        self.in_loop = True
        self._visit_statement(node.body)
        self.in_loop = old_in_loop

    def _visit_for(self, node: ForStmtNode) -> None:
        self.symbol_table.enter_scope("for loop")

        if node.init:
            if isinstance(node.init, VarDeclStmtNode):
                self._visit_var_decl(node.init)
            elif isinstance(node.init, ExprStmtNode):
                self._visit_expression_stmt(node.init)

        if node.condition:
            cond_type = self._visit_expression(node.condition)
            if cond_type and not cond_type.is_compatible_with(BOOL_TYPE):
                self.errors.add_error(
                    SemanticErrorCode.INVALID_CONDITION_TYPE,
                    "for condition must be boolean",
                    node.condition.line, node.condition.column,
                    expected="bool",
                    found=str(cond_type),
                    suggestion="use a boolean expression"
                )

        if node.update:
            self._visit_expression(node.update)

        old_in_loop = self.in_loop
        self.in_loop = True
        self._visit_statement(node.body)
        self.in_loop = old_in_loop

        self.symbol_table.exit_scope()

    def _visit_return(self, node: ReturnStmtNode) -> None:
        if not self.current_function:
            self.errors.add_error(
                SemanticErrorCode.INVALID_RETURN_TYPE,
                "return statement outside function",
                node.line, node.column,
                suggestion="move return inside a function"
            )
            return

        if node.value:
            value_type = self._visit_expression(node.value)
            if value_type and not value_type.is_compatible_with(self.current_return_type):
                self.errors.add_error(
                    SemanticErrorCode.INVALID_RETURN_TYPE,
                    f"return type mismatch",
                    node.line, node.column,
                    expected=str(self.current_return_type),
                    found=str(value_type),
                    suggestion=f"return value of type {self.current_return_type}"
                )
        else:
            if self.current_return_type != VOID_TYPE:
                self.errors.add_error(
                    SemanticErrorCode.INVALID_RETURN_TYPE,
                    f"function must return a value",
                    node.line, node.column,
                    expected=str(self.current_return_type),
                    found="void",
                    suggestion="add a return value or change function return type to void"
                )

    def _visit_expression_stmt(self, node: ExprStmtNode) -> None:
        self._visit_expression(node.expression)

    def _visit_expression(self, node: ASTNode) -> Optional[Type]:
        if isinstance(node, LiteralExprNode):
            return self._visit_literal(node)
        elif isinstance(node, IdentifierExprNode):
            return self._visit_identifier(node)
        elif isinstance(node, BinaryExprNode):
            return self._visit_binary(node)
        elif isinstance(node, UnaryExprNode):
            return self._visit_unary(node)
        elif isinstance(node, CallExprNode):
            return self._visit_call(node)
        elif isinstance(node, AssignmentExprNode):
            return self._visit_assignment(node)
        return None

    def _visit_literal(self, node: LiteralExprNode) -> Type:
        if isinstance(node.value, bool):
            return BOOL_TYPE
        elif isinstance(node.value, int):
            return INT_TYPE
        elif isinstance(node.value, float):
            return FLOAT_TYPE
        elif isinstance(node.value, str):
            return STRING_TYPE
        return INT_TYPE

    def _visit_identifier(self, node: IdentifierExprNode) -> Optional[Type]:
        symbol = self.symbol_table.lookup(node.name)
        if not symbol:
            self.errors.add_error(
                SemanticErrorCode.UNDECLARED_IDENTIFIER,
                f"undeclared identifier '{node.name}'",
                node.line, node.column,
                suggestion=f"declare '{node.name}' before using it"
            )
            return None
        return symbol.type

    def _visit_binary(self, node: BinaryExprNode) -> Optional[Type]:
        left_type = self._visit_expression(node.left)
        right_type = self._visit_expression(node.right)

        if left_type is None or right_type is None:
            return None

        result_type = TypeChecker.get_binary_result_type(left_type, right_type, node.operator)
        if result_type is None:
            self.errors.add_error(
                SemanticErrorCode.INVALID_OPERATOR,
                f"invalid operator '{node.operator}' for types {left_type} and {right_type}",
                node.line, node.column,
                expected="compatible types",
                found=f"{left_type} {node.operator} {right_type}",
                suggestion="use compatible types for this operation"
            )
            return None

        return result_type

    def _visit_unary(self, node: UnaryExprNode) -> Optional[Type]:
        operand_type = self._visit_expression(node.operand)

        if operand_type is None:
            return None

        result_type = TypeChecker.get_unary_result_type(operand_type, node.operator)
        if result_type is None:
            self.errors.add_error(
                SemanticErrorCode.INVALID_OPERATOR,
                f"invalid operator '{node.operator}' for type {operand_type}",
                node.line, node.column,
                expected="numeric or boolean type",
                found=str(operand_type),
                suggestion=f"use {node.operator} with numeric or boolean types"
            )
            return None

        return result_type

    def _visit_call(self, node: CallExprNode) -> Optional[Type]:
        callee_type = self._visit_expression(node.callee)

        if callee_type is None:
            return None

        symbol = None
        if isinstance(node.callee, IdentifierExprNode):
            symbol = self.symbol_table.lookup(node.callee.name)

        if not symbol or symbol.kind != SymbolKind.FUNCTION:
            self.errors.add_error(
                SemanticErrorCode.NOT_A_FUNCTION,
                f"'{node.callee}' is not a function",
                node.line, node.column,
                suggestion="call a defined function"
            )
            return None

        expected_count = len(symbol.param_types)
        actual_count = len(node.arguments)

        if expected_count != actual_count:
            self.errors.add_error(
                SemanticErrorCode.ARGUMENT_COUNT_MISMATCH,
                f"argument count mismatch in call to '{symbol.name}'",
                node.line, node.column,
                expected=f"{expected_count} arguments",
                found=f"{actual_count} arguments",
                suggestion=f"function {symbol.name} expects {expected_count} arguments"
            )
            return symbol.type

        for i, (arg, expected_type) in enumerate(zip(node.arguments, symbol.param_types)):
            arg_type = self._visit_expression(arg)
            if arg_type and not arg_type.is_compatible_with(expected_type):
                self.errors.add_error(
                    SemanticErrorCode.ARGUMENT_TYPE_MISMATCH,
                    f"argument {i + 1} type mismatch in call to '{symbol.name}'",
                    arg.line, arg.column,
                    expected=str(expected_type),
                    found=str(arg_type),
                    suggestion=f"pass value of type {expected_type}"
                )

        return symbol.type

    def _visit_assignment(self, node: AssignmentExprNode) -> Optional[Type]:
        target_type = self._visit_expression(node.target)
        value_type = self._visit_expression(node.value)

        if target_type is None or value_type is None:
            return None

        if not isinstance(node.target, IdentifierExprNode):
            self.errors.add_error(
                SemanticErrorCode.INVALID_ASSIGNMENT_TARGET,
                "invalid assignment target",
                node.line, node.column,
                suggestion="assign to a variable"
            )
            return None

        if not TypeChecker.is_assignable(target_type, value_type):
            self.errors.add_error(
                SemanticErrorCode.TYPE_MISMATCH,
                f"type mismatch in assignment",
                node.line, node.column,
                expected=str(target_type),
                found=str(value_type),
                suggestion=f"assign value of type {target_type}"
            )
            return None

        symbol = self.symbol_table.lookup(node.target.name)
        if symbol:
            symbol.is_initialized = True

        return target_type

    def _get_type_from_node(self, node: TypeNode) -> Type:
        type_map = {
            'int': INT_TYPE,
            'float': FLOAT_TYPE,
            'bool': BOOL_TYPE,
            'void': VOID_TYPE,
            'string': STRING_TYPE
        }

        if node.name in type_map:
            return type_map[node.name]

        symbol = self.symbol_table.lookup(node.name)
        if symbol and symbol.kind == SymbolKind.STRUCT:
            return symbol.type

        return INT_TYPE