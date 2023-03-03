from Tree import *
from Regex import *
from Drawer import *
from Postfix import *
from Subsets import *
from Thompson import *
from Minimization import *


if __name__ == '__main__':
    regexList = [
        "a+",                 # 0
        "ab*ab*",             # 1
        "a(a|b)*b",           # 2
        "(a|b)*abb",          # 3
        "0?(1|ε)?0*",         # 4
        "aa(a|b)*(b|a)bbb",   # 5
        "a(b*|a)bc*(a|b)*",   # 6
        "(a|b)*((a|b)|ε)*",   # 7
        "(a|b)*((a|(bb)*)ε)"  # 8
    ]

    '''
    REGEX
    '''
    # instanciamos regex
    regularExpression = Regex()

    # while para ver si la regex inputeada es valida
    while not regularExpression.isValid:
        # pedimos al usuario que ingrese una regex
        # regexInput = input("\nIngrese un regex, ex. 'a(a|b)*b': ")
        regularExpression.regex = regexList[4]

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
    nfa_drawer.draw(filename='graphs/dibujoAFN')

    '''
    NFA TO DFA
    '''
    # instanciamos subsets
    subsets = Subsets(nfa)

    # construimos el afd e imprimimos su informacion
    dfaSubsets = subsets.subDfaConstruction()
    dfaSubsets.print_dfa()
    dfaSubsets.dfa_info()

    # dibujamos el afd
    dfaSubsets_drawer = Drawer(
        dfaSubsets.transitions, dfaSubsets.initial_state, dfaSubsets.final_states, 'AFD S')
    dfaSubsets_drawer.draw(filename='graphs/dibujoADFSub')

    '''
    SUBSET DFA MINIMIZATION
    '''
    minSub = Minimization(dfaSubsets)

    # construimos el afd minimizado
    minDfaSubsets = minSub.minDFAConstruction()
    minDfaSubsets.print_dfa()
    minDfaSubsets.dfa_info()

    # dibujamos el afd minimizado
    minDfaSubsets_drawer = Drawer(
        minDfaSubsets.transitions, minDfaSubsets.initial_state, minDfaSubsets.final_states, 'Min S')
    minDfaSubsets_drawer.draw(filename='graphs/dibujoAFDMinSub')

    '''
    DFA DIRECLY
    '''
    tree = Tree(postfix)

    # construimos el afd directo
    dfaDirect = tree.dirDfaConstruction()
    dfaDirect.print_dfa()
    dfaDirect.dfa_info()

    # for node in tree.nodes:
    #     print(node)

    # dibujamos el afd
    dfaDirect_drawer = Drawer(
        dfaDirect.transitions, dfaDirect.initial_state, dfaDirect.final_states, 'AFD D')
    dfaDirect_drawer.draw(filename='graphs/dibujoAFDir')

    '''
    DIRECT DFA MINIMIZATION
    '''
    minDir = Minimization(dfaDirect)

    # construimos el afd minimizado
    minDfaDirect = minDir.minDFAConstruction()
    minDfaDirect.print_dfa()
    minDfaDirect.dfa_info()

    # dibujamos el afd minimizado
    minDfaDirect_drawer = Drawer(
        minDfaDirect.transitions, minDfaDirect.initial_state, minDfaDirect.final_states, 'Min D')
    minDfaDirect_drawer.draw(filename='graphs/dibujoAFDMinDir')
