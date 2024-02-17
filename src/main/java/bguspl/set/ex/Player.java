package bguspl.set.ex;
import java.time.Year;
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


    public int tokensCounter;

    public boolean foundSet;

    Object counterTokenLock;
    /**
     * an array to store the tokens that are placed or not placed
     */

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
        tokensCounter=0;
        foundSet=false;
        counterTokenLock = new Object();
       
            
       
            
        
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
                if(!table.removeToken(id,slot)){
                    if(tokensCounter< env.config.featureSize){
                    table.placeToken(id, slot); 
                    tokensCounter++;  
                    if(tokensCounter==env.config.featureSize) claimSet();
                    
                }
                }
                else{
                    --tokensCounter;
                    
                }
            }
           
        }
        try{
            Thread.currentThread().join();
        } catch(InterruptedException e){};
       
        if (!human) try { aiThread.join(); } catch (InterruptedException ignored) {}
        env.logger.info("thread " + Thread.currentThread().getName() + " terminated.");
    }

    /**
     * Creates an additional thread for an AI (computer) player. The main loop of this thread repeatedly generates
     * key presses. If the queue ofY
     *  key presses is full, the thread waits until it is not full.
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
       if(queueActions.size()<=env.config.featureSize) queueActions.add(slot);
    }

    /**
     * Award a point to a player and perform other related actions.
     *
     * @post - the player's score is increased by 1.
     * @post - the player's score is updated in the ui.
     */
    public void point() {
        try{
            System.out.println(2);
            
           
            int ignored = table.countCards(); // this part is just for demonstration in the unit tests
            env.ui.setScore(id, ++score);
            for(int i=0;i<env.config.pointFreezeMillis/1000;i++){
                env.ui.setFreeze(id, env.config.pointFreezeMillis-i*1000);
                Thread.sleep(1000);
            }
            env.ui.setFreeze(id,0);
            queueActions.clear();
            tokensCounter=0;
        }catch(InterruptedException e){
            if(terminate) terminate();
            Thread.currentThread().interrupt();
        };
        

       
    }

    /**
     * Penalize a player and perform other related actions.
     */
    public void penalty() {
        try {
           queueActions.clear();
        } finally {
            try {
                for(int i=0;i<env.config.penaltyFreezeMillis/1000;i++){
                    env.ui.setFreeze(id, env.config.penaltyFreezeMillis- i*1000 );
                    Thread.sleep(1000);
                    
                }
                
            env.ui.setFreeze(id, 0);
            queueActions.clear();
            } catch (InterruptedException e) {
                if(terminate) terminate();
                Thread.currentThread().interrupt();
            }
        }
    }

    public int score() {
        return score;
    }

    public Thread getPlayerThread(){
        return playerThread;
    }

    public boolean allTokensPlaced(){
       return tokensCounter == env.config.featureSize;
    }

    public void claimSet() {
        try {
            this.foundSet = false;
            dealer.setSempahore.acquire();
            if (!allTokensPlaced()) {
                dealer.setSempahore.release();
                return;
            }
            dealer.playerWhoClaimedSet = id;
            dealer.dealerThread.interrupt();
            dealer.setSempahore.release();
            
            synchronized (dealer.setSempahore) {
                dealer.setSempahore.wait();
            }
        } catch (InterruptedException e) {
            System.out.println("got interrupted");
            if (foundSet) 
                point();
            else 
                penalty();
        }
    }
}
//     public void claimSet(){
//         try{
//             this.foundSet=false;
//             dealer.setSempahore.acquire();
//             if(!hasSameCardsThatFormsSet()){
//                 dealer.setSempahore.release();
//                 return;
//             }
//             dealer.playerWhoClaimedSet=id;
//             dealer.dealerThread.interrupt();

//             dealer.setSempahore.wait();
//         } catch(InterruptedException e){
//             System.out.println("got inturpted");
//             if(foundSet=false) penalty();
//             else point();
//         }
//         dealer.setSempahore.release();
//     }
// }

   


