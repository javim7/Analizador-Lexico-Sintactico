import graphviz as gv


class NFADrawer:
    '''
    NFADrawer es la clase que se utiliza para poder dibujar el afn en pdf.
    Toma como parametros, las transiciones del afn, su estado inicial y final.
    '''

    def __init__(self, transitions, initial_state, final_state):
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_state = final_state
        # creamos el grafo para poder dibujar el nfa horizontalmente
        self.graph = gv.Digraph(graph_attr={'rankdir': 'LR'})

        # recorremos las transiciones para poder crear los nodos
        for transition in self.transitions:
            self.graph.edge(str(transition.state), str(
                transition.next_state), label=transition.symbol)

        # agregamos el estado inicial y el estado final para poder diferenciarlos
        self.graph.node(str(initial_state), shape='circle', style='bold')
        self.graph.node('start', shape='point')
        self.graph.edge('start', str(initial_state), arrowhead='normal')
        self.graph.node(str(final_state), shape='doublecircle')

    '''
    dibujamos el nfa
    '''

    def draw(self):
        return self.graph.view()
