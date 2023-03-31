import re
from Tree import *
from Regex import *
from Drawer import *
from Postfix import *
from Thompson import *
from Simulation import *

class YALex:
    def __init__(self, filename, outputname=None):
        try:
            self.filename = filename
            self.file = open(filename, 'r')
            self.outputname = outputname
            self.lines = self.file.readlines()
            self.regex_list = []
            self.regexFinalList = []
            self.updatedList = []
            self.regex_dict = {}
            self.identDict = {}
            self.errors = False
            self.errosList = []
            self.dfaList = []
            self.nfaList = []
            self.megaDFA = None
            self.megaRegex = ''
            self.tokens = {
                '+': '@',
                '*': '!',
                '.': ',',
                '(': '[',
                ')': ']',
            }
        except FileNotFoundError:
            raise Exception('File could not be opened')
   
    def compiler(self):

        if self.outputname == None:
            #eliminando comillas
            for i in range(len(self.lines)):
                self.lines[i] = self.lines[i].replace("'", "")

            # detectamos errores
            errores = self.detect_errors()

            # si hay errores, los mostramos, de lo contrario, continuamos
            if self.errors:
                errores_str = "\n".join(set(errores))
                raise Exception(errores_str)
            
            self.getRegexes()
            self.modifyRegexes()

            # print(self.regexFinalList)
            self.updatedList = self.getUpdatedList()
            # print("\nQUINTA LISTA - Regexes con Identidades:")
            # print(self.updatedList)

            self.megaRegex = '|'.join([ x  for x in self.updatedList])
            
            # print("\nMEGA REGEX - Todos los regex juntos:")
            # print(self.megaRegex)
            self.megaDFA = self.buildDFA()
            # self.megaDFA.print_dfa()
            # self.megaDFA.dfa_info()
        
        if self.outputname:
            self.generateOutput(self.outputname)

    def detect_errors(self):
        stack = []
        yaSonRules = False
        self.errorsList = []
        for i, line in enumerate(self.lines):
            # Check parentheses and curly braces are balanced and in correct order
            for c in line:
                if c == '(':
                    stack.append(c)
                    stack.append(i)
                elif c == ')':
                    if not stack or stack[-2] != '(':
                        self.errorsList.append(f"')' desbalanceado en la linea: {i+1}")
                    stack.pop()
                    stack.pop()
                elif c == '{':
                    stack.append(c)
                    stack.append(i)
                elif c == '}':
                    if not stack or stack[-2] != '{':
                        self.errorsList.append(f"'}}' desbalanceado en la linea: {i+1}")
                    stack.pop()
                    stack.pop()
            # Check import statements are correctly formatted
            if line.startswith("import"):
                if not re.search(r'import\s+[a-zA-Z0-9_]+\s*', line):
                    self.errorsList.append(f"Formato incorrecto de 'import' en la linea: {i+1}")
            # Check let statements are correctly formatted
            if line.startswith("let"):
                if yaSonRules:
                    self.errorsList.append(f"'let' en seccion erronea: {i+1}")
                if '=' not in line:
                    self.errorsList.append(f"Formato incorrecto de 'let' en la linea: {i+1}")
                if not re.search(r'let\s+[a-zA-Z][a-zA-Z0-9]*\s*=\s*.+', line):
                    self.errorsList.append(f"Formato incorrecto de 'let' en la linea: {i+1}")
            # Check rule statements are correctly formatted
            if line.startswith("rule"):
                yaSonRules = True
                if '=' not in line:
                    self.errorsList.append(f"Formato incorrecto de 'rule' en la linea: {i+1}")
                if not re.search(r'rule\s+[a-zA-Z0-9_]+\s*(\[[a-zA-Z0-9_, ]+\])?\s*=\s*\n', line):
                    self.errorsList.append(f"Formato incorrecto de 'rule' en la linea: {i+1}")
            if '=' in line:
                if not line.startswith("rule") and not line.startswith("let") and yaSonRules == False:
                    self.errorsList.append(f"Formato incorrecto de variable en la linea: {i+1}")
        if stack:
            self.errorsList.append(f"'{stack[-2]}' desbalanceado en la linea: {str(stack[-1]+1)}")
        if self.errorsList:
            self.errors = True
            return self.errorsList
        return None


    def getRegexes(self):

        pattern = r"let\s+(\w+)\s*=\s*(.*)"

        for i, line in enumerate(self.lines):
            match = re.match(pattern, line)
            if match:
                self.regex_dict[match.group(1)] = match.group(2)
            if line.startswith("rule"):
                for j,sub_line in enumerate(self.lines[i+1:]):
                      # Remove comments enclosed in '(**)'
                    # sub_line = re.sub(r'\(\*.*?\*\)', '', sub_line)
                    sub_line = sub_line.lstrip()

                    if sub_line.startswith("(*") and re.search(r"\*\)$", sub_line):
                        continue  # skip to next iteration if line is a comment
                    
                    # check if the line has curly braces '{}'
                    if "{" in sub_line and "}" in sub_line:
                        # extract the content inside the curly braces
                        brace_content = re.search(r'\{(.+?)\}', sub_line).group(1)
                        # use the content inside the braces as the key in the dictionary
                        self.identDict[brace_content] = ""
                        # remove the content inside the braces from the line
                        sub_line = re.sub(r'\{.*?\}', '', sub_line)
                    
                    regex = ""
                     # Remove comments enclosed in '(**)'
                    sub_line = re.sub(r'\(\*.*?\*\)', '', sub_line)
                    if j == 0:
                        # Remove actions enclosed in '{}'
                        sub_line = re.sub(r'\{.*?\}', '', sub_line)
                        if sub_line.startswith("|"):
                            sub_line = sub_line[1:].lstrip()
                        regex += sub_line
                        self.regex_list.append(regex.strip())
                        if brace_content:
                            self.identDict[brace_content] = regex.strip()
                            brace_content = None
                    else:
                        if sub_line.startswith("|"):
                            # Remove actions enclosed in '{}'
                            sub_line = re.sub(r'\{.*?\}', '', sub_line)
                            regex += sub_line.strip()[1:]
                            self.regex_list.append(regex.strip())
                            # print(f"Found regex: {regex}")
                            if brace_content:
                                self.identDict[brace_content] = regex.strip()
                                brace_content = None
                        else:
                            break

        # print("\nDICCIONARIO IDENT - Identificacion de los tokens:")
        # print(self.identDict)
        
        self.regex_list = [x.replace(' ', '') for x in self.regex_list]
        # print("\nPRIMERA LISTA - Regexes Originales:")
        # print(self.regex_list)
        
        for key in reversed(list(self.regex_dict.keys())):
            value = self.regex_dict[key]
            for inner_key, inner_value in self.regex_dict.items():
                if inner_key in value:
                    value = value.replace(inner_key, inner_value)
            self.regex_dict[key] = value


        for i in range(len(self.regex_list)):
            for key in self.regex_dict.keys():
                list2 = self.regex_list[i].split(" ")
                for j in range(len(list2)):
                    if key in list2[j]:
                        list2[j] = list2[j].replace(key, self.regex_dict[key]) 
                self.regex_list[i] = " ".join(list2)

        # print("\nDICCIONARIO REGEX - Regexes con sus valores originales:")
        # print(self.regex_dict)

        # print("\nSEGUNDA LISTA - Regexes Con valor Original:")
        # print(self.regex_list)

        for i in range(len(self.regex_list)):
            if self.regex_list[i] in self.tokens.keys():
                self.regex_list[i] = self.tokens[self.regex_list[i]]
            if '.' in self.regex_list[i]:
                self.regex_list[i] = self.regex_list[i].replace('.', ',')


        # print("\nTERCERA LISTA - Regexes Con Tokens Reemplazados:")
        # print(self.regex_list)

        return self.regex_list
    
    def modifyRegexes(self):

        for regex in self.regex_list:
            # print(regex)
            # Modify [0-9]+ to (0|1|2|3|4|5|6|7|8|9)+
            regex = re.sub(r'\[0-9\]', '(0|1|2|3|4|5|6|7|8|9)', regex)
            regex = re.sub(r"\['0'-'9'\]", '(0|1|2|3|4|5|6|7|8|9)', regex)

            # Modify [a-z] to (a|b|c|...|z)
            regex = re.sub(r'\[a-z\]', '(a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z)', regex)
            regex = re.sub(r"\['a'-'z'\]", '(a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z)', regex)


            # Modify [a-zA-Z] to (a|b|c|...|Z)
            regex = re.sub(r'\[a-zA-Z\]', '(a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z)', regex)
            regex = re.sub(r"\['a'-'z''A'-'Z'\]", '(a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z)', regex)
            
            # Modify [ \t\n\r] to ( |\t|\n\r)
            regex = re.sub(r'\[ \\t\\n\\r\]', '( |\t|\n|\r)', regex)
            regex = re.sub(r'\[ \\t\\n\]', '( |\t|\n)', regex)
            regex = re.sub(r'\[\\t\\n\]', '( |\t|\n)', regex)
            regex = re.sub(r'\[\\t\\n\\r\]', '(\t|\n|\r)', regex)
            regex = re.sub(r"\[' ''\\t''\\n'\]", '( |\t|\n)', regex)
            
            
            self.regexFinalList.append(regex)

        # print("\nCUARTA LISTA - Regexes Modificados:")
        # print(self.regexFinalList)
        return self.regexFinalList
    
    def getAFDs(self, list):
        afdList = []
        for regex in self.updatedList:
            postfix = Postfix(regex)
            postfix = postfix.infixToPostfix()

            tree = Tree(postfix)
            afd = tree.dirDfaConstruction()
            afdList.append(afd)

        for afd in afdList:
            reverse_tokens = {v: k for k, v in self.tokens.items()}  # reverse the keys and values in the dictionary
            for transition in afd.transitions:
                # print(transition)
                if transition.symbol in reverse_tokens.keys():
                    transition.symbol = reverse_tokens[transition.symbol]
                if transition.symbol == ',':
                    transition.symbol = '.'

        self.dfaList = afdList
        return afdList
    
    def simulateAFD(self, afd, token):
        simulation = DFASimulation(afd, token)
        # print(f"{token}  --> " + str(simulation.simulate()))
        return simulation.simulate()
            
    def isValidToken(self, token):
        if self.simulateAFD(self.megaDFA, token):
            return True
        return False

    def getUpdatedList(self):
        newList = []
        for regex in self.regexFinalList:
            regularExpression = Regex()
            regularExpression.regex = regex
            regex = regularExpression.checkRegex()
            # print("\nRegex: \n" + regex)
            # if para ver si la regex es falsa e imprimir los errores
            if not regularExpression.isValid:
                raise Exception(regex)
            newList.append(regex)

        return newList

    def getMegaRegex(self):
        megaRegex = ""
        for regex in self.regexFinalList:
            megaRegex += regex + "|"
        megaRegex = megaRegex[:-1]
        megaRegex = "(" + megaRegex + ")"
        # print(megaRegex)
        return megaRegex

    def buildDFA(self):
        postfix = Postfix(self.megaRegex)
        postfix = postfix.infixToPostfix()
        # print("\nPostfix:\n"+postfix)


        tree = Tree(postfix)
        megaDFA = tree.dirDfaConstruction()

        reverse_tokens = {v: k for k, v in self.tokens.items()}  # reverse the keys and values in the dictionary
        for transition in megaDFA.transitions:
            # print(transition)
            if transition.symbol in reverse_tokens.keys():
                transition.symbol = reverse_tokens[transition.symbol]
            if transition.symbol == ',':
                transition.symbol = '.'
       
        # megaDFA_drawer = Drawer(
        # megaDFA.transitions, megaDFA.initial_state, megaDFA.final_states)
        # megaDFA_drawer.draw(filename='graphs/megaAutomata')

        # directSim = DFASimulation(megaDFA, '2var')
        # print("AFD D  --> " + str(directSim.simulate()))


        return megaDFA
    
    def generateOutput(self, outputName):
        pythonCode = f"""#importamos la clase de Yalex para poder obtener toda su informacion
from YALex import *

#creamos el objeto de la clase YALex y compilamos el archivo
yalex = YALex('{self.filename}')
yalex.compiler()

def main():

    #input del archivo de entrada
    archivo = input('\\nIngrese el nombre del archivo de entrada: ')

    #creamos la variable del archivo
    texto = 'Inputs/'+archivo+'.txt'

    #creamos la variable del archivo
    # texto = 'Inputs/texto.txt'

    #leemos el archivo de texto
    with open(texto, 'r') as file:  
        data = file.read()
    
    words = data.split()
    #obtenemos la informacion del mega Automata
    megaAFD = yalex.megaDFA

    #mandamos a llamar al analizador lexico
    analizadorLexico(data, megaAFD)
    analizadorLexico2(words)

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

        if symbol == "\\n":
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
        print('\\n---ANALISIS LEXICO FALLIDO---')
        for error in errores:
            print(error)
    else:
        print('\\n-------ANALISIS LEXICO EXITOSO-------')
        max_lex_len = max(len(lex.strip()) for lex in lexemas)
        for i, lex in enumerate(lexemas):
            # Remove white spaces from lex
            lex = lex.strip()

            if lex == '':
                continue

            formatted_lex = lex.ljust(max_lex_len)
            tokens[i] = tokens[i].replace('print("', f'print("{{formatted_lex}} -> ')
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
        if '\\n' in word:
            line_number += 1
            position_number = 0

        for i, afd in enumerate(afdList):
            if yalex.simulateAFD(afd, word):
                tokens.append(keyTokenList[i])

        if not yalex.isValidToken(word):
            if len(word) == 1:
                errores.append(f"Error lexico en la linea {{line_number}}, posicion {{position_number}}: caracter '{{word}}' no reconocido.")
            else:
                errores.append(f"Error lexico en la linea {{line_number}}, posicion {{position_number}}: token '{{word}}' no reconocido.")

    if not errores:
        print('\\n-------ANALISIS LEXICO EXITOSO-------')
        max_lex_len = max(len(lex.strip()) for lex in data)
        for i, word in enumerate(data):
            # Remove white spaces from word
            word = word.strip()

            if word == '':
                continue

            # Update position number and line number for each word
            position_number += 1
            if '\\n' in word:
                line_number += 1
                position_number = 0

            formatted_word = word.ljust(max_lex_len)
            tokens[i] = tokens[i].replace('print("', f'print("{{formatted_word}} -> ')
            eval(tokens[i].strip())
    else:
        print('\\n---ANALISIS LEXICO FALLIDO---')
        for error in errores:
            print(error)


if __name__ == '__main__':
    main()
        """
      
        with open(outputName, 'w') as file:
            file.write(f"{pythonCode}")