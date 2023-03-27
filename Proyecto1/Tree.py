from Proyecto1.Automaton import *


class TreeNode():
    '''
    Clase TreeNode: representa un nodo de un arbol de expresiones regulares
    '''

    def __init__(self, val):
        self.val = val
        self.number = None
        self.nullable = False
        self.firstPos = []
        self.lastPos = []
        self.followPos = []
        self.left = None
        self.right = None

    '''
    metodo para poder imprimir el arbol de expresiones regulares
    '''

    def __str__(self):
        s = f"TreeNode: {self.val}, number: {self.number}, nullable: {self.nullable}, firstPos: {self.firstPos}, lastPos: {self.lastPos}, followPos: {self.followPos}"
        if self.left is not None:
            s += f"\n\tLeft: TreeNode: {self.left.val}, nullable: {self.left.nullable}, firstPos: {self.left.firstPos}, lastPos: {self.left.lastPos}, followPos: {self.left.followPos}"
        if self.right is not None:
            s += f"\n\tRight: TreeNode: {self.right.val}, nullable: {self.right.nullable}, firstPos: {self.right.firstPos}, lastPos: {self.right.lastPos}, followPos: {self.right.followPos}"
        return s


class Tree():
    '''
    clase Tree: representa el arbol sintactico que se crea a la hora de ingresar la regex
    '''

    def __init__(self, postfix):
        self.postfix = postfix+'#.'
        self.nodes = []
        self.root = None
        self.nodeDict = {}
        self.visited = []
        self.symbolsList = self.symbols()  # lista de simbolos disponibles
        self.initialState = 0  # estado inicial
        self.finalNumber = 0  # numero de estados finales
        self.finalStates = []
        self.transitions = {}  # diccionario para ver las transiciones de cada estado
        self.representDict = {}

    '''
    funcion para poder obtener los simbolos del afn sin contar epsilon.
    '''

    def symbols(self):
        symbol = []  # inicio de la lista de simbolos
        for character in self.postfix:  # for para recorrer todas las transiciones del afn
            # if para ver si el simbolo no esta en la lista y si no es epsilon
            if character not in ['.', '|', '*', '#', 'ε'] and character not in symbol:
                symbol.append(character)
        return symbol

    '''
    funcion para poder crear el arbol sintactico
    no toma parametros
    '''

    def createTree(self):
        # creamos una pila para poder ir agregando los nodos
        stack = []

        # iteramos sobre la regex en postfijo
        for i in range(len(self.postfix)):
            character = self.postfix[i]  # obtenemos el caracter actual

            # if para ver si el caracter actual no es un operador
            # si no es lo apendamos al stack
            if character not in ['.', '|', '*']:
                node = TreeNode(character)
                stack.append(node)
                self.nodes.append(node)
            # else, vemos que operador es
            else:
                # si es una union, creamos un nodo con el operador y agregamos los nodos hijos
                if character == '|':
                    node = TreeNode(character)
                    node.right = stack.pop()
                    node.left = stack.pop()
                    stack.append(node)
                    # agregamos el nodo a la lista de nodos
                    self.nodes.append(node)
                # si es una concatenacion, creamos un nodo con el operador y agregamos los nodos hijos
                if character == '.':
                    node = TreeNode(character)
                    node.right = stack.pop()
                    node.left = stack.pop()
                    stack.append(node)
                    # agregamos el nodo a la lista de nodos
                    self.nodes.append(node)
                # si es un kleene, creamos un nodo con el operador y agregamos el nodo hijo
                if character == '*':
                    node = TreeNode(character)
                    node.left = stack.pop()
                    stack.append(node)
                    # agregamos el nodo a la lista de nodos
                    self.nodes.append(node)

        # asignamos el nodo raiz
        self.root = self.nodes[-1]

        # retornammos el arbol
        return stack[-1]

    '''
    funcion para poder enumerar los nodos
    '''

    def enumerate(self):

        # contador para enumerar los nodos
        contador = 1

        # iteramos sobre los nodos
        for node in self.nodes:
            # si el nodo es un operador se ignora
            if node.val in ['.', '|', '*']:
                pass
            # else, asignamos el numero al nodo
            else:
                node.number = contador
                # agregamos el nodo al diccionario
                self.nodeDict[contador] = node
                contador += 1  # aumentamos el contador

        # asignamos el numero de estados finales
        self.finalNumber = contador-1

    '''
    funcion para poder asigna anulable o no
    '''

    def nullable(self):
        # iteramos la lista volteada
        for node in self.nodes:
            # print(node.val)
            # si el nodo es una concatencacion, se hace un and de los nodos hijos
            if node.val == '.':
                node.nullable = node.left.nullable and node.right.nullable
            # si el nodo es una union, se hace un or de los nodos hijos
            elif node.val == '|':
                node.nullable = node.left.nullable or node.right.nullable
            # si el nodo es un kleene, se hace true el nullable del nodo
            elif node.val == '*':
                node.nullable = True
            # si el nodo es un simbolo, se hace false el nullable del nodo si no es epsilon
            else:
                if node.val == 'ε':
                    node.nullable = True
                else:
                    node.nullable = False

    '''
    funcion para poder asignar firstPos
    '''

    def firstPos(self):
        # iteramos la lista volteada
        for node in self.nodes:
            # si el nodo es una concatenacion, se hace verifica el nullable
            if node.val == '.':
                # si es nullable, se agregan los firstPos de los nodos hijos
                if node.left.nullable:
                    node.firstPos.extend(node.left.firstPos)
                    node.firstPos.extend(node.right.firstPos)
                # si no es nullable, se agregan los firstPos del nodo izquierdo
                else:
                    node.firstPos.extend(node.left.firstPos)
            # si el nodo es una union, se agregan los firstPos de los nodos hijos
            elif node.val == '|':
                node.firstPos.extend(node.left.firstPos)
                node.firstPos.extend(node.right.firstPos)
            # si el nodo es un kleene, se agregan los firstPos del hijo
            elif node.val == '*':
                node.firstPos.extend(node.left.firstPos)
            # si el nodo es un simbolo, se agrega el numero del nodo si no es epsilon
            else:
                if node.val == 'ε':
                    pass
                else:
                    node.firstPos.append(node.number)
            # sorteamos la lista para que quede en orden
            node.firtPos = sorted(node.firstPos)
            # eliminamos los duplicados
            node.fistPos = list(set(node.firstPos))

    '''
    funcion para poder asignar lastPos
    '''

    def lastPos(self):
        # iteramos la lista volteada
        for node in self.nodes:
            # si el nodo es una concatenacion, se hace verifica el nullable
            if node.val == '.':
                # si es nullable, se agregan los lastPos de los nodos hijos
                if node.right.nullable:
                    node.lastPos.extend(node.left.lastPos)
                    node.lastPos.extend(node.right.lastPos)
                # si no es nullable, se agregan los lastPos del nodo derecho
                else:
                    node.lastPos.extend(node.right.lastPos)
            # si el nodo es una union, se agregan los lastPos de los nodos hijos
            elif node.val == '|':
                node.lastPos.extend(node.left.lastPos)
                node.lastPos.extend(node.right.lastPos)
            # si el nodo es un kleene, se agregan los lastPos del hijo
            elif node.val == '*':
                node.lastPos.extend(node.left.lastPos)
            # si el nodo es un simbolo, se agrega el numero del nodo si no es epsilon
            else:
                if node.val == 'ε':
                    pass
                else:
                    node.lastPos.append(node.number)
            # sorteamos la lista para que quede en orden
            node.lastPos = sorted(node.lastPos)
            # eliminamos duplicados
            node.lastPos = list(set(node.lastPos))

    '''
    funcion para poder asignar followPos
    '''

    def followPos(self):
        # iteramos la lista volteada
        for node in self.nodes:
            # verfiicar si el nodo es cancattenacion
            if node.val == '.':
                # iteramos sobre los lastPos del nodo izquierdo
                for i in node.left.lastPos:
                    # agregamos los firstPos del nodo derecho a los followPos de los lastPost nodo izquierdo
                    self.nodeDict[i].followPos.extend(node.right.firstPos)
                    # sorteamos el followPos
                    self.nodeDict[i].followPos = sorted(
                        self.nodeDict[i].followPos)
                    # eliminamos duplicados
                    self.nodeDict[i].followPos = list(
                        set(self.nodeDict[i].followPos))
            # verificar si el nodo es un kleene
            elif node.val == '*':
                # iteramos sobre los lastPos del nodo
                for i in node.lastPos:
                    # agregamos los firstPos del nodo a los followPos de los lastPost nodo
                    self.nodeDict[i].followPos.extend(node.firstPos)
                    # sorteamos el followPos
                    self.nodeDict[i].followPos = sorted(
                        self.nodeDict[i].followPos)
                    # eliminamos duplicados
                    self.nodeDict[i].followPos = list(
                        set(self.nodeDict[i].followPos))

    '''
    funcion para poder hacer el setup del automata
    '''

    def dfaSetup(self):
        # llamamos a las otras funcionas para poder tener toda la informacion
        self.createTree()
        self.enumerate()
        self.nullable()
        self.firstPos()
        self.lastPos()
        self.followPos()

        # obtenemos el estado inicial
        initialState = self.root.firstPos

        # llamado a laa funcion recursiva para poder crear el automata
        self.recursion(initialState)

        # volteamos el diccionario de transiciones
        self.transitions = dict(list(self.transitions.items())[::-1])

        # creando un diccionario que asigna enteros a los estados
        self.representDict = {}
        # iteramos sobre los estados
        i = 0
        for key in self.transitions:
            # vemos si la llave no esta vacia
            if key != ():
                # asignamos el entero al estado
                self.representDict[i] = key
                i += 1
        # print(self.representDict)

    '''
    funcion para realizar la recursion
    '''

    def recursion(self, state):

        # convertimos el estado en tupla
        state = tuple(state)

        # verificamos si el estado ya esta en visitados
        if state in self.visited:
            return

        # agregamos el estado a la lista de visitados
        self.visited.append(state)

        # creamos un diccionario temporal
        tempDict = {}
        # recorremoes la lista de simbolos
        for symbol in self.symbolsList:
            tempDict[symbol] = []
            for number in state:
                # verificamos que el nodo sea del valor del simbolo
                if self.nodeDict[number].val == symbol:
                    # agregamos los followPos del nodo al diccionario temporal
                    tempDict[symbol].extend(self.nodeDict[number].followPos)
                    # ordenamos la lista
                    tempDict[symbol] = sorted(tempDict[symbol])
                    # eliminamos duplicados
                    tempDict[symbol] = list(set(tempDict[symbol]))
            # llamamos recursivamente a la funcion
            self.recursion(tempDict[symbol])
        # agregamos la transicion al automata
        self.transitions[state] = tempDict

    '''
    funcion para poder crear el adf
    '''

    def dirDfaConstruction(self):
        # llamamos al setup
        self.dfaSetup()

        # agregamos los estados finales
        for key, value in self.representDict.items():
            if self.finalNumber in value:
                self.finalStates.append(key)

        # eliminamos estados finales repetidos
        self.finalStates = list(set(self.finalStates))

        # creamos el automata
        dfa = DFA(self.initialState, self.finalStates)

        # recorremos el diccionario para poder agregar las transiciones
        for key, value in self.transitions.items():
            # verificamos que la llave no este vacia
            if key != ():
                for k, v in value.items():
                    # verificamos que el valor no esta vacio
                    if v != []:
                        # recorremos el dicaionario de representacion
                        for k2, v2 in self.representDict.items():
                            if v2 == key:
                                state = k2
                                # print("state: ", state)
                            v = tuple(v)
                            if v2 == v:
                                nextState = k2
                                # print("nextState: ", nextState)
                        transition = Transition(state, k, nextState)
                        dfa.transitions.append(transition)

        # agregamos los estados del afd
        dfa.getStates()

        # retornamos el automata
        return dfa
