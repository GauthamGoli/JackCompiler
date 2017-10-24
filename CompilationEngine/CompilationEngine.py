
class CompilationEngine:

    def __init__(self, jackTokenizer, symbolTable, outputPath):
        self.tokenizer = jackTokenizer
        self.symbolTable = symbolTable
        self.compiledTags = []
        self.compiledVMcode = []
        self._labelIndex = 0
        self.tokenizer.advance()
        self.compileClass()
        fp = open(outputPath, 'w')
        fp.write('\n'.join(self.compiledVMcode))
        fp.close()

    def _incrementLabelIndex(self):
        self._labelIndex += 1

    def fetchUniqueLabel(self):
        unique_label = 'label-{}'.format(self._labelIndex)
        self._incrementLabelIndex()
        return unique_label

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
        isMethod = self.tokenizer.currentToken in ['method']
        subRoutineType = self._experimentalEat('constructor', 'function', 'method', openingTag=True, tagName='subroutineDec')
        self.returnType = self._experimentalEat('void', 'int', 'char', 'boolean', 'identifier')
        if isMethod:
            self.symbolTable.setSubRoutineScope(self.tokenizer.currentToken)
            self.symbolTable.startSubroutine()
        else:
            # Static method, hence set SubRoutineScope as None
            # Static methods don't have the implicit 'this' argument
            self.symbolTable.setSubRoutineScope(None)
            self.symbolTable.startSubroutine()

        subRoutineName = self._experimentalEat('identifier')
        self._experimentalEat('(')
        args = self.compileParameterList() + (1 if isMethod else 0)
        self._experimentalEat(')')
        # Insert function definition at the right place after determining the number of paramters
        #self.compiledVMcode.insert(len(self.compiledVMcode)-args, 'function {}.{} {}'.format(self.symbolTable.className, subRoutineName, args))
        self.compiledVMcode.append('function {}.{} {}'.format(self.symbolTable.className, subRoutineName, args))
        if subRoutineType == 'constructor':
            # Allocate sufficient memory on heap
            self.compiledVMcode.append('push constant {}'.format(len(self.symbolTable.subroutineLevel.keys())))
            self.compiledVMcode.append('call Memory.alloc 1')
            self.compiledVMcode.append('pop pointer 0')
        elif subRoutineType == 'method':
            self.compiledVMcode.append('push argument 0')
            self.compiledVMcode.append('pop pointer 0')
        self.compileSubroutineBody()

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
        count = 0
        try:
            typeOf = self.tokenizer.currentToken
            kind = 'arg'
            self._eat('int', 'char', 'boolean', 'identifier')
            self._eat('identifier', typeOf=typeOf, kind=kind)
            count += 1
            while True:
                try:
                    self._eat(',')
                    typeOf = self.tokenizer.currentToken
                    self._eat('int', 'char', 'boolean', 'identifier')
                    self._eat('identifier', typeOf = typeOf, kind=kind)
                    count += 1
                except:
                    break
            self._writeOpenCloseTags(False, 'parameterList')
        except:
            self._writeOpenCloseTags(False, 'parameterList')
        return count

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
        self._experimentalEat('if')
        self._experimentalEat('(')
        self.compileExpression()
        self._experimentalEat(')')
        # Negate condition
        self.compiledVMcode.append('not')
        l1 = self.fetchUniqueLabel()
        l2 = self.fetchUniqueLabel()
        self._experimentalEat('{')
        self.compiledVMcode.append('if-goto {}'.format(l1))
        self.compileStatements()
        self._experimentalEat('}')
        self.compiledVMcode.append('goto {}'.format(l2))
        try:
            self.compiledVMcode.append('label {}'.format(l1))
            self._experimentalEat('else')
            self._experimentalEat('{')
            self.compileStatements()
            self._experimentalEat('}')
            self.compiledVMcode.append('label {}'.format(l2))
        except:
            pass

    def compileWhile(self):
        self._experimentalEat('while')
        self._experimentalEat('(')
        l1 = self.fetchUniqueLabel()
        l2 = self.fetchUniqueLabel()
        self.compiledVMcode.append('label {}'.format(l1))
        self.compileExpression()
        self._experimentalEat(')')
        self.compiledVMcode.append('not')
        self.compiledVMcode.append('if-goto {}'.format(l2))
        self._experimentalEat('{')
        self.compileStatements()
        self._experimentalEat('}')
        self.compiledVMcode.append('goto {}'.format(l1))
        self.compiledVMcode.append('label {}'.format(l2))

    def compileLet(self):
        self._experimentalEat('let')
        id1 = self._experimentalEat('identifier')
        if self.tokenizer.currentToken == '[':
            self._experimentalEat('[')
            self.compiledVMcode.append('push {} {}'.format(self.symbolTable.kindOf(id1), self.symbolTable.indexOf(id1)))
            self.compileExpression()
            self._experimentalEat(']')
            self.compiledVMcode.append('add')
            self._experimentalEat('=')
            self.compileExpression()
            self.compiledVMcode.append('pop temp 0')
            self.compiledVMcode.append('pop pointer 1')
            self.compiledVMcode.append('push temp 0')
            self.compiledVMcode.append('pop that 0')
        else:
            self._experimentalEat('=')
            self.compileExpression()
            self.compiledVMcode.append('pop {} {}'.format(self.symbolTable.kindOf(id1), self.symbolTable.indexOf(id1)))
        self._experimentalEat(';')

    def compileDo(self):
        self._experimentalEat('do')
        id1 = self._experimentalEat('identifier')
        if self.tokenizer.currentToken == '(':
            self._experimentalEat('(')
            args = self.compileExpressionList()
            self._experimentalEat(')')
            self.compiledVMcode.append('call {} {}'.format(id1, args))
        elif self.tokenizer.currentToken == '.':
            self._experimentalEat('.')
            id2 = self._experimentalEat('identifier')
            self._experimentalEat('(')
            args = self.compileExpressionList()
            self._experimentalEat(')')
            self.compiledVMcode.append('call {}.{} {}'.format(id1, id2, args))
        self.compiledVMcode.append('pop temp 0')
        self._experimentalEat(';')

    def compileReturn(self):
        if self.returnType == 'void':
            self.compiledVMcode.append('push const 0')
            self._experimentalEat('return')
        else:
            self._experimentalEat('return')
            self.compileExpression()
        self.compiledVMcode.append('return')
        self._experimentalEat(';')

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
        opMap = {'+': 'add', '-': 'sub', '*': 'call Math.multiply 2', '/': 'call Math.divide 2', '<': 'lt',
                 '>': 'gt', '=': 'eq', '&': 'and', '|': 'or'}
        try:
            self.compileTerm()
            while True:
                try:
                    op1 = self._experimentalEat('+', '-', '*', '/', '&', '|', '<', '>', '=')
                    self.compileTerm()
                    self.compiledVMcode.append('{}'.format(opMap[op1] if op1 in opMap else op1))
                except:
                    break
        except:
            raise Exception("No expression found")

    def compileTerm(self):
        if self.tokenizer.tokenType == 'identifier':
            id1 = self._experimentalEat('identifier')
            if self.tokenizer.currentToken == '(':
                # Changed from curly to normal, Possible bug introduced
                # f(exp1, exp2, ..)
                self._experimentalEat('(')
                args = self.compileExpressionList()
                self._experimentalEat(')')
                self.compiledVMcode.append('call {} {}'.format(id1, args))
            elif self.tokenizer.currentToken == '[':
                self.compiledVMcode.append('push {} {}'.format(self.symbolTable.kindOf(id1), self.symbolTable.indexOf(id1)))
                self._eat('[')
                self.compileExpression()
                self.compiledVMcode.append('add')
                self.compiledVMcode.append('pop pointer 1')
                self.compiledVMcode.append('push that 0')
                self._eat(']')
            elif self.tokenizer.currentToken == '.':
                self._experimentalEat('.')
                id2 = self._experimentalEat('identifier')
                self._experimentalEat('(')
                args = self.compileExpressionList()
                self._experimentalEat(')')
                self.compiledVMcode.append('call {}.{} {}'.format(id1, id2, args))
            else:
                self.compiledVMcode.append('push {} {}'.format(self.symbolTable.kindOf(id1), self.symbolTable.indexOf(id1)))
        elif self.tokenizer.currentToken == '(':
            self._experimentalEat('(')
            self.compileExpression()
            self._experimentalEat(')')
        else:
            if self.tokenizer.tokenType == 'integerConstant':
                const1 = self._experimentalEat('integerConstant')#, 'true', 'false', 'null')#, 'stringConstant', 'true', 'false', 'null', 'this')
                self.compiledVMcode.append('push constant {}'.format(const1))
            elif self.tokenizer.currentToken == 'true':
                self._experimentalEat('true')
                self.compiledVMcode += ['push constant 1', 'neg']
            elif self.tokenizer.currentToken == 'false' or self.tokenizer.currentToken == 'null':
                self._eat('false', 'null')
                self.compiledVMcode.append('push constant 0')
            elif self.tokenizer.currentToken == 'this':
                self._eat('this')
                self.compiledVMcode.append('push pointer 0')
            elif self.tokenizer.tokenType == 'stringConstant':
                str_const = self._experimentalEat('stringConstant')
                self.compiledVMcode.append('push constant {}'.format(len(str_const)))
                self.compiledVMcode.append('call String.new 1')
                for letter in str_const:
                    self.compiledVMcode.append('push const {}'.format(ord(letter)))
                    self.compiledVMcode.append('call String.append 1')
            else:
                op1 = self._experimentalEat('-', '~')
                self.compileTerm()
                self.compiledVMcode.append('{}'.format('neg' if op1 == '~' else 'not'))

    def compileExpressionList(self):
        count = 0
        try:
            self.compileExpression()
            count += 1
            while True:
                try:
                    self._experimentalEat(',')
                    self.compileExpression()
                    count += 1
                except:
                    break
        except:
            pass
        return count

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
