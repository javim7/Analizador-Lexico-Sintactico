from YAPar import *
import subprocess

'''
Programa Main3: Encargado de correr el programa del proyecto 3
'''

if __name__ == '__main__':

    comandos = [
        "yapar yap1.yalp -l thelexer.py -o theparser.py", #0
        "yapar yap2.yalp -l thelexer.py -o theparser.py",  #1
        "yapar yap3.yalp -l thelexer.py -o theparser.py"  #2
    ]

    #obtenemos la informacion del comando
    commandInfo = comandos[2].split(" ")

    yapFile = 'YAPFiles/' +commandInfo[1]
    fileToGenerate = commandInfo[5]
    lexerFile = commandInfo[3]

    # instanciamos yapar
    yapar = YAPar(yapFile, fileToGenerate)

    yapar.compiler()
    # print(yapar.grammar)

    #corremos los archivos generados
    subprocess.run(["python", lexerFile])
    subprocess.run(["python", fileToGenerate])
