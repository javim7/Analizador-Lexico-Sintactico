from Automaton import *


class Minimization():
    '''
    clase Minimization: clase que contiene los métodos de minimización de un afd
    '''

    def __init__(self, dfa):
        self.dfa = dfa
        self.dfaFinalStates = dfa.final_states
        self.dfaStates = dfa.states
        self.dfaTransitions = dfa.transitions
        self.initialPartition = []
        self.partitions = []
        self.symbolsList = self.symbols()
        self.transitions = {}
        self.finalStates = []
        self.initialState = 0

    '''
    funcion para poder obtener los simbolos del afd
    '''

    def symbols(self):
        symbol = []  # inicio de la lista de simbolos
        for transition in self.dfaTransitions:  # for para recorrer todas las transiciones del afd
            # if para ver si el simbolo no esta en la lista
            if transition.symbol not in symbol:
                symbol.append(transition.symbol)
        return symbol

    '''
    metodo para poder obtener la particion inicial del afd
    '''

    def buildInitialPartition(self):
        accept = []  # lista para los estados de aceptacion
        # agregamos los estados de aceptacion a la lista
        accept.extend(self.dfaFinalStates)

        nonAccept = []  # lista para los estados no de aceptacion

        # for para poder recorrer todos los estados del afd
        for state in self.dfaStates:
            # if para ver si el estado es de aceptacion
            if state not in accept:
                nonAccept.append(state)

        # agregamos las listas a la particion
        self.initialPartition.append(accept)

        # if para ver si no esta vacia y poder agregarla
        if nonAccept:
            self.initialPartition.append(nonAccept)

        # llamamos a la funcion recursiva para poder obtener la nueva particion
        self.buildNewPartitions(self.initialPartition)

    '''
    funcion para poder obtener el resto de las transiciones
    '''

    def buildNewPartitions(self, partitions):

        # igualamos la nueva particion a la particion anterior
        self.partitions = partitions.copy()
        newPartitions = self.partitions.copy()
        # print("partitions: ", self.partitions)
        # print("new       : ", newPartitions)

        # for para poder recorrer todas las particiones de la particion anterior
        for partition in self.partitions:
            dicPartition = {}
            # if para ver que el len sea mayor a 1
            if len(partition) > 1:
                # recorremos los estados que estan en cada particion
                for state in partition:
                    # for para poder recorrer todos los simbolos
                    dicSymbol = {}
                    for symbol in self.symbolsList:
                        # recorremos las transiciones
                        for transition in self.dfaTransitions:
                            # if para ver si la transicion es igual al estado y el simbolo
                            if transition.state == state and transition.symbol == symbol:
                                # dicSymbol[symbol] = transition.next_state
                                # print(
                                #     "estado indice: " + str(self.getIndex(transition.next_state, self.partitions)))
                                dicSymbol["G"+symbol] = "G" + str(
                                    self.getIndex(
                                        transition.next_state, self.partitions))

                    # agregamos el diccionario de simbolos al diccionario de particiones
                    dicPartition[state] = dicSymbol
                    # print("dicPartition: ", dicPartition)

                # reemplazando el viejo valor por el nuevo
                index = newPartitions.index(partition)
                newPartitions.pop(index)
                # agregamos las nuevas particiones
                for i, l in enumerate(self.getCombinations(dicPartition)):
                    newPartitions.insert(index + i, l)
        # print("new       : ", newPartitions)

        # if para ver si la nueva particion es igual a la anterior
        if newPartitions == self.partitions:
            return self.partitions

        # sino son iguales llamamos a la funcion recursivamente con las nuevas particiones
        self.buildNewPartitions(newPartitions)

    '''
    funcion para poder obtener el indice de la particion dado un estado
    '''

    def getIndex(self, integer, list):
        for i, sublist in enumerate(list):
            if integer in sublist:
                return i

    '''
    funcion para obtener las combinaciones de las particiones
    '''

    def getCombinations(self, dicPartition):
        result = []  # lista para los resultados

        # set para poder obtener los valores unicos
        value_sets = set()
        value_dict = {}

        # for para poder recorrer el diccionario de particiones
        for key, values in dicPartition.items():
            value_set = frozenset(values.items())
            # if para ver si el valor no esta en el set
            if value_set not in value_sets:
                value_sets.add(value_set)
                value_dict[value_set] = [key]
            # sino esta en el set lo agregamos
            else:
                value_dict[value_set].append(key)

        # for para poder recorrer el diccionario de valores
        for key_set, keys in value_dict.items():
            result.append(keys)

        return result

    '''
    funcion para agregar las transiciones
    '''

    def minDFAConstruction(self):

        # llamamos a la funcion para poder obtener la particion inicial
        self.buildInitialPartition()
        # print("partitions1: ", self.partitions)
        # ordenando las particiones por su primer elemento
        self.partitions = sorted(self.partitions, key=lambda x: x[0])
        # print("partitions2: ", self.partitions)

        # agregando el estado inicial al principio de la lista para que su indice sea 0
        # tambien agregamos los estados finales
        # for partition in self.partitions:
        #     if self.dfa.initial_state in partition:
        #         self.partitions.remove(partition)
        #         self.partitions.insert(0, partition)

        # for para ver los estados finales
        for partition in self.partitions:
            for state in self.dfaFinalStates:
                if state in partition:
                    estadoNuevo = self.getIndex(state, self.partitions)
                    self.finalStates.append(estadoNuevo)

        # eliminando finales duplicados
        self.finalStates = list(set(self.finalStates))

        # creamos el nuevo afd
        dfa = DFA(self.initialState, self.finalStates)

        # recorremos las particiones
        for partition in self.partitions:
            # agarramos el primer elemento de cada particion
            representative = partition[0]
            index = self.getIndex(representative, self.partitions)
            dicSymbol = {}
            # for para poder recorrer todos los simbolos
            for symbol in self.symbolsList:
                # recorrer las transiciones
                for transition in self.dfaTransitions:
                    # if para ver si la transicion es igual al estado y el simbolo
                    if transition.state == representative and transition.symbol == symbol:
                        nextIndex = self.getIndex(
                            transition.next_state, self.partitions)
                        dicSymbol[symbol] = nextIndex
                        # creamos la nueva transiciones del afd y se la agregamos
                        transition = Transition(index, symbol, nextIndex)
                        dfa.transitions.append(transition)
            self.transitions[index] = dicSymbol
        # print("dic: ", self.transitions)

        # retornamos el nuevo afd
        return dfa
