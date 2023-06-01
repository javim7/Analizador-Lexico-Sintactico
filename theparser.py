#importamos la clase de Yalex para poder obtener toda su informacion
from YAPar import *

#creamos el objeto de la clase YALex y compilamos el archivo
yapar = YAPar('YAPFiles/yap1.yalp')

yapar.compiler()

def main():

    #input del archivo de entrada
    archivo = input('\nIngrese el nombre del archivo a parsear: ')

    #creamos la variable del archivo
    texto = 'YAPInputs/'+archivo+'.txt'

    #creamos la variable del archivo
    # texto = 'YAPInputs/input1.txt'

    #leemos el archivo de texto
    with open(texto, 'r') as file:  
        data = file.read().split()

    data.append('$')
    #llamar a la funcion de parseo
    parseo(data)
    
def parseo(data):
    # Definition of variables
    stack = []
    symbols = []
    errorList = []
    dataCopy = data.copy()
    actionTable = yapar.actionTable
    gotoTable = yapar.goToTable
    grammar = yapar.grammar
    stack.append(next(iter(actionTable)))
    production_numbers = enumerateGrammar(grammar.productions)

    # Start the parsing loop
    going = True
    contador = 0
    print("\n" + "-" * 60 + " PARSEO SLR " + "-" * 60)
    print(f"{'ITERACION':<10} {'PILA':<20} {'SIMBOLOS':<35} {'ENTRADA':<35} {'ACCION':<35}")
    print("-" * 132)
    while going:
        contador += 1
        
        # Obtain the elements to verify
        lastStack = stack[-1]
        firstData = data[0]

        # Check if it is accepted or not
        if actionTable.get(lastStack, {}).get(firstData) == 'acc':
            going = False
            break

        # Check if it is a shift
        elif actionTable.get(lastStack, {}).get(firstData, '\nerror')[0] == 's':
            symbols.append(firstData)
            stack.append(int(actionTable[lastStack][firstData][1:]))
            data.pop(0)
            action = 'desplazar'
            print(f"{contador:<10} {str(stack):<20} {str(symbols):<35} {str(data):<35} {action:<35}")

        # Check if it is a reduce
        elif actionTable.get(lastStack, {}).get(firstData, '\nerror')[0] == 'r':

            # Obtain the number of production
            prodNumber = int(actionTable[lastStack][firstData][1:])
            for production, number in production_numbers.items():
                if number == prodNumber:
                    break
            else:
                # print("\nError: numero invalido de produccion")
                errorList.append("Error: numero '" + number + "' invalido de produccion")
                break
            
            # Perform the necessary pops
            prodList = production.split()
            if len(prodList) > len(stack):
                # print("\nError: No se puede reducir debido a simbolos insuficientes en la pila")
                errorList.append("Error: No se puede realizar la reduccion 'r" + prodNumber + "' debido a simbolos insuficientes en la pila")
                break

            for _ in range(len(prodList)):
                stack.pop()

            # Obtain the header of the production
            header = None
            for key, value in grammar.productions.items():
                if production in value:
                    header = key
                    break
            else:
                # print("\nError: Encabezado de produccion no se pudo encontrar")
                errorList.append("Error: Encabezado de produccion '"+ header + "' no se pudo encontrar")
                break
            
            # Replace the production with the header in symbols
            prodList = production.split()
            symbolList = symbols[:]
            for i in range(len(symbolList)):
                if symbolList[i:i+len(prodList)] == prodList:
                    symbolList[i:i+len(prodList)] = [header]
            symbols = symbolList
            
            # Look up the value in goToTable for the production
            try:
                stack.append(gotoTable[stack[-1]][header])
            except KeyError:
                # print("\nError: Entrada invalida de Ir_A")
                errorList.append("Error: Entrada '("+ str(lastStack) +"," + firstData+ ")' invalida en tabla Ir_A")
                break

            action = f"reducir mediante {header} -> {production}"
            print(f"{contador:<10} {str(stack):<20} {str(symbols):<35} {str(data):<35} {action:<35}")

        else:
            # print("\nError: Accion vacia en la tabla")
            errorList.append("Error: Accion '("+ str(lastStack) +"," + firstData+ ")' vacia/inexistente en la tabla")
            break
    
    print("-" * 132)
    if not errorList:
        print(f"\n-----PARSEO EXITOSO!-----")
        for string in dataCopy:
            print(f"{string:<6} -> Accepted")
    else:
        print(f"\n-----PARSEO FALLIDO!-----")
        for error in errorList:
            print(error)
    
def enumerateGrammar(grammar):
    production_numbers = {}

    count = 1
    for key, values in grammar.items():
        for value in values:
            production_numbers[value] = count
            count += 1
    
    return production_numbers
    

if __name__ == '__main__':
    main()