from dataclasses import dataclass
from typing import List


@dataclass
class CompileError:
    message: str
    line: int
    column: int
    severity: str = "error"

    def __str__(self) -> str:
        return f"{self.severity.upper()}: {self.line}:{self.column}: {self.message}"


class ErrorHandler:
    def __init__(self):
        self.errors: List[CompileError] = []
        self.warnings: List[CompileError] = []

    def add_error(self, message: str, line: int, column: int) -> None:
        self.errors.append(CompileError(message, line, column, "error"))

    def add_warning(self, message: str, line: int, column: int) -> None:
        self.warnings.append(CompileError(message, line, column, "warning"))

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        return len(self.warnings) > 0

    def print_all(self) -> None:
        for error in self.errors:
            print(error)
        for warning in self.warnings:
            print(warning)

    def clear(self) -> None:
        self.errors.clear()
        self.warnings.clear()