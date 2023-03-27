from Proyecto1.Tree import *
from Proyecto2.YALex import *
from Proyecto1.Postfix import *
from Proyecto1.Thompson import *

'''
Programa Main2: Encargadro de correr el programa del proyecto 2
'''

if __name__ == '__main__':

    #lista de comandos
    commands = [
        "yalex ejemplo.yal -o thelexer.py",  #0
        "yalex ejemplo2.yal -o thelexer.py", #1
        "yalex ejemplo3.yal -o thelexer.py", #2
    ]

    #obtenemos la informacion del comando
    commandInfo = commands[2].split(" ")
    yalFile = 'Proyecto2/' + commandInfo[1]
    fileToGenerate = commandInfo[3]

    # instanciamos yalex
    yalex = YALex(yalFile)
    
    yalex.compiler()

    