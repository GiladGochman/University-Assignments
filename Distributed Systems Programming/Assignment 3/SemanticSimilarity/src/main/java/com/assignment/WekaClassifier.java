package com.assignment;

import weka.classifiers.Classifier;
import weka.classifiers.Evaluation;
import weka.classifiers.bayes.NaiveBayes;
import weka.core.Attribute;
import weka.core.DenseInstance;
import weka.core.Instances;
import weka.core.Instance;
import weka.core.FastVector;

import java.io.*;
import java.util.*;

/**
 * Weka-based classifier for determining semantic similarity between word pairs.
 */
public class WekaClassifier {

    private static final String VECTOR_FILE = "cooccurrence-vectors.txt"; // Output from MapReduce
    private static final String LABEL_FILE = "word-relatedness.txt"; // Labeled dataset (True/False)

    /**
     * Loads the labeled dataset of word pairs.
     * @return A map of word pairs to their similarity label (True/False).
     * @throws IOException If the file cannot be read.
     */
    private static Map<String, Boolean> loadWordRelatedness() throws IOException {
        Map<String, Boolean> relatednessMap = new HashMap<>();
        BufferedReader br = new BufferedReader(new FileReader(LABEL_FILE));
        String line;

        while ((line = br.readLine()) != null) {
            String[] tokens = line.split("\t");
            if (tokens.length != 3) continue;

            String wordPair = tokens[0] + "-" + tokens[1]; // Format: "word1-word2"
            boolean isRelated = tokens[2].equalsIgnoreCase("True");

            relatednessMap.put(wordPair, isRelated);
        }
        br.close();
        return relatednessMap;
    }

    /**
     * Loads the co-occurrence vectors and formats them for WEKA.
     * @param relatednessMap The ground truth labels for word pairs.
     * @return WEKA Instances dataset.
     * @throws IOException If the file cannot be read.
     */
    private static Instances loadDataset(Map<String, Boolean> relatednessMap) throws IOException {
        BufferedReader br = new BufferedReader(new FileReader(VECTOR_FILE));
        String line;

        // Define WEKA attributes
        FastVector attributes = new FastVector();
        for (int i = 0; i < 24; i++) { // 24 feature dimensions
            attributes.addElement(new Attribute("feature" + i));
        }

        // Class attribute (binary classification: similar / not similar)
        FastVector classValues = new FastVector(2);
        classValues.addElement("similar");
        classValues.addElement("not-similar");
        Attribute classAttribute = new Attribute("class", classValues);
        attributes.addElement(classAttribute);

        // Create dataset structure
        Instances dataset = new Instances("SemanticSimilarity", attributes, 10000);
        dataset.setClassIndex(attributes.size() - 1); // Last attribute is the class

        // Read vectors and add instances
        while ((line = br.readLine()) != null) {
            String[] parts = line.split("\t");
            if (parts.length != 2) continue;

            String word = parts[0];
            String[] features = parts[1].split(",");

            if (features.length != 24) continue; // Ensure correct feature size

            // Check if we have a ground truth label for this word
            if (!relatednessMap.containsKey(word)) continue;

            // Convert feature values to numeric form
            Instance instance = new DenseInstance(25); // 24 features + 1 class label
            for (int i = 0; i < 24; i++) {
                String[] featureParts = features[i].split(":");
                if (featureParts.length != 2) continue;
                instance.setValue((Attribute) attributes.elementAt(i), Double.parseDouble(featureParts[1]));
            }

            // Set class label
            instance.setValue(classAttribute, relatednessMap.get(word) ? "similar" : "not-similar");

            // Add instance to dataset
            dataset.add(instance);
        }
        br.close();
        return dataset;
    }

    /**
     * Trains and evaluates a classifier using 10-fold cross-validation.
     * @param dataset The dataset for training.
     * @throws Exception If the classifier training fails.
     */
    private static void trainAndEvaluate(Instances dataset) throws Exception {
        Classifier classifier = new NaiveBayes(); // Simple classifier for demonstration
        classifier.buildClassifier(dataset);

        // Perform 10-fold cross-validation
        Evaluation eval = new Evaluation(dataset);
        eval.crossValidateModel(classifier, dataset, 10, new Random(1));

        // Print evaluation results
        System.out.println("=== Classification Results ===");
        System.out.println("Precision: " + eval.precision(0));
        System.out.println("Recall: " + eval.recall(0));
        System.out.println("F1-score: " + eval.fMeasure(0));
    }

    public static void main(String[] args) {
        try {
            System.out.println("Loading word relatedness dataset...");
            Map<String, Boolean> relatednessMap = loadWordRelatedness();

            System.out.println("Loading co-occurrence vectors...");
            Instances dataset = loadDataset(relatednessMap);

            System.out.println("Training and evaluating the classifier...");
            trainAndEvaluate(dataset);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
