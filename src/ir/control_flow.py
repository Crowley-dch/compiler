from typing import List, Dict, Set, Optional
from src.ir.basic_block import BasicBlock


class ControlFlowGraph:
    def __init__(self):
        self.blocks: List[BasicBlock] = []
        self.entry_block: Optional[BasicBlock] = None
        self.exit_blocks: List[BasicBlock] = []

    def add_block(self, block: BasicBlock) -> None:
        self.blocks.append(block)

    def set_entry(self, block: BasicBlock) -> None:
        self.entry_block = block

    def add_edge(self, from_block: BasicBlock, to_block: BasicBlock) -> None:
        from_block.add_successor(to_block)
        to_block.add_predecessor(from_block)

    def get_dot(self) -> str:
        lines = ["digraph CFG {", "  node [shape=box];"]

        for block in self.blocks:
            label = block.name.replace("\\", "\\\\")
            lines.append(f'  "{label}" [label="{label}"];')

        for block in self.blocks:
            for succ in block.successors:
                lines.append(f'  "{block.name}" -> "{succ.name}";')

        lines.append("}")
        return "\n".join(lines)

    def __str__(self) -> str:
        lines = []
        for block in self.blocks:
            lines.append(str(block))
        return "\n".join(lines)
