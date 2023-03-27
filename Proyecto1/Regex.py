import re


class Regex:
    '''
    Regex: es la clase que se utiliza para poder verificar que la regex ingresada sea valida.
    No se le pasan parametros, pero tiene un atributo regex que es el regex ingresado por el usuario.
    Este atributo es el que pasa por una serie de ifs para ver si es valido o no. 
    Si no es valido, se le asigna un mensaje de error al atributo regex, por medio de una funcion.
    Si es valido, se le asigna True al atributo isValid y se retorna el regex aceptado.
    '''

    def __init__(self):
        self.regex = ""
        self.isValid = False

    '''
    verificamos que el regex ingresado sea valido
    '''

    def checkRegex(self):
        valid = r"^[a-zA-Z0-9()ε+*|?\s\\.]*$"# regex aceptado
        operators = ['*', '|', '+', '?']  # lista de operadores

        # le agregamos los puntos de concatenacion al regex
        self.regex = self.addDots(operators)

        # verificamos que el regex ingresado sea valido
        pattern = re.compile(valid)
        matcher = pattern.match(self.regex)

        # para ver si hay dos puntos seguidos
        last_was_dot = False
        for c in self.regex:
            if c == '.':
                if last_was_dot:
                    return 'Error en la expresión regular ingresada. No se puede tener 2 puntos seguidos.'
                last_was_dot = True
            else:
                last_was_dot = False
        # for para ver si hay 2 operadores seguidos
        last_was_operator = False
        for c in self.regex:
            if c in operators:
                if last_was_operator and c != ')' and c != '|':
                    return 'Error en la expresión regular ingresada. No se puede tener 2 operadores seguidos.'
                last_was_operator = True
            else:
                last_was_operator = False

        # ifs para ver que errores tiene el regex
        if not self.regex[0].isalnum() and self.regex[0] != '(':
            self.isValid = False
            return self.getOperatorErrors()

        if not matcher:
            self.isValid = False
            return self.getSyntaxErrors()

        if '(' in self.regex or ')' in self.regex:
            self.isValid = False
            return self.getParenthesesErrors()

        if '()' in self.regex:
            self.isValid = False
            return "Error en la expresión regular ingresada. El operador '()' no se está aplicando a ningún símbolo."

        self.isValid = True
        return self.getRegex()

    '''
    funcion para agregarlo los puntos de concatenacion al regex
    '''

    def addDots(self, operators):
        newRegex = ''  # creamos el nuevo regex vacio

        # for para recorrer el regex
        for i in range(len(self.regex)):
            char = self.regex[i]  # obtenemos el caracter actual

            # if para ver si el caracter actual es un operador
            if i + 1 < len(self.regex):
                nextChar = self.regex[i + 1]  # obtenemos el siguiente caracter
                newRegex += char  # agregamos el caracter actual al nuevo regex

                # ifs para ver si el siguiente caracter no esta en la lista de operadores
                # ifs para ver si el caracter actual no esta en la lista de operadores binarios
                if char != '(':
                    if nextChar != ')':
                        if nextChar not in operators:
                            if char != '|':
                                newRegex += '.'

        return newRegex + self.regex[-1]

    '''
    funcion para obtener el regex modificiado en caso sea necesario
    '''

    def getRegex(self):
        # modificamos el regex para que no tenga ?
        if '?' in self.regex:
            self.regex = self.regex.replace('?', '|ε')
            self.regex = self.regex.replace('.|ε', '|ε.')
            parts = self.regex.split('.')
            for i in range(len(parts)):
                if '|ε' in parts[i]:
                    parts[i] = f"({parts[i]})"
            self.regex = ".".join(parts)

        # modificamos el regex para que no tenga +
        if '+' in self.regex:
            parts = self.regex.split('.')
            new_parts = []
            for i, part in enumerate(parts):
                if '+' in part:
                    if '(' in part and ')' in part and part.index('(') < part.index('+') < part.index(')'):
                        subparts = part[part.index(
                            '(') + 1:part.index(')')].split('+')
                        new_part = f"({subparts[0]}.{subparts[0]}*)"
                        new_parts.append(new_part)
                    else:
                        subparts = part.split('+')
                        new_part = f"{subparts[0]}.{subparts[0]}*"
                        new_parts.append(new_part)
                else:
                    new_parts.append(part)
            self.regex = ".".join(new_parts)

        return self.regex

    '''
    verificando que no incie con un operador
    '''

    def getOperatorErrors(self):
        op = self.regex[0]
        if op == '.':
            return "Error en la expresión regular ingresada. El operador '.' no se está aplicando a ningún símbolo."
        elif op == '*':
            return "Error en la expresión regular ingresada. El operador '*' no se está aplicando a ningún símbolo."
        elif op == '+':
            return "Error en la expresión regular ingresada. El operador '+' no se está aplicando a ningún símbolo."
        elif op == '?':
            return "Error en la expresión regular ingresada. El operador '?' no se está aplicando a ningún símbolo."
        elif op == '|':
            return "Error en la expresión regular ingresada. El operador '|' no se está aplicando a ningún símbolo."
        else:
            return f"Error en la expresión regular ingresada. El operador '{op}' no se está aplicando a ningún símbolo."

    '''
    verificando que no tenga caracteres invalidos
    '''

    def getSyntaxErrors(self):
        for c in self.regex:
            if not (c.isalnum() or c in '()+*|?.'):
                return f"Error en la expresion regular ingresada. El caracter '{c}' no es un caracter valido."
        return "Error en la expresion regular ingresada. La expresion regular no es valida."

    '''
    verificando que los parentesis estan balanceados
    '''

    def getParenthesesErrors(self):
        openParenCount = 0
        for c in self.regex:
            if c == '(':
                openParenCount += 1
            elif c == ')':
                openParenCount -= 1
                if openParenCount < 0:
                    return "Error en la expresion regular ingresada. Falta un parentesis abierto."

        if openParenCount > 0:
            return "Error en la expresion regular ingresada. Falta un parentesis cerrado."
        else:
            self.isValid = True
            return self.getRegex()
