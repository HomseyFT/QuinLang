from typing import Optional
from . import ast as A
from .emitter import Emitter
from .sema import Context

class CodeGen8086:
    def __init__(self):
        self.em = Emitter()

    def generate(self, program: A.Program, ctx: Context) -> str:
        # Emit functions
        for fn in program.functions:
            self._emit_function(fn, ctx)
        return self.em.render()

    def _emit_function(self, fn: A.Function, ctx: Context):
        self.em.emit(f"global {fn.name}")
        self.em.label(fn.name)
        for st in fn.body:
            self._emit_stmt(st, ctx)
        self.em.emit("ret")

    def _emit_stmt(self, st: A.Stmt, ctx: Context):
        if isinstance(st, A.Print):
            self._emit_expr(st.value, ctx)
            # Decide by type at runtime: if expression is string literal we put DX to label and call DOS 09h
            if isinstance(st.value, A.Literal) and isinstance(st.value.value, str):
                lbl = self.em.add_string(st.value.value)
                self.em.emit(f"mov dx, {lbl}")
                self.em.emit("mov ah, 0x09")
                self.em.emit("int 0x21")
            else:
                # assume AX contains integer
                self.em.emit("call rt_print_num16")
        elif isinstance(st, A.Return):
            if st.value:
                self._emit_expr(st.value, ctx)
            self.em.emit("ret")
        elif isinstance(st, A.ExprStmt):
            self._emit_expr(st.expr, ctx)
        elif isinstance(st, A.VarDecl):
            if st.init:
                self._emit_expr(st.init, ctx)
            # variables not persisted in this minimal backend
        elif isinstance(st, A.Assign):
            self._emit_expr(st.value, ctx)
        elif isinstance(st, A.If) or isinstance(st, A.While):
            # Not implemented in minimal version
            pass

    def _emit_expr(self, e: A.Expr, ctx: Context):
        if isinstance(e, A.Literal):
            if isinstance(e.value, int):
                self.em.emit(f"mov ax, {e.value}")
                return
            if isinstance(e.value, str):
                # string handled by caller (PRINT)
                return
        if isinstance(e, A.Identifier):
            # no variables yet; treat as 0
            self.em.emit("xor ax, ax")
            return
        if isinstance(e, A.Unary):
            self._emit_expr(e.right, ctx)
            if e.op == '-':
                self.em.emit("neg ax")
            elif e.op == '!':
                # boolean not: ax = (ax == 0)
                self.em.emit("cmp ax, 0")
                self.em.emit("mov ax, 0")
                self.em.emit("sete al")  # not available on 8086; fallback below
                # Fallback for 8086: set ax=1 if zero
                self.em.emit("jne .not_zero")
                self.em.emit("mov ax, 1")
                self.em.emit(".not_zero:")
            return
        if isinstance(e, A.Binary):
            # Evaluate left, push; evaluate right, then apply
            self._emit_expr(e.left, ctx)
            self.em.emit("push ax")
            self._emit_expr(e.right, ctx)
            self.em.emit("pop bx")
            if e.op == '+':
                self.em.emit("add ax, bx")
            elif e.op == '-':
                self.em.emit("sub bx, ax")
                self.em.emit("mov ax, bx")
            elif e.op == '*':
                self.em.emit("imul bx")
            elif e.op == '/':
                self.em.emit("cwd")
                self.em.emit("idiv bx")
            elif e.op in ('==', '!=', '<', '<=', '>', '>='):
                self.em.emit("cmp bx, ax")
                t = self.em.unique_label("T")
                e_lbl = self.em.unique_label("E")
                if e.op == '==':
                    self.em.emit(f"je {t}")
                elif e.op == '!=':
                    self.em.emit(f"jne {t}")
                elif e.op == '<':
                    self.em.emit(f"jl {t}")
                elif e.op == '<=':
                    self.em.emit(f"jle {t}")
                elif e.op == '>':
                    self.em.emit(f"jg {t}")
                elif e.op == '>=':
                    self.em.emit(f"jge {t}")
                self.em.emit("xor ax, ax")
                self.em.emit(f"jmp {e_lbl}")
                self.em.label(t)
                self.em.emit("mov ax, 1")
                self.em.label(e_lbl)
            return
        if isinstance(e, A.Call):
            # only support calling other functions, ignoring args
            self.em.emit(f"call {e.callee}")
            return
        # default
        self.em.emit("xor ax, ax")