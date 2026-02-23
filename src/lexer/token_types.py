from enum import Enum, auto


class TokenType(Enum):
    KW_IF = auto()
    KW_ELSE = auto()
    KW_WHILE = auto()
    KW_FOR = auto()
    KW_INT = auto()
    KW_FLOAT = auto()
    KW_BOOL = auto()
    KW_RETURN = auto()
    KW_TRUE = auto()
    KW_FALSE = auto()
    KW_VOID = auto()
    KW_STRUCT = auto()
    KW_FN = auto()

    IDENTIFIER = auto()
    INT_LITERAL = auto()
    FLOAT_LITERAL = auto()
    STRING_LITERAL = auto()
    BOOL_LITERAL = auto()

    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    ASSIGN = auto()
    EQ = auto()
    NEQ = auto()
    LT = auto()
    LTE = auto()
    GT = auto()
    GTE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    PLUS_ASSIGN = auto()
    MINUS_ASSIGN = auto()
    STAR_ASSIGN = auto()
    SLASH_ASSIGN = auto()

    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    SEMICOLON = auto()
    COMMA = auto()
    COLON = auto()

    END_OF_FILE = auto()
    ERROR = auto()


KEYWORDS_MAP = {
    'if': TokenType.KW_IF,
    'else': TokenType.KW_ELSE,
    'while': TokenType.KW_WHILE,
    'for': TokenType.KW_FOR,
    'int': TokenType.KW_INT,
    'float': TokenType.KW_FLOAT,
    'bool': TokenType.KW_BOOL,
    'return': TokenType.KW_RETURN,
    'true': TokenType.KW_TRUE,
    'false': TokenType.KW_FALSE,
    'void': TokenType.KW_VOID,
    'struct': TokenType.KW_STRUCT,
    'fn': TokenType.KW_FN,
}

SINGLE_CHAR_TOKENS_MAP = {
    '+': TokenType.PLUS,
    '-': TokenType.MINUS,
    '*': TokenType.STAR,
    '/': TokenType.SLASH,
    '%': TokenType.PERCENT,
    '=': TokenType.ASSIGN,
    '<': TokenType.LT,
    '>': TokenType.GT,
    '!': TokenType.NOT,
    '(': TokenType.LPAREN,
    ')': TokenType.RPAREN,
    '{': TokenType.LBRACE,
    '}': TokenType.RBRACE,
    '[': TokenType.LBRACKET,
    ']': TokenType.RBRACKET,
    ';': TokenType.SEMICOLON,
    ',': TokenType.COMMA,
    ':': TokenType.COLON,
}

DOUBLE_CHAR_TOKENS_MAP = {
    '==': TokenType.EQ,
    '!=': TokenType.NEQ,
    '<=': TokenType.LTE,
    '>=': TokenType.GTE,
    '&&': TokenType.AND,
    '||': TokenType.OR,
    '+=': TokenType.PLUS_ASSIGN,
    '-=': TokenType.MINUS_ASSIGN,
    '*=': TokenType.STAR_ASSIGN,
    '/=': TokenType.SLASH_ASSIGN,
}

SINGLE_CHAR_OPERATORS = set(SINGLE_CHAR_TOKENS_MAP.keys())
DOUBLE_CHAR_OPERATORS = set(DOUBLE_CHAR_TOKENS_MAP.keys())