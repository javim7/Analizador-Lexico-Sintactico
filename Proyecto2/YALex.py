import re
from Proyecto1.Tree import *
from Proyecto1.Regex import *
from Proyecto1.Drawer import *
from Proyecto1.Postfix import *
from Proyecto1.Thompson import *
from Proyecto1.Simulation import *

class YALex:
    def __init__(self, filename):
        try:
            self.file = open(filename, 'r')
            self.lines = self.file.readlines()
            self.regex_list = []
            self.regexFinalList = []
            self.updatedList = []
            self.regex_dict = {}
            self.erros = False
            self.dfaList = []
            self.nfaList = []
            self.megaRegex = ''
        except FileNotFoundError:
            raise Exception('File could not be opened')
   
    def compiler(self):
        # detectamos errores
        errores = self.detect_errors()

        # si hay errores, los mostramos, de lo contrario, continuamos
        if self.erros:
            raise Exception(errores)
        
        self.getRegexes()
        self.modifyRegexes()

        # print(self.regexFinalList)
        self.updatedList = self.getUpdatedList()
        # print(self.updatedList)

        self.megaRegex = '|'.join([ x  for x in self.updatedList])

        print(self.megaRegex)
        self.buildDFA()

    def detect_errors(self):
        stack = []
        rule_list = []
        for i, line in enumerate(self.lines):
            # print( i, line)
            # Check parentheses and curly braces are balanced and in correct order
            for c in line:
                if c == '(':
                    stack.append(c)
                    stack.append(i)
                elif c == ')':
                    if not stack or stack[-2] != '(':
                        self.erros = True
                        return f"')' desbalanceado en la linea: {i+1}"
                    stack.pop()
                    stack.pop()
                elif c == '{':
                    stack.append(c)
                    stack.append(i)
                elif c == '}':
                    if not stack or stack[-2] != '{':
                        self.erros = True
                        return "'}' desbalanceado en la linea: " + i+1
                    stack.pop()
                    stack.pop()
            # Check import statements are correctly formatted
            if line.startswith("import"):
                if not re.search(r'import\s+[a-zA-Z0-9_]+\s*', line):
                    self.erros = True
                    return f"Formato incorrecto de 'import' en la linea: {i+1}"
            # Check let statements are correctly formatted
            if line.startswith("let"):
                if rule_list:
                    self.erros = True
                    return f"'let' despues de 'rule' en la linea: {i+1}"
                if '=' not in line:
                    self.erros = True
                    return f"Formato incorrecto de 'let' en la linea: {i+1}"
                if not re.search(r'let\s+[a-zA-Z0-9_]+\s*=\s*\".*\"\s*[\+\-\/\*]?[\s]*[a-zA-Z0-9_]*\S', line):
                    self.errors = True
                    return f"Formato incorrecto de 'let' en la linea: {i+1}"
            # Check rule statements are correctly formatted
            if line.startswith("rule"):
                if '=' not in line:
                    self.erros = True
                    return f"Formato incorrecto de 'rule' en la linea: {i+1}"
                if not re.search(r'rule\s+[a-zA-Z0-9_]+\s*(\[[a-zA-Z0-9_, ]+\])?\s*=\s*\n', line):
                    self.erros = True
                    return f"Formato incorrecto de 'rule' en la linea: {i+1}"
                rule_list.append(line.strip().split()[1])
            if '=' in line:
                if not line.startswith("rule") and not line.startswith("let"):
                    self.erros = True
                    return f"Formato incorrecto de variable en la linea: {i+1}"
        if stack:
            self.erros = True
            return f"'{stack[-2]}' desbalanceado en la linea: {str(stack[-1]+1)}"
        return None


    def getRegexes(self):

        pattern = r"let\s+(\w+)\s*=\s*(.*)"

        for i, line in enumerate(self.lines):
            match = re.match(pattern, line)
            if match:
                self.regex_dict[match.group(1)] = match.group(2)
            if line.startswith("rule"):
                for j, sub_line in enumerate(self.lines[i+1:]):
                      # Remove comments enclosed in '(**)'
                    sub_line = re.sub(r'\(\*.*?\*\)', '', sub_line)
                for j,sub_line in enumerate(self.lines[i+1:]):
                    sub_line = sub_line.lstrip()
                    if sub_line.startswith("(*") and re.search(r"\*\)$", sub_line):
                        continue  # skip to next iteration if line is a comment
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
                    else:
                        if sub_line.startswith("|"):
                            # Remove actions enclosed in '{}'
                            sub_line = re.sub(r'\{.*?\}', '', sub_line)
                            regex += sub_line.strip()[1:]
                            self.regex_list.append(regex.strip())
                            # print(f"Found regex: {regex}")
                        else:
                            break
        
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

        # print(self.regex_dict)
        # print(self.regex_list)
        return self.regex_list
    
    def modifyRegexes(self):

        for regex in self.regex_list:
            # print(regex)
            # Modify [0-9]+ to (0|1|2|3|4|5|6|7|8|9)+
            regex = re.sub(r'\[0-9\]', '(0|1|2|3|4|5|6|7|8|9)', regex)
            
            # Modify [a-z] to (a|b|c|...|z)
            regex = re.sub(r'\[a-z\]', '(a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z)', regex)

            # Modify [a-zA-Z] to (a|b|c|...|Z)
            regex = re.sub(r'\[a-zA-Z\]', '(a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z)', regex)
            
            # Modify [ \t\n\r] to ( |\t|\n\r)
            regex = re.sub(r'\[ \\t\\n\\r\]', '( |\t|\n|\r)', regex)
            
            # Modify [ \t\n\r] to ( |\t|\n\r)
            regex = re.sub(r'\[\\t\\n\\r\]', '(\t|\n|\r)', regex)
            
            self.regexFinalList.append(regex)

        # print(self.regexFinalList)
        return self.regexFinalList
    
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
        print(megaRegex)
        return megaRegex

    def buildDFA(self):
        postfix = Postfix(self.megaRegex)
        postfix = postfix.infixToPostfix()
        print("\nPostfix:\n"+postfix)

        tree = Tree(postfix)
        megaDFA = tree.dirDfaConstruction()
        
        # megaDFA_drawer = Drawer(
        # megaDFA.transitions, megaDFA.initial_state, megaDFA.final_states)
        # megaDFA_drawer.draw(filename='Proyecto2/graphs/megaAutomata')
        
        directSim = DFASimulation(megaDFA, 'abc352')
        print("AFD D  --> " + str(directSim.simulate()))