import copy
import pydot
import prettytable as pt

from Set import *
from Drawer import *
from Grammar import *
from Automaton import *
from collections import OrderedDict

class YAPar:
    def __init__(self, inputname, outputname=None):
        try:
            self.filename = inputname
            self.file = open(inputname, 'r')
            self.outputname = outputname
            self.lines = self.file.readlines()
            self.errors = False
            self.tokens = []
            self.grammar = {}
            self.increasedGrammar = {}
            self.estados = 0
            self.sets = []
            self.afdLR0 = None
            self.afdLR02 = None
            self.actionTable = {}
            self.goToTable = {}
            self.first = {}
            self.follow = {}
        except FileNotFoundError:
            raise Exception('File could not be opened')
        
    def compiler(self):
        if self.outputname is None:
            # detectamos errores
            errores = self.detectErrors()

            # si hay errores, los mostramos, de lo contrario, continuamos
            if self.errors:
                errores_str = "\n".join(set(errores))
                raise Exception(errores_str)
            
            # si no hay errores, continuamos

            #obtenemos los tokens y verificamos que esten en el yalex
            self.tokens = self.getTokens()
            self.check_tokens(self.tokens)

            #obtenemos la gramatica y la aumentamos
            self.grammar = self.defineGrammar()
            self.increasedGrammar = self.increaseGrammar(self.grammar)

            #obtenemos el primer conjunto y con esto el automata LR(0)
            self.firstSet(self.increasedGrammar)

            self.grammar.first = self.compute_first(self.grammar.productions)
            self.grammar.follow = self.compute_follow(self.grammar.productions)

            #construimos la tabla SLR
            self.actionTable, self.goToTable = self.createSLRTable()
            self.drawTable()
        
        else:
            self.generateOutput(self.outputname)

    def detectErrors(self):
        errors = []
        yaSonProducciones = False
        for i, line in enumerate(self.lines):
            if line.strip().startswith("/*") and not line.strip().endswith("*/"):
                print(line)
                errors.append(f"Formato incorrecto de 'comentario' en la linea: {i+1}")
            if line.strip().endswith("*/") and not line.strip().startswith("/*"):
                print(line)
                errors.append(f"Formato incorrecto de 'comentario' en la linea: {i+1}")
            if line.startswith("%") and line.strip() != '%%':
                if yaSonProducciones:
                    errors.append(f"Token en seccion incorrecta en la linea: {i+1}")
                if line.startswith("%token"):
                    words = line.split()
                    if len(words) < 2:
                        errors.append(f"'%token' no identificado en la linea: {i+1}")
                else:
                    errors.append(f"Formato incorrecto de 'token' en la linea: {i+1}")
            if 'token' in line and not line.startswith("%"):
                errors.append(f"Formato incorrecto de '%token' en la linea: {i+1}")
            if line.startswith("IGNORE"):
                words = line.split()
                if len(words) < 2:
                    errors.append(f"'IGNORE' no identificado en la linea: {i+1}")
            if line.strip() == '%%':
                yaSonProducciones = True
        if not yaSonProducciones:
            errors.append("No se encontro la marca '%%' en el archivo")
        self.errors = bool(errors)
        return errors if errors else None

    
    def getTokens(self):
        tokens = []
        ignored_tokens = set()
        for line in self.lines:
            line = line.strip()
            if line == '%%':
                break
            elif line.startswith('/*') and line.endswith('*/'):
                # Ignore comments
                continue
            elif line.startswith('%token'):
                # Get tokens
                line_tokens = line.split()[1:]
                tokens.extend(line_tokens)
            elif line.startswith('IGNORE'):
                # Get ignored tokens
                ignored_tokens.update(line.split()[1:])
            
        # Remove ignored tokens from the token list
        tokens = [token for token in tokens if token not in ignored_tokens]
        return tokens

    def check_tokens(self, tokens):
        print("\n-----CHECKING TOKENS-----")
        with open('tokens.txt', 'r') as file:
            file_tokens = [line.strip() for line in file.readlines()]
        
        all_tokens_present = True
        
        for token in tokens:
            if token in file_tokens:
                print(f"{token}: True")
            else:
                print(f"{token}: False")
                all_tokens_present = False
        
        print(f"Tokens checked = {len(tokens)}, Token Check = {all_tokens_present}")
        return all_tokens_present


    def defineGrammar(self):
        grammar = Grammar()
        nonTerminals = []
        terminals = []

        # Skip lines until "%%"
        i = 0
        while i < len(self.lines) and not self.lines[i].startswith("%%"):
            i += 1
        if i == len(self.lines):
            raise Exception("Grammar productions not found")

       # Read productions
        nonterm = None
        prods = []
        for line in self.lines[i+1:]:
            line = line.strip()
            if not line:
                continue
            if line.endswith(":"):
                # New non-terminal name
                if nonterm is not None:
                    grammar.productions[nonterm] = prods
                    nonTerminals.append(nonterm)
                nonterm = line[:-1].strip()
                prods = []
            else:
                if line.startswith('/*') and line.endswith('*/'):
                    continue
                # Production alternative
                productions = [prod.strip() for prod in line.split("|") if prod.strip()]
                prods.extend(productions)
                for prod in productions:
                    for symbol in prod.split():
                        if symbol.islower():
                            nonTerminals.append(symbol)
                        elif symbol != ";":
                            terminals.append(symbol)

        # Add last non-terminal
        if nonterm is not None:
            grammar.productions[nonterm] = prods
            nonTerminals.append(nonterm)

        # Clean up lists
        nonTerminals = list(set(nonTerminals))
        terminals = list(set(terminals))

        # Remove semicolons from productions
        for nonterm, prods in grammar.productions.items():
            grammar.productions[nonterm] = [prod for prod in prods if prod != ";"]

        grammar.initialState = next(iter(grammar.productions.keys()))
        grammar.nonTerminals = sorted(nonTerminals)
        grammar.terminals = sorted(terminals)

        # print(grammar)
        return grammar

    def increaseGrammar(self, grammar):
        tempGrammar = copy.deepcopy(grammar)
        newInitialState = tempGrammar.initialState + "'"
        if newInitialState in tempGrammar.productions:
            tempGrammar.productions[newInitialState].insert(0, tempGrammar.initialState)
            key = newInitialState
            value = tempGrammar.productions.pop(key)
            tempGrammar.productions = OrderedDict([(key, value)] + list(tempGrammar.productions.items()))
        else:
            tempGrammar.productions = OrderedDict([(newInitialState, [tempGrammar.initialState])] + list(tempGrammar.productions.items()))

        tempGrammar.productions = dict(tempGrammar.productions)

        # print("original")
        # print(grammar)
        # print("temp")
        # print(tempGrammar)
        return tempGrammar

    def firstSet(self, grammar):
        set = Set()
        tempGrammar = copy.deepcopy(grammar)
        increasedItem = next(iter(tempGrammar.productions.items()))

        #agregando el punto
        withDot = '.' + increasedItem[1][0]
        increasedItem[1][0] = withDot

        set.corazon[increasedItem[0]] = increasedItem[1]
        set.productions[increasedItem[0]] = increasedItem[1]

        # print(set.corazon)
        # print(set)

        firstSet = self.cerradura(set)
        firstSet.estado = self.estados
        self.estados += 1
        # print(firstSet)
        self.buildAutomaton(firstSet)
        # self.buildAutomaton2(firstSet)

    # Define a function to format the state labels
    def format_label(self, set):
        label = f"State {set.estado}\n"
        for key, value in set.productions.items():
            if key in set.corazon:
                label += f"*** {key} -> {' | '.join(value)}\\l"
            else:
                label += f"{key} -> {' | '.join(value)}\\l"
        
        return label


    def buildAutomaton(self, firstSet):
        afd = DFA(firstSet.estado, [0])
        corazones = []

        self.sets.append(firstSet)
        corazones.append(firstSet.corazon)
        # print("corazones -> ",corazones)
        for set in self.sets:
            symbols = self.getSetSymbols(set)
            # print("symbols -> ", symbols)
            for symbol in symbols:
                # print("symbol -> ",symbol)
                newSet = self.irA(set, symbol)
                # print(newSet)
                if newSet.corazon not in corazones:
                    newSet.estado = self.estados
                    self.estados += 1
                    # print(newSet)
                    self.sets.append(newSet)
                    corazones.append(newSet.corazon)
                    transition = Transition(set, symbol, newSet) #aca se puede agregar el estado o las producciones dependiendo de que se necesite
                    afd.transitions.append(transition)
                    # print("corazones -> ",corazones)
                    # print()
                else:
                    nextStateIndex = corazones.index(newSet.corazon)
                    nextState = self.sets[nextStateIndex]
                    transition = Transition(set, symbol, nextState) #aca se puede agregar el estado o las producciones dependiendo de que se necesite
                    afd.transitions.append(transition)

        graph = pydot.Dot(graph_type='digraph')

        for set in self.sets:
            label = self.format_label(set)
            node = pydot.Node(label)
            graph.add_node(node)

        for transition in afd.transitions:
            state = self.format_label(transition.state)
            next_state = self.format_label(transition.next_state)
            edge = pydot.Edge(state, next_state, label=transition.symbol)
            graph.add_edge(edge)
        
        for transition in afd.transitions[::-1]:
            if transition.state.estado == 1:
                state = self.format_label(transition.state)
                next_state = 'accept'
                edge = pydot.Edge(state, next_state, label='$')
                graph.add_edge(edge)
                break
            elif transition.next_state.estado == 1:
                state = self.format_label(transition.next_state)
                next_state = 'accept'
                edge = pydot.Edge(state, next_state, label='$')
                graph.add_edge(edge)
                break

        graph.write_pdf('graphs/LR0.pdf')
        afd.final_states = []
        afd.final_states.append('accept')

        # afd.print_dfa()
        # afd.dfa_info()

        self.afdLR0 = afd
        return self.afdLR0

    def buildAutomaton2(self, firstSet):
        afd = DFA(firstSet.estado, [0])
        corazones = []

        self.sets.append(firstSet)
        corazones.append(firstSet.corazon)
        # print("corazones -> ",corazones)
        for set in self.sets:
            symbols = self.getSetSymbols(set)
            # print("symbols -> ", symbols)
            for symbol in symbols:
                # print("symbol -> ",symbol)
                newSet = self.irA(set, symbol)
                # print(newSet)
                if newSet.corazon not in corazones:
                    newSet.estado = self.estados
                    self.estados += 1
                    # print(newSet)
                    self.sets.append(newSet)
                    corazones.append(newSet.corazon)
                    transition = Transition(set.estado, symbol, newSet.estado) #aca se puede agregar el estado o las producciones dependiendo de que se necesite
                    afd.transitions.append(transition)
                    # print("corazones -> ",corazones)
                    # print()
                else:
                    nextStateIndex = corazones.index(newSet.corazon)
                    nextState = self.sets[nextStateIndex]
                    transition = Transition(set.estado, symbol, nextState.estado) #aca se puede agregar el estado o las producciones dependiendo de que se necesite
                    afd.transitions.append(transition)
        
        for i, transition in enumerate(afd.transitions[::-1]):
            if transition.state == 1:
                afd.getStates()
                finalState = len(afd.states)
                transition = Transition(transition.state, '$', finalState)
                afd.transitions.insert(len(afd.transitions) - i, transition)
                afd.final_states = []
                afd.final_states.append(finalState)
                break
            elif transition.next_state == 1:
                afd.getStates()
                finalState = len(afd.states)
                transition = Transition(transition.next_state, '$', finalState)
                afd.transitions.insert(len(afd.transitions) - i, transition)
                afd.final_states = []
                afd.final_states.append(finalState)
                break
               
        afd_drawer = Drawer(
            afd.transitions, afd.initial_state, afd.final_states, 'LR(0)')
        afd_drawer.draw(filename='graphs/LR0')
        
        afd.print_dfa()
        afd.dfa_info()

        self.afdLR02 = afd
        return self.afdLR0

    def cerradura(self, I):
        J = copy.deepcopy(I)
        # J.productions = {"term": ['term TIMES factor.']}
        added = True  # flag to indicate whether any new items were added
        while added:
            added = False
            # create a copy of the dictionary to avoid "dictionary changed size during iteration" error
            productions_copy = dict(J.productions)
            for key, value in productions_copy.items():
                for prod in value:
                    parts = prod.split()
                    for part in parts:
                        if '.' in part:
                            if part[-1] == '.':
                                next_part_idx = parts.index(part) + 1
                                if next_part_idx == len(parts) or parts[next_part_idx] in self.increasedGrammar.terminals:
                                    continue
                                else:
                                    part = parts[next_part_idx]
                            sinPunto = part.replace('.', '')
                            # print(sinPunto)
                            if sinPunto in self.increasedGrammar.productions:
                                for new_prod in self.increasedGrammar.productions[sinPunto]:
                                    new_item = '.' + new_prod
                                    if new_item not in J.productions.setdefault(sinPunto, []):
                                        J.productions.setdefault(sinPunto, []).append(new_item)
                                        J.resto.setdefault(sinPunto, []).append(new_item)
                                        added = True
        return J

    def irA(self, I, X):
        J = Set()
        I2 = copy.deepcopy(I)
        for key, value in I2.productions.items():
            for prod in value:
                parts = prod.split()
                # print(parts)
                for i, part in enumerate(parts):
                    if '.' in part:
                        if part.startswith('.'):
                            sinPunto = part.replace('.', '')
                            if sinPunto == X:
                                # new_item = part.replace('.' + X, X + '.')
                                # new_prod = prod.replace(part, new_item)
                                new_prod = ' '.join([X + '.' if p == '.' + X else p for p in parts])
                                J.productions.setdefault(key, []).append(new_prod)
                                J.corazon.setdefault(key, []).append(new_prod)
                        elif part.endswith('.'):
                            part_idx = parts.index(part)
                            next_part_idx = parts.index(part) + 1
                            if next_part_idx == len(parts):
                                continue
                            # print("parte ",part)
                            next_part = parts[next_part_idx]
                            sinPunt = part.replace('.', '')
                            if next_part == X:
                                next_part += '.'
                                parts[next_part_idx] = next_part
                                parts[part_idx] = sinPunt
                                new_prod = ' '.join(parts)
                                J.productions.setdefault(key, []).append(new_prod)
                                J.corazon.setdefault(key, []).append(new_prod)

        # print(J)
        return self.cerradura(J)
    
    def getSetSymbols(self, I):
        symbols = []
        for value in I.productions.values():
            for production in value:
                parts = production.split()
                # print(parts)
                for i, part in enumerate(parts):
                    part = part.strip()
                    if not part:
                        continue
                    if '.' in part:
                        if part.startswith('.'):
                            next_symbol = part[1:]
                            # print(next_symbol)
                            if next_symbol not in symbols:
                                symbols.append(next_symbol)
                        elif part.endswith('.'):
                            if i < len(parts) - 1:
                                next_part = parts[i+1].strip()
                                next_symbol = next_part.split()[0]
                                if next_symbol not in symbols:
                                    symbols.append(next_symbol)

        return symbols
    
    def compute_first(self, grammar):
        first = {nonterminal: [] for nonterminal in grammar}
        changes = True
        while changes:
            changes = False
            for nonterminal in grammar:
                for production in grammar[nonterminal]:
                    symbols = production.split()
                    for i, symbol in enumerate(symbols):
                        if symbol.isupper():
                            # Terminal symbol
                            if symbol not in first[nonterminal]:
                                first[nonterminal].append(symbol)
                                changes = True
                            break
                        else:
                            # Nonterminal symbol
                            for first_symbol in first[symbol]:
                                if first_symbol not in first[nonterminal]:
                                    first[nonterminal].append(first_symbol)
                                    changes = True
                            if 'EPSILON' not in first[symbol]:
                                break
                    else:
                        # All symbols in the production derive EPSILON
                        if 'EPSILON' not in first[nonterminal]:
                            first[nonterminal].append('EPSILON')
                            changes = True
        return first
    
    def compute_follow(self, grammar):
        # Initialize follow sets to empty lists
        follow = {nonterminal: [] for nonterminal in grammar}

        # Initialize the start symbol's follow set to [$]
        start_symbol = list(grammar.keys())[0]
        follow[start_symbol].append('$')

        # Compute the first sets for the grammar
        first = self.compute_first(grammar)

        # Keep track of changes to the follow sets
        changes = True
        while changes:
            changes = False
            for nonterminal in grammar:
                for production in grammar[nonterminal]:
                    symbols = production.split()
                    for i, symbol in enumerate(symbols):
                        if symbol.islower():
                            # Nonterminal symbol
                            if i == len(symbols) - 1:
                                # Last symbol in the production
                                for follow_symbol in follow[nonterminal]:
                                    if follow_symbol not in follow[symbol]:
                                        follow[symbol].append(follow_symbol)
                                        changes = True
                            else:
                                # Not the last symbol in the production
                                if symbols[i+1].islower():
                                    # Next symbol is a nonterminal
                                    for first_symbol in first[symbols[i+1]]:
                                        if first_symbol != 'EPSILON' and first_symbol not in follow[symbol]:
                                            follow[symbol].append(first_symbol)
                                            changes = True
                                    if 'EPSILON' in first[symbols[i+1]]:
                                        for follow_symbol in follow[nonterminal]:
                                            if follow_symbol not in follow[symbol]:
                                                follow[symbol].append(follow_symbol)
                                                changes = True
                                else:
                                    # Next symbol is a terminal
                                    if symbols[i+1] not in first:
                                        # Add the terminal symbol to the first set
                                        first[symbols[i+1]] = [symbols[i+1]]
                                    if symbols[i+1] != 'EPSILON' and symbols[i+1] not in follow[symbol]:
                                        follow[symbol].append(symbols[i+1])
                                        changes = True
                        else:
                            # Terminal symbol
                            continue
        return follow
    
    def createSLRTable(self):
        grammar_productions = self.grammar.productions
        terminals = self.grammar.terminals
        nonTerminals = self.grammar.nonTerminals
        follow = self.grammar.follow
        lr0 = self.afdLR0
        augmented_header = self.grammar.initialState + "'"
        
        action = {}
        goTo = {}

        lr0.getStates2()
        for state in lr0.states:
            state_number = state.estado

            if state_number not in action:
                action[state_number] = {}
            if state_number not in goTo:
                goTo[state_number] = {}

            if state_number == 1:
                action[state_number]['$'] = 'acc'

            for transition in lr0.transitions:
                if transition.state == state:
                    if transition.symbol == '$':
                        action[state_number]['$'] = 'acc'

                    elif transition.symbol in terminals:
                        action[state_number][transition.symbol] = 's' + str(transition.next_state.estado)

                    elif transition.symbol in nonTerminals:
                        goTo[state_number][transition.symbol] = transition.next_state.estado

            for production_key, production_values in state.productions.items():
                if production_key != augmented_header:  # Check if production key is not the augmented header
                    for production in production_values:
                        if production.endswith('.'):
                            # print(production_key, ' -> ', production)
                            key = production_key
                            follow_set = follow[key]
                            reduced_production = production[:-1]
                            production_numbers = {}

                            count = 1
                            for key, values in grammar_productions.items():
                                for value in values:
                                    production_numbers[value] = count
                                    count += 1

                            production_number = production_numbers[reduced_production]

                            for terminal in follow_set:
                                existing_action = action[state_number].get(terminal)
                                if existing_action is not None:
                                    if existing_action.startswith('r') and existing_action != 'r' + str(production_number):
                                        raise Exception("Conflicto: Reducción-Desplazamiento en el estado {} y símbolo {}".format(state_number, terminal))
                                    elif existing_action.startswith('s') and existing_action != 's' + str(production_number):
                                        raise Exception("Conflicto: Desplazamiento-Reducción en el estado {} y símbolo {}".format(state_number, terminal))
                                else:
                                    action[state_number][terminal] = 'r' + str(production_number)


        return action, goTo


    def drawTable(self):
        # Get the list of terminals and non-terminals
        terminals = self.grammar.terminals.copy()
        terminals.append('$')
        nonTerminals = self.grammar.nonTerminals

        # Determine the width of each column
        estado_width = max(len(str(state)) for state in self.actionTable.keys()) + 2
        acciones_width = max(len(term) for term in terminals) + 2
        ir_a_width = max(len(nt) for nt in nonTerminals) + 2

        # Create the table
        table = pt.PrettyTable()
        table.field_names = ['estado', 'acciones'] + terminals + ['', 'ir_A'] + nonTerminals

        # Add the rows to the table
        for state, actions in self.actionTable.items():
            action_values = [actions.get(term, '') for term in terminals]
            goto_values = [self.goToTable[state].get(nt, '') for nt in nonTerminals]

            row = [state, ''] + action_values + ['', ''] + goto_values
            table.add_row(row)

        # Set column alignments
        table.align = 'l'

        # Set column alignments for subcolumns
        table.align['estado'] = 'c'
        table.align['acciones'] = 'c'
        table.align[''] = 'c'
        table.align['ir_A'] = 'c'

        # Print the table
        print()
        print(table.get_string(title="SLR TABLE"))

    def generateOutput(self, outputName):
        pythonCode = f"""#importamos la clase de Yalex para poder obtener toda su informacion
from YAPar import *

#creamos el objeto de la clase YALex y compilamos el archivo
yapar = YAPar('{self.filename}')

yapar.compiler()

def main():

    #input del archivo de entrada
    archivo = input('\\nIngrese el nombre del archivo a parsear: ')

    #creamos la variable del archivo
    texto = 'YAPInputs/'+archivo+'.txt'

    #creamos la variable del archivo
    # texto = 'YAPInputs/input1.txt'

    #leemos el archivo de texto
    with open(texto, 'r') as file:  
        data = file.read().split()

    data.append('$')
    #llamar a la funcion de parseo
    parseo(data)
    
def parseo(data):
    # Definition of variables
    stack = []
    symbols = []
    errorList = []
    dataCopy = data.copy()
    actionTable = yapar.actionTable
    gotoTable = yapar.goToTable
    grammar = yapar.grammar
    stack.append(next(iter(actionTable)))
    production_numbers = enumerateGrammar(grammar.productions)

    # Start the parsing loop
    going = True
    contador = 0
    print("\\n" + "-" * 60 + " PARSEO SLR " + "-" * 60)
    print(f"{{'ITERACION':<10}} {{'PILA':<20}} {{'SIMBOLOS':<35}} {{'ENTRADA':<35}} {{'ACCION':<35}}")
    print("-" * 132)
    while going:
        contador += 1
        
        # Obtain the elements to verify
        lastStack = stack[-1]
        firstData = data[0]

        # Check if it is accepted or not
        if actionTable.get(lastStack, {{}}).get(firstData) == 'acc':
            going = False
            break

        # Check if it is a shift
        elif actionTable.get(lastStack, {{}}).get(firstData, '\\nerror')[0] == 's':
            symbols.append(firstData)
            stack.append(int(actionTable[lastStack][firstData][1:]))
            data.pop(0)
            action = 'desplazar'
            print(f"{{contador:<10}} {{str(stack):<20}} {{str(symbols):<35}} {{str(data):<35}} {{action:<35}}")

        # Check if it is a reduce
        elif actionTable.get(lastStack, {{}}).get(firstData, '\\nerror')[0] == 'r':

            # Obtain the number of production
            prodNumber = int(actionTable[lastStack][firstData][1:])
            for production, number in production_numbers.items():
                if number == prodNumber:
                    break
            else:
                # print("\\nError: numero invalido de produccion")
                errorList.append("Error: numero '" + number + "' invalido de produccion")
                break
            
            # Perform the necessary pops
            prodList = production.split()
            if len(prodList) > len(stack):
                # print("\\nError: No se puede reducir debido a simbolos insuficientes en la pila")
                errorList.append("Error: No se puede realizar la reduccion 'r" + prodNumber + "' debido a simbolos insuficientes en la pila")
                break

            for _ in range(len(prodList)):
                stack.pop()

            # Obtain the header of the production
            header = None
            for key, value in grammar.productions.items():
                if production in value:
                    header = key
                    break
            else:
                # print("\\nError: Encabezado de produccion no se pudo encontrar")
                errorList.append("Error: Encabezado de produccion '"+ header + "' no se pudo encontrar")
                break
            
            # Replace the production with the header in symbols
            prodList = production.split()
            symbolList = symbols[:]
            for i in range(len(symbolList)):
                if symbolList[i:i+len(prodList)] == prodList:
                    symbolList[i:i+len(prodList)] = [header]
            symbols = symbolList
            
            # Look up the value in goToTable for the production
            try:
                stack.append(gotoTable[stack[-1]][header])
            except KeyError:
                # print("\\nError: Entrada invalida de Ir_A")
                errorList.append("Error: Entrada '("+ str(lastStack) +"," + firstData+ ")' invalida en tabla Ir_A")
                break

            action = f"reducir mediante {{header}} -> {{production}}"
            print(f"{{contador:<10}} {{str(stack):<20}} {{str(symbols):<35}} {{str(data):<35}} {{action:<35}}")

        else:
            # print("\\nError: Accion vacia en la tabla")
            errorList.append("Error: Accion '("+ str(lastStack) +"," + firstData+ ")' vacia/inexistente en la tabla")
            symbols.append(firstData)
            data.pop(0)
    
    print("-" * 132)
    if not errorList:
        print(f"\\n-----PARSEO EXITOSO!-----")
        for string in dataCopy:
            print(f"{{string:<6}} -> Accepted")
    else:
        print(f"\\n-----PARSEO FALLIDO!-----")
        for error in errorList:
            print(error)
    
def enumerateGrammar(grammar):
    production_numbers = {{}}

    count = 1
    for key, values in grammar.items():
        for value in values:
            production_numbers[value] = count
            count += 1
    
    return production_numbers
    

if __name__ == '__main__':
    main()"""
      
        with open(outputName, 'w') as file:
            file.write(f"{pythonCode}")