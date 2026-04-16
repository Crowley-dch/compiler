from typing import Dict, List, Optional, Tuple
from src.parser.ast import (
    ProgramNode, FunctionDeclNode, StructDeclNode, VarDeclStmtNode,
    BlockStmtNode, IfStmtNode, WhileStmtNode, ForStmtNode, ReturnStmtNode,
    ExprStmtNode, LiteralExprNode, IdentifierExprNode, BinaryExprNode,
    UnaryExprNode, CallExprNode, AssignmentExprNode, TypeNode
)
from src.semantic.type_system import (
    Type, INT_TYPE, FLOAT_TYPE, BOOL_TYPE, VOID_TYPE, STRING_TYPE
)
from src.semantic.symbol_table import SymbolTable, Symbol, SymbolKind
from src.ir.ir_instructions import (
    Operand, OpType, Instruction, InstType,
    temp, var, lit, label, mem,
    add, sub, mul, div, mod, neg,
    and_op, or_op, not_op,
    cmp_eq, cmp_ne, cmp_lt, cmp_le, cmp_gt, cmp_ge,
    load, store, alloca, move,
    jump, jump_if, jump_if_not, label_inst,
    call, return_inst, param
)
from src.ir.basic_block import BasicBlock
from src.ir.control_flow import ControlFlowGraph


