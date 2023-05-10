import copy
import pydot
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
            self.first = {}
            self.follow = {}
        except FileNotFoundError:
            raise Exception('File could not be opened')
        
    def compiler(self):
        # detectamos errores
        errores = self.detectErrors()

        # si hay errores, los mostramos, de lo contrario, continuamos
        if self.errors:
            errores_str = "\n".join(set(errores))
            raise Exception(errores_str)
        
        # si no hay errores, continuamos

        #obtenemos los tokens y definimos la gramatica
        self.tokens = self.getTokens()
        self.grammar = self.defineGrammar()
        #aumentamos la gramtica
        self.increasedGrammar = self.increaseGrammar(self.grammar)

        #obtenemos el primer conjunto y con esto el automata LR(0)
        self.firstSet(self.increasedGrammar)

        self.grammar.first = self.compute_first(self.grammar.productions)
        self.grammar.follow = self.compute_follow(self.grammar.productions)

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
        afd.dfa_info()

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
        
        # afd.print_dfa()
        afd.dfa_info()

        self.afdLR0 = afd
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

