from dataclasses import dataclass
from typing import Any, Optional
from lexer.token_types import TokenType

@dataclass
class Token:
    type: TokenType
    lexeme: str
    line: int
    column: int
    literal_value: Optional[Any] = None

    def __str__(self) -> str:
        if self.literal_value is not None:
            if self.type.name == 'STRING_LITERAL':
                return f"{self.line}:{self.column} {self.type.name} \"{self.lexeme}\" \"{self.literal_value}\""
            else:
                return f"{self.line}:{self.column} {self.type.name} \"{self.lexeme}\" {self.literal_value}"
        return f"{self.line}:{self.column} {self.type.name} \"{self.lexeme}\""