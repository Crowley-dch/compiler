
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from dataclasses import dataclass, field
from src.semantic.type_system import Type, INT_TYPE, FLOAT_TYPE, BOOL_TYPE, VOID_TYPE, STRING_TYPE


class SymbolKind(Enum):
    VARIABLE = "variable"
    PARAMETER = "parameter"
    FUNCTION = "function"
    STRUCT = "struct"
    FIELD = "field"


@dataclass
class Symbol:

    name: str
    kind: SymbolKind
    type: Type
    line: int
    column: int
    param_types: List[Type] = field(default_factory=list)
    fields: Dict[str, Type] = field(default_factory=dict)
    stack_offset: int = 0
    is_initialized: bool = False

    def __str__(self) -> str:
        if self.kind == SymbolKind.FUNCTION:
            params = ", ".join(str(t) for t in self.param_types)
            return f"{self.name}: {self.kind.value}({params}) -> {self.type}"
        elif self.kind == SymbolKind.STRUCT:
            fields_str = ", ".join(f"{n}:{t}" for n, t in self.fields.items())
            return f"{self.name}: {self.kind.value} {{ {fields_str} }}"
        else:
            return f"{self.name}: {self.kind.value} {self.type}"

    def is_function(self) -> bool:
        return self.kind == SymbolKind.FUNCTION

    def is_struct(self) -> bool:
        return self.kind == SymbolKind.STRUCT

    def is_variable(self) -> bool:
        return self.kind in (SymbolKind.VARIABLE, SymbolKind.PARAMETER)


class Scope:

    def __init__(self, name: str = "", parent: Optional['Scope'] = None):
        self.name = name
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}
        self.depth = parent.depth + 1 if parent else 0

    def insert(self, symbol: Symbol) -> bool:
        if symbol.name in self.symbols:
            return False
        self.symbols[symbol.name] = symbol
        return True

    def lookup_local(self, name: str) -> Optional[Symbol]:
        return self.symbols.get(name)

    def lookup(self, name: str) -> Optional[Symbol]:
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def get_all_symbols(self) -> List[Symbol]:
        return list(self.symbols.values())

    def __str__(self) -> str:
        lines = []
        if self.name:
            lines.append(f"Scope: {self.name} (depth={self.depth})")
        else:
            lines.append(f"Scope (depth={self.depth})")

        for symbol in self.symbols.values():
            lines.append(f"  {symbol}")

        return "\n".join(lines)


class SymbolTable:

    def __init__(self):
        self.global_scope = Scope(name="global")
        self.current_scope = self.global_scope
        self.scope_stack: List[Scope] = [self.global_scope]
        self.all_symbols: List[Symbol] = []
        self._next_offset = 0

    def enter_scope(self, name: str = "") -> None:

        new_scope = Scope(name=name, parent=self.current_scope)
        self.current_scope = new_scope
        self.scope_stack.append(new_scope)

    def exit_scope(self) -> None:

        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
            self.current_scope = self.scope_stack[-1]

    def current_depth(self) -> int:
        return self.current_scope.depth

    def insert(self, symbol: Symbol) -> bool:

        if self.current_scope.insert(symbol):
            self.all_symbols.append(symbol)
            return True
        return False

    def lookup(self, name: str) -> Optional[Symbol]:

        return self.current_scope.lookup(name)

    def lookup_local(self, name: str) -> Optional[Symbol]:

        return self.current_scope.lookup_local(name)

    def lookup_global(self, name: str) -> Optional[Symbol]:

        return self.global_scope.lookup_local(name)

    def is_defined_in_current_scope(self, name: str) -> bool:
        return self.lookup_local(name) is not None

    def is_defined(self, name: str) -> bool:

        return self.lookup(name) is not None

    def get_symbols_in_scope(self) -> List[Symbol]:
        return self.current_scope.get_all_symbols()

    def get_all_symbols(self) -> List[Symbol]:

        return self.all_symbols.copy()

    def get_scope_stack(self) -> List[Scope]:

        return self.scope_stack.copy()

    def allocate_offset(self, size: int = 4) -> int:

        offset = self._next_offset
        self._next_offset += size
        return offset

    def reset_offsets(self) -> None:
        self._next_offset = 0

    def print_table(self) -> str:

        lines = []
        lines.append("SYMBOL TABLE")

        def print_scope(scope: Scope, indent: int = 0) -> None:
            indent_str = "  " * indent
            lines.append(f"{indent_str}{scope}")
            for child in self._get_child_scopes(scope):
                print_scope(child, indent + 1)

        print_scope(self.global_scope)

        return "\n".join(lines)

    def _get_child_scopes(self, scope: Scope) -> List[Scope]:
        children = []
        for s in self.scope_stack:
            if s.parent == scope and s != scope:
                children.append(s)
        return children

    def dump_json(self) -> dict:


        def symbol_to_dict(sym: Symbol) -> dict:
            return {
                "name": sym.name,
                "kind": sym.kind.value,
                "type": str(sym.type),
                "line": sym.line,
                "column": sym.column,
                "param_types": [str(t) for t in sym.param_types] if sym.param_types else None,
                "fields": {k: str(v) for k, v in sym.fields.items()} if sym.fields else None,
                "stack_offset": sym.stack_offset,
                "is_initialized": sym.is_initialized
            }

        def scope_to_dict(scope: Scope) -> dict:
            return {
                "name": scope.name,
                "depth": scope.depth,
                "symbols": [symbol_to_dict(s) for s in scope.symbols.values()],
                "children": [scope_to_dict(child) for child in self._get_child_scopes(scope)]
            }

        return scope_to_dict(self.global_scope)


BUILTIN_FUNCTIONS = {
    # Пример встроенной функции print
    # 'print': Symbol(
    #     name="print",
    #     kind=SymbolKind.FUNCTION,
    #     type=VOID_TYPE,
    #     line=0,
    #     column=0,
    #     param_types=[STRING_TYPE]
    # )
}
