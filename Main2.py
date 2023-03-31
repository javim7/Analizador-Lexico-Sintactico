from YALex import *

'''
Programa Main2: Encargado de correr el programa del proyecto 2
'''

if __name__ == '__main__':

    #lista de comandos
    commands = [
        "yalex ejemplo.yal -o thelexer.py",  #0
        "yalex ejemplo2.yal -o thelexer.py", #1
        "yalex ejemplo3.yal -o thelexer.py", #2
        "yalex ejemplo4.yal -o thelexer.py", #3
    ]

    #obtenemos la informacion del comando
    commandInfo = commands[3].split(" ")
    yalFile = 'YALFiles/' + commandInfo[1]
    fileToGenerate = commandInfo[3]

    # instanciamos yalex
    yalex = YALex(yalFile, fileToGenerate)
    
    yalex.compiler()

    