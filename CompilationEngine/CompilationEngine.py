class CompilationEngine:

    def __init__(self, jackTokenizer, outputPath):
        self.tokenizer = jackTokenizer
        self.compiledTags = []
        self.tokenizer.advance()
        self.compileClass()
        fp = open(outputPath, 'w')
        fp.write('\n'.join(self.compiledTags))
        fp.close()

    def compileClass(self):
        self._eat('class', openingTag=True, tagName='class')
        self._eat('identifier')
        self._eat('{')
        while True:
            try:
                self.compileClassVarDec()
            except:
                break

        while True:
            try:
                self.compileSubroutineDec()
            except:
                break

        self._eat('}', openingTag = False, tagName = 'class')

    def compileClassVarDec(self):
        self._eat('static','field', openingTag = True, tagName = 'classVarDec')
        self._eat('int','char','boolean','identifier')
        self._eat('identifier')
        while True:
            try:
                self._eat(',')
                self._eat('identifier')
            except:
                break
        self._eat(';', openingTag = False, tagName = 'classVarDec')

    def compileSubroutineDec(self):
        self._eat('constructor','function', 'method', openingTag = True, tagName = 'subroutineDec')
        self._eat('void', 'int', 'char', 'boolean', 'identifier')
        self._eat('identifier')
        self._eat('(')
        self.compileParameterList()
        self._eat(')')
        self.compileSubroutineBody()
        self._writeOpenCloseTags(False, 'subroutineDec')

    def compileSubroutineBody(self):
        self._writeOpenCloseTags(True, 'subroutineBody')
        self._eat('{')
        while True:
            try:
                self.compileVarDec()
            except:
                break
        self.compileStatements()
        self._eat('}')
        self._writeOpenCloseTags(False, 'subroutineBody')

    def compileVarDec(self):
        self._eat('var', openingTag = True, tagName = 'varDec')
        self._eat('int', 'char', 'boolean', 'identifier')
        self._eat('identifier')
        while True:
            try:
                self._eat(',')
                self._eat('identifier')
            except:
                break
        self._eat(';', openingTag = False, tagName = 'varDec')

    def compileParameterList(self):
        try:
            self._writeOpenCloseTags(True, 'parameterList')
            self._eat('int', 'char', 'boolean', 'identifier')
            self._eat('identifier')
            while True:
                try:
                    self._eat(',')
                    self._eat('int', 'char', 'boolean', 'identifier')
                    self._eat('identifier')
                except:
                    break
            self._writeOpenCloseTags(False, 'parameterList')
        except:
            self._writeOpenCloseTags(False, 'parameterList')

    def compileStatements(self):
        self._writeOpenCloseTags(True, 'statements')
        while True:
            try:
                self.compileStatement()
            except:
                break
        self._writeOpenCloseTags(False, 'statements')

    def compileStatement(self):
        if self.tokenizer.currentToken == 'if':
            self.compileIf()
        elif self.tokenizer.currentToken == 'let':
            self.compileLet()
        elif self.tokenizer.currentToken == 'while':
            self.compileWhile()
        elif self.tokenizer.currentToken == 'do':
            self.compileDo()
        elif self.tokenizer.currentToken == 'return':
            self.compileReturn()
        else:
            raise Exception("Unknown Statement")
            
    def compileIf(self):
        self._writeOpenCloseTags(True, 'ifStatement')
        self._eat('if')
        self._eat('(')
        self.compileExpression()
        self._eat(')')
        self._eat('{')
        self.compileStatements()
        self._eat('}')
        try:
            self._eat('else')
            self._eat('{')
            self.compileStatements()
            self._eat('}')
        except:
            pass
        self._writeOpenCloseTags(False, 'ifStatement')

    def compileWhile(self):
        self._writeOpenCloseTags(True, 'whileStatement')
        self._eat('while')
        self._eat('(')
        self.compileExpression()
        self._eat(')')
        self._eat('{')
        self.compileStatements()
        self._eat('}')
        self._writeOpenCloseTags(False, 'whileStatement')

    def compileLet(self):
        self._writeOpenCloseTags(True, 'letStatement')
        self._eat('let')
        self._eat('identifier')
        try:
            self._eat('[')
            self.compileExpression()
            self._eat(']')
        except:
            pass
        self._eat('=')
        self.compileExpression()
        self._eat(';')
        self._writeOpenCloseTags(False, 'letStatement')

    def compileDo(self):
        self._writeOpenCloseTags(True, 'doStatement')
        self._eat('do')
        self._eat('identifier')
        if self.tokenizer.currentToken == '(':
            self._eat('(')
            self.compileExpressionList()
            self._eat(')')
        elif self.tokenizer.currentToken == '.':
            self._eat('.')
            self._eat('identifier')
            self._eat('(')
            self.compileExpressionList()
            self._eat(')')
        self._eat(';')
        self._writeOpenCloseTags(False, 'doStatement')

    def compileReturn(self):
        self._writeOpenCloseTags(True, 'returnStatement')
        self._eat('return')
        try:
            self.compileExpression()
        except:
            pass
        self._eat(';')
        self._writeOpenCloseTags(False, 'returnStatement')

    def compileExpression(self):
        try:
            self._writeOpenCloseTags(True, 'expression')
            self.compileTerm()
            while True:
                try:
                    self._eat('+', '-', '*', '/', '&', '|', '<', '>', '=')
                    self.compileTerm()
                except:
                    break
            self._writeOpenCloseTags(False, 'expression')
        except:
            self.compiledTags.pop()

    def compileTerm(self):
        if self.tokenizer.tokenType == 'identifier':
            self._writeOpenCloseTags(True, 'term')
            self._eat('identifier')
            if self.tokenizer.currentToken == '{':
               self._eat('{')
               self.compileExpressionList()
               self._eat('}')
            elif self.tokenizer.currentToken == '[':
                self._eat('[')
                self.compileExpression()
                self._eat(']')
            elif self.tokenizer.currentToken == '.':
                self._eat('.')
                self._eat('identifier')
                self._eat('(')
                self.compileExpressionList()
                self._eat(')')
        elif self.tokenizer.currentToken == '(':
            self._writeOpenCloseTags(True, 'term')
            self._eat('(')
            self.compileExpression()
            self._eat(')')
        else:
            try:
                self._writeOpenCloseTags(True, 'term')
                self._eat('integerConstant', 'stringConstant', 'true', 'false', 'null', 'this')
            except:
                exceptionFlag = False
                try:
                    self._eat('-', '~')
                    self.compileTerm()
                except:
                    self.compiledTags.pop()
                    exceptionFlag = True
                if exceptionFlag:
                    raise Exception("Term not found")
        self._writeOpenCloseTags(False, 'term')

    def compileExpressionList(self):
        self._writeOpenCloseTags(True, 'expressionList')
        try:
            self.compileExpression()
            while True:
                try:
                    self._eat(',')
                    self.compileExpression()
                except:
                    break
        except:
            pass
        self._writeOpenCloseTags(False, 'expressionList')

    def _eat(self, *token, **kwargs):
        if len(token) == 0:
            self._writeOpenCloseTags(kwargs.get('openingTag'), kwargs.get('tagName'))
            return
        elif self.tokenizer.currentToken not in token and self.tokenizer.tokenType not in token:
            raise Exception("Token not found")
        else:
            self._writeOpenCloseTags(kwargs.get('openingTag', False), kwargs.get('tagName', None), True, False)
            self.compiledTags.append('<{}>{}</{}>'.format(self.tokenizer.tokenType, self.tokenizer.currentToken, self.tokenizer.tokenType))
            self._writeOpenCloseTags(kwargs.get('openingTag', False), kwargs.get('tagName', None), False)
            self.tokenizer.advance()

    def _writeOpenCloseTags(self, openingTag = False, tagName = None, opening=True, closing=True):
        if openingTag and tagName and opening:
            self.compiledTags.append('<{}>'.format(tagName))
        if (not openingTag) and tagName and closing:
            self.compiledTags.append('</{}>'.format(tagName))
