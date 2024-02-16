package bguspl.set.ex;

import bguspl.set.Env;
import java.util.Arrays;
import java.util.LinkedList;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.Semaphore;
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

    public Semaphore semaphore;


    

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
        this.semaphore = new Semaphore(1,true);
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
        this.semaphore = new Semaphore(1,true);
    }

    /**
     * This method prints all possible legal sets of cards that are currently on the table.
     */
    public void hints() {
        List<Integer> deck = Arrays.stream(slotToCard).filter(Objects::nonNull).collect(Collectors.toList());
        env.util.findSets(deck, Integer.MAX_VALUE).forEach(set -> {
            StringBuilder sb = new StringBuilder().append("Hint: Set found: ");
            List<Integer> slots = Arrays.stream(set).mapToObj(card -> cardToSlot[card]).sorted().collect(Collectors.toList());
            int[][] features = env.util.cardsToFeatures(set);
            System.out.println(sb.append("slots: ").append(slots).append(" features: ").append(Arrays.deepToString(features)));
        });
    }

    /**
     * Count the number of cards currently on the table.
     *
     * @return - the number of cards on the table.
     */
    public int countCards() {
        int cards = 0;
        for (Integer card : slotToCard)
            if (card != null)
                ++cards;
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
        try {
            semaphore.acquire();
            cardToSlot[card] = slot;
            slotToCard[slot] = card;
            env.ui.placeCard(card, slotForUi(slot));
        } catch (InterruptedException ignored) {
        } finally {
            semaphore.release();
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
        try{
            semaphore.acquire();
            int card = slotToCard[slot];
            cardToSlot[card] = null;
            slotToCard[slot] = null;
            tokens[slot] = new LinkedList<Integer>();
            env.ui.removeTokens(slotForUi(slot));
            env.ui.removeCard(slotForUi(slot));
        } catch(InterruptedException ignored) {};
        semaphore.release();
    }

    /**
     * Places a player token on a grid slot.
     * @param player - the player the token belongs to.
     * @param slot   - the slot on which to place the token.
     */
    public void placeToken(int player, int slot) {
        try{
            semaphore.acquire();
            tokens[slot].add(player);
            env.ui.placeToken(player, slotForUi(slot));
        } catch(InterruptedException ignored){};
        semaphore.release();
        
    }

    /**
     * Removes a token of a player from a grid slot.
     * @param player - the player the token belongs to.
     * @param slot   - the slot from which to remove the token.
     * @return       - true iff a token was successfully removed.
     */
    public boolean removeToken(int player, int slot) {
        try {
            semaphore.acquire();
            int index=-1;
            int counter=0;
            for(int playerId:tokens[slot]){
                if(playerId==player){
                    index=counter;
                    break;
                } 
                counter++;
            }
            if(index==-1) return false;
            tokens[slot].remove(index);
            env.ui.removeToken(player, slotForUi(slot));
           
        } catch (InterruptedException ignored) {
           
        } 
        semaphore.release();
        return true;
    }
    // function to convert slot for Ui placement
    private int slotForUi(int gridSlot){
        int row = (gridSlot)/env.config.columns;
        int col = gridSlot % env.config.columns;
        return row*env.config.columns+col;
    }

    // public void removeAllCards(){
    //     try{
    //         semaphore.acquire();
           
    //     }
    // }
}
