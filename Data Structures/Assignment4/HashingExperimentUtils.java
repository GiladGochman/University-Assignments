import java.util.Collections;
import java.util.Random;

public class HashingExperimentUtils {
    final private static int k = 16;

    public static Pair<Double, Double> measureOperationsChained(double maxLoadFactor) {
        // Build a hash table of size 2^16
        ProbingHashTable<Integer, Integer> table = new ProbingHashTable<>(new ModularHash(), k, maxLoadFactor);

        // Insert items to fill the table up to the maximal load factor (without causing rehashing!)
        int numItems = (int) (Math.pow(2, k) * maxLoadFactor);
        for (int i = 0; i < numItems; i++) {
            table.insert(i, i);
        }

        // Perform 2^16 * max-load-factor searches - where 50% of all searches are successful and the rest are unsuccessful.
        int numSearches = (int) (Math.pow(2, k) * maxLoadFactor);
        int numSuccessfulSearches = numSearches / 2;
        int numUnsuccessfulSearches = numSearches - numSuccessfulSearches;

        // Start the timer for insertion
        long startInsertion = System.nanoTime();

        // Perform the successful searches
        for (int i = 0; i < numSuccessfulSearches; i++) {
            table.search(i);
        }

        // Perform the unsuccessful searches
        for (int i = 0; i < numUnsuccessfulSearches; i++) {
            table.search(i + numItems);
        }

        // Stop the timer for insertion
        long endInsertion = System.nanoTime();

        // Calculate the average insertion time
        double averageInsertionTime = (endInsertion - startInsertion) / (double) numItems;

        // Start the timer for search
        long startSearch = System.nanoTime();

        // Perform the successful searches
        for (int i = 0; i < numSuccessfulSearches; i++) {
            table.search(i);
        }

        // Perform the unsuccessful searches
        for (int i = 0; i < numUnsuccessfulSearches; i++) {
            table.search(i + numItems);
        }

        // Stop the timer for search
        long endSearch = System.nanoTime();

        // Calculate the average search time
        double averageSearchTime = (endSearch - startSearch) / (double) numSearches;

        // Return a Pair with the average insertion and search times
        return new Pair<>(averageInsertionTime, averageSearchTime);
    }

    public static void main(String[] args) {
        double[] maxLoadFactors = { 0.5, 0.75, 0.875, 0.9375 };
        double[] Icounters = {0,0,0,0,0};
        double[] Scounters = {0,0,0,0,0};
        int i=0;
        for (double maxLoadFactor : maxLoadFactors) {
        	for (int j=0;j<30;j++) {
        		Pair<Double, Double> measurements = measureOperationsChained(maxLoadFactor);
        		System.out.println("Max Load Factor: " + maxLoadFactor);
        		System.out.println("Average Insertion Time: " + measurements.first() + " ns");
        		Icounters[i]=Icounters[i]+measurements.first() ;
        		System.out.println("Average Search Time: " + measurements.second() + " ns");
        		Scounters[i]=Scounters[i]+measurements.second() ;
        		System.out.println();}
        		i++;
        }
        for (int k=0 ; k<4;k++) {
        	System.out.println(Icounters[k]/30);

        	System.out.println(Scounters[k]/30);
        }
    }
}
