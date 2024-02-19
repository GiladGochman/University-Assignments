package bguspl.set.ex;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;
import bguspl.set.Env;
import java.util.Arrays;
import java.util.LinkedList;
import java.util.List;
import java.util.Objects;
// import java.util.concurrent.Semaphore;
import java.util.stream.Collectors;

/**
 * This class contains the data that is visible to the player.
 *
 * @inv slotToCard[x] == y iff cardToSlot[y] == x
 */
public class Table {

  /**
   * The game environment object.
   */
  private final Env env;

  /**
   * Mapping between a slot and the card placed in it (null if none).
   */
  protected final Integer[] slotToCard; // card per slot (if any)

  /**
   * Mapping between a card and the slot it is in (null if none).
   */
  protected final Integer[] cardToSlot; // slot per card (if any)

  /*
   * DataStructure to hold the tokens
   */
  protected LinkedList<Integer>[] tokens;
  /**
   * data structure to hold all the playersTokens for each player
   */
  public LinkedList<Integer>[] playersTokens;
  /*
   * objects to sync for slots usage
   */
  public Object[] slotLocks;

  // objects to sync for playerToken usage

    public Object [] playersLock;

    public ReadWriteLock lock; // for purpuse to make sure when the dealer replaces cards no one will enter the table


    

  /**
   * Constructor for testing.
   *
   * @param env        - the game environment objects.
   * @param slotToCard - mapping between a slot and the card placed in it (null if none).
   * @param cardToSlot - mapping between a card and the slot it is in (null if none).
   */
  public Table(Env env, Integer[] slotToCard, Integer[] cardToSlot) {
    this.env = env;
    this.slotToCard = slotToCard;
    this.cardToSlot = cardToSlot;
    this.tokens = new LinkedList[env.config.tableSize];
    for (int i = 0; i < env.config.tableSize; i++) {
      tokens[i] = new LinkedList<Integer>();
    }
    this.playersTokens = new LinkedList[env.config.players];
    for (int i = 0; i < env.config.players; i++) {
      playersTokens[i] = new LinkedList<Integer>();
    }
    this.slotLocks = new Object[env.config.tableSize];
    for (int i = 0; i < env.config.tableSize; i++) {
      slotLocks[i] = new Object();
    }

        this.playersLock = new Object[env.config.players];
        for(int i=0; i<env.config.players;i++){
            playersLock[i] = new Object();
        }
        this.lock = new  ReentrantReadWriteLock();
    }

    /**
     * Constructor for actual usage.
     *
     * @param env - the game environment objects.
     */
    public Table(Env env) {

        this(env, new Integer[env.config.tableSize], new Integer[env.config.deckSize]);
        this.tokens = new LinkedList[env.config.tableSize];
        for (int i = 0; i < env.config.tableSize; i++) {
            tokens[i] = new LinkedList<Integer>();
        }
        this.slotLocks = new Object[env.config.tableSize];
        for(int i=0;i<env.config.tableSize;i++){
            slotLocks[i] = new Object();
        }
        this.playersTokens=new LinkedList[env.config.players];
        for(int i=0;i<env.config.players;i++){
            playersTokens[i] = new LinkedList<Integer>();
        }
        this.lock = new ReentrantReadWriteLock();
    }

  /**
   * This method prints all possible legal sets of cards that are currently on the table.
   */
  public void hints() {
    List<Integer> deck = Arrays
      .stream(slotToCard)
      .filter(Objects::nonNull)
      .collect(Collectors.toList());
    env.util
      .findSets(deck, Integer.MAX_VALUE)
      .forEach(set -> {
        StringBuilder sb = new StringBuilder().append("Hint: Set found: ");
        List<Integer> slots = Arrays
          .stream(set)
          .mapToObj(card -> cardToSlot[card])
          .sorted()
          .collect(Collectors.toList());
        int[][] features = env.util.cardsToFeatures(set);
        System.out.println(
          sb
            .append("slots: ")
            .append(slots)
            .append(" features: ")
            .append(Arrays.deepToString(features))
        );
      });
  }

  /**
   * Count the number of cards currently on the table.
   *
   * @return - the number of cards on the table.
   */
  public int countCards() {
    int cards = 0;
    for (Integer card : slotToCard) if (card != null) ++cards;
    return cards;
  }

  /**
   * Places a card on the table in a grid slot.
   * @param card - the card id to place in the slot.
   * @param slot - the slot in which the card should be placed.
   *
   * @post - the card placed is on the table, in the assigned slot.
   */
  public void placeCard(int card, int slot) {
    try {
      Thread.sleep(env.config.tableDelayMillis);
    } catch (InterruptedException ignored) {}
    synchronized (slotLocks[slot]) {
      cardToSlot[card] = slot;
      slotToCard[slot] = card;
      env.ui.placeCard(card, slotForUi(slot));
    }
  }

