public class Transition {

    // atributos
    public int state;
    public Character symbol;
    public Integer nextState;

    public Transition(int state, char symbol, int nextState) {
        this.state = state;
        this.symbol = symbol;
        this.nextState = nextState;
    }

    public void printTransition() {
        System.out.println("[State: " + state + ", Symbol: " + symbol + ", NextState: " + nextState + "]");
    }

}
