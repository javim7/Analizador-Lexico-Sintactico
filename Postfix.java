import java.util.ArrayDeque;
import java.util.Deque;

public class Postfix {

    /**
     * 
     * @param c
     * @return precedenceedence of the character
     */
    // metodo para poder verificar la precedenceedencia del caracter a analizar
    public static int precedence(char c) {
        switch (c) {
            case '|':
                return 1;
            case '.':
                return 2;
            case '*':
            case '+':
                return 3;
        }
        return -1;
    }

    /**
     * 
     * @param infix
     * @return postfix
     */
    // metodo para poder convertir la infixresion infix a postfix
    public static String infixToPostfix(String infix) {

        String postfix = "";

        // initializing empty stack
        Deque<Character> stack = new ArrayDeque<Character>();

        // System.out.println(infix);

        for (int i = 0; i < infix.length(); ++i) {

            char c = infix.charAt(i);

            // si el caracter es una letra o digito se agrega al ressultado
            if (Character.isLetterOrDigit(c))
                postfix += c;

            // Si el caracter es '(', push al stack.
            else if (c == '(')
                stack.push(c);

            // Si el caracter es ')', pop y output del stack hasta que se encuentre un '('
            else if (c == ')') {
                while (!stack.isEmpty()
                        && stack.peek() != '(') {
                    postfix += stack.peek();
                    stack.pop();
                }

                stack.pop();
            } else // si ha encontrado un operador
            {
                while (!stack.isEmpty()
                        && precedence(c) <= precedence(stack.peek())) {

                    postfix += stack.peek();
                    stack.pop();
                }
                stack.push(c);
            }
        }

        // pop de todos los operadores del stack
        while (!stack.isEmpty()) {
            if (stack.peek() == '(')
                return "Invalid infixression";
            postfix += stack.peek();
            stack.pop();
        }

        return postfix;

    }

}
