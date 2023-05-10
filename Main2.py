from YALex import *

'''
Programa Main2: Encargado de correr el programa del proyecto 2
'''

if __name__ == '__main__':

    #lista de comandos
    commands = [
        "yalex YALex1.yal -o thelexer.py",  #0
        "yalex YALex2.yal -o thelexer.py", #1
        "yalex YALex3.yal -o thelexer.py", #2
        "yalex e1.yal -o thelexer.py",    #3
        "yalex e2.yal -o thelexer.py",    #4
    ]

    #obtenemos la informacion del comando
    commandInfo = commands[3].split(" ")

    # yalex ejemplo4.yal -o thelexer.py
    # command = input("lexer(main)> ")
    # commandInfo = command.split(" ")
    yalFile = 'YALFiles/' + commandInfo[1]
    fileToGenerate = commandInfo[3]

    # instanciamos yalex
    yalex = YALex(yalFile, fileToGenerate)
    
    yalex.compiler()

    