
class NFASimulation():
    '''
    clase NFASimulation: clase para poder ver si una cadena pertenece al AFN o no
    '''

    def __init__(self, nfa, string):
        self.nfa = nfa
        self.string = string+'$'
        self.actualIndex = 0
        self.eof = self.string[-1]
        self.eClosures = []  # lista para ver los eclosures de cada estado

    '''
    funcion para poder simular el afn
    '''

    def simulate(self):
        # obtenemos el primer eclosure
        S = self.subsets(
            self.nfa.initial_state, self.nfa.initial_state)
        # print("SOriginal: ", S)
        # obtenemos el siguiente caracter de la cadena
        nextC = self.nextC()
        # while para poder obtener todos los estados e eclosures
        while nextC != self.eof:
            # vaciamos la lista de eclosures
            self.eClosures = []
            move = self.moves(S, nextC)
            S = self.subsets(move, move)
            # print("nextC: ", nextC)
            nextC = self.nextC()
            # print("move: ", move)
            # print("S: ", S)

        # if para ver si el estado final este en S
        if self.nfa.final_state in S:
            return True

        # se devuelve false si no esta
        return False

    '''
    funcion para ver cual es el siguiente caracter
    '''

    def nextC(self):
        # definimos el siguiente caracter de la cadena
        nextC = self.string[self.actualIndex]

        # aumenamos el indice
        self.actualIndex += 1

        return nextC

    '''
    este metodo se utilizada para poder obtener el eclosure de un estado, por medio de recursividad.
    Toma como parametro el estado.
    Retorna una lista con los estados que pertenecen al eclosure.
    '''

    def subsets(self, estados, ogState):

        # si el estado es un entero, lo convertimos a una lista
        if isinstance(estados, int):
            estados = [estados]
        if isinstance(ogState, int):
            ogState = [ogState]

        # for para poder recorrer todos los estados de la lista
        for estado in estados:
            if estado not in self.eClosures:
                self.eClosures.append(estado)
            # for para poder recorrer todas las transiciones del afn
            for transicion in self.nfa.transitions:
                if transicion.state == estado:  # if para ver si el estado es el mismo que estamos testeado
                    if transicion.symbol == 'ε':  # if para ver si el simbolo es epsilon
                        # si el estado al que apunta la transicion no esta en la lista de self.eclosures, lo agregamos
                        if transicion.next_state not in self.eClosures:
                            self.eClosures.append(transicion.next_state)
                            self.subsets(transicion.next_state, ogState)

        return self.eClosures

    '''
    funcion para obtener los moves posibles dado un estado y un caracter
    '''

    def moves(self, states, char):

        # lista vacia para otros eclosures
        otherEClosures = []

        # recorremos la lista para ver todos los estados
        for state in states:
            for transition in self.nfa.transitions:
                if transition.state == state and transition.symbol == char:
                    otherEClosures.append(transition.next_state)

        return otherEClosures


class DFASimulation():
    '''
    clase DFASimulation: clase para poder ver si una cadena pertencece al AFD o no
    '''

    def __init__(self, dfa, string):
        self.dfa = dfa
        self.string = string
        self.actualIndex = 0
        self.eof = self.string[-1]

    '''
    funcion para poder simular el afd
    '''

    def simulate(self):
        # obtenemos el primer estado
        currentState = self.dfa.initial_state
        # print("estado inicial: ", currentState)
        # iteramos todos los caracteres de la cadena
        for symbol in self.string:
            # print("symbol: ", symbol)
            nexState = None
            # iteramos todoas las transiciones del afd
            for transition in self.dfa.transitions:
                # if para ver si la transicion es la que estamos buscando
                if transition.state == currentState and transition.symbol == symbol:
                    # si es la transicion que buscamos, cambiamos el estado actual
                    nexState = transition.next_state
                    # print("currentState: ", nexState)
                    break
            # vemos si no se encontro una transicion
            if nexState == None:
                return False
            # si se encontro, cambiamos el estado actual
            currentState = nexState

        # al finalizar el loop, vemos si el current state esta en los estados finales
        if currentState in self.dfa.final_states:
            return True
        # si no esta, retornamos false
        return False
