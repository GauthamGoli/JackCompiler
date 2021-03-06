import re

class JackTokenizer:
    def __init__(self, filePath):
        self.inputPath = filePath
        filePointer = open(filePath)
        self.lines = filePointer.readlines()
        self.stripComments()
        self.currentToken = None
        self.tokenType = None
        self.keywords = 'class|constructor|function|method|field|static|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return'
        self.symbols = '\{|\}|\(|\)|\[|\]|\.|,|;|\+|-|\*|/|&|<|>|~|=|~|\|'
        self.lineIndex = 0
        self.currentLineSeekIndex = 0
        self.tokenMappings = { 'keyword': 'KEYWORD',
                               'symbol' : 'SYMBOL',
                               'identifier': 'IDENTIFIER',
                               'integerConstant': 'INT_CONST',
                               'stringConstant': 'STRING_CONST' }

    def stripComments(self):
        strippedLines = []
        for line in self.lines[:]:
            if '//' in line:
                strippedLines.append(line[:line.index('//')].rstrip().lstrip())
            elif '/**' in line:
                strippedLines.append(line[:line.index('/**')].rstrip().lstrip())
            else:
                strippedLines.append(line.strip())
        self.lines = [line for line in strippedLines if line]

    def hasMoreTokens(self):
        if self.lineIndex >= len(self.lines):
            return False
        elif self.currentLineSeekIndex < len(self.lines[self.lineIndex]):
            return True

    def advance(self):
        if self.hasMoreTokens():
            # Split by space, but don't split strings with double quotes
            if self.lines[self.lineIndex][self.currentLineSeekIndex] == '"':
                stringEndPos = self.lines[self.lineIndex][self.currentLineSeekIndex+1:].index('"')+self.currentLineSeekIndex+2
                lineComponents = [self.lines[self.lineIndex][self.currentLineSeekIndex: stringEndPos]]
                lineComponents += self.lines[self.lineIndex][stringEndPos:].split()
                self.currentLineSeekIndex -= 0 if self.lines[self.lineIndex][stringEndPos] == ' ' else 1
            else:
                lineComponents = self.lines[self.lineIndex][self.currentLineSeekIndex:].split()
                # Fix wierd bug where spaces are incorrectly calculated
                if self.lines[self.lineIndex][self.currentLineSeekIndex] == ' ':
                    self.currentLineSeekIndex += 1
            for componentPosition, lineComponent in enumerate(lineComponents):
                if self.regexSearchWrapper('^({})({})?$'.format(self.keywords, self.symbols), lineComponent):
                    self.currentToken = self.match.group(1)
                    self.tokenType = 'keyword'
                elif self.regexSearchWrapper('^\d{1,5}', lineComponent):
                    self.currentToken = self.match.group(0)
                    self.tokenType = 'integerConstant'
                elif self.regexSearchWrapper('^({})'.format(self.symbols), lineComponent):
                    self.currentToken = self.match.group(0)
                    self.tokenType = 'symbol'
                elif self.regexSearchWrapper('^"(.*)"', lineComponent):
                    self.currentToken = self.match.group(1)
                    self.tokenType = 'stringConstant'
                elif self.regexSearchWrapper('^([^0-9][a-zA-Z0-9_]*)', lineComponent):
                    self.currentToken = self.match.group(0)
                    self.tokenType = 'identifier'
                else:
                    raise Exception("No match found")
                # Update seek Pos in current line
                # Before that see if there is space adjacent to current token
                if len(self.currentToken) == len(lineComponent) and self.tokenType is not 'stringConstant':
                    adjacentSpace = 1
                elif len(self.currentToken) == len(lineComponent) - 2 and self.tokenType is 'stringConstant':
                    adjacentSpace = 2+1
                else:
                    adjacentSpace = 0
                self.currentLineSeekIndex += len(self.currentToken) + adjacentSpace
                # Update current line index, if seek index reached end, then update line index
                if self.currentLineSeekIndex >= len(self.lines[self.lineIndex]):
                    self.currentLineSeekIndex = 0
                    self.lineIndex += 1
                return

    def regexSearchWrapper(self, pattern, textToMatch):
        self.match = re.search(pattern, textToMatch)
        return self.match

    def tokenType(self):
        return self.tokenMappings[self.tokenType] if self.tokenType in self.tokenMappings else None

    def keyWord(self):
        return self.currentToken.upper if self.tokenMappings[self.tokenType] is 'KEYWORD' else None

    def symbol(self):
        return self.currentToken.upper if self.tokenMappings[self.tokenType] is 'SYMBOL' else None
    
    def identifier(self):
        return self.currentToken.upper if self.tokenMappings[self.tokenType] is 'IDENTIFIER' else None

    def intVal(self):
        return self.currentToken.upper if self.tokenMappings[self.tokenType] is 'INT_CONST' else None

    def stringVal(self):
        return self.currentToken.upper if self.tokenMappings[self.tokenType] is 'STRING_CONST' else None
