class Transition:
    '''
    Transition: Es la clase que se utiliza para poder crear las transiciones del afn.
    Toma como parametros el estado actual, el simbolo y el estado siguiente.
    De esta manera podemos ver que transiciones se realizan en el afn, de una manera ordenada. 
    '''

    def __init__(self, state, symbol, next_state):
        self.state = state
        self.symbol = symbol
        self.next_state = next_state

    # def __repr__(self):
    def __str__(self):
        return f"[State: {self.state}, Symbol: {self.symbol}, NextState: {self.next_state}]"

    # def __str__(self):
    def print_transition(self):
        print(
            f"[State: {self.state}, Symbol: {self.symbol}, NextState: {self.next_state}]")


class NFA:
    '''
    NFA: clase que se utiliza para poder tener el obejto del afn.
    Toma como parametros el estado inicial y el estado final.
    El afn tiene una lista de transiciones, un estado inicial y un estado final.
    En la clase tambien hay metodos que sirven para poder imprimir el afn y verlo de una manera mas sencilla.
    '''

    def __init__(self, initial_state, final_state):
        self.transitions = []
        self.initial_state = initial_state
        self.final_state = final_state
        self.states = []

    # funcion para poder obtener los estados del afn
    def getStates(self):
        states = []  # lista vacia para los estados

        # recorremos las transiciones
        for transition in self.transitions:
            # vemos si el estado no esta en la lista y lo agregamos en caso no
            if transition.state not in states:
                states.append(transition.state)
            if transition.next_state not in states:
                states.append(transition.next_state)
        self.states = sorted(states)

    # imprimiumos las transiciones del afn
    def print_dfa(self):
        print("\n-------AFN-------")
        print("Transiciones AFN:")
        for transition in self.transitions:
            print(
                f"[{transition.state}, {transition.symbol}, {transition.next_state}]")

    # imprimimos la informacion general del afn
    def dfa_info(self):
        print("\nInformacion General AFN:")
        print(f"- Estado Inicial : {self.initial_state}")
        print(f"- Estado Final   : {self.final_state}")

        # lista vacia para ver los estados del dfa
        estados = []
        # recorremos las transiciones
        for transition in self.transitions:
            # vemos si el estado no esta en la lista y lo agregamos en caso no
            if transition.state not in estados:
                estados.append(transition.state)
            if transition.next_state not in estados:
                estados.append(transition.next_state)
        print(f"- Numero de estados: {len(estados)}")


class DFA:
    '''
    DFA: clase que se utiliza para poder tener el obejto del afd.
    Toma como parametros el estado inicial y el estado final.
    El afd tiene una lista de transiciones, un estado inicial y un estado final.
    En la clase tambien hay metodos que sirven para poder imprimir el afd y verlo de una manera mas sencilla.
    '''

    def __init__(self, initial_state, final_states):
        self.transitions = []
        self.initial_state = initial_state
        self.final_states = final_states
        self.states = []

    # funcion para poder obtener los estados del afd
    def getStates(self):
        states = []  # lista vacia para los estados

        # recorremos las transiciones
        for transition in self.transitions:
            # vemos si el estado no esta en la lista y lo agregamos en caso no
            if transition.state not in states:
                states.append(transition.state)
            if transition.next_state not in states:
                states.append(transition.next_state)

        # agregamos al atributo
        self.states = sorted(states)

     # imprimiumos las transiciones del afn
    def print_dfa(self):
        print("\n-------AFD-------")
        print("Transiciones AFD:")
        for transition in self.transitions:
            print(
                f"[{transition.state}, {transition.symbol}, {transition.next_state}]")

     # imprimimos la informacion general del afn
    def dfa_info(self):
        print("\nInformacion General AFD:")
        print(f"- Estado Inicial  : {self.initial_state}")
        print(f"- Estados Finales : {self.final_states}")

        # lista vacia para ver los estados del afn
        estados = []
        # recorremos las transiciones
        for transition in self.transitions:
            # vemos si el estado no esta en la lista y lo agregamos en caso no
            if transition.state not in estados:
                estados.append(transition.state)
            if transition.next_state not in estados:
                estados.append(transition.next_state)
        print(f"- Numero de estados: {len(estados)}")
