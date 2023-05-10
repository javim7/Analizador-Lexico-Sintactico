class Grammar:
    def __init__(self):
        self.initialState = None
        self.productions = {}
        self.terminals = []
        self.nonTerminals = []
        self.first = {}
        self.follow = {}
    
    def __str__(self):
        firstStr = "\n---------------GRAMMAR INFO--------------\n"
        productions_str = "\n\t".join([f"{nt} -> {' | '.join(rhs)}" for nt, rhs in self.productions.items()])
        return f"{firstStr}Initial state-> {self.initialState}\nTerminals    -> {self.terminals}\nNon-terminals-> {self.nonTerminals}\nFirst        -> {self.first}\nFollow       -> {self.follow}\nProductions  ->\n\t{productions_str}"
    
    def getInitialState(self):
        return self.initialState

    def getProductions(self):
        return self.productions

    def getTerminals(self):
        return self.terminals

    def getNonTerminals(self):
        return self.nonTerminals