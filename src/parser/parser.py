from typing import List, Optional, Any
from src.lexer.token import Token
from src.lexer import TokenType
from src.utils.error_handler import ErrorHandler
from src.parser.ast import (
    # Базовые классы
    ASTNode, DeclarationNode, StatementNode, ExpressionNode,
    # Конкретные узлы
    ProgramNode, FunctionDeclNode, StructDeclNode, VarDeclStmtNode,
    ParamNode, TypeNode, BlockStmtNode, IfStmtNode, WhileStmtNode,
    ForStmtNode, ReturnStmtNode, ExprStmtNode, AssignmentExprNode,
    BinaryExprNode, UnaryExprNode, LiteralExprNode, IdentifierExprNode,
    CallExprNode
)


class ParseError(Exception):
    """Исключение для ошибок парсинга."""
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"{message} at {token.line}:{token.column}")


class Parser:
    """
    Основной класс парсера.
    Принимает список токенов и строит AST.
    """

    def __init__(self, tokens: List[Token], error_handler: Optional[ErrorHandler] = None):
        self.tokens = tokens
        self.current = 0
        self.error_handler = error_handler or ErrorHandler()

    # === Вспомогательные методы ===

    def peek(self) -> Token:
        """Возвращает текущий токен без продвижения."""
        if self.is_at_end():
            return self.tokens[-1]
        return self.tokens[self.current]

    def previous(self) -> Token:
        """Возвращает предыдущий токен."""
        return self.tokens[self.current - 1]

    def is_at_end(self) -> bool:
        """Проверяет, достигнут ли конец токенов."""
        return self.current >= len(self.tokens) or \
               self.tokens[self.current].type == TokenType.END_OF_FILE

    def advance(self) -> Token:
        """Переходит к следующему токену и возвращает текущий."""
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def check(self, token_type: TokenType) -> bool:
        """Проверяет, является ли текущий токен заданного типа."""
        if self.is_at_end():
            return False
        return self.peek().type == token_type

    def match(self, *types: TokenType) -> bool:
        """
        Проверяет, является ли текущий токен одним из заданных типов.
        Если да, продвигается к следующему токену.
        """
        for token_type in types:
            if self.check(token_type):
                self.advance()
                return True
        return False

    def consume(self, token_type: TokenType, message: str) -> Token:
        """
        Потребляет токен ожидаемого типа или сообщает об ошибке.
        """
        if self.check(token_type):
            return self.advance()

        current = self.peek()
        self.error_handler.add_error(
            f"{message} (expected {token_type.name}, got {current.type.name})",
            current.line, current.column
        )
        return current

    def synchronize(self) -> None:
        """
        Синхронизация после ошибки.
        Пропускает токены до следующей точки синхронизации.
        """
        self.advance()

        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return

            if self.peek().type in [
                TokenType.KW_FN, TokenType.KW_STRUCT,
                TokenType.KW_IF, TokenType.KW_WHILE, TokenType.KW_FOR,
                TokenType.KW_RETURN, TokenType.LBRACE,
                TokenType.KW_INT, TokenType.KW_FLOAT, TokenType.KW_BOOL
            ]:
                return

            self.advance()

    # === Основной метод парсинга ===

    def parse(self) -> ProgramNode:
        """
        Главный метод парсинга.
        Возвращает корень AST - ProgramNode.
        """
        declarations = []

        while not self.is_at_end():
            # Пропускаем END_OF_FILE
            if self.peek().type == TokenType.END_OF_FILE:
                break

            decl = self.parse_declaration()
            if decl:
                declarations.append(decl)
            else:
                # Если объявление не распознано, продвигаемся вперед
                self.advance()

        return ProgramNode(declarations)

    # === Объявления (верхний уровень) ===

    def parse_declaration(self) -> Optional[DeclarationNode]:
        """Парсит объявление на верхнем уровне."""
        # Сначала проверяем конец файла
        if self.is_at_end() or self.peek().type == TokenType.END_OF_FILE:
            return None

        token = self.peek()
        print(f"DEBUG: parse_declaration sees: {token.type.name} at {token.line}:{token.column}")  # Отладка

        if token.type == TokenType.KW_FN:
            print("DEBUG: Found function declaration")
            return self.parse_function_decl()
        elif token.type == TokenType.KW_STRUCT:
            print("DEBUG: Found struct declaration")
            return self.parse_struct_decl()
        elif token.type in [TokenType.KW_INT, TokenType.KW_FLOAT,
                           TokenType.KW_BOOL, TokenType.IDENTIFIER]:
            print("DEBUG: Found variable declaration")
            return self.parse_global_var_decl()
        else:
            print(f"DEBUG: Unexpected token: {token.type.name}")
            self.error_handler.add_error(
                f"Expected global declaration (fn, struct, or variable), got {token.type.name}",
                token.line, token.column
            )
            return None
    def parse_function_decl(self) -> FunctionDeclNode:
        """Парсит объявление функции."""
        # Потребляем 'fn'
        fn_token = self.advance()

        # Имя функции
        name_token = self.consume(TokenType.IDENTIFIER, "Expected function name")
        name = name_token.lexeme

        # Параметры
        self.consume(TokenType.LPAREN, "Expected '(' after function name")
        parameters = self.parse_parameters()
        self.consume(TokenType.RPAREN, "Expected ')' after parameters")

        # Возвращаемый тип
        return_type = TypeNode("void", fn_token.line, fn_token.column)
        if self.match(TokenType.ARROW):
            return_type = self.parse_type()

        # Тело функции
        body = self.parse_block()

        return FunctionDeclNode(
            name=name,
            parameters=parameters,
            return_type=return_type,
            body=body,
            line=fn_token.line,
            column=fn_token.column
        )

    def parse_struct_decl(self) -> StructDeclNode:
        """Парсит объявление структуры."""
        # Потребляем 'struct'
        struct_token = self.advance()

        # Имя структуры
        name_token = self.consume(TokenType.IDENTIFIER, "Expected struct name")
        name = name_token.lexeme

        # Открывающая скобка
        self.consume(TokenType.LBRACE, "Expected '{{' after struct name")

        # Поля структуры
        fields = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            field = self.parse_struct_field()
            if field:
                fields.append(field)

        # Закрывающая скобка
        self.consume(TokenType.RBRACE, "Expected '}}' after struct fields")

        return StructDeclNode(
            name=name,
            fields=fields,
            line=struct_token.line,
            column=struct_token.column
        )

    def parse_struct_field(self) -> Optional[VarDeclStmtNode]:
        """Парсит поле структуры."""
        type_node = self.parse_type()
        if not type_node:
            return None

        name_token = self.consume(TokenType.IDENTIFIER, "Expected field name")
        name = name_token.lexeme

        self.consume(TokenType.SEMICOLON, "Expected ';' after field declaration")

        return VarDeclStmtNode(
            var_type=type_node,
            name=name,
            initializer=None,
            line=type_node.line,
            column=type_node.column
        )

    def parse_global_var_decl(self) -> Optional[VarDeclStmtNode]:
        """Парсит глобальное объявление переменной."""
        type_node = self.parse_type()
        if not type_node:
            return None

        name_token = self.consume(TokenType.IDENTIFIER, "Expected variable name")
        name = name_token.lexeme

        initializer = None
        if self.match(TokenType.ASSIGN):
            initializer = self.parse_expression()

        self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration")

        return VarDeclStmtNode(
            var_type=type_node,
            name=name,
            initializer=initializer,
            line=type_node.line,
            column=type_node.column
        )

    def parse_parameters(self) -> List[ParamNode]:
        """Парсит список параметров функции."""
        parameters = []

        if self.check(TokenType.RPAREN):
            return parameters

        # Первый параметр
        param = self.parse_parameter()
        if param:
            parameters.append(param)

        # Остальные параметры
        while self.match(TokenType.COMMA):
            param = self.parse_parameter()
            if param:
                parameters.append(param)

        return parameters

    def parse_parameter(self) -> Optional[ParamNode]:
        """Парсит один параметр функции."""
        type_node = self.parse_type()
        if not type_node:
            return None

        name_token = self.consume(TokenType.IDENTIFIER, "Expected parameter name")
        name = name_token.lexeme

        return ParamNode(
            param_type=type_node,
            name=name,
            line=type_node.line,
            column=type_node.column
        )

    def parse_type(self) -> Optional[TypeNode]:
        """Парсит тип."""
        token = self.peek()

        if token.type == TokenType.KW_INT:
            self.advance()
            return TypeNode("int", token.line, token.column)
        elif token.type == TokenType.KW_FLOAT:
            self.advance()
            return TypeNode("float", token.line, token.column)
        elif token.type == TokenType.KW_BOOL:
            self.advance()
            return TypeNode("bool", token.line, token.column)
        elif token.type == TokenType.KW_VOID:
            self.advance()
            return TypeNode("void", token.line, token.column)
        elif token.type == TokenType.IDENTIFIER:
            self.advance()
            return TypeNode(token.lexeme, token.line, token.column)
        else:
            self.error_handler.add_error(
                f"Expected type, got {token.type.name}",
                token.line, token.column
            )
            return None

    # === Инструкции (внутри функций) ===

    def parse_statement(self) -> Optional[StatementNode]:
        """Парсит инструкцию внутри функции."""
        token = self.peek()

        if token.type == TokenType.LBRACE:
            return self.parse_block()
        elif token.type == TokenType.KW_IF:
            return self.parse_if_statement()
        elif token.type == TokenType.KW_WHILE:
            return self.parse_while_statement()
        elif token.type == TokenType.KW_FOR:
            return self.parse_for_statement()
        elif token.type == TokenType.KW_RETURN:
            return self.parse_return_statement()
        elif token.type == TokenType.SEMICOLON:
            self.advance()  # пустая инструкция
            return None
        elif token.type in [TokenType.KW_INT, TokenType.KW_FLOAT,
                           TokenType.KW_BOOL, TokenType.IDENTIFIER]:
            return self.parse_local_var_decl()
        else:
            return self.parse_expression_statement()

    def parse_block(self) -> BlockStmtNode:
        """Парсит блок инструкций."""
        # Потребляем '{'
        brace_token = self.advance()
        statements = []

        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)

        self.consume(TokenType.RBRACE, "Expected '}}' after block")

        return BlockStmtNode(
            statements=statements,
            line=brace_token.line,
            column=brace_token.column
        )

    def parse_local_var_decl(self) -> Optional[VarDeclStmtNode]:
        """Парсит объявление переменной внутри функции."""
        type_node = self.parse_type()
        if not type_node:
            return None

        name_token = self.consume(TokenType.IDENTIFIER, "Expected variable name")
        name = name_token.lexeme

        initializer = None
        if self.match(TokenType.ASSIGN):
            initializer = self.parse_expression()

        self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration")

        return VarDeclStmtNode(
            var_type=type_node,
            name=name,
            initializer=initializer,
            line=type_node.line,
            column=type_node.column
        )

    def parse_if_statement(self) -> IfStmtNode:
        """Парсит условную инструкцию."""
        # Потребляем 'if'
        if_token = self.advance()

        self.consume(TokenType.LPAREN, "Expected '(' after 'if'")
        condition = self.parse_expression()
        self.consume(TokenType.RPAREN, "Expected ')' after condition")

        then_branch = self.parse_statement()
        if not then_branch:
            then_branch = BlockStmtNode([], if_token.line, if_token.column)

        else_branch = None
        if self.match(TokenType.KW_ELSE):
            else_branch = self.parse_statement()

        return IfStmtNode(
            condition=condition,
            then_branch=then_branch,
            else_branch=else_branch,
            line=if_token.line,
            column=if_token.column
        )

    def parse_while_statement(self) -> WhileStmtNode:
        """Парсит цикл while."""
        # Потребляем 'while'
        while_token = self.advance()

        self.consume(TokenType.LPAREN, "Expected '(' after 'while'")
        condition = self.parse_expression()
        self.consume(TokenType.RPAREN, "Expected ')' after condition")

        body = self.parse_statement()
        if not body:
            body = BlockStmtNode([], while_token.line, while_token.column)

        return WhileStmtNode(
            condition=condition,
            body=body,
            line=while_token.line,
            column=while_token.column
        )

    def parse_for_statement(self) -> ForStmtNode:
        """Парсит цикл for."""
        # Потребляем 'for'
        for_token = self.advance()

        self.consume(TokenType.LPAREN, "Expected '(' after 'for'")

        # Инициализация
        init = None
        if not self.check(TokenType.SEMICOLON):
            if self.check(TokenType.KW_INT) or self.check(TokenType.KW_FLOAT) or \
               self.check(TokenType.KW_BOOL) or self.check(TokenType.IDENTIFIER):
                init = self.parse_local_var_decl()
            else:
                init = self.parse_expression_statement()
        else:
            self.consume(TokenType.SEMICOLON, "Expected ';'")

        # Условие
        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after loop condition")

        # Обновление
        update = None
        if not self.check(TokenType.RPAREN):
            update = self.parse_expression()
        self.consume(TokenType.RPAREN, "Expected ')' after for clauses")

        # Тело
        body = self.parse_statement()
        if not body:
            body = BlockStmtNode([], for_token.line, for_token.column)

        return ForStmtNode(
            init=init,
            condition=condition,
            update=update,
            body=body,
            line=for_token.line,
            column=for_token.column
        )

    def parse_return_statement(self) -> ReturnStmtNode:
        """Парсит инструкцию return."""
        # Потребляем 'return'
        return_token = self.advance()

        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.parse_expression()

        self.consume(TokenType.SEMICOLON, "Expected ';' after return")

        return ReturnStmtNode(
            value=value,
            line=return_token.line,
            column=return_token.column
        )

    def parse_expression_statement(self) -> ExprStmtNode:
        """Парсит инструкцию-выражение."""
        expr = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after expression")
        return ExprStmtNode(expression=expr, line=expr.line, column=expr.column)

    # === Выражения ===

    def parse_expression(self) -> ExpressionNode:
        """Парсит выражение."""
        return self.parse_assignment()

    def parse_assignment(self) -> ExpressionNode:
        """Парсит присваивание."""
        expr = self.parse_logical_or()

        if self.match(TokenType.ASSIGN, TokenType.PLUS_ASSIGN,
                     TokenType.MINUS_ASSIGN, TokenType.STAR_ASSIGN,
                     TokenType.SLASH_ASSIGN):
            operator = self.previous().lexeme
            value = self.parse_assignment()
            expr = AssignmentExprNode(
                target=expr,
                operator=operator,
                value=value,
                line=expr.line,
                column=expr.column
            )

        return expr

    def parse_logical_or(self) -> ExpressionNode:
        """Парсит логическое ИЛИ."""
        expr = self.parse_logical_and()

        while self.match(TokenType.OR):
            operator = self.previous().lexeme
            right = self.parse_logical_and()
            expr = BinaryExprNode(
                left=expr,
                operator=operator,
                right=right,
                line=expr.line,
                column=expr.column
            )

        return expr

    def parse_logical_and(self) -> ExpressionNode:
        """Парсит логическое И."""
        expr = self.parse_equality()

        while self.match(TokenType.AND):
            operator = self.previous().lexeme
            right = self.parse_equality()
            expr = BinaryExprNode(
                left=expr,
                operator=operator,
                right=right,
                line=expr.line,
                column=expr.column
            )

        return expr

    def parse_equality(self) -> ExpressionNode:
        """Парсит равенство."""
        expr = self.parse_relational()

        while self.match(TokenType.EQ, TokenType.NEQ):
            operator = self.previous().lexeme
            right = self.parse_relational()
            expr = BinaryExprNode(
                left=expr,
                operator=operator,
                right=right,
                line=expr.line,
                column=expr.column
            )

        return expr

    def parse_relational(self) -> ExpressionNode:
        """Парсит сравнение."""
        expr = self.parse_additive()

        while self.match(TokenType.LT, TokenType.LTE, TokenType.GT, TokenType.GTE):
            operator = self.previous().lexeme
            right = self.parse_additive()
            expr = BinaryExprNode(
                left=expr,
                operator=operator,
                right=right,
                line=expr.line,
                column=expr.column
            )

        return expr

    def parse_additive(self) -> ExpressionNode:
        """Парсит сложение/вычитание."""
        expr = self.parse_multiplicative()

        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous().lexeme
            right = self.parse_multiplicative()
            expr = BinaryExprNode(
                left=expr,
                operator=operator,
                right=right,
                line=expr.line,
                column=expr.column
            )

        return expr

    def parse_multiplicative(self) -> ExpressionNode:
        """Парсит умножение/деление."""
        expr = self.parse_unary()

        while self.match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            operator = self.previous().lexeme
            right = self.parse_unary()
            expr = BinaryExprNode(
                left=expr,
                operator=operator,
                right=right,
                line=expr.line,
                column=expr.column
            )

        return expr

    def parse_unary(self) -> ExpressionNode:
        """Парсит унарные операторы."""
        if self.match(TokenType.MINUS, TokenType.NOT):
            operator = self.previous().lexeme
            expr = self.parse_unary()
            return UnaryExprNode(
                operator=operator,
                operand=expr,
                line=self.previous().line,
                column=self.previous().column
            )

        return self.parse_call()

    def parse_call(self) -> ExpressionNode:
        """Парсит вызов функции."""
        expr = self.parse_primary()

        while self.match(TokenType.LPAREN):
            arguments = []
            if not self.check(TokenType.RPAREN):
                arguments.append(self.parse_expression())
                while self.match(TokenType.COMMA):
                    arguments.append(self.parse_expression())
            self.consume(TokenType.RPAREN, "Expected ')' after arguments")

            expr = CallExprNode(
                callee=expr,
                arguments=arguments,
                line=expr.line,
                column=expr.column
            )

        return expr

    def parse_primary(self) -> ExpressionNode:
        """Парсит первичные выражения."""
        token = self.peek()

        if self.match(TokenType.INT_LITERAL):
            return LiteralExprNode(
                value=int(self.previous().lexeme),
                line=token.line,
                column=token.column
            )

        if self.match(TokenType.FLOAT_LITERAL):
            return LiteralExprNode(
                value=float(self.previous().lexeme),
                line=token.line,
                column=token.column
            )

        if self.match(TokenType.STRING_LITERAL):
            return LiteralExprNode(
                value=self.previous().literal_value,
                line=token.line,
                column=token.column
            )

        if self.match(TokenType.KW_TRUE):
            return LiteralExprNode(
                value=True,
                line=token.line,
                column=token.column
            )

        if self.match(TokenType.KW_FALSE):
            return LiteralExprNode(
                value=False,
                line=token.line,
                column=token.column
            )

        if self.match(TokenType.IDENTIFIER):
            return IdentifierExprNode(
                name=self.previous().lexeme,
                line=token.line,
                column=token.column
            )

        if self.match(TokenType.LPAREN):
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr

        self.error_handler.add_error(
            f"Expected expression, got {token.type.name}",
            token.line, token.column
        )
        self.advance()
        return LiteralExprNode(0, token.line, token.column)