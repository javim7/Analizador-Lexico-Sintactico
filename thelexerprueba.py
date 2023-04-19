#importamos la clase de Yalex para poder obtener toda su informacion
from YALex import *

#creamos el objeto de la clase YALex y compilamos el archivo
yalex = YALex('YALFiles/ejemplo4.yal')
yalex.compiler()

delimitadores = yalex.delimitadores

def main():

    #input del archivo de entrada
    archivo = input('\nIngrese el nombre del archivo de entrada: ')

    #creamos la variable del archivo
    texto = 'Inputs/'+archivo+'.txt'

    #creamos la variable del archivo
    # texto = 'Inputs/texto.txt'

    #leemos el archivo de texto
    with open(texto, 'r') as file:  
        data = file.read()

    if ' ' in delimitadores:
        words = data.split()
    else:
        words = data.split(delimitadores[0])
    #obtenemos la informacion del mega Automata
    megaAFD = yalex.megaDFA


    #mandamos a llamar al analizador lexico
    analizadorLexico(data, megaAFD)
    analizadorLexico2(words)
    validate_lexemas(data, delimitadores, megaAFD)

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


def analizadorLexico2(data):

    # obtain the list of tokens
    listOfTokens = yalex.identDict
    keyTokenList = list(listOfTokens.keys())

    # obtain the AFDs of each token
    afdList = yalex.getAFDs(yalex.updatedList)
    tokens = []
    errores = []

    line_number = 1
    position_number = 0

    for word in data:
        # Update position number and line number for each word
        position_number += 1
        if '\n' in word:
            line_number += 1
            position_number = 0

        for i, afd in enumerate(afdList):
            if yalex.simulateAFD(afd, word):
                tokens.append(keyTokenList[i])

        if not yalex.isValidToken(word):
            if len(word) == 1:
                errores.append(f"Error lexico en la linea {line_number}, posicion {position_number}: caracter '{word}' no reconocido.")
            else:
                errores.append(f"Error lexico en la linea {line_number}, posicion {position_number}: token '{word}' no reconocido.")

    if not errores:
        print('\n-------ANALISIS LEXICO EXITOSO-------')
        max_lex_len = max(len(lex.strip()) for lex in data)
        for i, word in enumerate(data):
            # Remove white spaces from word
            word = word.strip()

            if word == '':
                continue

            # Update position number and line number for each word
            position_number += 1
            if '\n' in word:
                line_number += 1
                position_number = 0

            formatted_word = word.ljust(max_lex_len)
            tokens[i] = tokens[i].replace('print("', f'print("{formatted_word} -> ')
            eval(tokens[i].strip())
    else:
        print('\n---ANALISIS LEXICO FALLIDO---')
        for error in errores:
            print(error)

def validate_lexemas(data, delimiters, megaAFD):
    

    #obtenemos la informacion del megaAFD
    transitions = megaAFD.transitions
    final_states = megaAFD.final_states
    listOfTokens = yalex.identDict
    keyTokenList = list(listOfTokens.keys())
    afdList = yalex.getAFDs(yalex.updatedList)

    # variables para el analisis lexico
    # delimiters = ['#']
    lexemas = []
    errors = []
    tokens = []
    current_lexema = ''
    current_state = 0
    in_string = False

    line_number = 1
    char_index = 0
    while char_index < len(data):
        char = data[char_index]

        if char == "\n":
            line_number += 1
        if char in delimiters:
            if current_lexema != '':
                if current_state in final_states:
                    lexemas.append(current_lexema)
                else:
                    if len(current_lexema) == 1:
                        errors.append(f"Error lexico en la linea {line_number}, posicion {char_index}: caracter '{current_lexema}' no reconocido.")
                    else:
                        errors.append(f"Error lexico en la linea {line_number}, posicion {char_index}: token '{current_lexema}' no reconocido.")
            current_lexema = ''
            current_state = 0
        else:
            current_lexema += char
            transition_found = False

            for transition in transitions:
                if transition.state == current_state and transition.symbol == char:
                    current_state = transition.next_state
                    transition_found = True
                    break

            if not transition_found:
                if in_string:
                    # Find the next delimiter to break out of the loop
                    next_delimiter_index = len(data)
                    for delimiter in delimiters:
                        delimiter_index = data.find(delimiter, char_index)
                        if delimiter_index != -1 and delimiter_index < next_delimiter_index:
                            next_delimiter_index = delimiter_index
                    current_lexema += data[char_index + 1:next_delimiter_index]
                    if len(current_lexema) == 1:
                        errors.append(f"Error lexico en la linea {line_number}, posicion {char_index}: caracter '{current_lexema}' no reconocido.")
                    else:
                        errors.append(f"Error lexico en la linea {line_number}, posicion {char_index}: token '{current_lexema}' no reconocido.")
                    current_lexema = ''
                    in_string = False
                    char_index = next_delimiter_index
                elif current_state in final_states:
                    lexemas.append(current_lexema[:-1])
                    current_lexema = current_lexema[-1]
                else:
                    if len(current_lexema) == 1:
                        errors.append(f"Error lexico en la linea {line_number}, posicion {char_index}: caracter '{current_lexema}' no reconocido.")
                    else:
                        errors.append(f"Error lexico en la linea {line_number}, posicion {char_index}: token '{current_lexema}' no reconocido.")
                    current_lexema = ''
                current_state = 0
            elif current_state == 3:
                in_string = True

        char_index += 1

    if current_lexema != '':
        if current_state in final_states:
            lexemas.append(current_lexema)
        else:
            if len(current_lexema) == 1:
                errors.append(f"Error lexico en la linea {line_number}, posicion {char_index}: caracter '{current_lexema}' no reconocido.")
            else:
                errors.append(f"Error lexico en la linea {line_number}, posicion {char_index}: token '{current_lexema}' no reconocido.")

    for lexema in lexemas:
        for i, afd in enumerate(afdList):
            if yalex.simulateAFD(afd, lexema):
                tokens.append(keyTokenList[i])

    if errors != []:
        print('\n---ANALISIS LEXICO FALLIDO---')
        for error in errors:
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
        