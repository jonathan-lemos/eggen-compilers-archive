#!/usr/bin/python
from grammar import grammar
from SemAnalyzer import analyze_prgm, SemAnalyzerException
from CodeGen import default_gen
import sys
import re

patterns = [
    ("RELOP", r">=|<=|==|!=|>|<"),
    ("ADDOP", r"\+|-"),
    ("MULOP", r"\*|/"),
    ("NUM", r"\d+"),
    ("ID", r"[A-Za-z]+")
]

cfg = [
    "program -> declaration-list",
    "declaration-list -> declaration-list declaration | declaration",
    "declaration -> var-declaration | fun-declaration",
    "var-declaration -> type-specifier ID ; | type-specifier ID [ NUM ] ;",
    "type-specifier -> int | void",
    "fun-declaration -> type-specifier ID ( params ) compound-stmt",
    "params -> param-list | void",
    "param-list -> param-list , param | param",
    "param -> type-specifier ID | type-specifier ID [ ]",
    "compound-stmt -> { local-declarations statement-list }",
    "local-declarations -> local-declarations var-declaration | #",
    "statement-list -> statement-list statement | #",
    "statement -> expression-stmt | compound-stmt | selection-stmt | iteration-stmt | return-stmt",
    "expression-stmt -> expression ; | ;",
    "selection-stmt -> if ( expression ) statement | if ( expression ) statement else statement",
    "iteration-stmt -> while ( expression ) statement",
    "return-stmt -> return ; | return expression ;",
    "expression -> var = expression | simple-expression",
    "var -> ID | ID [ expression ]",
    "simple-expression -> additive-expression RELOP additive-expression | additive-expression",
    "additive-expression -> additive-expression ADDOP term | term",
    "term -> term MULOP factor | factor",
    "factor -> ( expression ) | var | call | NUM",
    "call -> ID ( args )",
    "args -> arg-list | #",
    "arg-list -> arg-list , expression | expression"
]

string = "\n".join(re.sub(r"//.*$", "", x) for x in re.sub(r"/\*.*?\*/", "", open(sys.argv[1], "r").read(), flags=re.MULTILINE | re.DOTALL).split("\n"))
gram = grammar(cfg)
x = gram.parse(gram.lex(string, patterns))

# print(repr(x))

if not x:
    print("REJECT")
    exit(0)
try:
    analyze_prgm(x)
    # print("ACCEPT")
except SemAnalyzerException as e:
    print("REJECT")
    exit(0)
y = default_gen(x)
print("\n".join(" ".join(str(z).ljust(12) for z in x) for x in y))

