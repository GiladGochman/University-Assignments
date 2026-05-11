
public class SkipListExperimentUtils {
    public static double measureLevels(double p, int x) {
    	IndexableSkipList test = new IndexableSkipList(p);
    	double sum = 0;
    	for (int i = 0; i < x; i++) {
			sum += test.generateHeight();
		}
    	double avg= sum / x;
    	return avg;
    }

    /*
     * The experiment should be performed according to these steps:
     * 1. Create the empty Data-Structure.
     * 2. Generate a randomly ordered list (or array) of items to insert.
     *
     * 3. Save the start time of the experiment (notice that you should not
     *    include the previous steps in the time measurement of this experiment).
     * 4. Perform the insertions according to the list/array from item 2.
     * 5. Save the end time of the experiment.
     *
     * 6. Return the DS and the difference between the times from 3 and 5.
     */
    public static Pair<AbstractSkipList, Double> measureInsertions(double p, int size) {
    	IndexableSkipList myISL = new IndexableSkipList(p);
    	int[] toInsert = makeRandomArray(size);
    	long startTime = System.nanoTime();
    	for (int i = 0; i < toInsert.length; i++) { //toInsert.length == size+1
    		myISL.insert(toInsert[i] * 2); // inserts the values times 2 { 0, 2, ..., 2*size}
		}
    	long endTime = System.nanoTime();
    	long avgDuration = (endTime-startTime)/(size+1);
    	Pair res = new Pair(myISL,avgDuration);
    	return res;
    }
    
    private static int[] makeRandomArray(int size) {
    	int[] array = new int[size + 1];

        // Make values bank with values 0, 1, ..., size
        for (int i = 0; i <= size; i++) {
            array[i] = i;
        }

        // Rearrange values bank array
        for (int i = array.length - 1; i > 0; i--) {
            int j = (int) (Math.random() * (i + 1));
            int temp = array[i];
            array[i] = array[j];
            array[j] = temp;
        }
        return array;
    }

    public static double measureSearch(AbstractSkipList skipList, int size) {
    	int[] toSearch = makeRandomArray(2*size);
    	
    	long startTime = System.nanoTime();
    	for (int i = 0; i < toSearch.length; i++) { //toSearch.length == 2*size+1
    		skipList.search(toSearch[i]);
		}
    	long endTime = System.nanoTime();
    	long avgDuration = (endTime-startTime)/toSearch.length;
    	return avgDuration;
    }

    public static double measureDeletions(AbstractSkipList skipList, int size) {
    	int[] toSearch = makeRandomArray(size);
    	AbstractSkipList.Node[] nodesToDelete = new AbstractSkipList.Node[size+1];

    	for (int i = 0; i < toSearch.length; i++) {
    		nodesToDelete[i] = skipList.find(toSearch[i]*2);
		}
    	long startTime = System.nanoTime();
    	for (int i = 0; i < nodesToDelete.length; i++) {
    		skipList.delete(nodesToDelete[i]);
		}
    	long endTime = System.nanoTime();
    	long avgDuration = (endTime-startTime)/nodesToDelete.length;
    	return avgDuration;
    }

    public static void main(String[] args) {
    	
//    	**********2.2.2 Test:*************
    	System.out.println("**********2.2.2 Test:*************");
    	final int experiments=5;
    	final double probability=0.9;
    	final double expected=1/probability;
    	System.out.println("Expected: "+expected);
        int[] Xs = {10, 100, 1000, 10000};
        double[] avgHeights= new double[experiments];
        for (int i = 0; i < Xs.length; i++) {
            double sumAvgs =0;

        	System.out.println("Testing for: "+Xs[i]);

        	for (int j = 0; j < experiments; j++) {
            	avgHeights[j] = measureLevels(probability, Xs[i]);
            	System.out.println("avg"+j+": "+avgHeights[j]);
            	sumAvgs += avgHeights[j];
			}
        	
        	System.out.println("Average  delta: "+Math.abs( (sumAvgs/experiments)-expected)); 
        	
		}
        
//      **************2.2.3 Test:***************
    	System.out.println("**********2.2.3 Test:*************");
        int[] sizes = {1000 , 2500, 5000, 10000, 15000, 20000, 50000};
        for (int index = 0; index < sizes.length; index++) {
        	int size = sizes[index];
        	System.out.println("SIZE: " + size);
        	long sumAvgInsertTime=0;
        	double sumAvgSearchTime=0;
        	double sumAvgDeletionTime=0;
        	for (int i = 0; i < 30; i++) {
        		Pair a = measureInsertions(0.9, size); // also creates skiplist
        		sumAvgInsertTime += (long)a.second();
        		sumAvgSearchTime += measureSearch((AbstractSkipList)a.first(),size);
        		sumAvgDeletionTime += measureDeletions((AbstractSkipList)a.first(),size);
    		}
            System.out.println("Average Insert Time: "+sumAvgInsertTime/30);
            System.out.println("Average Search Time: "+sumAvgSearchTime/30);
            System.out.println("Average Deletion Time: "+sumAvgDeletionTime/30);
		}

    }
}
