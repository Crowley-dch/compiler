from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Any, Union


class OpType(Enum):
    TEMP = "temp"
    VAR = "var"
    LITERAL = "literal"
    LABEL = "label"
    MEM = "mem"


@dataclass
class Operand:
    type: OpType
    value: Any
    type_hint: Optional[str] = None

    def __str__(self) -> str:
        if self.type == OpType.TEMP:
            return f"t{self.value}"
        elif self.type == OpType.VAR:
            return self.value
        elif self.type == OpType.LITERAL:
            if isinstance(self.value, bool):
                return "true" if self.value else "false"
            elif isinstance(self.value, str):
                return f'"{self.value}"'
            return str(self.value)
        elif self.type == OpType.LABEL:
            return self.value
        elif self.type == OpType.MEM:
            return f"[{self.value}]"
        return "?"


class InstType(Enum):
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    MOD = "MOD"
    NEG = "NEG"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    XOR = "XOR"
    CMP_EQ = "CMP_EQ"
    CMP_NE = "CMP_NE"
    CMP_LT = "CMP_LT"
    CMP_LE = "CMP_LE"
    CMP_GT = "CMP_GT"
    CMP_GE = "CMP_GE"
    LOAD = "LOAD"
    STORE = "STORE"
    ALLOCA = "ALLOCA"
    MOVE = "MOVE"
    JUMP = "JUMP"
    JUMP_IF = "JUMP_IF"
    JUMP_IF_NOT = "JUMP_IF_NOT"
    LABEL = "LABEL"
    CALL = "CALL"
    RETURN = "RETURN"
    PARAM = "PARAM"
    PHI = "PHI"


@dataclass
class Instruction:
    type: InstType
    dest: Optional[Operand] = None
    src1: Optional[Operand] = None
    src2: Optional[Operand] = None
    src3: Optional[Operand] = None
    label: Optional[str] = None
    args: Optional[List[Operand]] = None
    comment: Optional[str] = None

    def __str__(self) -> str:
        parts = [self.type.value]

        if self.dest:
            parts.append(str(self.dest))
        if self.src1:
            parts.append(str(self.src1))
        if self.src2:
            parts.append(str(self.src2))
        if self.src3:
            parts.append(str(self.src3))
        if self.label:
            parts.append(self.label)
        if self.args:
            parts.append(", ".join(str(a) for a in self.args))

        result = " ".join(parts)
        if self.comment:
            result += f"  # {self.comment}"
        return result


def temp(index: int, type_hint: str = None) -> Operand:
    return Operand(OpType.TEMP, index, type_hint)


def var(name: str, type_hint: str = None) -> Operand:
    return Operand(OpType.VAR, name, type_hint)


def lit(value: Any, type_hint: str = None) -> Operand:
    return Operand(OpType.LITERAL, value, type_hint)


def label(name: str) -> Operand:
    return Operand(OpType.LABEL, name)


def mem(addr: Operand, type_hint: str = None) -> Operand:
    return Operand(OpType.MEM, addr, type_hint)


def add(dest: Operand, src1: Operand, src2: Operand, comment: str = None) -> Instruction:
    return Instruction(InstType.ADD, dest, src1, src2, comment=comment)


def sub(dest: Operand, src1: Operand, src2: Operand, comment: str = None) -> Instruction:
    return Instruction(InstType.SUB, dest, src1, src2, comment=comment)


def mul(dest: Operand, src1: Operand, src2: Operand, comment: str = None) -> Instruction:
    return Instruction(InstType.MUL, dest, src1, src2, comment=comment)


def div(dest: Operand, src1: Operand, src2: Operand, comment: str = None) -> Instruction:
    return Instruction(InstType.DIV, dest, src1, src2, comment=comment)


def mod(dest: Operand, src1: Operand, src2: Operand, comment: str = None) -> Instruction:
    return Instruction(InstType.MOD, dest, src1, src2, comment=comment)


