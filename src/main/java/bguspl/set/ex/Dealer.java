package bguspl.set.ex;

import bguspl.set.Env;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.Semaphore;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

/**
 * This class manages the dealer's threads and data
 */
public class Dealer implements Runnable {

    /**
     * The game environment object.
     */
    private final Env env;

    /**
     * Game entities.
     */
    private final Table table;
    private final Player[] players;

    /**
     * The list of card ids that are left in the dealer's deck.
     */
    private final List<Integer> deck;

    /**
     * True iff game should be terminated.
     */
    private volatile boolean terminate;

    /*
     * variable to hold the timer value in the ui
     */
    private long timerValue;

    /*
     * semaphore for checking sets
     */
    public Semaphore setSempahore;



    /**
     * The time when the dealer needs to reshuffle the deck due to turn timeout.
     */
    private long reshuffleTime = Long.MAX_VALUE;

    public Dealer(Env env, Table table, Player[] players) {
        this.env = env;
        this.table = table;
        this.players = players;
        deck = IntStream.range(0, env.config.deckSize).boxed().collect(Collectors.toList());
        terminate=false;
        timerValue=env.config.turnTimeoutMillis;
        setSempahore = new Semaphore(1,true);
        reshuffleTime=env.config.turnTimeoutMillis;
    }

    /**
     * The dealer thread starts here (main loop for the dealer thread).
     */
    @Override
    public void run() {
        env.logger.info("thread " + Thread.currentThread().getName() + " starting.");
        shuffleDeck();
        placeCardsOnTable();

        for(Player player:players){
            Thread playerThread=new Thread(()->player.run());
            playerThread.start();
        }
        env.ui.setCountdown(timerValue, false);
        while (!shouldFinish()) {
            placeCardsOnTable();
            timerLoop();
            updateTimerDisplay(true);
            removeAllCardsFromTable();
        }
        announceWinners();
        env.logger.info("thread " + Thread.currentThread().getName() + " terminated.");
    }

    /**
     * The inner loop of the dealer thread that runs as long as the countdown did not time out.
     */
    private void timerLoop() {
        long start=System.currentTimeMillis();
        while (!terminate && System.currentTimeMillis() <start+ reshuffleTime) {
            sleepUntilWokenOrTimeout();
            updateTimerDisplay(false);
            removeCardsFromTable();
            placeCardsOnTable();
            // System.out.println("finnished loop, " + timerValue );

        }
    }

    /**
     * Called when the game should be terminated.
     */
    public void terminate() {
       try{
        for(Player player:players){
            player.terminate();
        }
        Thread.currentThread().join();
       }catch (InterruptedException e){};
     
    }

    /**
     * Check if the game should be terminated or the game end conditions are met.
     *
     * @return true iff the game should be finished.
     */
    private boolean shouldFinish() {
        return terminate || env.util.findSets(deck, 1).size() == 0;
    }

    /**
     * Checks cards should be removed from the table and removes them.
     */
    private void removeCardsFromTable() {
        
    }

    /**
     * Check if any cards can be removed from the deck and placed on the table.
     */
    private void placeCardsOnTable() {
       for(int i=0;i<table.slotToCard.length;i++){
        if(table.slotToCard[i]==null){

            int cardToPlace=deck.remove(0);
            table.placeCard(cardToPlace, i);
        }
       }
    }

    /**
     * Sleep for a fixed amount of time or until the thread is awakened for some purpose.
     */
    // private void sleepUntilWokenOrTimeout() {
        
    //     long start = System.currentTimeMillis();
    //     long remainingTime=1000;
    //     while(remainingTime>0){
           
    //         try{

    //             Thread.sleep(remainingTime);
    //             remainingTime=0;
    //         } catch(InterruptedException i){
    //             //do some action
    
    
    //             remainingTime=start+1000-System.currentTimeMillis();
    //         }
    //     }
    //     timerValue-=1000;
        
    // }
    private void sleepUntilWokenOrTimeout() {
        long start = System.currentTimeMillis();
        long remainingTime = 1000;
        while (remainingTime > 0) {
            try {
                // Wait for the semaphore with a timeout
                boolean acquired = this.setSempahore.tryAcquire(1, remainingTime, TimeUnit.MILLISECONDS);
                if (acquired) {
                    // A player claimed a set, break out of the loop
                    break;
                }
            } catch (InterruptedException e) {
                // Handle interruption if necessary
                Thread.currentThread().interrupt();
            }
    
            // Calculate remaining time after waiting for the semaphore
            long elapsed = System.currentTimeMillis() - start;
            remainingTime = 1000 - elapsed;
        }
        
        // Decrease the timer value after waiting
        timerValue -= 1000;
    }

    /**
     * Reset and/or update the countdown and the countdown display.
     */
    private void updateTimerDisplay(boolean reset) {
        if(reset){
            env.ui.setCountdown(env.config.turnTimeoutMillis, false);
            timerValue=env.config.turnTimeoutMillis;
        } 
        else env.ui.setCountdown(timerValue, false);
        // System.out.println("updated timer display, " + timerValue );
    }

    /**
     * Returns all the cards from the table to the deck.
     */
    private void removeAllCardsFromTable() {
        
    }

    /**
     * Check who is/are the winner/s and displays them.
     */
    private void announceWinners() {
        // TODO implement
    }

    private void shuffleDeck(){
        Collections.shuffle(deck);
    }
}
