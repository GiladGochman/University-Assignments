import java.io.*;
import java.util.*;

/**
 * Evaluation class for calculating Precision, Recall, and F1-score manually.
 */
public class Evaluation {

    private static final String PREDICTIONS_FILE = "classified-pairs.txt"; // Output from WekaClassifier
    private static final String LABEL_FILE = "word-relatedness.txt"; // Ground truth labels
    private static final String REPORT_FILE = "evaluation-results.txt"; // Output file

    /**
     * Loads the labeled dataset (ground truth word similarity labels).
     * @return A map of word pairs to their similarity label (True/False).
     * @throws IOException If the file cannot be read.
     */
    private static Map<String, Boolean> loadGroundTruth() throws IOException {
        Map<String, Boolean> groundTruth = new HashMap<>();
        BufferedReader br = new BufferedReader(new FileReader(LABEL_FILE));
        String line;

        while ((line = br.readLine()) != null) {
            String[] tokens = line.split("\t");
            if (tokens.length != 3) continue;

            String wordPair = tokens[0] + "-" + tokens[1]; // Format: "word1-word2"
            boolean isRelated = tokens[2].equalsIgnoreCase("True");

            groundTruth.put(wordPair, isRelated);
        }
        br.close();
        return groundTruth;
    }

    /**
     * Loads the predicted word similarity classifications.
     * @return A map of word pairs to their predicted similarity label (True/False).
     * @throws IOException If the file cannot be read.
     */
    private static Map<String, Boolean> loadPredictions() throws IOException {
        Map<String, Boolean> predictions = new HashMap<>();
        BufferedReader br = new BufferedReader(new FileReader(PREDICTIONS_FILE));
        String line;

        while ((line = br.readLine()) != null) {
            String[] tokens = line.split("\t");
            if (tokens.length != 2) continue;

            String wordPair = tokens[0]; // Format: "word1-word2"
            boolean predictedSimilar = tokens[1].equalsIgnoreCase("similar");

            predictions.put(wordPair, predictedSimilar);
        }
        br.close();
        return predictions;
    }

    /**
     * Computes Precision, Recall, and F1-score.
     * @param groundTruth The actual similarity labels.
     * @param predictions The predicted similarity labels.
     * @throws IOException If the report file cannot be written.
     */
    private static void computeMetrics(Map<String, Boolean> groundTruth, Map<String, Boolean> predictions) throws IOException {
        int TP = 0, FP = 0, FN = 0, TN = 0;

        for (String wordPair : groundTruth.keySet()) {
            boolean actual = groundTruth.get(wordPair);
            boolean predicted = predictions.getOrDefault(wordPair, false); // Default to False if missing

            if (actual && predicted) TP++; // True Positive
            else if (!actual && predicted) FP++; // False Positive
            else if (actual && !predicted) FN++; // False Negative
            else TN++; // True Negative
        }

        double precision = (TP + FP) > 0 ? (double) TP / (TP + FP) : 0;
        double recall = (TP + FN) > 0 ? (double) TP / (TP + FN) : 0;
        double f1 = (precision + recall) > 0 ? 2 * (precision * recall) / (precision + recall) : 0;

        // Print results
        System.out.println("=== Evaluation Metrics ===");
        System.out.println("Precision: " + precision);
        System.out.println("Recall: " + recall);
        System.out.println("F1-score: " + f1);

        // Write results to file
        BufferedWriter bw = new BufferedWriter(new FileWriter(REPORT_FILE));
        bw.write("Precision: " + precision + "\n");
        bw.write("Recall: " + recall + "\n");
        bw.write("F1-score: " + f1 + "\n");
        bw.close();
    }

    public static void main(String[] args) {
        try {
            System.out.println("Loading ground truth labels...");
            Map<String, Boolean> groundTruth = loadGroundTruth();

            System.out.println("Loading classifier predictions...");
            Map<String, Boolean> predictions = loadPredictions();

            System.out.println("Computing evaluation metrics...");
            computeMetrics(groundTruth, predictions);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
