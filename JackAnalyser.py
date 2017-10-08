import os
from tokenizer.JackTokenizer import JackTokenizer

jt = JackTokenizer(os.path.abspath('./test.jack'))

while jt.hasMoreTokens():
    jt.advance()
    print '{}:{}'.format(jt.currentToken, jt.tokenType)