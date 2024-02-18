package bguspl.set.ex;

import bguspl.set.Env;

import java.time.Year;
import java.util.Collections;
import java.util.LinkedList;
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

    public int [] cardsSet;



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
        // reshuffleTime = env.config.turnTimeoutMillis;
        playerWhoClaimedSet=-1;
        cardsSet=new int[env.config.featureSize];
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
            shuffleDeck();
        }
        announceWinners();
        env.logger.info("thread " + Thread.currentThread().getName() + " terminated.");
    }

    /**
     * The inner loop of the dealer thread that runs as long as the countdown did not time out.
     */
    private void timerLoop() {
        reshuffleTime=System.currentTimeMillis()+ env.config.turnTimeoutMillis;
        while (!terminate && System.currentTimeMillis() < reshuffleTime) {
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
        if(playerWhoClaimedSet!=-1){
            for(int card:cardsSet){
                LinkedList<Integer> playersWhoPlacedTokens= table.getAllPlayersThatPlacedTokenOnSlot(table.cardToSlot[card]);
                for(int playerId: playersWhoPlacedTokens){
                    players[playerId].tokensCounter--;
                }
                table.removeCard(table.cardToSlot[card]);
            }
        }
        
    }

    /**
     * Check if any cards can be removed from the deck and placed on the table.
     */
    private void placeCardsOnTable() {
       for(int i=0;i<table.slotToCard.length;i++){
        if(table.slotToCard[i]==null){
            //pulling a card from the deck and adding it to the table
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
        long remainingTime = 1000;
    
        while (remainingTime > 0) {
            try {
                // dealer thread trying to sleep for 1 sec
                Thread.sleep(remainingTime);
                remainingTime = 0;
            } catch (InterruptedException ignored) {
                //the case some player tries to claim a set or the game is terminated
                if (terminate) return;
                //if someone tries to claim a set
                if (playerWhoClaimedSet != -1) {
                    
                        synchronized (players[playerWhoClaimedSet]) {
                            //get the cards from the table, each player has a list of tokens on the table data structure
                            cardsSet=table.getSetCards(playerWhoClaimedSet);
                            //if there is a set
                            if (env.util.testSet(cardsSet)) {
                                //update the field in the player whos waiting for set
                                players[playerWhoClaimedSet].foundSet = true;
                                //removing the cards and will update in the function the token counters for players
                                removeCardsFromTable();
                                // interrupt the player to update his state
                                players[playerWhoClaimedSet].getPlayerThread().interrupt();
                                playerWhoClaimedSet=-1;
                                // update the time of reshuffeling
                                reshuffleTime=System.currentTimeMillis() + env.config.turnTimeoutMillis;
                                //need to add a flag to change the time to reset
                                return;
                            }
                            players[playerWhoClaimedSet].getPlayerThread().interrupt();
                            playerWhoClaimedSet=-1;
                            
                        
                    }
                    //sync on the player who claim the set
              
                }
                remainingTime = start + 1000 - System.currentTimeMillis();
            }
        }
    
        timerValue -= 1000;
    }
    // private void sleepUntilWokenOrTimeout() {
        
    //     long start = System.currentTimeMillis();
    //     long remainingTime=1000;
    //     while(remainingTime>0){
           
    //         try{
    //             Thread.sleep(remainingTime);
    //             remainingTime=0;
    //         } catch(InterruptedException i){
    //             if(terminate) return;
    //             if(env.util.testSet(table.getSetCards(playerWhoClaimedSet))) {
    //                 System.out.println("1");
    //                 players[playerWhoClaimedSet].foundSet=true;
    //                 removeCardsFromTable();
    //             }
    //             System.out.println("now interupting");
    //             players[playerWhoClaimedSet].getPlayerThread().interrupt();
    //             System.out.println("h1");
    
    
    //             remainingTime=start+1000-System.currentTimeMillis();
    //         }
    //     }
    //     timerValue-=1000;
        
    // }
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
       LinkedList<Integer> winners = new LinkedList<>();
       int highscore=0;
       // iterating through all players 
       for(Player player: players){
            // if we found some player with the same highscore we add him
            if(player.score()== highscore) winners.add(player.id);
            //if we found some player with higher score , we remove all the other players that were on the old highscore and add the player with the new highscore
            else if(player.score() > highscore){
                winners.clear();
                highscore=player.score();
                winners.add(player.id);
            }
       }
       // make an array from the linked list
       int [] winnerPlayers = new int[winners.size()];
       for(int i=0;i<winners.size();i++){
        winnerPlayers[i]=winners.removeFirst();
       }
       //display the winner
       env.ui.announceWinner(winnerPlayers);
       
    }

    private void shuffleDeck(){
        Collections.shuffle(deck);
    }
    // Useless because the dealer is not approachable from table:
    // public void decreasePlayerTokenCounter(int player){
    //     players[player].tokensCounter--;
    // } 

}