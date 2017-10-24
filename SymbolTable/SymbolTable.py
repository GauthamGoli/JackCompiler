class SymbolTable:

    def __init__(self):
        self.kindOfMappings = {'field': 'this',
                               'static': 'static',
                               'arg': 'argument',
                               'var': 'local'}
        self.subroutineLevel = {}
        self.subroutineLevelIndex = {}
        self.classLevel  = {}
        self.classLevelIndex = {}

    def setClassScope(self, className):
        self.className = className

    def setSubRoutineScope(self, methodName=None):
        self.subRoutineName = methodName

    def startSubroutine(self):
        self.subroutineLevel = {}
        self.subroutineLevelIndex = {}
        if self.subRoutineName is not None:
            self.define('this', self.className, 'arg')

    def define(self, name, typeOf, kind):
        if kind in ['static', 'field']:
            if self.classLevelIndex.has_key(kind) and not self.classLevel.has_key(kind):
                self.classLevelIndex[kind] += 1
                self.classLevel[name] = [typeOf, kind, self.classLevelIndex[kind]]
            else:
                self.classLevelIndex[kind] = 0
                self.classLevel[name] = [typeOf, kind, 0]

        elif kind in ['arg', 'var']:
            if self.subroutineLevelIndex.has_key(kind) and not self.subroutineLevel.has_key(kind):
                self.subroutineLevelIndex[kind] += 1
                self.subroutineLevel[name] = [typeOf, kind, self.subroutineLevelIndex[kind]]
            else:
                self.subroutineLevelIndex[kind] = 0
                self.subroutineLevel[name] = [typeOf, kind, 0]

    def hasSymbol(self, name):
        return name in self.classLevel or name in self.subroutineLevel

    def varCount(self, kind):
        if self.classLevelIndex.has_key(kind):
            return self.classLevelIndex[kind]
        elif self.subroutineLevelIndex.has_key(kind):
            return self.subroutineLevelIndex[kind]
        else:
            return 0

    def kindOf(self, name):
        if self.classLevel.has_key(name):
            return self.kindOfMappings[self.classLevel[name][1]]
        elif self.subroutineLevel.has_key(name):
            return self.kindOfMappings[self.subroutineLevel[name][1]]
        else:
            return "NONE"

    def typeOf(self, name):
        if self.classLevel.has_key(name):
            return self.classLevel[name][0]
        elif self.subroutineLevel.has_key(name):
            return self.subroutineLevel[name][0]
        else:
            return "NONE"

    def indexOf(self, name):
        if self.classLevel.has_key(name):
            return self.classLevel[name][2]
        elif self.subroutineLevel.has_key(name):
            return self.subroutineLevel[name][2]
        else:
            return "NONE"