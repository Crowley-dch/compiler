from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple


class Type(ABC):
    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        pass

    @abstractmethod
    def is_compatible_with(self, other: 'Type', implicit_conversion: bool = True) -> bool:
        pass

    @abstractmethod
    def size(self) -> int:
        pass


class PrimitiveType(Type):
    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, PrimitiveType):
            return False
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    def is_compatible_with(self, other: Type, implicit_conversion: bool = True) -> bool:
        if self == other:
            return True
        if implicit_conversion:
            if self.name == 'int' and isinstance(other, PrimitiveType) and other.name == 'float':
                return True
        return False

    def size(self) -> int:
        sizes = {
            'int': 4,
            'float': 4,
            'bool': 1,
            'void': 0,
            'string': 8
        }
        return sizes.get(self.name, 4)


class StructType(Type):
    def __init__(self, name: str, fields: Dict[str, Type]):
        self.name = name
        self.fields = fields

    def __str__(self) -> str:
        return f"struct {self.name}"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, StructType):
            return False
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    def is_compatible_with(self, other: Type, implicit_conversion: bool = True) -> bool:
        return self == other

    def size(self) -> int:
        total = 0
        for field_type in self.fields.values():
            total += field_type.size()
        return total

    def get_field_type(self, field_name: str) -> Optional[Type]:
        return self.fields.get(field_name)


class FunctionType(Type):
    def __init__(self, param_types: List[Type], return_type: Type):
        self.param_types = param_types
        self.return_type = return_type

    def __str__(self) -> str:
        params = ", ".join(str(t) for t in self.param_types)
        return f"({params}) -> {self.return_type}"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, FunctionType):
            return False
        if len(self.param_types) != len(other.param_types):
            return False
        for p1, p2 in zip(self.param_types, other.param_types):
            if p1 != p2:
                return False
        return self.return_type == other.return_type

    def is_compatible_with(self, other: Type, implicit_conversion: bool = True) -> bool:
        return self == other

    def size(self) -> int:
        return 8


class ArrayType(Type):
    def __init__(self, element_type: Type, length: int):
        self.element_type = element_type
        self.length = length

    def __str__(self) -> str:
        return f"{self.element_type}[{self.length}]"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ArrayType):
            return False
        return (self.element_type == other.element_type and
                self.length == other.length)

    def is_compatible_with(self, other: Type, implicit_conversion: bool = True) -> bool:
        if not isinstance(other, ArrayType):
            return False
        return (self.length == other.length and
                self.element_type.is_compatible_with(other.element_type, implicit_conversion))

    def size(self) -> int:
        return self.element_type.size() * self.length


INT_TYPE = PrimitiveType("int")
FLOAT_TYPE = PrimitiveType("float")
BOOL_TYPE = PrimitiveType("bool")
VOID_TYPE = PrimitiveType("void")
STRING_TYPE = PrimitiveType("string")


