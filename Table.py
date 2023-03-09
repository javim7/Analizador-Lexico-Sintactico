from tabulate import tabulate
from collections import defaultdict


class Table():
    '''
    clase Table: clase para poder dibujar la tabla de transiciones de los AF generados
    '''

    def __init__(self, automata):
        self.automata = automata
        self.symbolsList = self.getSymbols()
        self.table = self.createTable()

    '''
    getSymbols: metodo para obtener los simbolos del alfabeto del AF
    '''

    def getSymbols(self):
        symbolsList = []
        # for para iterar por cada una de las transiciones del AF
        for transition in self.automata.transitions:
            if transition.symbol not in symbolsList:
                symbolsList.append(transition.symbol)
        return symbolsList

    '''
    createTable: metodo para crear la tabla de transiciones
    '''

    def createTable(self):
        # Get all the states
        states = list(set([transition.state for transition in self.automata.transitions] + [
                        transition.next_state for transition in self.automata.transitions]))
        # Sort states in ascending order
        # states.sort()

        # Create a list of lists to store the table data
        table_data = []

        # Add the header row with the symbols as column headers
        header_row = ['Estado'] + self.symbolsList
        table_data.append(header_row)
        header_separator = ['-'*10] + ['-'*3]*len(self.symbolsList)
        table_data.append(header_separator)

        # Add a row for each state
        for state in states:
            row = [str(state)]

            # Add a column for each symbol
            for symbol in self.symbolsList:
                # Get the next state for the current state and symbol
                next_states = []
                for transition in self.automata.transitions:
                    if transition.state == state and transition.symbol == symbol:
                        next_states.append(str(transition.next_state))

                # Add the next state(s) to the row
                if len(next_states) > 0:
                    row.append('[' + ', '.join(next_states) + ']')
                else:
                    row.append('-')

            table_data.append(row)
            row_separator = ['-'*10] + ['-'*3]*len(self.symbolsList)
            table_data.append(row_separator)

        # Use tabulate to create the table
        table = tabulate(table_data, headers='firstrow', tablefmt='orgtbl')

        # Return the table as a string
        return table

