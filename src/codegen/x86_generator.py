from typing import Dict, List, Optional
from src.ir.ir_instructions import Instruction, InstType, Operand, OpType
from src.ir.basic_block import BasicBlock
from src.ir.control_flow import ControlFlowGraph


class X86Generator:
    def __init__(self):
        self.output_lines = []
        self.temp_to_stack = {}
        self.stack_offset = 0

    def generate(self, functions: Dict[str, ControlFlowGraph]) -> str:
        self.output_lines = []
        self.output_lines.append("section .text")
        self.output_lines.append("global main")
        self.output_lines.append("")

        for name, cfg in functions.items():
            self._generate_function(name, cfg)

        return "\n".join(self.output_lines)

    def _generate_function(self, name: str, cfg: ControlFlowGraph) -> None:
        self.temp_to_stack = {}
        self.var_to_stack = {}
        self.var_counter = 0
        self.label_counter = 0

        self.output_lines.append(f"; Function: {name}")
        self.output_lines.append(f"global {name}")
        self.output_lines.append(f"{name}:")
        self.output_lines.append(f"    push rbp")
        self.output_lines.append(f"    mov rbp, rsp")

        self._allocate_locals(cfg)

        for block in cfg.blocks:
            if block.name != "entry":
                self.output_lines.append(f"{block.name}:")
            for inst in block.instructions:
                self._generate_instruction(inst)

        self.output_lines.append(f"    pop rbp")
        self.output_lines.append(f"    ret")
        self.output_lines.append("")

    def _allocate_locals(self, cfg: ControlFlowGraph) -> None:
        max_temp = 0
        for block in cfg.blocks:
            for inst in block.instructions:
                if inst.dest and inst.dest.type == OpType.TEMP:
                    max_temp = max(max_temp, inst.dest.value)

        if max_temp > 0:
            stack_size = (max_temp * 4 + 15) & ~15
            self.output_lines.append(f"    sub rsp, {stack_size}")

            for i in range(1, max_temp + 1):
                self.temp_to_stack[i] = -(i * 4)

    def _get_operand(self, op: Optional[Operand]) -> str:
        if op is None:
            return "0"
        if op.type == OpType.TEMP:
            if op.value in self.temp_to_stack:
                return f"dword [rbp{self.temp_to_stack[op.value]:+d}]"
            return "eax"
        elif op.type == OpType.VAR:
            if op.value not in self.var_to_stack:
                self.var_counter += 1
                self.var_to_stack[op.value] = -(self.var_counter * 4)
            return f"dword [rbp{self.var_to_stack[op.value]:+d}]"
        elif op.type == OpType.LITERAL:
            if isinstance(op.value, bool):
                return "1" if op.value else "0"
            return str(op.value)
        return str(op.value)

    def _generate_instruction(self, inst: Instruction) -> None:
        if inst.type == InstType.MOVE:
            dest = self._get_operand(inst.dest)
            src = self._get_operand(inst.src1)

            if dest.startswith('[') and src.startswith('['):
                self.output_lines.append(f"    mov eax, {src}")
                self.output_lines.append(f"    mov {dest}, eax")
            else:
                self.output_lines.append(f"    mov dword {dest}, {src}")

        elif inst.type == InstType.ADD:
            dest = self._get_operand(inst.dest)
            src1 = self._get_operand(inst.src1)
            src2 = self._get_operand(inst.src2)

            self.output_lines.append(f"    mov eax, {src1}")
            self.output_lines.append(f"    add eax, {src2}")
            self.output_lines.append(f"    mov {dest}, eax")

        elif inst.type == InstType.SUB:
            dest = self._get_operand(inst.dest)
            src1 = self._get_operand(inst.src1)
            src2 = self._get_operand(inst.src2)

            self.output_lines.append(f"    mov eax, {src1}")
            self.output_lines.append(f"    sub eax, {src2}")
            self.output_lines.append(f"    mov {dest}, eax")

        elif inst.type == InstType.MUL:
            dest = self._get_operand(inst.dest)
            src1 = self._get_operand(inst.src1)
            src2 = self._get_operand(inst.src2)

            self.output_lines.append(f"    mov eax, {src1}")
            self.output_lines.append(f"    imul eax, {src2}")
            self.output_lines.append(f"    mov {dest}, eax")


        elif inst.type == InstType.RETURN:
            if inst.src1:
                src = self._get_operand(inst.src1)
                self.output_lines.append(f"    mov eax, {src}")
            else:
                self.output_lines.append(f"    mov eax, 0")
        elif inst.comment:
            self.output_lines.append(f"    ; {inst.comment}")