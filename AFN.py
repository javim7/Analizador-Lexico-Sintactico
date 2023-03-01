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
        print(f"- Estado Inicial: {self.initial_state}")
        print(f"- Estado Final: {self.final_state}")

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
