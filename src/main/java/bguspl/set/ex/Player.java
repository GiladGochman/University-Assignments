package bguspl.set.ex;

import bguspl.set.Env;
import java.time.Year;
import java.util.List;
import java.util.Random;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.CountDownLatch;

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
    this.dealer = dealer;
    this.queueActions = new ConcurrentLinkedQueue<>();
    tokensCounter = 0;
    foundSet = false;
    counterTokenLock = new Object();
  }

  /**
   * The main player thread of each player starts here (main loop for the player thread).
   */
  @Override
  public void run() {
    playerThread = Thread.currentThread();
    env.logger.info(
      "thread " + Thread.currentThread().getName() + " starting."
    );
    if (!human) createArtificialIntelligence();

    while (!terminate) {
      // checking if the queue is empty
      if (queueActions.size() > 0) {
        //enqueing action
        int slot = queueActions.remove();
        if (table.slotToCard[slot] != null) {
          //trying to remove the token
          if (!table.removeToken(id, slot)) {
            // the token isnt removed
            // checking whether we already have 3 tokens on the table
            if (tokensCounter < env.config.featureSize) {
              //placing the token
              table.placeToken(id, slot);
              if (table.slotToCard(slot) != null) tokensCounter++;
              //checking if we put right now 3 tokens and then claim a set
              if (tokensCounter == env.config.featureSize) claimSet();
            }
          } else {
            //decrease the counter because we successfully removed a token
            --tokensCounter;
          }
          //release readwritelock
        }
      }
    }
    try {
      // at the end of the game we join the main thread
      Thread.currentThread().join();
    } catch (InterruptedException e) {}
    if (!human) try {
      aiThread.join();
    } catch (InterruptedException ignored) {}

    env.logger.info(
      "thread " + Thread.currentThread().getName() + " terminated."
    );
  }

  /**
   * Creates an additional thread for an AI (computer) player. The main loop of this thread repeatedly generates
   * key presses. If the queue ofY
   *  key presses is full, the thread waits until it is not full.
   */
  private void createArtificialIntelligence() {
    Random rand = new Random();
    // note: this is a very, very smart AI (!)
    aiThread =
      new Thread(
        () -> {
          env.logger.info(
            "thread " + Thread.currentThread().getName() + " starting."
          );
          while (!terminate) {
            try {
              synchronized (this) {
                Thread.sleep(0);
                keyPressed(rand.nextInt(env.config.tableSize));
              }
            } catch (InterruptedException ignored) {}
          }
          env.logger.info(
            "thread " + Thread.currentThread().getName() + " terminated."
          );
        },
        "computer-" + id
      );
    aiThread.start();
  }

  /**
   * Called when the game should be terminated.
   */
  public void terminate() {
    terminate = true;
  }

  /**
   * This method is called when a key is pressed.
   *
   * @param slot - the slot corresponding to the key pressed.
   */
  public void keyPressed(int slot) {
    if (queueActions.size() <= env.config.featureSize) queueActions.add(slot);
  }

  /**
   * Award a point to a player and perform other related actions.
   *
   * @post - the player's score is increased by 1.
   * @post - the player's score is updated in the ui.
   */
  public void point() {
    try {
      int ignored = table.countCards(); // this part is just for demonstration in the unit tests
      // setting the score in the ui
      env.ui.setScore(id, ++score);
      // sleeping for 1 sec * pointFreezeMs
      for (int i = 0; i < env.config.pointFreezeMillis / 1000; i++) {
        // updating the timer
        env.ui.setFreeze(id, env.config.pointFreezeMillis - i * 1000);
        //sleep for another sec;
        Thread.sleep(1000);
      }
      // unfreeze
      env.ui.setFreeze(id, 0);
      //clearing the queue actions.
      queueActions.clear();
    } catch (InterruptedException e) {
      if (terminate) terminate();
      Thread.currentThread().interrupt();
    }
  }

  /**
   * Penalize a player and perform other related actions.
   */
  public void penalty() {
    try {
      queueActions.clear();
    } finally {
      try {
        // sleeping for freeze time like in point
        for (int i = 0; i < env.config.penaltyFreezeMillis / 1000; i++) {
          env.ui.setFreeze(id, env.config.penaltyFreezeMillis - i * 1000);
          Thread.sleep(1000);
        }
        // unfreeze and clear action queue
        env.ui.setFreeze(id, 0);
        queueActions.clear();
      } catch (InterruptedException e) {
        if (terminate) terminate();
        Thread.currentThread().interrupt();
      }
    }
  }

  public int score() {
    return score;
  }

  public Thread getPlayerThread() {
    return playerThread;
  }

  public boolean allTokensPlaced() {
    return tokensCounter == env.config.featureSize;
  }

  public void claimSet() {
    try {
      //initilizing for not finding a set
      this.foundSet = false;
      //accuire the semaphore
      dealer.setSempahore.acquire();
      // check that no cards from the set were removed (by other player completing a set just before)
      if (!allTokensPlaced()) {
        // if my tokens are removed i'll release the semaphore and notify all players that want to claim set
        dealer.setSempahore.release();
        return;
      }
      dealer.updatePlayerWhoClaimedSet(id); 
      // waiting for the dealer to check my set
      synchronized (dealer.setSempahore) {
        dealer.dealerThread.interrupt();
        while(true){
          // trying to wait for the dealer and if we didnt successed of catching him we notify him again after 3 ms
          dealer.setSempahore.wait(3);
          dealer.updatePlayerWhoClaimedSet(id);
          dealer.dealerThread.interrupt();
        }
        
      }
    } catch (InterruptedException e) {
      // the dealer stopped checking my set now ill check if my foundset flag has changed
      
      dealer.setSempahore.release();
      if (foundSet) point(); else penalty();
    }
    // realase the semaphore

  }
}