class TypeChecker:
    BINARY_OPERATOR_RULES = {
        '+': [
            (('int', 'int'), 'int'),
            (('float', 'float'), 'float'),
            (('int', 'float'), 'float'),
            (('float', 'int'), 'float'),
        ],
        '-': [
            (('int', 'int'), 'int'),
            (('float', 'float'), 'float'),
            (('int', 'float'), 'float'),
            (('float', 'int'), 'float'),
        ],
        '*': [
            (('int', 'int'), 'int'),
            (('float', 'float'), 'float'),
            (('int', 'float'), 'float'),
            (('float', 'int'), 'float'),
        ],
        '/': [
            (('int', 'int'), 'int'),
            (('float', 'float'), 'float'),
            (('int', 'float'), 'float'),
            (('float', 'int'), 'float'),
        ],
        '%': [
            (('int', 'int'), 'int'),
        ],
        '==': [
            (('int', 'int'), 'bool'),
            (('float', 'float'), 'bool'),
            (('int', 'float'), 'bool'),
            (('float', 'int'), 'bool'),
            (('bool', 'bool'), 'bool'),
        ],
        '!=': [
            (('int', 'int'), 'bool'),
            (('float', 'float'), 'bool'),
            (('int', 'float'), 'bool'),
            (('float', 'int'), 'bool'),
            (('bool', 'bool'), 'bool'),
        ],
        '<': [
            (('int', 'int'), 'bool'),
            (('float', 'float'), 'bool'),
            (('int', 'float'), 'bool'),
            (('float', 'int'), 'bool'),
        ],
        '<=': [
            (('int', 'int'), 'bool'),
            (('float', 'float'), 'bool'),
            (('int', 'float'), 'bool'),
            (('float', 'int'), 'bool'),
        ],
        '>': [
            (('int', 'int'), 'bool'),
            (('float', 'float'), 'bool'),
            (('int', 'float'), 'bool'),
            (('float', 'int'), 'bool'),
        ],
        '>=': [
            (('int', 'int'), 'bool'),
            (('float', 'float'), 'bool'),
            (('int', 'float'), 'bool'),
            (('float', 'int'), 'bool'),
        ],
        '&&': [
            (('bool', 'bool'), 'bool'),
        ],
        '||': [
            (('bool', 'bool'), 'bool'),
        ],
    }

    UNARY_OPERATOR_RULES = {
        '-': [
            ('int', 'int'),
            ('float', 'float'),
        ],
        '!': [
            ('bool', 'bool'),
        ],
    }

    @classmethod
    def get_binary_result_type(cls, left_type: Type, right_type: Type, operator: str) -> Optional[Type]:
        left_name = left_type.name if isinstance(left_type, PrimitiveType) else str(left_type)
        right_name = right_type.name if isinstance(right_type, PrimitiveType) else str(right_type)

        rules = cls.BINARY_OPERATOR_RULES.get(operator)
        if not rules:
            return None

        for (lt, rt), result_name in rules:
            if lt == left_name and rt == right_name:
                if result_name == 'int':
                    return INT_TYPE
                elif result_name == 'float':
                    return FLOAT_TYPE
                elif result_name == 'bool':
                    return BOOL_TYPE
                return None

        if (isinstance(left_type, PrimitiveType) and left_type.name in ('int', 'float') and
                isinstance(right_type, PrimitiveType) and right_type.name in ('int', 'float')):
            for (lt, rt), result_name in rules:
                if lt in ('int', 'float') and rt in ('int', 'float'):
                    if result_name == 'int':
                        return INT_TYPE
                    elif result_name == 'float':
                        return FLOAT_TYPE
                    elif result_name == 'bool':
                        return BOOL_TYPE
                    return None

        return None

    @classmethod
    def get_unary_result_type(cls, operand_type: Type, operator: str) -> Optional[Type]:
        op_name = operand_type.name if isinstance(operand_type, PrimitiveType) else str(operand_type)

        rules = cls.UNARY_OPERATOR_RULES.get(operator)
        if not rules:
            return None

        for ot, result_name in rules:
            if ot == op_name:
                if result_name == 'int':
                    return INT_TYPE
                elif result_name == 'float':
                    return FLOAT_TYPE
                elif result_name == 'bool':
                    return BOOL_TYPE
                return None

        if operator == '-' and isinstance(operand_type, PrimitiveType) and operand_type.name in ('int', 'float'):
            return FLOAT_TYPE if operand_type.name == 'float' else INT_TYPE

        return None

    @classmethod
    def is_assignable(cls, target_type: Type, value_type: Type) -> bool:
        return value_type.is_compatible_with(target_type, implicit_conversion=True)

    @classmethod
    def get_common_type(cls, t1: Type, t2: Type) -> Optional[Type]:
        if t1 == t2:
            return t1

        if (isinstance(t1, PrimitiveType) and t1.name == 'int' and
                isinstance(t2, PrimitiveType) and t2.name == 'float'):
            return FLOAT_TYPE
        if (isinstance(t1, PrimitiveType) and t1.name == 'float' and
                isinstance(t2, PrimitiveType) and t2.name == 'int'):
            return FLOAT_TYPE

        return None