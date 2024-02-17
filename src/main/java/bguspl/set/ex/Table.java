package bguspl.set.ex;

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

    public LinkedList<Integer>[] playersTokens;

    public Object [] slotLocks;

    public Object [] playersLock;


    

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
        this.playersTokens=new LinkedList[env.config.players];
        for(int i=0;i<env.config.players;i++){
            playersTokens[i] = new LinkedList<Integer>();
        }
        this.slotLocks = new Object[env.config.tableSize];
        for(int i=0;i<env.config.tableSize;i++){
            slotLocks[i] = new Object();
        }

        this.playersLock = new Object[env.config.players];
        for(int i=0; i<env.config.players;i++){
            playersLock[i] = new Object();
        }
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
        synchronized(slotLocks[slot]){
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
        synchronized(slotLocks[slot]){
            int card = slotToCard[slot];
            cardToSlot[card] = null;
            slotToCard[slot] = null;
            tokens[slot] = new LinkedList<Integer>();
            for(LinkedList<Integer> playerTokens:playersTokens){
                for(int i=0;i<playerTokens.size();i++){
                    synchronized(playersLock[i]){
                    if(playerTokens.get(i)==slot){
                        playerTokens.remove(i);
                        break;
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
        synchronized(slotLocks[slot]) {
            synchronized(playersLock[player]){
                if(playersTokens[player].size()<env.config.featureSize)
                tokens[slot].add(player);
                playersTokens[player].add(slot);
                env.ui.placeToken(player, slotForUi(slot));
            }
         }
        }
    

    /**
     * Removes a token of a player from a grid slot.
     * @param player - the player the token belongs to.
     * @param slot   - the slot from which to remove the token.
     * @return       - true iff a token was successfully removed.
     */
    public boolean removeToken(int player, int slot) {
        synchronized(slotLocks[slot]){
            synchronized(playersLock[player]){
            int index=-1;
            int counter=0;
            for(int playerId:tokens[slot]){
                if(playerId==player){
                    index=counter;
                    break;
                } 
                counter++;
            }
            if(index==-1){
                
                return false;
            } 
            for(int i=0;i<playersTokens[player].size();i++){
                if(playersTokens[player].get(i)==slot) playersTokens[player].remove(i);
            }
            tokens[slot].remove(index);
            
            env.ui.removeToken(player, slotForUi(slot));
           
        
       
        return true;
        }
    }
    }
    // function to convert slot for Ui placement
    private int slotForUi(int gridSlot){
        int row = (gridSlot)/env.config.columns;
        int col = gridSlot % env.config.columns;
        return row*env.config.columns+col;
    }

    public int [] getSetCards(int player){
        int [] cards = new int[env.config.featureSize];
        int counter=0;
        synchronized(playersLock[player]){
            for(int slot:playersTokens[player]){
                synchronized(slotLocks[slot]){
                    cards[counter] = slotToCard[slot];
                    counter++;
                }
            }
        }
        return cards;
    }

    // public void removeAllCards(){
    //     try{
    //         semaphore.acquire();
           
    //     }
    // }
}
