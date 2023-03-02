from Tree import *
from Regex import *
from Drawer import *
from Postfix import *
from Subsets import *
from Thompson import *


if __name__ == '__main__':
    # regexInput = "a+"
    # regexInput = "ab*ab*"
    # regexInput = "a(a|b)*b"
    # regexInput = "(a|b)*abb"
    # regexInput = "0?(1|ε)?0*"
    # regexInput = "aa(a|b)*(b|a)bbb"
    # regexInput = "a(b*|a)bc*(a|b)*"
    # regexInput = "(a|b)*((a|b)|ε)*"
    # regexInput = "(a|b)*((a|(bb)*)ε)"

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
    nfa_drawer = Drawer(nfa.transitions, nfa.initial_state,
                        [nfa.final_state], 'AFN')
    nfa_drawer.draw(filename='dibujoAFN')

    '''
    NFA TO DFA
    '''
    # instanciamos subsets
    subsets = Subsets(nfa)

    # construimos el afd e imprimimos su informacion
    dfaSubsets = subsets.dfaConstruction()
    dfaSubsets.print_dfa()
    dfaSubsets.dfa_info()

    # dibujamos el afd
    dfaSubsets_drawer = Drawer(
        dfaSubsets.transitions, dfaSubsets.initial_state, dfaSubsets.final_states, 'AFD S')
    dfaSubsets_drawer.draw(filename='dibujoADFSub')

    '''
    DFA DIRECLY
    '''
    tree = Tree(postfix)

    # construimos el afd directo
    dfaDirect = tree.dfaConstruction()
    dfaDirect.print_dfa()
    dfaDirect.dfa_info()

    # for node in tree.nodes:
    #     print(node)

    # dibujamos el afd
    dfaDirect_drawer = Drawer(
        dfaDirect.transitions, dfaDirect.initial_state, dfaDirect.final_states, 'AFD D')
    dfaDirect_drawer.draw(filename='dibujoADFDir')
