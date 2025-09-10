
# FuncLang Interpreter
# Autor: ChatGPT
# Uso: python func_lang.py [archivo]    (por defecto lee 'codigo.txt')

from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any, Union
import math

# (All classes were defined above within this notebook cell.)
# To keep this single-file executable, we embed everything here by duplicating the implementation.
# For maintainability in this environment, we will import from this notebook context if available.
# However, to ensure standalone usage after download, we reproduce the implementation below.

# =====================
# Lexer


class Token:
    def __init__(self, type, value, line, col):
        self.type = type
        self.value = value
        self.line = line
        self.col = col

class LexerError(Exception):
    pass

class ParserError(Exception):
    pass

class SemanticError(Exception):
    pass

class RuntimeEvalError(Exception):
    pass

KEYWORDS = {
    "func": "FUNC",
    "print": "PRINT",
}

SINGLE_CHAR_TOKENS = {
    '+': 'PLUS',
    '-': 'MINUS',
    '*': 'MUL',
    '/': 'DIV',
    '^': 'POW',
    '(': 'LPAREN',
    ')': 'RPAREN',
    ',': 'COMMA',
    ';': 'SEMI',
    '=': 'EQ',
}

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.col = 1

    def peek(self) -> str:
        if self.pos >= len(self.text):
            return '\0'
        return self.text[self.pos]

    def advance(self):
        if self.pos < len(self.text):
            ch = self.text[self.pos]
            self.pos += 1
            if ch == '\n':
                self.line += 1
                self.col = 1
            else:
                self.col += 1

    def lex(self) -> list:
        tokens = []
        while True:
            ch = self.peek()
            if ch == '\0':
                tokens.append(Token('EOF', None, self.line, self.col))
                break
            elif ch.isspace():
                self.advance()
                continue
            elif ch.isalpha() or ch == '_':
                start_line, start_col = self.line, self.col
                ident = []
                while self.peek().isalnum() or self.peek() == '_':
                    ident.append(self.peek())
                    self.advance()
                ident_str = ''.join(ident)
                ttype = KEYWORDS.get(ident_str, 'ID')
                tokens.append(Token(ttype, ident_str, start_line, start_col))
            elif ch.isdigit():
                start_line, start_col = self.line, self.col
                num = []
                while self.peek().isdigit():
                    num.append(self.peek())
                    self.advance()
                tokens.append(Token('NUMBER', ''.join(num), start_line, start_col))
            elif ch in SINGLE_CHAR_TOKENS:
                ttype = SINGLE_CHAR_TOKENS[ch]
                tokens.append(Token(ttype, ch, self.line, self.col))
                self.advance()
            else:
                err_line, err_col = self.line, self.col
                bad = self.peek()
                self.advance()
                raise LexerError(f"Símbolo desconocido '{bad}' en línea {err_line}, columna {err_col}")
        return tokens

# =====================
# AST Nodes
# =====================

class Number:
    def __init__(self, value):
        self.value = int(value)

class Var:
    def __init__(self, name):
        self.name = name

class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Call:
    def __init__(self, name, args):
        self.name = name
        self.args = args

class FuncDef:
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class PrintStmt:
    def __init__(self, call):
        self.call = call

