from typing import List, Optional, Set
from src.ir.ir_instructions import Instruction


class BasicBlock:
    def __init__(self, name: str):
        self.name = name
        self.instructions: List[Instruction] = []
        self.predecessors: Set['BasicBlock'] = set()
        self.successors: Set['BasicBlock'] = set()

    def add_instruction(self, inst: Instruction) -> None:
        self.instructions.append(inst)

    def add_predecessor(self, block: 'BasicBlock') -> None:
        self.predecessors.add(block)

    def add_successor(self, block: 'BasicBlock') -> None:
        self.successors.add(block)

    def is_terminated(self) -> bool:
        if not self.instructions:
            return False
        last = self.instructions[-1]
        return last.type.value in ['JUMP', 'JUMP_IF', 'JUMP_IF_NOT', 'RETURN']

    def __str__(self) -> str:
        lines = [f"{self.name}:"]
        for inst in self.instructions:
            lines.append(f"    {inst}")
        return "\n".join(lines)
