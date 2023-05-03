class Set:
    def __init__(self):
        self.estado = 0
        self.corazon = {}
        self.resto = {}
        self.productions = {}
    
    def __str__(self):
        estado_str = f"Estado: {self.estado}\n"
        corazon_str = f"Corazon: {self.corazon}\n"
        resto_str = f"Resto: {self.resto}\n"
        productions_str = "\n\t".join([f"{nt} -> {' | '.join(rhs)}" for nt, rhs in self.productions.items()])
        return f"{estado_str}{corazon_str}{resto_str}Producciones:\n\t{productions_str}"

    def getCorazon(self):
        return self.corazon
    
    def getResto(self):
        return self.resto
    
    def getproductions(self):
        return self.productions