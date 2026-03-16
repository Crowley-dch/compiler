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
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"{message} at {token.line}:{token.column}")


class Parser:

    def __init__(self, tokens: List[Token], error_handler: Optional[ErrorHandler] = None):
        self.tokens = tokens
        self.current = 0
        self.error_handler = error_handler or ErrorHandler()


    def peek(self) -> Token:
        if self.is_at_end():
            return self.tokens[-1]
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def is_at_end(self) -> bool:
        return self.current >= len(self.tokens) or \
               self.tokens[self.current].type == TokenType.END_OF_FILE

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def check(self, token_type: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == token_type

    def match(self, *types: TokenType) -> bool:

        for token_type in types:
            if self.check(token_type):
                self.advance()
                return True
        return False

    def consume(self, token_type: TokenType, message: str) -> Token:

        if self.check(token_type):
            return self.advance()

        current = self.peek()
        self.error_handler.add_error(
            f"{message} (expected {token_type.name}, got {current.type.name})",
            current.line, current.column
        )
        return current

    def synchronize(self) -> None:

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


    def parse(self) -> ProgramNode:

        declarations = []

        while not self.is_at_end():
            if self.peek().type == TokenType.END_OF_FILE:
                break

            decl = self.parse_declaration()
            if decl:
                declarations.append(decl)
            else:
                self.advance()

        return ProgramNode(declarations)


    def parse_declaration(self) -> Optional[DeclarationNode]:
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
        fn_token = self.advance()

        name_token = self.consume(TokenType.IDENTIFIER, "Expected function name")
        name = name_token.lexeme

        self.consume(TokenType.LPAREN, "Expected '(' after function name")
        parameters = self.parse_parameters()
        self.consume(TokenType.RPAREN, "Expected ')' after parameters")

        return_type = TypeNode("void", fn_token.line, fn_token.column)
        if self.match(TokenType.ARROW):
            return_type = self.parse_type()

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
        struct_token = self.advance()

        name_token = self.consume(TokenType.IDENTIFIER, "Expected struct name")
        name = name_token.lexeme

        self.consume(TokenType.LBRACE, "Expected '{{' after struct name")

        fields = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            field = self.parse_struct_field()
            if field:
                fields.append(field)

        self.consume(TokenType.RBRACE, "Expected '}}' after struct fields")

        return StructDeclNode(
            name=name,
            fields=fields,
            line=struct_token.line,
            column=struct_token.column
        )

    def parse_struct_field(self) -> Optional[VarDeclStmtNode]:
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
        parameters = []

        if self.check(TokenType.RPAREN):
            return parameters

        param = self.parse_parameter()
        if param:
            parameters.append(param)

        while self.match(TokenType.COMMA):
            param = self.parse_parameter()
            if param:
                parameters.append(param)

        return parameters

    def parse_parameter(self) -> Optional[ParamNode]:
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


    def parse_statement(self) -> Optional[StatementNode]:
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

        for_token = self.advance()

        self.consume(TokenType.LPAREN, "Expected '(' after 'for'")


        init = None
        if not self.check(TokenType.SEMICOLON):
            if self.check(TokenType.KW_INT) or self.check(TokenType.KW_FLOAT) or \
               self.check(TokenType.KW_BOOL) or self.check(TokenType.IDENTIFIER):
                init = self.parse_local_var_decl()
            else:
                init = self.parse_expression_statement()
        else:
            self.consume(TokenType.SEMICOLON, "Expected ';'")

        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after loop condition")

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
        expr = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after expression")
        return ExprStmtNode(expression=expr, line=expr.line, column=expr.column)


    def parse_expression(self) -> ExpressionNode:

        return self.parse_assignment()

    def parse_assignment(self) -> ExpressionNode:
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