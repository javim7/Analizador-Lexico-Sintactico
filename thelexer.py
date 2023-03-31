#importamos la clase de Yalex para poder obtener toda su informacion
from YALex import *

#creamos el objeto de la clase YALex y compilamos el archivo
yalex = YALex('YALFiles/ejemplo4.yal')
yalex.compiler()

def main():

    #input del archivo de entrada
    archivo = input('Ingrese el nombre del archivo de entrada: ')

    #creamos la variable del archivo
    texto = 'Inputs/'+archivo+'.txt'

    #creamos la variable del archivo
    # texto = 'Inputs/texto.txt'

    #leemos el archivo de texto
    with open(texto, 'r') as file:  
        data = file.read()

    #obtenemos la informacion del mega Automata
    megaAFD = yalex.megaDFA

    #mandamos a llamar al analizador lexico
    analizadorLexico(data, megaAFD)

def analizadorLexico(data, megaAFD):

    # obtain the list of tokens
    listOfTokens = yalex.identDict
    keyTokenList = list(listOfTokens.keys())

    # obtain the AFDs of each token
    afdList = yalex.getAFDs(yalex.updatedList)

    transitions = megaAFD.transitions
    finalStates = megaAFD.final_states
    pos = 0
    line_num = 1
    actualState = 0
    lexema = ''
    lexemas = []
    tokens = []
    errores = []

    while pos < len(data):
        symbol = data[pos]

        if symbol == "\n":
            line_num += 1

        # buscar la transicion
        foundTransition = False
        for transition in transitions:
            if transition.state == actualState and transition.symbol == symbol:
                actualState = transition.next_state
                lexema += symbol
                foundTransition = True
                break

        if not foundTransition:
            if actualState in finalStates:
                lexemas.append(lexema)
                lexema = ''
                actualState = 0
            else:
                # print line_num and pos+1 in error message
                if len(lexema) == 1:
                    errores.append('Error lexico en la linea ' + str(line_num) + ', posicion '+ str(pos+1) + ': caracter no reconocido.')
                else:
                    errores.append('Error lexico en la linea ' + str(line_num) + ', posicion '+ str(pos+1) + ': token no reconocido.')
                pos += 1
        
        if foundTransition:
            pos += 1

    if actualState in finalStates:
        lexemas.append(lexema)
        lexema = ''
        actualState = 0

    if lexema != '':
        if len(lexema) == 1:
            errores.append('Error lexico en la linea ' + str(line_num) + ', posicion '+ str(pos+1) + ': caracter no reconocido.')
        else:
            errores.append('Error lexico en la linea ' + str(line_num) + ', posicion '+ str(pos+1) + ': token no reconocido.')

    for lexema in lexemas:
        for i, afd in enumerate(afdList):
            if yalex.simulateAFD(afd, lexema):
                tokens.append(keyTokenList[i])
    # print(lexemas)
    # print(tokens)

    if errores != []:
        print('\n---ANALISIS LEXICO FALLIDO---')
        for error in errores:
            print(error)
    else:
        print('\n-------ANALISIS LEXICO EXITOSO-------')
        max_lex_len = max(len(lex.strip()) for lex in lexemas)
        for i, lex in enumerate(lexemas):
            # Remove white spaces from lex
            lex = lex.strip()

            if lex == '':
                continue

            formatted_lex = lex.ljust(max_lex_len)
            tokens[i] = tokens[i].replace('print("', f'print("{formatted_lex} -> ')
            eval(tokens[i].strip())

if __name__ == '__main__':
    main()
        