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
            self.grammar = None
            self.increasedGrammar = None
            self.estados = 0
            self.sets = []
            self.afdLR0 = None
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
        self.grammar = self.defineGrammar()

        self.increasedGrammar = self.increaseGrammar(self.grammar)

        self.firstSet(self.increasedGrammar)

    def detectErrors(self):
        pass
    
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
        tempGrammar.productions = OrderedDict([(newInitialState, [tempGrammar.initialState])] + list(tempGrammar.productions.items()))

        tempGrammar.productions = dict(tempGrammar.productions)

        # print("temp")
        # print(tempGrammar)
        # print("original")
        # print(grammar)
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
    def format_label(self, state, state_number):
        label = f"State {state_number}\n"
        for key, value in state.items():
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
            label = self.format_label(set.productions, set.estado)
            node = pydot.Node(label)
            graph.add_node(node)

        for transition in afd.transitions:
            state = self.format_label(transition.state.productions, transition.state.estado)
            next_state = self.format_label(transition.next_state.productions, transition.next_state.estado)
            edge = pydot.Edge(state, next_state, label=transition.symbol)
            graph.add_edge(edge)
        
        for transition in afd.transitions[::-1]:
            if transition.state.estado == 1:
                state = self.format_label(transition.state.productions, transition.state.estado)
                next_state = 'accept'
                edge = pydot.Edge(state, next_state, label='$')
                graph.add_edge(edge)

        graph.write_pdf('graphs/LR0.pdf')
        afd.final_states = []
        afd.final_states.append('accept')

        afd.print_dfa()
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
               
        afd_drawer = Drawer(
            afd.transitions, afd.initial_state, afd.final_states, 'LR(0)')
        afd_drawer.draw(filename='graphs/LR0')
        
        afd.print_dfa()
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


