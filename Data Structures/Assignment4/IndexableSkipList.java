public class IndexableSkipList extends AbstractSkipList {
    final protected double probability;
    public IndexableSkipList(double probability) {
        super();
        this.probability = probability;
    }

    @Override
    public Node find(int val) {
        int height = head.height();
        Node current = head;

        for (int level = height; level >= 0; level--) {
            while (current.getNext(level) != null && current.getNext(level).key() <= val) {
                current = current.getNext(level);
            }
        }
        
        return current;
    }


    @Override
    public int generateHeight() {
    	int height=1;
    	while (Math.random() > probability) {
    		//for example for probability 0.1: if the random number is bigger than 0.1 the height will increase, therefore there is a probability of 0.1 to end the process.
    		height++;
    	}
    	return height;
    }

    public int rank(int val) {
        throw new UnsupportedOperationException("Replace this by your implementation");
    }

    public int select(int index) {
        throw new UnsupportedOperationException("Replace this by your implementation");
    }
}
