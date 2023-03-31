import graphviz as gv


class Drawer:
    '''
    NFADrawer es la clase que se utiliza para poder dibujar el afn en pdf.
    Toma como parametros, las transiciones del afn, su estado inicial y final.
    '''

    def __init__(self, transitions, initial_state, final_states, title=None):
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_states = final_states
        # create the graph to draw the NFA horizontally
        self.graph = gv.Digraph(graph_attr={'rankdir': 'LR'})

        # create nodes for each state and add transitions between them
        for transition in self.transitions:
            self.graph.edge(str(transition.state), str(
                transition.next_state), label=transition.symbol)

        # add initial state and final states to the graph
        self.graph.node(str(initial_state), shape='circle', style='bold')
        self.graph.node('start', shape='point')
        self.graph.edge('start', str(initial_state), arrowhead='normal')

        for final_state in final_states:
            self.graph.node(str(final_state), shape='doublecircle')

        # agregamos el titulo del grafo
        if title:
            self.graph.node('title', label=title, shape='none',
                        fontsize='20', fontcolor='black', fontname='Arial')

    '''
    dibujamos el nfa
    '''

    def draw(self, filename='my_nfa'):
        return self.graph.view(filename=filename)
