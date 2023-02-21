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
