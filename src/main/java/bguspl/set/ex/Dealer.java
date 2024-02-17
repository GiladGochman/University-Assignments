package bguspl.set.ex;

import bguspl.set.Env;

import java.time.Year;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;
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

    public Thread dealerThread;

    /*
    Hash map to find all the threds that locks the semaphore
    */ 


    public int playerWhoClaimedSet;

    public int [] setCards;



    /**
     * The time when the dealer needs to reshuffle the deck due to turn timeout.
     */
    private long reshuffleTime = Long.MAX_VALUE;

    public Dealer(Env env, Table table, Player[] players) {
        this.env = env;
        this.table = table;
        this.players = players;
        deck = IntStream.range(0, env.config.deckSize).boxed().collect(Collectors.toList());
        terminate = false;
        timerValue = env.config.turnTimeoutMillis;
        setSempahore = new Semaphore(1,true);
        reshuffleTime = env.config.turnTimeoutMillis;
        playerWhoClaimedSet=-1;
        setCards=new int[env.config.featureSize];
    }

    /**
     * The dealer thread starts here (main loop for the dealer thread).
     */
    @Override
    public void run() {
        dealerThread=Thread.currentThread();
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
        // for(int i=0;i<3;i++){
        //     table.removeCard(table.cardToSlot[setCards[i]]);
        //     for(Player player:players){
        //         for(int j=0;j<3;j++){
        //             if(player.getToken()[j]==setCards[i]){
        //                 player.counterTokens--;
        //                 player.getToken()[j]=-1;
        //             }
        //         }
        //     }
        // }
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
    private void sleepUntilWokenOrTimeout() {
        
        long start = System.currentTimeMillis();
        long remainingTime=1000;
        while(remainingTime>0){
           
            try{
                Thread.sleep(remainingTime);
                remainingTime=0;
            } catch(InterruptedException i){
                if(terminate) return;
                if(env.util.testSet(setCards)) {
                    players[playerWhoClaimedSet].point();
                    removeCardsFromTable();
                }
                else{
                    players[playerWhoClaimedSet].penalty();
                }
    
    
                remainingTime=start+1000-System.currentTimeMillis();
            }
        }
        timerValue-=1000;
        
    }
    /**
     * Sleep for a fixed amount of time or until the thread is awakened for some purpose.
     */
    // private void sleepUntilWokenOrTimeout() {
    //     long start = System.currentTimeMillis();
    //     long remainingTime = 1000;
    //     while (remainingTime > 0) {
    //         try {
    //             // Wait for players to latch or timeout
    //             boolean latched = latch.await(remainingTime, TimeUnit.MILLISECONDS);
    //             if (latched) {
    //                if(env.util.testSet(setCards)) {
    //                 players[playerWhoClaimedSet].point();
    //                 removeCardsFromTable();
    //                 latch = new CountDownLatch(1);
    //                }
    //                else{
    //                 players[playerWhoClaimedSet].penalty();
    //                }
    //             }
    //         } catch (InterruptedException e) {
    //             // Handle interruption if necessary
    //             Thread.currentThread().interrupt();
    //         }
    
    //         // Calculate remaining time after waiting for the semaphore
    //         long elapsed = System.currentTimeMillis() - start;
    //         remainingTime = 1000 - elapsed;
    //     }
        
    //     // Decrease the timer value after waiting
    //     timerValue -= 1000;
    // }

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

    public void claimSet(int player){
    //     try{
    //         setSempahore.acquire();
    //         if(!players[player].hasSameCardsThatFormsSet()){
    //             setSempahore.release();
    //             return;
    //         }
    //         setCards=players[player].getCards();
    //         playerWhoClaimedSet=player;
    //         dealerThread.interrupt();
            
    //     } catch(InterruptedException e){

    //     }
    //     setSempahore.release();
    }
}
