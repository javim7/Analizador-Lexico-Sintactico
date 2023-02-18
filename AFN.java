import java.util.ArrayList;

public class AFN {

    public ArrayList<Transition> transitions = new ArrayList<Transition>();

    public int initialState;
    public int finalState;

    public AFN(int initialState, int finalState) {
        this.initialState = initialState;
        this.finalState = finalState;
    }

    public void printAFN() {
        System.out.println("");
        for (Transition transition : transitions) {
            System.out.println("[" + transition.state + ", " + transition.symbol + ", " + transition.nextState + "]");
        }
    }

    public void AFNInfo() {
        System.out.println("\nInitial State: " + initialState);
        System.out.println("Final State: " + finalState);
    }

}
