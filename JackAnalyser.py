import os
from tokenizer.JackTokenizer import JackTokenizer
from CompilationEngine.CompilationEngine import CompilationEngine
jt = JackTokenizer(os.path.abspath('/Users/gautham/Desktop/nand2tetris/projects/10/ExpressionLessSquare/Main.jack'))
CompilationEngine(jt)