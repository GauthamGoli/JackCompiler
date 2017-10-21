import os
import sys
import glob
from tokenizer.JackTokenizer import JackTokenizer
from CompilationEngine.CompilationEngine import CompilationEngine
from SymbolTable.SymbolTable import SymbolTable

if (len(sys.argv) < 2):
    print "Supply file/dir location."
    sys.exit()
else:
    input_path = os.path.abspath(sys.argv[1])
    jack_files = glob.glob(input_path + '/*.jack') if os.path.isdir(input_path) else [input_path]
    for jack_file in jack_files:
        st = SymbolTable()
        jt = JackTokenizer(os.path.abspath(jack_file))
        CompilationEngine(jt, st, jt.inputPath.replace('.jack', '_output.xml'))
        print '{} compiled successfully'.format(jack_file)
