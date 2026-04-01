from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class SemanticErrorCode(Enum):
    UNDECLARED_IDENTIFIER = "undeclared_identifier"
    DUPLICATE_DECLARATION = "duplicate_declaration"
    TYPE_MISMATCH = "type_mismatch"
    ARGUMENT_COUNT_MISMATCH = "argument_count_mismatch"
    ARGUMENT_TYPE_MISMATCH = "argument_type_mismatch"
    INVALID_RETURN_TYPE = "invalid_return_type"
    INVALID_CONDITION_TYPE = "invalid_condition_type"
    USE_BEFORE_DECLARATION = "use_before_declaration"
    INVALID_ASSIGNMENT_TARGET = "invalid_assignment_target"
    UNINITIALIZED_VARIABLE = "uninitialized_variable"
    MISSING_RETURN = "missing_return"
    INCOMPATIBLE_TYPES = "incompatible_types"
    INVALID_OPERATOR = "invalid_operator"
    NOT_A_FUNCTION = "not_a_function"
    NOT_A_STRUCT = "not_a_struct"
    FIELD_NOT_FOUND = "field_not_found"


@dataclass
class SemanticError:
    code: SemanticErrorCode
    message: str
    line: int
    column: int
    context: Optional[str] = None
    expected: Optional[str] = None
    found: Optional[str] = None
    suggestion: Optional[str] = None

    def __str__(self) -> str:
        parts = []
        parts.append(f"semantic error: {self.message}")
        parts.append(f"  --> {self.line}:{self.column}")

        if self.context:
            parts.append(f"  |")
            parts.append(f"  | {self.context}")

        parts.append(f"  |")

        if self.expected and self.found:
            parts.append(f"  = expected: {self.expected}")
            parts.append(f"  = found: {self.found}")

        if self.suggestion:
            parts.append(f"  = note: {self.suggestion}")

        return "\n".join(parts)


class SemanticErrorCollector:
    def __init__(self):
        self.errors: List[SemanticError] = []
        self.warnings: List[SemanticError] = []

    def add_error(
            self,
            code: SemanticErrorCode,
            message: str,
            line: int,
            column: int,
            context: Optional[str] = None,
            expected: Optional[str] = None,
            found: Optional[str] = None,
            suggestion: Optional[str] = None
    ) -> None:
        error = SemanticError(
            code=code,
            message=message,
            line=line,
            column=column,
            context=context,
            expected=expected,
            found=found,
            suggestion=suggestion
        )
        self.errors.append(error)

    def add_warning(
            self,
            code: SemanticErrorCode,
            message: str,
            line: int,
            column: int,
            context: Optional[str] = None,
            suggestion: Optional[str] = None
    ) -> None:
        warning = SemanticError(
            code=code,
            message=message,
            line=line,
            column=column,
            context=context,
            suggestion=suggestion
        )
        self.warnings.append(warning)

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        return len(self.warnings) > 0

    def print_all(self) -> None:
        for error in self.errors:
            print(error)
        for warning in self.warnings:
            print(f"warning: {warning}")

    def clear(self) -> None:
        self.errors.clear()
        self.warnings.clear()

    def get_error_count(self) -> int:
        return len(self.errors)

    def get_warning_count(self) -> int:
        return len(self.warnings)
