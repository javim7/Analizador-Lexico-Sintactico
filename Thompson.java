import java.util.Stack;

public class Thompson {

    public String postfix;
    public int generatedStates = 0;

    public Thompson(String postfix) {
        this.postfix = postfix;
    }

    /**
     * Genera un AFN a partir de un simbolo
     * 
     * @param symbol
     * @return AFN afn
     */
    public AFN symbolRule(char symbol) {
        int state = generatedStates;
        generatedStates++;

        int nextState = generatedStates;
        generatedStates++;
        AFN afn = new AFN(state, nextState);
        Transition transition = new Transition(state, symbol, nextState);

        afn.transitions.add(transition);

        return afn;
    }

    /**
     * 
     * @param afn1
     * @param afn2
     * @return AFN afn (afn1 | afn2)
     */
    public AFN orExpression(AFN afn1, AFN afn2) {

        // informacion del estado inicial
        int initialState = generatedStates;
        int state1 = generatedStates; // el estado inicial sera el primer nuevo nodo
        generatedStates++;

        // informacion del estado final
        int finalState = generatedStates;
        int state2 = generatedStates; // el estado final sera el segundo nuevo nodo
        generatedStates++;

        AFN afn = new AFN(initialState, finalState); // creamos un AFN nuevo
        // transiciones del estado inicial a los estados iniciales de cada AFN
        Transition transition1 = new Transition(state1, 'ε', afn1.initialState);
        Transition transition2 = new Transition(state1, 'ε', afn2.initialState);

        // transiciones del estado final a los estados finales de cada AFN
        Transition transition3 = new Transition(afn1.finalState, 'ε', state2);
        Transition transition4 = new Transition(afn2.finalState, 'ε', state2);

        // agregando las primeras transiciones
        afn.transitions.add(transition1);
        afn.transitions.add(transition2);

        // agragando las transiciones de cada AFN
        for (Transition transition : afn1.transitions) {
            afn.transitions.add(transition);
        }
        for (Transition transition : afn2.transitions) {
            afn.transitions.add(transition);
        }

        // agregando las transiciones finales
        afn.transitions.add(transition3);
        afn.transitions.add(transition4);

        return afn;
    }

    /**
     * Concatena dos AFN
     * 
     * @param afn1
     * @param afn2
     * @return AFN afn (afn1 + afn2)
     */
    public AFN concatExpression(AFN afn1, AFN afn2) {
        AFN afn = new AFN(afn1.initialState, afn2.finalState);

        // agregando todas las transiciones del afn1 al nuevo afn
        for (Transition transition : afn1.transitions) {
            afn.transitions.add(transition);
        }

        // obteniendo los estados final del af1 e inicial del afn2
        int finalAFN1 = afn1.finalState;
        int initialAFN2 = afn2.initialState;

        // cambiando el estado inicial del afn2 al estado final del afn1
        for (Transition transition : afn2.transitions) {
            if (transition.state == initialAFN2) {
                transition.state = finalAFN1;
                // transition.nextState--;
            } else {
                // transition.state--;
                // transition.nextState--;
            }
        }
        // generatedStates--; // restamos uno al contador de estados generados

        // agregamos las transiciones del afn2 al nuevo afn
        for (Transition transition : afn2.transitions) {
            afn.transitions.add(transition);
        }

        return afn;

    }

    /**
     * Genera un AFN que acepta el simbolo cero o mas veces
     * 
     * @param afn1
     * @return AFN afn (afn1*)
     */
    public AFN kleeneExpression(AFN afn1) {

        // obtenemos los estados inicial y finales para el nuevo afn
        // estos seran dos estanos nuevos
        int initialState = generatedStates;
        generatedStates++;

        int finalState = generatedStates;
        generatedStates++;

        // creamos el nuevo afn
        AFN afn = new AFN(initialState, finalState);

        // creamos y agreagmos la primera transicion
        Transition transition1 = new Transition(initialState, 'ε', afn1.initialState);
        afn.transitions.add(transition1);

        // agragamos todas las transiciones del afn1
        for (Transition transition : afn1.transitions) {
            afn.transitions.add(transition);
        }

        // creando y agregando las nuevas transiciones restantes
        Transition transition2 = new Transition(afn1.finalState, 'ε', afn1.initialState);
        Transition transition3 = new Transition(afn1.finalState, 'ε', finalState);
        Transition transition4 = new Transition(initialState, 'ε', finalState);

        afn.transitions.add(transition2);
        afn.transitions.add(transition3);
        afn.transitions.add(transition4);

        return afn;

    }

    /**
     * Genera un AFN siguendo la cerradura positiva
     * 
     * @param afn1
     * @return AFN afn (afn1+)
     */
    public AFN plusExpression(AFN afn1) {

        // obtenemos los estados inicial y finales para el nuevo afn
        // estos seran dos estanos nuevos
        int initialState = generatedStates;
        generatedStates++;

        int finalState = generatedStates;
        generatedStates++;

        // creamos el nuevo afn
        AFN afn = new AFN(initialState, finalState);

        // creamos y agreagmos la primera transicion
        Transition transition1 = new Transition(initialState, 'ε', afn1.initialState);
        afn.transitions.add(transition1);

        // agragamos todas las transiciones del afn1
        for (Transition transition : afn1.transitions) {
            afn.transitions.add(transition);
        }

        // creando y agregando las nuevas transiciones restantes
        Transition transition2 = new Transition(afn1.finalState, 'ε', afn1.initialState);
        Transition transition3 = new Transition(afn1.finalState, 'ε', finalState);

        afn.transitions.add(transition2);
        afn.transitions.add(transition3);

        return afn;

    }

    /**
     * Genera un AFN con el postfix dado
     * 
     * @param
     * @return AFN afn (afn1?)
     */
    public AFN afnConstruction() {

        // creando el stack para poder construir el AFN
        Stack<AFN> stack = new Stack<AFN>();

        // for para poder recorrer toda la expresion regular
        for (int i = 0; i < this.postfix.length(); i++) {
            char character = this.postfix.charAt(i);

            // si el caracter es un simbolo, se crea un AFN con ese simbolo
            if (Character.isLetterOrDigit(character)) {
                stack.push(symbolRule(character));
            } else {
                // si el caracter es un or, se crea un AFN con la union de los dos AFN
                if (character == '|' | character == '+') {
                    AFN afn2 = stack.pop();
                    AFN afn1 = stack.pop();
                    stack.push(orExpression(afn1, afn2));
                }
                if (character == '.') {
                    AFN afn2 = stack.pop();
                    AFN afn1 = stack.pop();
                    stack.push(concatExpression(afn1, afn2));
                }
                if (character == '*') {
                    AFN afn1 = stack.pop();
                    stack.push(kleeneExpression(afn1));
                }
            }

        }

        return stack.peek();
    }

}