class IRGenerator:
    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table
        self.temp_counter = 0
        self.label_counter = 0
        self.current_function: Optional[FunctionDeclNode] = None
        self.current_cfg: Optional[ControlFlowGraph] = None
        self.current_block: Optional[BasicBlock] = None
        self.var_to_temp: Dict[str, Operand] = {}
        self.functions: Dict[str, ControlFlowGraph] = {}

    def generate(self, ast: ProgramNode) -> Dict[str, ControlFlowGraph]:
        for decl in ast.declarations:
            if isinstance(decl, FunctionDeclNode):
                self._generate_function(decl)
        return self.functions

    def get_function_ir(self, name: str) -> Optional[ControlFlowGraph]:
        return self.functions.get(name)

    def get_all_ir(self) -> Dict[str, ControlFlowGraph]:
        return self.functions

    def _new_temp(self, type_hint: str = None) -> Operand:
        self.temp_counter += 1
        return temp(self.temp_counter, type_hint)

    def _new_label(self) -> str:
        self.label_counter += 1
        return f"L{self.label_counter}"

    def _generate_function(self, node: FunctionDeclNode) -> None:
        self.current_function = node
        self.temp_counter = 0
        self.label_counter = 0
        self.var_to_temp = {}
        self.current_cfg = ControlFlowGraph()

        entry_block = BasicBlock("entry")
        self.current_cfg.add_block(entry_block)
        self.current_cfg.set_entry(entry_block)
        self.current_block = entry_block

        for param in node.parameters:
            param_temp = self._new_temp()
            self.var_to_temp[param.name] = param_temp
            self.current_block.add_instruction(
                move(param_temp, var(param.name), f"param {param.name}")
            )

        self._generate_block(node.body)

        if not self.current_block.is_terminated():
            self.current_block.add_instruction(
                return_inst(None, "implicit return")
            )

        self.functions[node.name] = self.current_cfg

    def _generate_block(self, node: BlockStmtNode) -> None:
        for stmt in node.statements:
            self._generate_statement(stmt)

    def _generate_statement(self, node) -> None:
        if isinstance(node, VarDeclStmtNode):
            self._generate_var_decl(node)
        elif isinstance(node, ExprStmtNode):
            self._generate_expression(node.expression)
        elif isinstance(node, IfStmtNode):
            self._generate_if(node)
        elif isinstance(node, WhileStmtNode):
            self._generate_while(node)
        elif isinstance(node, ForStmtNode):
            self._generate_for(node)
        elif isinstance(node, ReturnStmtNode):
            self._generate_return(node)

    def _generate_var_decl(self, node: VarDeclStmtNode) -> None:
        temp_op = self._new_temp()
        self.var_to_temp[node.name] = temp_op
        if node.initializer:
            value = self._generate_expression(node.initializer)
            self.current_block.add_instruction(
                move(temp_op, value, f"init {node.name}")
            )
        else:
            self.current_block.add_instruction(
                move(temp_op, lit(0), f"init {node.name} to 0")
            )

    def _generate_expression(self, node) -> Operand:
        if isinstance(node, LiteralExprNode):
            return self._generate_literal(node)
        elif isinstance(node, IdentifierExprNode):
            return self._generate_identifier(node)
        elif isinstance(node, BinaryExprNode):
            return self._generate_binary(node)
        elif isinstance(node, UnaryExprNode):
            return self._generate_unary(node)
        elif isinstance(node, CallExprNode):
            return self._generate_call(node)
        elif isinstance(node, AssignmentExprNode):
            return self._generate_assignment(node)
        return lit(0)

    def _generate_literal(self, node: LiteralExprNode) -> Operand:
        return lit(node.value, str(node.type) if node.type else None)

    def _generate_identifier(self, node: IdentifierExprNode) -> Operand:
        if node.name in self.var_to_temp:
            return self.var_to_temp[node.name]
        return var(node.name, str(node.type) if node.type else None)

    def _generate_binary(self, node: BinaryExprNode) -> Operand:
        left = self._generate_expression(node.left)
        right = self._generate_expression(node.right)
        dest = self._new_temp()

        op = node.operator
        if op == '+':
            self.current_block.add_instruction(add(dest, left, right, str(node)))
        elif op == '-':
            self.current_block.add_instruction(sub(dest, left, right, str(node)))
        elif op == '*':
            self.current_block.add_instruction(mul(dest, left, right, str(node)))
        elif op == '/':
            self.current_block.add_instruction(div(dest, left, right, str(node)))
        elif op == '%':
            self.current_block.add_instruction(mod(dest, left, right, str(node)))
        elif op == '&&':
            self.current_block.add_instruction(and_op(dest, left, right, str(node)))
        elif op == '||':
            self.current_block.add_instruction(or_op(dest, left, right, str(node)))
        elif op == '==':
            self.current_block.add_instruction(cmp_eq(dest, left, right, str(node)))
        elif op == '!=':
            self.current_block.add_instruction(cmp_ne(dest, left, right, str(node)))
        elif op == '<':
            self.current_block.add_instruction(cmp_lt(dest, left, right, str(node)))
        elif op == '<=':
            self.current_block.add_instruction(cmp_le(dest, left, right, str(node)))
        elif op == '>':
            self.current_block.add_instruction(cmp_gt(dest, left, right, str(node)))
        elif op == '>=':
            self.current_block.add_instruction(cmp_ge(dest, left, right, str(node)))

        return dest

    def _generate_unary(self, node: UnaryExprNode) -> Operand:
        operand = self._generate_expression(node.operand)
        dest = self._new_temp()

        if node.operator == '-':
            self.current_block.add_instruction(neg(dest, operand, str(node)))
        elif node.operator == '!':
            self.current_block.add_instruction(not_op(dest, operand, str(node)))

        return dest

    def _generate_call(self, node: CallExprNode) -> Operand:
        args = []
        for arg in node.arguments:
            args.append(self._generate_expression(arg))

        for i, arg in enumerate(args):
            self.current_block.add_instruction(param(i, arg, f"arg{i}"))

        dest = self._new_temp()
        self.current_block.add_instruction(
            call(dest, node.callee.name, args, str(node))
        )
        return dest

    def _generate_assignment(self, node: AssignmentExprNode) -> Operand:
        value = self._generate_expression(node.value)

        if isinstance(node.target, IdentifierExprNode):
            if node.target.name in self.var_to_temp:
                dest = self.var_to_temp[node.target.name]
                self.current_block.add_instruction(move(dest, value, str(node)))
                return value

        return value

    def _generate_if(self, node: IfStmtNode) -> None:
        cond = self._generate_expression(node.condition)

        then_label = self._new_label()
        endif_label = self._new_label()

        self.current_block.add_instruction(
            jump_if_not(cond, endif_label, f"if condition false")
        )

        then_block = BasicBlock(then_label)
        self.current_cfg.add_block(then_block)
        self.current_cfg.add_edge(self.current_block, then_block)
        self.current_block = then_block

        self._generate_statement(node.then_branch)

        if not self.current_block.is_terminated():
            self.current_block.add_instruction(jump(endif_label))

        if node.else_branch:
            else_label = self._new_label()
            else_block = BasicBlock(else_label)
            self.current_cfg.add_block(else_block)
            self.current_cfg.add_edge(self.current_block, else_block)
            self.current_block = else_block

            self._generate_statement(node.else_branch)

            if not self.current_block.is_terminated():
                self.current_block.add_instruction(jump(endif_label))

        endif_block = BasicBlock(endif_label)
        self.current_cfg.add_block(endif_block)
        self.current_cfg.add_edge(self.current_block, endif_block)
        self.current_block = endif_block

    def _generate_while(self, node: WhileStmtNode) -> None:
        header_label = self._new_label()
        body_label = self._new_label()
        exit_label = self._new_label()

        self.current_block.add_instruction(jump(header_label))

        header_block = BasicBlock(header_label)
        self.current_cfg.add_block(header_block)
        self.current_cfg.add_edge(self.current_block, header_block)
        self.current_block = header_block

        cond = self._generate_expression(node.condition)
        self.current_block.add_instruction(
            jump_if_not(cond, exit_label, "while condition false")
        )

        body_block = BasicBlock(body_label)
        self.current_cfg.add_block(body_block)
        self.current_cfg.add_edge(self.current_block, body_block)
        self.current_block = body_block

        self._generate_statement(node.body)

        if not self.current_block.is_terminated():
            self.current_block.add_instruction(jump(header_label))

        exit_block = BasicBlock(exit_label)
        self.current_cfg.add_block(exit_block)
        self.current_cfg.add_edge(self.current_block, exit_block)
        self.current_block = exit_block

    def _generate_for(self, node: ForStmtNode) -> None:
        header_label = self._new_label()
        body_label = self._new_label()
        update_label = self._new_label()
        exit_label = self._new_label()

        if node.init:
            if isinstance(node.init, VarDeclStmtNode):
                self._generate_var_decl(node.init)
            elif isinstance(node.init, ExprStmtNode):
                self._generate_expression(node.init.expression)

        self.current_block.add_instruction(jump(header_label))

        header_block = BasicBlock(header_label)
        self.current_cfg.add_block(header_block)
        self.current_cfg.add_edge(self.current_block, header_block)
        self.current_block = header_block

        if node.condition:
            cond = self._generate_expression(node.condition)
            self.current_block.add_instruction(
                jump_if_not(cond, exit_label, "for condition false")
            )
        else:
            self.current_block.add_instruction(jump(body_label))

        body_block = BasicBlock(body_label)
        self.current_cfg.add_block(body_block)
        self.current_cfg.add_edge(self.current_block, body_block)
        self.current_block = body_block

        self._generate_statement(node.body)

        if not self.current_block.is_terminated():
            self.current_block.add_instruction(jump(update_label))

        update_block = BasicBlock(update_label)
        self.current_cfg.add_block(update_block)
        self.current_cfg.add_edge(self.current_block, update_block)
        self.current_block = update_block

        if node.update:
            self._generate_expression(node.update)

        self.current_block.add_instruction(jump(header_label))

        exit_block = BasicBlock(exit_label)
        self.current_cfg.add_block(exit_block)
        self.current_cfg.add_edge(self.current_block, exit_block)
        self.current_block = exit_block

    def _generate_return(self, node: ReturnStmtNode) -> None:
        if node.value:
            value = self._generate_expression(node.value)
            self.current_block.add_instruction(return_inst(value, str(node)))
        else:
            self.current_block.add_instruction(return_inst(None, "void return"))
