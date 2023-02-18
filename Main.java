class Main {

	public static void main(String args[]) {

		// variable tipo String = regex
		// String regex = "(a|b)*.a.b.b";
		String regex = "a.(a|b)*.b";

		// pasamos de infix a postfix e imprimimos el postfix
		String postfix = Postfix.infixToPostfix(regex);
		System.out.println("\nPostfix: " + postfix);

		// creamos un objeto de la clase Thompson
		Thompson thompson = new Thompson(postfix);

		// generamos el AFN con el postfix dado
		AFN afn = thompson.afnConstruction();
		afn.printAFN(); // imprimimos el AFN
		afn.AFNInfo();

	}
}
