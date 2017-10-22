
class CompilationEngine:

    def __init__(self, jackTokenizer, symbolTable, outputPath):
        self.tokenizer = jackTokenizer
        self.symbolTable = symbolTable
        self.compiledTags = []
        self.compiledVMcode = []
        self.tokenizer.advance()
        self.compileClass()
        fp = open(outputPath, 'w')
        fp.write('\n'.join(self.compiledTags))
        fp.close()

    def compileClass(self):
        self._eat('class', openingTag=True, tagName='class')
        self.symbolTable.setClassScope(self.tokenizer.currentToken)
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

        self._eat('}', openingTag=False, tagName='class')

    def compileClassVarDec(self):
        kind = self.tokenizer.currentToken
        self._eat('static', 'field', openingTag=True, tagName='classVarDec')
        typeOf = self.tokenizer.currentToken
        self._eat('int', 'char', 'boolean', 'identifier')
        self._eat('identifier', kind=kind, typeOf=typeOf)
        while True:
            try:
                self._eat(',')
                self._eat('identifier', kind=kind, typeOf=typeOf)
            except:
                break
        self._eat(';', openingTag=False, tagName='classVarDec')

    def compileSubroutineDec(self):
        subRoutineType = self.tokenizer.currentToken in ['method', 'constructor']
        self._eat('constructor', 'function', 'method', openingTag=True, tagName='subroutineDec')
        self._eat('void', 'int', 'char', 'boolean', 'identifier')
        if subRoutineType:
            self.symbolTable.setSubRoutineScope(self.tokenizer.currentToken)
            self.symbolTable.startSubroutine()
        else:
            # Static method, hence set SubRoutineScope as None
            # Static methods don't have the implicit 'this' argument
            self.symbolTable.setSubRoutineScope(None)
            self.symbolTable.startSubroutine()
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
        kind = self.tokenizer.currentToken
        self._eat('var', openingTag=True, tagName='varDec')
        typeOf = self.tokenizer.currentToken
        self._eat('int', 'char', 'boolean', 'identifier')
        self._eat('identifier', kind=kind, typeOf=typeOf)
        while True:
            try:
                self._eat(',')
                self._eat('identifier', kind=kind, typeOf=typeOf)
            except:
                break
        self._eat(';', openingTag=False, tagName='varDec')

    def compileParameterList(self):
        try:
            self._writeOpenCloseTags(True, 'parameterList')
            typeOf = self.tokenizer.currentToken
            kind = 'arg'
            self._eat('int', 'char', 'boolean', 'identifier')
            self._eat('identifier', typeOf=typeOf, kind=kind)
            while True:
                try:
                    self._eat(',')
                    typeOf = self.tokenizer.currentToken
                    self._eat('int', 'char', 'boolean', 'identifier')
                    self._eat('identifier', typeOf = typeOf, kind=kind)
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

    # def codeWrite(self):
    #     if self.tokenizer.tokenType == 'integerConstant':
    #         self.compiledVMcode.append('push {}'.format(self.tokenizer.currentToken))
    #         self.tokenizer.advance()
    #     elif self.tokenizer.tokenType == 'identifier':
    #         self.compiledVMcode.append('push {}'.format(self.tokenizer.currentToken))
    #         self.tokenizer.advance()
    #
    #     elif self.tokenizer.currentToken == '(':
    #         # Assume it is (expression1) op (expression2)
    #         self.codeWrite()
    #
    #     elif self.tokenizer.tokenType == 'symbol' and self.tokenizer.currentToken in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
    #     # Assume it is (op expression)
    #         op = self.tokenizer.currentToken
    #         self.codeWrite()
    #         self.compiledVMcode.append('{}'.format(op))
    #     elif


    def compileExpression(self):
        try:
            self.compileTerm()
            while True:
                try:
                    op1 = self._experimentalEat('+', '-', '*', '/', '&', '|', '<', '>', '=')
                    self.compileTerm()
                    self.compiledVMcode.append('{}'.format(op1))
                except:
                    break
        except:
            self.compiledTags.pop()

    def compileTerm(self):
        if self.tokenizer.tokenType == 'identifier':
            id1 = self._experimentalEat('identifier')
            if self.tokenizer.currentToken == '(':
                # Changed from curly to normal, Possible bug introduced
                # f(exp1, exp2, ..)
                self._experimentalEat('(')
                self.compileExpressionList()
                self._experimentalEat(')')
                self.compiledVMcode.append('call {}'.format(id1))
            elif self.tokenizer.currentToken == '[':
                self._eat('[')
                self.compileExpression()
                self._eat(']')
            elif self.tokenizer.currentToken == '.':
                self._experimentalEat('.')
                id2 = self._experimentalEat('identifier')
                self._experimentalEat('(')
                self.compileExpressionList()
                self._experimentalEat(')')
                self.compiledVMcode.append('call {}.{}'.format(id1, id2))
            else:
                self.compiledVMcode.append('push {}'.format(id1))
        elif self.tokenizer.currentToken == '(':
            self._experimentalEat('(')
            self.compileExpression()
            self._experimentalEat(')')
        else:
            try:
                const1 = self._experimentalEat('integerConstant' )#, 'stringConstant', 'true', 'false', 'null', 'this')
                self.compiledVMcode.append('push {}'.format(const1))
            except:
                exceptionFlag = False
                try:
                    op1 = self._experimentalEat('-', '~')
                    self.compileTerm()
                    self.compiledVMcode.append('{}'.format(op1))
                except:
                    self.compiledTags.pop()
                    exceptionFlag = True
                if exceptionFlag:
                    raise Exception("Term not found")

    def compileExpressionList(self):
        try:
            self.compileExpression()
            while True:
                try:
                    self._experimentalEat(',')
                    self.compileExpression()
                except:
                    break
        except:
            pass

    def _experimentalEat(self, *token, **kwargs):
        if self.tokenizer.currentToken not in token and self.tokenizer.tokenType not in token:
            raise Exception("Token not found")
        else:
            to_return = self.tokenizer.currentToken
            self.tokenizer.advance()
            return to_return

    def _eat(self, *token, **kwargs):
        if len(token) == 0:
            self._writeOpenCloseTags(kwargs.get('openingTag'), kwargs.get('tagName'))
            return
        elif self.tokenizer.currentToken not in token and self.tokenizer.tokenType not in token:
            raise Exception("Token not found")
        else:
            self._writeOpenCloseTags(kwargs.get('openingTag', False), kwargs.get('tagName', None), True, False)
            skipFlag = False
            if kwargs.get('kind', False) and kwargs.get('typeOf', False):
                self.symbolTable.define(self.tokenizer.currentToken, kwargs.get('typeOf'), kwargs.get('kind'))
                self.compiledTags.append('<{}:{}:{}:def>{}</{}:{}:{}:def>'.format(self.tokenizer.tokenType,
                                                                                self.symbolTable.kindOf(
                                                                                    self.tokenizer.currentToken),
                                                                                self.symbolTable.typeOf(
                                                                                    self.tokenizer.currentToken),
                                                                                self.tokenizer.currentToken,
                                                                                self.tokenizer.tokenType,
                                                                                self.symbolTable.kindOf(
                                                                                    self.tokenizer.currentToken),
                                                                                self.symbolTable.typeOf(
                                                                                    self.tokenizer.currentToken)))
                skipFlag = True
            elif self.tokenizer.identifier() and self.symbolTable.hasSymbol(self.tokenizer.currentToken):
                self.compiledTags.append('<{}:{}:{}:{}>{}</{}:{}:{}:{}>'.format(self.tokenizer.tokenType,
                                                                          self.symbolTable.kindOf(self.tokenizer.currentToken),
                                                                          self.symbolTable.typeOf(self.tokenizer.currentToken),
                                                                          self.symbolTable.indexOf(self.tokenizer.currentToken),
                                                                          self.tokenizer.currentToken,
                                                                          self.tokenizer.tokenType,
                                                                          self.symbolTable.kindOf(self.tokenizer.currentToken),
                                                                          self.symbolTable.typeOf(self.tokenizer.currentToken),
                                                                          self.symbolTable.indexOf(self.tokenizer.currentToken)))
                skipFlag = True
            if not skipFlag:
                self.compiledTags.append('<{}>{}</{}>'.format(self.tokenizer.tokenType, self.tokenizer.currentToken, self.tokenizer.tokenType))
            self._writeOpenCloseTags(kwargs.get('openingTag', False), kwargs.get('tagName', None), False)
            self.tokenizer.advance()

    def _writeOpenCloseTags(self, openingTag = False, tagName = None, opening=True, closing=True):
        if openingTag and tagName and opening:
            self.compiledTags.append('<{}>'.format(tagName))
        if (not openingTag) and tagName and closing:
            self.compiledTags.append('</{}>'.format(tagName))
