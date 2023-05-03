class Grammar:
    def __init__(self):
        self.initialState = None
        self.productions = {}
        self.terminals = []
        self.nonTerminals = []
    
    def __str__(self):
        productions_str = "\n\t".join([f"{nt} -> {' | '.join(rhs)}" for nt, rhs in self.productions.items()])
        return f"Initial state: {self.initialState}\nTerminals: {self.terminals}\nNon-terminals: {self.nonTerminals}\nProductions:\n\t{productions_str}"
    
    def getInitialState(self):
        return self.initialState

    def getProductions(self):
        return self.productions

    def getTerminals(self):
        return self.terminals

    def getNonTerminals(self):
        return self.nonTerminals