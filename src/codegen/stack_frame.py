class StackFrame:
    def __init__(self):
        self.locals = {}
        self.local_offset = 0
        self.temp_offset = 0
        self.total_size = 0

    def add_local(self, name: str, size: int = 8) -> int:
        self.local_offset -= size
        self.locals[name] = self.local_offset
        self.total_size = max(self.total_size, abs(self.local_offset))
        return self.local_offset

    def add_temp(self, temp_id: int, size: int = 8) -> int:
        self.temp_offset -= size
        self.locals[f"t{temp_id}"] = self.temp_offset
        self.total_size = max(self.total_size, abs(self.temp_offset))
        return self.temp_offset

    def get_offset(self, name: str) -> int:
        return self.locals.get(name, 0)

    def get_frame_size(self) -> int:
        return (self.total_size + 15) & ~15

    def clear(self) -> None:
        self.locals = {}
        self.local_offset = 0
        self.temp_offset = 0
        self.total_size = 0
