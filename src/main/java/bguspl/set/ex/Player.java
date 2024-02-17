package bguspl.set.ex;
import java.util.List;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.CountDownLatch;

import bguspl.set.Env;


/**
 * This class manages the players' threads and data
 *
 * @inv id >= 0
 * @inv score >= 0
 */
public class Player implements Runnable {

    /**
     * The game environment object.
     */
    private final Env env;

    /**
     * Game entities.
     */
    private final Table table;

   /**
    * Dealer
    */
    private final Dealer dealer;

    /**
     * The id of the player (starting from 0).
     */
    public final int id;

    /**
     * The thread representing the current player.
     */
    private Thread playerThread;

    /**
     * The thread of the AI (computer) player (an additional thread used to generate key presses).
     */
    private Thread aiThread;

    /**
     * True iff the player is human (not a computer player).
     */
    private final boolean human;

    /**
     * True iff game should be terminated.
     */
    private volatile boolean terminate;

    /**
     * The current score of the player.
     */
    private int score;


    /**
     * Queue for saving key actions
     */
    private ConcurrentLinkedQueue<Integer> queueActions;


    int counterTokens;
    /**
     * an array to store the tokens that are placed or not placed
     */
    private int [] tokens;

    /**
     * The class constructor.
     *
     * @param env    - the environment object.
     * @param dealer - the dealer object.
     * @param table  - the table object.
     * @param id     - the id of the player.
     * @param human  - true iff the player is a human player (i.e. input is provided manually, via the keyboard).
     */
    public Player(Env env, Dealer dealer, Table table, int id, boolean human) {
        this.env = env;
        this.table = table;
        this.id = id;
        this.human = human;
        this.dealer=dealer;
        this.queueActions=new ConcurrentLinkedQueue<>();
        this.tokens= new int[3];
        for(int i=0;i<3;i++){
            tokens[i]=-1;
        }
        counterTokens=0;
       
            
       
            
        
    }

    /**
     * The main player thread of each player starts here (main loop for the player thread).
     */
    @Override
    public void run() {
        playerThread = Thread.currentThread();
        env.logger.info("thread " + Thread.currentThread().getName() + " starting.");
        if (!human) createArtificialIntelligence();

        while (!terminate) {
            if(queueActions.size()>0){
                int slot=queueActions.remove();
                if(!table.removeToken(id,slot )){
                    table.placeToken(id, slot);
                    for(int i=0;i<3;i++){
                        if(tokens[i]==-1) {
                            tokens[i]= slot;
                            counterTokens++;
                            break;
                        }
                    }
                    if(counterTokens==3) dealer.claimSet(id);
                }
                else{
                    counterTokens--;
                    for(int i=0;i<3;i++){
                        if(tokens[i]==slot) {
                            tokens[i]= -1;
                            break;
                        }
                    }
                }
            }
           
        }
        if (!human) try { aiThread.join(); } catch (InterruptedException ignored) {}
        env.logger.info("thread " + Thread.currentThread().getName() + " terminated.");
    }

    /**
     * Creates an additional thread for an AI (computer) player. The main loop of this thread repeatedly generates
     * key presses. If the queue of key presses is full, the thread waits until it is not full.
     */
    private void createArtificialIntelligence() {
        // note: this is a very, very smart AI (!)
        aiThread = new Thread(() -> {
            env.logger.info("thread " + Thread.currentThread().getName() + " starting.");
            while (!terminate) {
                // TODO implement player key press simulator
                try {
                    synchronized (this) { wait(); }
                } catch (InterruptedException ignored) {}
            }
            env.logger.info("thread " + Thread.currentThread().getName() + " terminated.");
        }, "computer-" + id);
        aiThread.start();
    }

    /**
     * Called when the game should be terminated.
     */
    public void terminate() {
       terminate=true;
    }

    /**
     * This method is called when a key is pressed.
     *
     * @param slot - the slot corresponding to the key pressed.
     */
    public void keyPressed(int slot) {
       if(queueActions.size()<=3) queueActions.add(slot);
    }

    /**
     * Award a point to a player and perform other related actions.
     *
     * @post - the player's score is increased by 1.
     * @post - the player's score is updated in the ui.
     */
    public void point() {
        try{
            playerThread.sleep(env.config.pointFreezeMillis);
            int ignored = table.countCards(); // this part is just for demonstration in the unit tests
            env.ui.setScore(id, ++score);
        }catch(InterruptedException e){};
        

       
    }

    /**
     * Penalize a player and perform other related actions.
     */
    public void penalty() {
        try{
            playerThread.sleep(env.config.penaltyFreezeMillis);
        } catch(InterruptedException e){};
        
    }

    public int score() {
        return score;
    }

    public Thread getPlayerThread(){
        return playerThread;
    }

    public boolean hasSameCardsThatFormsSet(){
       return counterTokens == 3;
    }

    public int[] getCards(){
        int[] cards= new int[3];
        int i=0;
        for(int slot:tokens){
            cards[i]=table.slotToCard[slot];
            i++;
           
        }
        
        return cards;
    }
    public int[] getToken(){
        return tokens;
    }
}