def neg(dest: Operand, src: Operand, comment: str = None) -> Instruction:
    return Instruction(InstType.NEG, dest, src, comment=comment)


def and_op(dest: Operand, src1: Operand, src2: Operand, comment: str = None) -> Instruction:
    return Instruction(InstType.AND, dest, src1, src2, comment=comment)


def or_op(dest: Operand, src1: Operand, src2: Operand, comment: str = None) -> Instruction:
    return Instruction(InstType.OR, dest, src1, src2, comment=comment)


def not_op(dest: Operand, src: Operand, comment: str = None) -> Instruction:
    return Instruction(InstType.NOT, dest, src, comment=comment)


def cmp_eq(dest: Operand, src1: Operand, src2: Operand, comment: str = None) -> Instruction:
    return Instruction(InstType.CMP_EQ, dest, src1, src2, comment=comment)


def cmp_ne(dest: Operand, src1: Operand, src2: Operand, comment: str = None) -> Instruction:
    return Instruction(InstType.CMP_NE, dest, src1, src2, comment=comment)


def cmp_lt(dest: Operand, src1: Operand, src2: Operand, comment: str = None) -> Instruction:
    return Instruction(InstType.CMP_LT, dest, src1, src2, comment=comment)


def cmp_le(dest: Operand, src1: Operand, src2: Operand, comment: str = None) -> Instruction:
    return Instruction(InstType.CMP_LE, dest, src1, src2, comment=comment)


def cmp_gt(dest: Operand, src1: Operand, src2: Operand, comment: str = None) -> Instruction:
    return Instruction(InstType.CMP_GT, dest, src1, src2, comment=comment)


def cmp_ge(dest: Operand, src1: Operand, src2: Operand, comment: str = None) -> Instruction:
    return Instruction(InstType.CMP_GE, dest, src1, src2, comment=comment)


def load(dest: Operand, addr: Operand, comment: str = None) -> Instruction:
    return Instruction(InstType.LOAD, dest, addr, comment=comment)


def store(addr: Operand, src: Operand, comment: str = None) -> Instruction:
    return Instruction(InstType.STORE, None, addr, src, comment=comment)


def alloca(dest: Operand, size: int, comment: str = None) -> Instruction:
    return Instruction(InstType.ALLOCA, dest, lit(size), comment=comment)


def move(dest: Operand, src: Operand, comment: str = None) -> Instruction:
    return Instruction(InstType.MOVE, dest, src, comment=comment)


def jump(label: str, comment: str = None) -> Instruction:
    return Instruction(InstType.JUMP, label=label, comment=comment)


def jump_if(cond: Operand, label: str, comment: str = None) -> Instruction:
    return Instruction(InstType.JUMP_IF, src1=cond, label=label, comment=comment)


def jump_if_not(cond: Operand, label: str, comment: str = None) -> Instruction:
    return Instruction(InstType.JUMP_IF_NOT, src1=cond, label=label, comment=comment)


def label_inst(name: str, comment: str = None) -> Instruction:
    return Instruction(InstType.LABEL, label=name, comment=comment)


def call(dest: Operand, func: str, args: List[Operand], comment: str = None) -> Instruction:
    return Instruction(InstType.CALL, dest, src1=lit(func), args=args, comment=comment)


def return_inst(value: Optional[Operand] = None, comment: str = None) -> Instruction:
    return Instruction(InstType.RETURN, src1=value, comment=comment)


def param(idx: int, value: Operand, comment: str = None) -> Instruction:
    return Instruction(InstType.PARAM, dest=lit(idx), src1=value, comment=comment)


def phi(dest: Operand, values: List[tuple], comment: str = None) -> Instruction:
    args = []
    for val, blk in values:
        args.append(Operand(OpType.LITERAL, f"({val}, {blk})"))
    return Instruction(InstType.PHI, dest, args=args, comment=comment)
