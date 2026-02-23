from typing import Optional, List
from lexer.token import Token
from lexer.token_types import (
    TokenType, KEYWORDS_MAP, SINGLE_CHAR_TOKENS_MAP,
    DOUBLE_CHAR_TOKENS_MAP, DOUBLE_CHAR_OPERATORS
)
from utils.error_handler import ErrorHandler

class Scanner:
    def __init__(self, source: str, error_handler: Optional[ErrorHandler] = None):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.error_handler = error_handler or ErrorHandler()

    def is_at_end(self) -> bool:
        return self.position >= len(self.source)

    def peek_char(self) -> Optional[str]:
        if self.is_at_end():
            return None
        return self.source[self.position]

    def peek_next_char(self) -> Optional[str]:
        if self.position + 1 >= len(self.source):
            return None
        return self.source[self.position + 1]

    def next_char(self) -> Optional[str]:
        if self.is_at_end():
            return None

        char = self.source[self.position]
        self.position += 1

        if char == '\n':
            self.line += 1
            self.column = 1
        elif char != '\r':
            self.column += 1

        return char

    def skip_whitespace(self) -> None:
        while not self.is_at_end():
            char = self.peek_char()
            if char in (' ', '\t', '\r', '\n'):
                self.next_char()
            else:
                break

    def skip_comment(self) -> bool:
        if self.peek_char() != '/':
            return False

        next_char = self.peek_next_char()
        if next_char == '/':
            while not self.is_at_end() and self.peek_char() != '\n':
                self.next_char()
            return True

        elif next_char == '*':
            self.next_char()
            self.next_char()

            while not self.is_at_end():
                if self.peek_char() == '*' and self.peek_next_char() == '/':
                    self.next_char()
                    self.next_char()
                    return True
                self.next_char()

            self.error_handler.add_error(
                "Unterminated multi-line comment",
                self.line, self.column
            )
            return True

        return False

    def read_identifier(self) -> str:
        result = []
        while not self.is_at_end():
            char = self.peek_char()
            if char and (char.isalnum() or char == '_'):
                result.append(self.next_char())
            else:
                break
        return ''.join(result)

    def read_number(self) -> Token:
        start_column = self.column
        result = []
        is_float = False

        while not self.is_at_end():
            char = self.peek_char()
            if char and char.isdigit():
                result.append(self.next_char())
            elif char == '.' and not is_float:
                next_char = self.peek_next_char()
                if next_char and next_char.isdigit():
                    is_float = True
                    result.append(self.next_char())
                else:
                    break
            else:
                break

        number_str = ''.join(result)

        if is_float:
            try:
                value = float(number_str)
                return Token(
                    TokenType.FLOAT_LITERAL,
                    number_str,
                    self.line,
                    start_column,
                    value
                )
            except ValueError:
                self.error_handler.add_error(
                    f"Invalid float literal: {number_str}",
                    self.line, start_column
                )
                return Token(
                    TokenType.ERROR,
                    number_str,
                    self.line,
                    start_column
                )
        else:
            try:
                value = int(number_str)
                if value < -2**31 or value > 2**31 - 1:
                    self.error_handler.add_warning(
                        f"Integer out of 32-bit range: {value}",
                        self.line, start_column
                    )
                return Token(
                    TokenType.INT_LITERAL,
                    number_str,
                    self.line,
                    start_column,
                    value
                )
            except ValueError:
                self.error_handler.add_error(
                    f"Invalid integer literal: {number_str}",
                    self.line, start_column
                )
                return Token(
                    TokenType.ERROR,
                    number_str,
                    self.line,
                    start_column
                )

    def read_string(self) -> Token:
        start_column = self.column
        self.next_char()
        result = []

        while not self.is_at_end():
            char = self.peek_char()
            if char == '"':
                self.next_char()
                string_value = ''.join(result)
                return Token(
                    TokenType.STRING_LITERAL,
                    string_value,
                    self.line,
                    start_column,
                    string_value
                )
            elif char == '\n':
                break
            else:
                result.append(self.next_char())

        self.error_handler.add_error(
            "Unterminated string",
            self.line, start_column
        )
        return Token(
            TokenType.ERROR,
            ''.join(result),
            self.line,
            start_column
        )

    def next_token(self) -> Token:
        self.skip_whitespace()

        if self.is_at_end():
            return Token(TokenType.END_OF_FILE, "", self.line, self.column)

        if self.skip_comment():
            return self.next_token()

        char = self.peek_char()
        start_column = self.column

        if char and (char.isalpha() or char == '_'):
            identifier = self.read_identifier()

            if identifier in KEYWORDS_MAP:
                token_type = KEYWORDS_MAP[identifier]
                if identifier in ('true', 'false'):
                    return Token(
                        token_type,
                        identifier,
                        self.line,
                        start_column,
                        identifier == 'true'
                    )
                return Token(token_type, identifier, self.line, start_column)

            return Token(TokenType.IDENTIFIER, identifier, self.line, start_column)

        if char and char.isdigit():
            return self.read_number()

        if char == '"':
            return self.read_string()

        if char and self.peek_next_char():
            two_chars = char + self.peek_next_char()
            if two_chars in DOUBLE_CHAR_OPERATORS:
                self.next_char()
                self.next_char()
                token_type = DOUBLE_CHAR_TOKENS_MAP[two_chars]
                return Token(token_type, two_chars, self.line, start_column)

        if char and char in SINGLE_CHAR_TOKENS_MAP:
            self.next_char()
            token_type = SINGLE_CHAR_TOKENS_MAP[char]
            return Token(token_type, char, self.line, start_column)

        self.next_char()
        self.error_handler.add_error(
            f"Invalid character: '{char}'",
            self.line, start_column
        )
        return Token(
            TokenType.ERROR,
            char or '',
            self.line,
            start_column
        )

    def peek_token(self) -> Token:
        saved_position = self.position
        saved_line = self.line
        saved_column = self.column

        token = self.next_token()

        self.position = saved_position
        self.line = saved_line
        self.column = saved_column

        return token

    def get_line(self) -> int:
        return self.line

    def get_column(self) -> int:
        return self.column

    def tokenize_all(self) -> List[Token]:
        tokens = []
        while True:
            token = self.next_token()
            tokens.append(token)
            if token.type == TokenType.END_OF_FILE:
                break
        return tokens