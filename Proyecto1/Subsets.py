from Proyecto1.Automaton import *


class Subsets():
    '''
    Subsets: clase para poder hacer la construccion del afn a afd por medio de subconjuntos.
    Toma como parametro el afn.
    '''

    def __init__(self, nfa):
        # obteniendo la informacion del afn recibido como paremetro
        self.nfa = nfa
        self.nfaTransitions = nfa.transitions
        self.nfaInitialState = nfa.initial_state
        self.nfaFinalState = nfa.final_state
        # ifnormacion para el nuevo afd
        self.generated_states = 0
        self.symbolsList = self.symbols()  # lista de simbolos disponibles
        # diccionario para ver las transiciones de cada estado
        self.dfaTransitions = {}
        self.stateSubsets = {}  # diccionario para ver los subconjuntos de cada estado
        # lista para ver los estados ya visitados
        self.visited = [[self.nfaInitialState]]
        self.eClosures = []  # lista para ver los eclosures de cada estado

    '''
    funcion para poder obtener los simbolos del afn sin contar epsilon.
    '''

    def symbols(self):
        symbol = []  # inicio de la lista de simbolos
        for transition in self.nfaTransitions:  # for para recorrer todas las transiciones del afn
            # if para ver si el simbolo no esta en la lista y si no es epsilon
            if transition.symbol not in symbol and transition.symbol != 'ε':
                symbol.append(transition.symbol)
        return symbol

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
            for transicion in self.nfaTransitions:
                if transicion.state == estado:  # if para ver si el estado es el mismo que estamos testeado
                    if transicion.symbol == 'ε':  # if para ver si el simbolo es epsilon
                        # si el estado al que apunta la transicion no esta en la lista de eclosures, lo agregamos
                        if transicion.next_state not in self.eClosures:
                            self.eClosures.append(transicion.next_state)
                            self.subsets(transicion.next_state, ogState)

        # agregando el eclosure del estado a la lista de transiciones
        self.stateSubsets[tuple(ogState)] = self.eClosures

        # llamada a la función moves después de que la recursión ha finalizado
        # self.moves(self.eClosures)

        return self.eClosures

    '''
    funcion para ver las transiciones disponibles por cada simbolo
    '''

    def moves(self, eclosure):
        eclosureCopy = eclosure.copy()  # copia del eclosure
        self.eClosures = []  # reiniciando la lista de eclosures
        tempDic = {}  # diccionario temporal para ver las transiciones de cada estado

        # for para poder recorrer todos los simbolos
        for symbol in self.symbolsList:
            next_states = []
            for estado in eclosureCopy:  # for para poder recorrer todos los estados del eclosure
                for transicion in self.nfaTransitions:  # for para poder recorrer todas las transiciones del afn
                    # if para ver si el estado y el simbolo son los mismos
                    if transicion.state == estado and transicion.symbol == symbol:
                        next_states.append(transicion.next_state)
                # if para ver si el simbolo es vacio y el estado esta en la lista de estados siguientes
                if symbol == '' and estado in next_states:
                    next_states.remove(estado)
                    next_states.extend(self.eclosure(estado))
            # if para ver si la lista de estados siguientes esta vacia y agregar un null
            if len(next_states) == 0:
                next_states.append(None)
            # agregando el diccionario temporal a la lista de transiciones
            tempDic[symbol] = list(set(next_states))
        # for para poder recorrer todos los subconjuntos de estados y agregar la transicion
        for k, v in self.stateSubsets.items():
            if v == eclosureCopy:
                self.dfaTransitions[k] = tempDic
        for k, v in tempDic.items():  # for para poder recorrer todos los estados siguientes y agregarlos a la lista de visitados
            if v != [None]:
                if v not in self.visited:
                    # Append v to visited after the loop that iterates over symbols
                    self.visited.append(v)
                    # self.subsets(v, v)
        return tempDic

    '''
    Funcion para agregar todas las transiciones del nuevo afd al diccionario de transiciones.
    Es un metodo recursivo. que toma un estado como parametro.
    '''

    def dfaAddTransitions(self, estado):
        # obteniendo el eclosure del estado
        self.subsets(estado, estado)

        # creamos un diccionario que contiene los moves posibles del eclosure
        dic = self.moves(self.eClosures)

        # foreach para poder volver a llamar a la funcion de nuevo con los estados siguientes
        for k, v in dic.items():
            # if para verificar si para verificar si el estado ya esta en el diccionario de transiicones
            if v in self.visited and tuple(v) not in self.dfaTransitions:
                self.dfaAddTransitions(v)  # volvemos a llamar al metodo

    '''
    Funcion para construir el afd
    '''

    def subDfaConstruction(self):

        # llamamos al metodo de transiciones para poder obtener todas las transiciones
        self.dfaAddTransitions(self.nfaInitialState)

        # sorteamos las transiciones para remover los estados repetidos
        # y poder crear el afd
        sorted_dfaTransitions = {}
        subsets = self.stateSubsets.copy()

        # for para poder iterar cada llave y valor del diccionario de transiciones
        for key, value in self.dfaTransitions.items():
            sorted_key = tuple(sorted(key))
            sorted_value = {}
            for k, v in value.items():  # for para poder iterar cada llave y valor del diccionario de transiciones
                # agregamos el valor al diccionario
                sorted_value[k] = sorted(list(set(v)))
            # agregamos el valor al diccionario
            sorted_dfaTransitions[sorted_key] = sorted_value

        # print("subsetsPorEstado " + str(self.stateSubsets))
        # print("transiciones " + str(self.dfaTransitions))
        # print("transiciones " + str(sorted_dfaTransitions))

        # creando un nuevo diccionario para poder asignarle un numero a cada estado
        asignState = {i: key for i, key in enumerate(subsets)}
        # print(asignState)

        # creando un nuevo diccionario para poder sortear los estados de subsets
        new_dict = {}
        for key, value in asignState.items():  # iteramos el diccionario asignado
            sorted_value = tuple(sorted(value))
            if sorted_value not in new_dict.values():  # si el valor no esta en el diccionario
                # agregamos el valor al diccionario
                new_dict[key] = sorted_value

        # print("dic2: ", new_dict)

        # empezando las construcccion del afd
        # informacion basica del afd
        afdInitial = 0
        afdFinals = []
        dfa = DFA(afdInitial, afdFinals)  # instanciamos el nuevo afd

        # iteramos el diccionario sorteado para poder crear las transiciones del afd
        for key, value in sorted_dfaTransitions.items():
            for k, v in value.items():  # iteramos cada valor del diccionario
                if v != [None]:  # si el valor no es null
                    v = tuple(v)
                    for i, j in new_dict.items():
                        sortedJ = tuple(sorted(j))
                        if j == v or sortedJ == v:  # buscamos la llave del valor
                            v = i
                        if j == key or sortedJ == key:  # buscamos la llave del estado
                            key = i
                    transition = Transition(key, k, v)  # creamos la transicion
                    # agregamos la transicion al afd
                    dfa.transitions.append(transition)

        # agregamos los estados finales del afd
        for i, j in self.stateSubsets.items():
            if self.nfaFinalState in j:  # si el estado final del afn esta en el eclosure
                for x, y in new_dict.items():  # buscamos la llave del estado
                    sortedI = tuple(sorted(i))
                    if y == i or y == sortedI:  # si el estado es igual al estado del diccionario
                        state = x
                        # agregamos el estado al afd
                        dfa.final_states.append(state)
        # eliminando estados finales repetidos
        dfa.final_states = list(set(dfa.final_states))
        # agregamos los estados del afd
        dfa.getStates()

        # retornamos el afd
        return dfa
