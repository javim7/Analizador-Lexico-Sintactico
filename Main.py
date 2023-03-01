from AFN import *
from Regex import *
from Drawer import *
from Postfix import *
from Subsets import *
from Thompson import *
from NFADrawer import *


if __name__ == '__main__':
    # regexInput = "a+"
    # regexInput = "a(a|b)*b"
    # regexInput = "0?(1|ε)?0*"
    # regexInput = "(a|b)*abb"
    # regexInput = "a(b*|a)bc*(a|b)*"
    # regexInput = "aa(a|b)*(b|a)bbb"

    '''
    REGEX
    '''
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

    '''
    POSTFIX
    '''
    # pasamos la regex de infix a postfix
    postfix = Postfix(regex)
    postfix = postfix.infixToPostfix()
    print("Postfix: " + postfix)

    # instanciamos thompson
    thompson = Thompson(postfix)

    '''
    NFA
    '''
    # construimos el afn
    nfa = thompson.nfaConstruction()
    nfa.print_dfa()
    nfa.dfa_info()

    # dibujamos el afn
    nfa_drawer = Drawer(nfa.transitions, nfa.initial_state, [nfa.final_state])
    nfa_drawer.draw(filename='afnDibujado')

    '''
    NFA TO DFA
    '''
    # instanciamos subsets
    subsets = Subsets(nfa)

    # construimos el afd e imprimimos su informacion
    dfa = subsets.dfaConstruction()
    dfa.print_dfa()
    dfa.dfa_info()

    # dibujamos el afd
    dfa_drawer = Drawer(
        dfa.transitions, dfa.initial_state, dfa.final_states)
    dfa_drawer.draw(filename='afdDibujado')
