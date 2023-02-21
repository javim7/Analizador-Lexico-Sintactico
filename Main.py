from NFA import *
from Regex import *
from Postfix import *
from Thompson import *
from NFADrawer import *

if __name__ == '__main__':
    # regexInput = "a+"
    # regexInput = "a(a|b)*b"
    # regexInput = "0?(1?)?0*"
    # regexInput = "(a|b)*abb"
    # regexInput = "a(b*|a)bc*(a|b)*"
    # regexInput = "aa(a|b)*(b|a)bbb"

    # instanciamos regex
    regularExpression = Regex()

    # while para ver si la regex inputeada es valida
    while not regularExpression.isValid:
        # pedimos al usuario que ingrese una regex
        regexInput = input("\nIngrese un regex, ex. 'a(a|b)*b': ")
        regularExpression.regex = regexInput

        # verificamos que la regex sea valida
        regex = regularExpression.checkRegex()
        # if para ver si la regex es falsa e imprimir los errores
        if not regularExpression.isValid:
            print(f"\n{regex}")

    # si la regex es valida, imprimimos la regex
    print("\nRegex: " + regex)

    # pasamos la regex de infix a postfix
    postfix = Postfix(regex)
    postfix = postfix.infixToPostfix()
    print("Postfix: " + postfix)

    # instanciamos thompson
    thompson = Thompson(postfix)

    # construimos el afn
    nfa = thompson.nfaConstruction()
    nfa.print_afn()
    nfa.afn_info()

    # obtenemos la informacion general del afn
    transitions = nfa.transitions
    initial_state = nfa.initial_state
    final_state = nfa.final_state

    # dibujamos el afn
    nfa_drawer = NFADrawer(transitions, initial_state, final_state)
    nfa_drawer.draw()
