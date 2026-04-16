
from abc import ABC, abstractmethod
from typing import List, Optional, Any
from enum import Enum
from typing import Optional, List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from src.semantic.type_system import Type

class ASTNode(ABC):

    def __init__(self, line: int = 0, column: int = 0):
        self.line = line
        self.column = column

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def accept(self, visitor: 'ASTVisitor') -> Any:
        pass



class TypeNode(ASTNode):

    def __init__(self, name: str, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name  # "int", "float", "bool", "void", или имя структуры

    def __str__(self) -> str:
        return self.name

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_type(self)



class ExpressionNode(ASTNode, ABC):
    def __init__(self, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.type: 'Type' = None


class LiteralExprNode(ExpressionNode):

    def __init__(self, value: Any, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.value = value
        self.type = self._infer_type()

    def _infer_type(self) -> str:
        if isinstance(self.value, int):
            return "int"
        elif isinstance(self.value, float):
            return "float"
        elif isinstance(self.value, bool):
            return "bool"
        elif isinstance(self.value, str):
            return "string"
        else:
            return "unknown"

    def __str__(self) -> str:
        if self.type == "string":
            return f'"{self.value}"'
        elif self.type == "bool":
            return "true" if self.value else "false"
        else:
            return str(self.value)

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_literal(self)


class IdentifierExprNode(ExpressionNode):

    def __init__(self, name: str, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name

    def __str__(self) -> str:
        return self.name

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_identifier(self)


class BinaryExprNode(ExpressionNode):

    def __init__(self, left: ExpressionNode, operator: str, right: ExpressionNode,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.left = left
        self.operator = operator
        self.right = right

    def __str__(self) -> str:
        return f"({self.left} {self.operator} {self.right})"

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_binary(self)


class UnaryExprNode(ExpressionNode):

    def __init__(self, operator: str, operand: ExpressionNode,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.operator = operator
        self.operand = operand

    def __str__(self) -> str:
        return f"({self.operator}{self.operand})"

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_unary(self)


class CallExprNode(ExpressionNode):

    def __init__(self, callee: IdentifierExprNode, arguments: List[ExpressionNode],
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.callee = callee
        self.arguments = arguments

    def __str__(self) -> str:
        args = ", ".join(str(arg) for arg in self.arguments)
        return f"{self.callee}({args})"

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_call(self)


class AssignmentExprNode(ExpressionNode):

    def __init__(self, target: ExpressionNode, operator: str, value: ExpressionNode,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.target = target
        self.operator = operator
        self.value = value

    def __str__(self) -> str:
        return f"({self.target} {self.operator} {self.value})"

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_assignment(self)



class StatementNode(ASTNode, ABC):
    pass


class BlockStmtNode(StatementNode):

    def __init__(self, statements: List[StatementNode], line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.statements = statements

    def __str__(self) -> str:
        if not self.statements:
            return "{}"
        result = "{\n"
        for stmt in self.statements:
            stmt_str = str(stmt).replace("\n", "\n  ")
            result += f"  {stmt_str}\n"
        result += "}"
        return result

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_block(self)


class ExprStmtNode(StatementNode):

    def __init__(self, expression: ExpressionNode, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.expression = expression

    def __str__(self) -> str:
        return f"{self.expression};"

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_expr_stmt(self)


class IfStmtNode(StatementNode):

    def __init__(self, condition: ExpressionNode, then_branch: StatementNode,
                 else_branch: Optional[StatementNode] = None,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def __str__(self) -> str:
        result = f"if ({self.condition}) {self.then_branch}"
        if self.else_branch:
            result += f" else {self.else_branch}"
        return result

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_if(self)


class WhileStmtNode(StatementNode):

    def __init__(self, condition: ExpressionNode, body: StatementNode,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.condition = condition
        self.body = body

    def __str__(self) -> str:
        return f"while ({self.condition}) {self.body}"

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_while(self)


class ForStmtNode(StatementNode):

    def __init__(self, init: Optional[StatementNode],
                 condition: Optional[ExpressionNode],
                 update: Optional[ExpressionNode],
                 body: StatementNode,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body

    def __str__(self) -> str:
        init_str = str(self.init)[:-1] if self.init else ""
        cond_str = str(self.condition) if self.condition else ""
        update_str = str(self.update) if self.update else ""
        return f"for ({init_str}; {cond_str}; {update_str}) {self.body}"

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_for(self)


class ReturnStmtNode(StatementNode):

    def __init__(self, value: Optional[ExpressionNode] = None,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.value = value

    def __str__(self) -> str:
        if self.value:
            return f"return {self.value};"
        return "return;"

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_return(self)


class VarDeclStmtNode(StatementNode):

    def __init__(self, var_type: TypeNode, name: str,
                 initializer: Optional[ExpressionNode] = None,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.var_type = var_type
        self.name = name
        self.initializer = initializer

    def __str__(self) -> str:
        if self.initializer:
            return f"{self.var_type} {self.name} = {self.initializer};"
        return f"{self.var_type} {self.name};"

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_var_decl(self)



class DeclarationNode(ASTNode, ABC):
    pass


class ParamNode(ASTNode):

    def __init__(self, param_type: TypeNode, name: str,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.param_type = param_type
        self.name = name

    def __str__(self) -> str:
        return f"{self.param_type} {self.name}"

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_param(self)


class FunctionDeclNode(DeclarationNode):

    def __init__(self, name: str, parameters: List[ParamNode],
                 return_type: TypeNode, body: BlockStmtNode,
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.body = body

    def __str__(self) -> str:
        params = ", ".join(str(p) for p in self.parameters)
        return f"fn {self.name}({params}) -> {self.return_type} {self.body}"

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_function(self)


class StructDeclNode(DeclarationNode):

    def __init__(self, name: str, fields: List[VarDeclStmtNode],
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name
        self.fields = fields

    def __str__(self) -> str:
        fields_str = "\n".join(f"  {f}" for f in self.fields)
        return f"struct {self.name} {{\n{fields_str}\n}}"

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_struct(self)
        return visitor.visit_struct(self)


class ProgramNode(ASTNode):

    def __init__(self, declarations: List[DeclarationNode],
                 line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.declarations = declarations

    def __str__(self) -> str:
        return "\n\n".join(str(d) for d in self.declarations)

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_program(self)



class ASTVisitor(ABC):

    @abstractmethod
    def visit_program(self, node: ProgramNode) -> Any:
        pass

    @abstractmethod
    def visit_type(self, node: TypeNode) -> Any:
        pass

    # Выражения
    @abstractmethod
    def visit_literal(self, node: LiteralExprNode) -> Any:
        pass

    @abstractmethod
    def visit_identifier(self, node: IdentifierExprNode) -> Any:
        pass

    @abstractmethod
    def visit_binary(self, node: BinaryExprNode) -> Any:
        pass

    @abstractmethod
    def visit_unary(self, node: UnaryExprNode) -> Any:
        pass

    @abstractmethod
    def visit_call(self, node: CallExprNode) -> Any:
        pass

    @abstractmethod
    def visit_assignment(self, node: AssignmentExprNode) -> Any:
        pass

    # Инструкции
    @abstractmethod
    def visit_block(self, node: BlockStmtNode) -> Any:
        pass

    @abstractmethod
    def visit_expr_stmt(self, node: ExprStmtNode) -> Any:
        pass

    @abstractmethod
    def visit_if(self, node: IfStmtNode) -> Any:
        pass

    @abstractmethod
    def visit_while(self, node: WhileStmtNode) -> Any:
        pass

    @abstractmethod
    def visit_for(self, node: ForStmtNode) -> Any:
        pass

    @abstractmethod
    def visit_return(self, node: ReturnStmtNode) -> Any:
        pass

    @abstractmethod
    def visit_var_decl(self, node: VarDeclStmtNode) -> Any:
        pass

    @abstractmethod
    def visit_param(self, node: ParamNode) -> Any:
        pass

    @abstractmethod
    def visit_function(self, node: FunctionDeclNode) -> Any:
        pass

    @abstractmethod
    def visit_struct(self, node: StructDeclNode) -> Any:
        pass



class DebugVisitor(ASTVisitor):

    def __init__(self, indent: int = 0):
        self.indent = indent

    def _print(self, text: str):
        print("  " * self.indent + text)

    def visit_program(self, node: ProgramNode) -> Any:
        self._print(f"Program [line {node.line}]")
        for decl in node.declarations:
            decl.accept(self)

    def visit_type(self, node: TypeNode) -> Any:
        self._print(f"Type: {node.name}")

    def visit_literal(self, node: LiteralExprNode) -> Any:
        self._print(f"Literal: {node.value} ({node.type})")

    def visit_identifier(self, node: IdentifierExprNode) -> Any:
        self._print(f"Identifier: {node.name}")

    def visit_binary(self, node: BinaryExprNode) -> Any:
        self._print(f"Binary: {node.operator}")
        self.indent += 1
        node.left.accept(self)
        node.right.accept(self)
        self.indent -= 1

    def visit_unary(self, node: UnaryExprNode) -> Any:
        self._print(f"Unary: {node.operator}")
        self.indent += 1
        node.operand.accept(self)
        self.indent -= 1

    def visit_call(self, node: CallExprNode) -> Any:
        self._print(f"Call: {node.callee.name}")
        self.indent += 1
        for arg in node.arguments:
            arg.accept(self)
        self.indent -= 1

    def visit_assignment(self, node: AssignmentExprNode) -> Any:
        self._print(f"Assignment: {node.operator}")
        self.indent += 1
        node.target.accept(self)
        node.value.accept(self)
        self.indent -= 1

    def visit_block(self, node: BlockStmtNode) -> Any:
        self._print("Block:")
        self.indent += 1
        for stmt in node.statements:
            stmt.accept(self)
        self.indent -= 1

    def visit_expr_stmt(self, node: ExprStmtNode) -> Any:
        self._print("ExprStmt:")
        self.indent += 1
        node.expression.accept(self)
        self.indent -= 1

    def visit_if(self, node: IfStmtNode) -> Any:
        self._print("IfStmt:")
        self.indent += 1
        self._print("Condition:")
        self.indent += 1
        node.condition.accept(self)
        self.indent -= 1
        self._print("Then:")
        self.indent += 1
        node.then_branch.accept(self)
        self.indent -= 1
        if node.else_branch:
            self._print("Else:")
            self.indent += 1
            node.else_branch.accept(self)
            self.indent -= 1
        self.indent -= 1

    def visit_while(self, node: WhileStmtNode) -> Any:
        self._print("WhileStmt:")
        self.indent += 1
        self._print("Condition:")
        self.indent += 1
        node.condition.accept(self)
        self.indent -= 1
        self._print("Body:")
        self.indent += 1
        node.body.accept(self)
        self.indent -= 1
        self.indent -= 1

    def visit_for(self, node: ForStmtNode) -> Any:
        self._print("ForStmt:")
        self.indent += 1
        if node.init:
            self._print("Init:")
            self.indent += 1
            node.init.accept(self)
            self.indent -= 1
        if node.condition:
            self._print("Condition:")
            self.indent += 1
            node.condition.accept(self)
            self.indent -= 1
        if node.update:
            self._print("Update:")
            self.indent += 1
            node.update.accept(self)
            self.indent -= 1
        self._print("Body:")
        self.indent += 1
        node.body.accept(self)
        self.indent -= 1
        self.indent -= 1

    def visit_return(self, node: ReturnStmtNode) -> Any:
        self._print("ReturnStmt:")
        if node.value:
            self.indent += 1
            node.value.accept(self)
            self.indent -= 1

    def visit_var_decl(self, node: VarDeclStmtNode) -> Any:
        self._print(f"VarDecl: {node.var_type} {node.name}")
        if node.initializer:
            self.indent += 1
            node.initializer.accept(self)
            self.indent -= 1

    def visit_param(self, node: ParamNode) -> Any:
        self._print(f"Param: {node.param_type} {node.name}")

    def visit_function(self, node: FunctionDeclNode) -> Any:
        self._print(f"FunctionDecl: {node.name} -> {node.return_type}")
        self.indent += 1
        self._print("Parameters:")
        self.indent += 1
        for param in node.parameters:
            param.accept(self)
        self.indent -= 1
        self._print("Body:")
        self.indent += 1
        node.body.accept(self)
        self.indent -= 1
        self.indent -= 1

    def visit_struct(self, node: StructDeclNode) -> Any:
        self._print(f"StructDecl: {node.name}")
        self.indent += 1
        for field in node.fields:
            field.accept(self)
        self.indent -= 1



if __name__ == "__main__":
    prog = ProgramNode([
        FunctionDeclNode(
            name="main",
            parameters=[],
            return_type=TypeNode("void", 1, 1),
            body=BlockStmtNode([
                VarDeclStmtNode(
                    var_type=TypeNode("int", 2, 5),
                    name="x",
                    initializer=LiteralExprNode(42, 2, 15),
                    line=2, column=5
                ),
                ReturnStmtNode(
                    value=IdentifierExprNode("x", 3, 5),
                    line=3, column=5
                )
            ], line=1, column=11),
            line=1, column=1
        )
    ], line=1, column=1)

    print("=== AST Debug Output ===")
    visitor = DebugVisitor()
    prog.accept(visitor)

    print("\n=== Pretty Print ===")
    print(prog)