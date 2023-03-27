from collections import deque


class Postfix:
    '''
    Postfix: Es la clase que se utiliza para poder convertir la expresion a postfix, desde un infix. 
    Toma como parametro el regex en infix.
    Se guarda la precedencia de cada operador para poder construir el postifx de manera correcta.
    '''

    def __init__(self, infix):
        self.infix = infix

    '''
    definimos la precedencia de los operadores
    '''

    def precedence(self, c):
        if c == '|':
            return 1
        elif c == '.':
            return 2
        elif c == '*':
            return 3
        else:
            return -1

    '''
    pasamos el regex de infix a postifx
    '''

    def infixToPostfix(self):
        postfix = ""

        # creamos una pila
        stack = deque()

        # iteramos por cada uno de los caracteres del regex
        for i in range(len(self.infix)):
            c = self.infix[i]

            # si es un operando lo agregamos al postfix
            if c.isalnum():
                postfix += c
            # si es un parentesis izquierdo lo agregamos a la pila
            elif c == '(':
                stack.append(c)
            # si es un parentesis derecho sacamos todos los elementos de la pila hasta encontrar un parentesis izquierdo
            elif c == ')':
                while stack and stack[-1] != '(':
                    postfix += stack.pop()
                if stack and stack[-1] == '(':
                    stack.pop()
            # si es un operador
            else:
                while stack and self.precedence(c) <= self.precedence(stack[-1]):
                    postfix += stack.pop()
                stack.append(c)

        while stack:
            if stack[-1] == '(':
                return "Invalid Infix Expression"
            postfix += stack.pop()

        return postfix