  /**
   * Removes a card from a grid slot on the table.
   * @param slot - the slot from which to remove the card.
   */
  public void removeCard(int slot) {
    try {
      Thread.sleep(env.config.tableDelayMillis);
    } catch (InterruptedException ignored) {}
    synchronized (slotLocks[slot]) {
      // syncing the slot
      int card = slotToCard[slot];
      cardToSlot[card] = null;
      slotToCard[slot] = null;
      // clear all tokens
      tokens[slot] = new LinkedList<Integer>();
      // Iterating all players to find which hold tokens on the removed card
      for (int playerId = 0; playerId < playersTokens.length; playerId++) {
        LinkedList<Integer> playerTokens = playersTokens[playerId];
        // for(LinkedList<Integer> playerTokens:playersTokens){
        // Iterating a certain player's tokens to find one that represents the slot
        for (int i = 0; i < playerTokens.size(); i++) {
          synchronized (playersLock[playerId]) {
            if (playerTokens.get(i) == slot) {
              playerTokens.remove(i);
              break; //breaks out of the player search loop, continues removing tokens from other players.
            }
          }
        }
      }
      env.ui.removeTokens(slotForUi(slot));
      env.ui.removeCard(slotForUi(slot));
    }
  }

    /**
     * Places a player token on a grid slot.
     * @param player - the player the token belongs to.
     * @param slot   - the slot on which to place the token.
     */
    public void placeToken(int player, int slot){
        this.lock.readLock().lock();
        // sync the slot and the player
        System.out.println("placed");
        synchronized(slotLocks[slot]) {
            synchronized(playersLock[player]){
                //checking if the player put already 3 tokens
                if(playersTokens[player].size()<env.config.featureSize){
                // adding the token to the playersToken array and to the table tokens
                tokens[slot].add(player);
                playersTokens[player].add(slot);
                //displaying in the ui
                env.ui.placeToken(player, slotForUi(slot));
                }
            }
         }
         this.lock.readLock().unlock();
        }
    

    /**
     * Removes a token of a player from a grid slot.
     * @param player - the player the token belongs to.
     * @param slot   - the slot from which to remove the token.
     * @return       - true iff a token was successfully removed.
     */
    public boolean removeToken(int player, int slot) {
        this.lock.readLock().lock();
        // sync on the slot and on the player lock so only 1 action per player and per slot
        synchronized(slotLocks[slot]){
            synchronized(playersLock[player]){
            int index=-1;
            int counter=0;
            // searching for the player token in the slot
            for(int playerId:tokens[slot]){
                if(playerId==player){
                    index=counter;
                    break;
                } 
                counter++;
            }
            if(index==-1){
                // if we didnt found a token on the player we return false
                this.lock.readLock().unlock();
                return false;
            } 
            // removing the token from the playerTokens list
            for(int i=0;i<playersTokens[player].size();i++){
                if(playersTokens[player].get(i)==slot) playersTokens[player].remove(i);
            }
            tokens[slot].remove(index);
            // updating in the ui
            env.ui.removeToken(player, slotForUi(slot));
           
        
        this.lock.readLock().unlock();
      
        return true;
      }
    }
  }

  // function to convert slot for Ui placement
  private int slotForUi(int gridSlot) {
    int row = (gridSlot) / env.config.columns;
    int col = gridSlot % env.config.columns;
    return row * env.config.columns + col;
  }

  // a function for the dealer to check a set from a certain player
  /**
   *
   * @param player
   * @pre playersToken[player].length = env.config.featuresize
   *
   */
  public int[] getSetCards(int player) {
    int[] cards = new int[env.config.featureSize];
    int counter = 0;
    synchronized (playersLock[player]) {
      for (int slot : playersTokens[player]) {
        synchronized (slotLocks[slot]) {
          cards[counter] = slotToCard[slot];
          counter++;
        }
      }
    }
    return cards;
  }

  // this function get all the players that has put thier token on a certain slot for use in remove cards in dealer class
  public LinkedList<Integer> getAllPlayersThatPlacedTokenOnSlot(int slot) {
    LinkedList<Integer> players = new LinkedList<>();
    // sync on the slot
    synchronized (slotLocks[slot]) {
      // adding all the players id that put thier token on the slot
      for (int player : tokens[slot]) {
        players.add(player);
      }
    }
    return players;
  }
  // public void removeAllCards(){
  //     try{
  //         semaphore.acquire();

  //     }
  // }
}