# =====================
# Parser
# =====================

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0
        self.errors = []
        self.functions_seen = {}
        self.current_function = None

    def peek(self):
        if self.i >= len(self.tokens):
            last = self.tokens[-1] if self.tokens else Token('EOF', None, 1, 1)
            return Token('EOF', None, last.line, last.col)
        return self.tokens[self.i]

    def advance(self):
        tok = self.peek()
        if self.i < len(self.tokens):
            self.i += 1
        return tok

    def match(self, *types):
        if self.peek().type in types:
            return self.advance()
        return None

    def expect(self, ttype):
        tok = self.peek()
        if tok.type == ttype:
            return self.advance()
        else:
            raise ParserError(f"Se esperaba {ttype} pero se encontró {tok.type} en línea {tok.line}, columna {tok.col}")

    def parse(self):
        stmts = []
        while self.peek().type != 'EOF':
            try:
                if self.peek().type == 'FUNC':
                    fd = self.parse_func_def()
                    if fd:
                        if fd.name in self.functions_seen:
                            self.errors.append(f"Error: función '{fd.name}' redefinida (línea {self.peek().line})")
                        else:
                            self.functions_seen[fd.name] = fd
                            stmts.append(fd)
                elif self.peek().type == 'PRINT':
                    pr = self.parse_print()
                    if pr:
                        call_name = pr.call.name
                        if call_name not in self.functions_seen:
                            self.errors.append(f"Error: función no definida '{call_name}' (línea {self.peek().line})")
                        else:
                            expected = len(self.functions_seen[call_name].params)
                            if len(pr.call.args) != expected:
                                self.errors.append(f"Error: número incorrecto de parámetros en {call_name} (esperado {expected}, recibido {len(pr.call.args)})")
                            stmts.append(pr)
                else:
                    tok = self.peek()
                    raise ParserError(f"Instrucción inválida en línea {tok.line}, columna {tok.col}. Se esperaba 'func' o 'print'.")
            except ParserError as e:
                self.errors.append(str(e))
                self.sync_to_semi()
                self.match('SEMI')
            except SemanticError as e:
                self.errors.append(str(e))
                self.sync_to_semi()
                self.match('SEMI')
        return stmts, self.errors

    def sync_to_semi(self):
        while self.peek().type not in ('SEMI', 'EOF'):
            self.advance()

    def parse_func_def(self):
        self.expect('FUNC')
        name_tok = self.expect('ID')
        name = name_tok.value
        self.expect('LPAREN')
        params = self.parse_param_list()
        self.expect('RPAREN')
        self.expect('EQ')
        prev_current = self.current_function
        self.current_function = name
        body = self.parse_expr()
        self.current_function = prev_current
        self.expect('SEMI')
        return FuncDef(name, params, body)

    def parse_print(self):
        self.expect('PRINT')
        call = self.parse_call(check_semantics=True)
        self.expect('SEMI')
        return PrintStmt(call)

    def parse_param_list(self):
        params = []
        if self.peek().type == 'ID':
            params.append(self.advance().value)
            while self.match('COMMA'):
                tok = self.expect('ID')
                params.append(tok.value)
        return params

    def parse_call(self, check_semantics=False):
        name_tok = self.expect('ID')
        name = name_tok.value
        self.expect('LPAREN')
        args = []
        if self.peek().type != 'RPAREN':
            args.append(self.parse_expr())
            while self.match('COMMA'):
                args.append(self.parse_expr())
        self.expect('RPAREN')
        if check_semantics or self.current_function is not None:
            if name != self.current_function and name not in self.functions_seen:
                raise SemanticError(f"Error: función no definida '{name}' (línea {name_tok.line})")
            if name in self.functions_seen:
                expected = len(self.functions_seen[name].params)
                if expected != len(args):
                    raise SemanticError(f"Error: número incorrecto de parámetros en {name} (esperado {expected}, recibido {len(args)})")
        return Call(name, args)

    def parse_expr(self):
        node = self.parse_term()
        while self.peek().type in ('PLUS', 'MINUS'):
            op = self.advance().type
            right = self.parse_term()
            node = BinOp(node, op, right)
        return node

    def parse_term(self):
        node = self.parse_power()
        while self.peek().type in ('MUL', 'DIV'):
            op = self.advance().type
            right = self.parse_power()
            node = BinOp(node, op, right)
        return node

    def parse_power(self):
        left = self.parse_factor()
        if self.peek().type == 'POW':
            self.advance()
            right = self.parse_power()
            return BinOp(left, 'POW', right)
        return left

    def parse_factor(self):
        tok = self.peek()
        if tok.type == 'NUMBER':
            self.advance()
            return Number(int(tok.value))
        elif tok.type == 'ID':
            if self._lookahead().type == 'LPAREN':
                return self.parse_call(check_semantics=False)
            else:
                self.advance()
                if self.current_function is None:
                    raise SemanticError(f"Error: identificador '{tok.value}' fuera de contexto de función (línea {tok.line})")
                return Var(tok.value)
        elif tok.type == 'LPAREN':
            self.advance()
            expr = self.parse_expr()
            if self.peek().type != 'RPAREN':
                raise ParserError(f"Paréntesis desbalanceados en línea {tok.line}")
            self.expect('RPAREN')
            return expr
        else:
            raise ParserError(f"Factor inesperado '{tok.type}' en línea {tok.line}, columna {tok.col}")

    def _lookahead(self):
        if self.i + 1 < len(self.tokens):
            return self.tokens[self.i + 1]
        return Token('EOF', None, self.peek().line, self.peek().col)

