class RegisterAllocator:
    def __init__(self):
        self.general_regs = ['rax', 'rcx', 'rdx', 'rsi', 'rdi', 'r8', 'r9', 'r10', 'r11']
        self.callee_saved = ['rbx', 'r12', 'r13', 'r14', 'r15']
        self.reg_map = {}
        self.free_regs = self.general_regs.copy()

    def alloc(self, temp_id: int) -> str:
        if temp_id in self.reg_map:
            return self.reg_map[temp_id]
        if self.free_regs:
            reg = self.free_regs.pop(0)
            self.reg_map[temp_id] = reg
            return reg
        return None

    def free(self, temp_id: int) -> None:
        if temp_id in self.reg_map:
            reg = self.reg_map.pop(temp_id)
            self.free_regs.append(reg)

    def get_reg(self, temp_id: int, stack_offset: int = 0) -> str:
        if temp_id in self.reg_map:
            return self.reg_map[temp_id]
        if self.free_regs:
            reg = self.free_regs.pop(0)
            self.reg_map[temp_id] = reg
            return reg
        return f"[rbp{stack_offset:+d}]"

    def clear(self) -> None:
        self.reg_map = {}
        self.free_regs = self.general_regs.copy()
