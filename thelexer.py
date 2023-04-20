#importamos la clase de Yalex para poder obtener toda su informacion
from YALex import *

#creamos el objeto de la clase YALex y compilamos el archivo
yalex = YALex('YALFiles/YALex3.yal')
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

    # buscar las cadenas en comillas dobles y reemplazar los espacios en blanco por guiones bajos
    start = 0
    while True:
        start = data.find('"', start)  # encontrar el primer par de comillas dobles
        if start == -1:
            break
        end = data.find('"', start+1)  # encontrar el siguiente par de comillas dobles
        if end == -1:
            break
        s = data[start:end+1]  # obtener la subcadena dentro de las comillas dobles
        s_new = s.replace(' ', '_')  # reemplazar los espacios en blanco con guiones bajos
        data = data[:start] + s_new + data[end+1:]  # reemplazar la subcadena en el texto original
        start += len(s_new)  # actualizar la posición de inicio para buscar la siguiente subcadena

    #obtenemos la informacion del mega Automata
    megaAFD = yalex.megaDFA

    #mandamos a llamar al analizador lexico
    analizador_lexico(data, delimitadores, megaAFD)

def analizador_lexico(data, delimiters, megaAFD):

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
                break

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
            if '"' in lex:
                lex = lex.replace('"', '')
            if '_' in lex:
                lex = lex.replace('_', ' ')

            formatted_lex = lex.ljust(max_lex_len)
            tokens[i] = tokens[i].replace('print("', f'print("{formatted_lex} -> ')
            eval(tokens[i].strip())

if __name__ == '__main__':
    main()
        