# =====================
# Interpreter / Evaluator
# =====================

class Interpreter:
    def __init__(self, stmts):
        self.funcs = {}
        self.prints = []
        for s in stmts:
            if isinstance(s, FuncDef):
                self.funcs[s.name] = s
            elif isinstance(s, PrintStmt):
                self.prints.append(s)

    def eval(self):
        outputs = []
        errors = []
        for pr in self.prints:
            try:
                value = self.eval_call(pr.call, env={})
                if isinstance(value, float) and value.is_integer():
                    value = int(value)
                outputs.append(str(value))
            except RuntimeEvalError as e:
                errors.append(str(e))
        return outputs, errors

    def eval_expr(self, node, env):
        if isinstance(node, Number):
            return float(node.value)
        elif isinstance(node, Var):
            if node.name not in env:
                raise RuntimeEvalError(f"Error: variable no definida '{node.name}'")
            return float(env[node.name])
        elif isinstance(node, BinOp):
            left = self.eval_expr(node.left, env)
            if node.op == 'DIV':
                right = self.eval_expr(node.right, env)
                if right == 0:
                    raise RuntimeEvalError("Error: división por cero")
                return left / right
            elif node.op == 'MUL':
                right = self.eval_expr(node.right, env)
                return left * right
            elif node.op == 'PLUS':
                right = self.eval_expr(node.right, env)
                return left + right
            elif node.op == 'MINUS':
                right = self.eval_expr(node.right, env)
                return left - right
            elif node.op == 'POW':
                right = self.eval_expr(node.right, env)
                try:
                    return float(left ** right)
                except OverflowError:
                    raise RuntimeEvalError("Error: overflow en potencia")
            else:
                raise RuntimeEvalError(f"Error: operador desconocido '{node.op}'")
        elif isinstance(node, Call):
            return self.eval_call(node, env)
        else:
            raise RuntimeEvalError("Error: nodo de AST desconocido")

    def eval_call(self, call, env):
        if call.name not in self.funcs:
            raise RuntimeEvalError(f"Error: función no definida '{call.name}'")
        fdef = self.funcs[call.name]
        if len(call.args) != len(fdef.params):
            raise RuntimeEvalError(f"Error: número incorrecto de parámetros en {call.name} (esperado {len(fdef.params)}, recibido {len(call.args)})")
        arg_vals = [self.eval_expr(arg, env) for arg in call.args]
        new_env = {p: v for p, v in zip(fdef.params, arg_vals)}
        return self.eval_expr(fdef.body, new_env)

# =====================
# CLI
# =====================

def main():
    import sys
    file = "codigo.txt"
    if len(sys.argv) > 1:
        file = sys.argv[1]
    try:
        with open(file, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"No se encontró el archivo {file}. Colócalo en el mismo directorio o pásalo como argumento.")
        sys.exit(1)

    try:
        lexer = Lexer(source)
        tokens = lexer.lex()
    except LexerError as e:
        print(str(e))
        sys.exit(1)

    parser = Parser(tokens)
    stmts, parse_errors = parser.parse()

    for err in parse_errors:
        print(err)

    intr = Interpreter(stmts)
    outputs, runtime_errors = intr.eval()
    for err in runtime_errors:
        print(err)
    for out in outputs:
        print(out)

if __name__ == "__main__":
    main()
