### Jack Compiler: A compiler for Hack programming language


Consists:
  - Tokenizer: Tokenizes the high level HACK language, which becomes the input for Parser
  - Parser: Recursive Descent primarily of LL(1) but LL(2) for few cases
  - SymbolTable: Handles class level and subroutine level variables
  - Compilation Engine and VMWriter: Recursive top-down compilation engine

### Contributing
Feel free to make any improvements and open a PR

### Usage:
`$ python JackAnalyser.py [filename.jack/Directory]`

### Input:

 - fileName.jack: the name of a single source file, or
 - directoryName: the name of a directory containing one or more .jack source files

### Output:
 - fileName_output.vm : Contains bytecode for an intermediate stack based virtual machine, which can be translated to assembly code using [VMtranslator](https://github.com/GauthamGoli/VMtranslator)
