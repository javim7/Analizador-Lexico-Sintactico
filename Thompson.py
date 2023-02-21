from Transition import *
from NFA import *


class Thompson:
    '''
    Thompson: Es la clase que se utiliza para poder construir el afn a partir de un postfix.
    Toma como parametro el postfix.
    En esta clase estan todas las funciones con todas las reglas del algoritmo de thompson.
    Por ultimo, hay un metodo que construye el afn por medio de un stack y las reglas.
    '''

    def __init__(self, postfix):
        self.postfix = postfix
        self.generated_states = 0

    '''
    genera un afn con la regla simbolo

    parametro symbolo
    retrona nfa nfa
    '''

    def symbolRule(self, symbol):
        # generando el primer estado
        state = self.generated_states
        self.generated_states += 1

        # generando el segundo estado
        next_state = self.generated_states
        self.generated_states += 1

        # creando el nfa y las transiciones
        nfa = NFA(state, next_state)
        transition = Transition(state, symbol, next_state)
        nfa.transitions.append(transition)

        return nfa

    '''
    genera un afn con la regla or

    parametro nfa1 nfa
    return nfa (nfa1|nfa2)
    '''

    def orExpression(self, nfa1, nfa2):
        # informacion del estado inicial
        initial_state = self.generated_states
        state1 = self.generated_states  # el estado inicial sera el primer nuevo nodo
        self.generated_states += 1  # aumentamos el contador de estados

        # informacion del estado final
        final_state = self.generated_states
        state2 = self.generated_states  # el estado final sera el segundo nuevo nodo
        self.generated_states += 1  # aumentamos el contador de estados

        # creamos el nfa
        nfa = NFA(initial_state, final_state)

        # transiciones del estado inicial a los estados iniciales de cada nfa
        transition1 = Transition(state1, 'ε', nfa1.initial_state)
        transition2 = Transition(state1, 'ε', nfa2.initial_state)

        # transiciones de los estados finales de cada nfa al estado final
        transition3 = Transition(nfa1.final_state, 'ε', state2)
        transition4 = Transition(nfa2.final_state, 'ε', state2)

        # agregamos las primeras transiciones
        nfa.transitions.append(transition1)
        nfa.transitions.append(transition2)

        # agregamos las transiciones de cada nfa
        for transition in nfa1.transitions:
            nfa.transitions.append(transition)
        for transition in nfa2.transitions:
            nfa.transitions.append(transition)

        # agregando las transiciones finales
        nfa.transitions.append(transition3)
        nfa.transitions.append(transition4)

        return nfa

    '''
    genera un afn con la expresion concatenacion

    parametro nfa1 nfa
    return nfa (nfa1.nfa2)
    '''

    def concatExpression(self, nfa1, nfa2):
        # creamos el nfa con sus estados inicial y final
        nfa = NFA(nfa1.initial_state, nfa2.final_state)

        # agregamos las transiciones del primer nfa
        for transition in nfa1.transitions:
            nfa.transitions.append(transition)

        # obteniendo los estados final del afn1 e inicial del afn2
        final_nfa1 = nfa1.final_state
        initial_nfa2 = nfa2.initial_state

        # cambiando el estado inicial del nfa2 al estado final del nfa1
        for transition in nfa2.transitions:
            if transition.state == initial_nfa2:
                transition.state = final_nfa1

        # agregamos las transiciones del segundo nfa
        for transition in nfa2.transitions:
            nfa.transitions.append(transition)

        return nfa

    '''
    Genera un afn con la expresion kleene

    parametro nfa1 nfa
    return nfa (nfa1*)
    '''

    def kleeneExpression(self, nfa1):
        # obtenemos el estado inicial para el nuevo afn
        initial_state = self.generated_states
        self.generated_states += 1

        # obtenemos el estado final para el nuevo afn
        final_state = self.generated_states
        self.generated_states += 1

        # creamos el nuevo afn
        nfa = NFA(initial_state, final_state)

        # creamos y agregamos la primera transiciones
        transition1 = Transition(initial_state, 'ε', nfa1.initial_state)
        nfa.transitions.append(transition1)

        # agregamos las transiciones del nfa1
        for transition in nfa1.transitions:
            nfa.transitions.append(transition)

        # creamos las nuevas transiciones
        transition2 = Transition(nfa1.final_state, 'ε', nfa1.initial_state)
        transition3 = Transition(nfa1.final_state, 'ε', final_state)
        transition4 = Transition(initial_state, 'ε', final_state)

        # agregamos las transiciones
        nfa.transitions.append(transition2)
        nfa.transitions.append(transition3)
        nfa.transitions.append(transition4)

        return nfa

    '''
    Genera un afn dado el postifx dado

    return nfa
    '''

    def nfaConstruction(self):
        # creamos stack vacio para poder hacer la construccions
        stack = []

        # for para iterar por cada uno de los caracteres del postfix
        for i in range(len(self.postfix)):
            character = self.postfix[i]

            # if para ver si es un simbolo o un operador
            if character.isalnum():
                stack.append(self.symbolRule(character))
            else:
                # if para ver si es un or
                if character == '|':
                    nfa2 = stack.pop()
                    nfa1 = stack.pop()
                    stack.append(self.orExpression(nfa1, nfa2))
                # if para ver si es concat
                if character == '.':
                    nfa2 = stack.pop()
                    nfa1 = stack.pop()
                    stack.append(self.concatExpression(nfa1, nfa2))
                # if para ver si es kleene
                if character == '*':
                    nfa1 = stack.pop()
                    stack.append(self.kleeneExpression(nfa1))

        # retornamos el ultimo elemento del stack que es el afn final
        return stack[-1]
