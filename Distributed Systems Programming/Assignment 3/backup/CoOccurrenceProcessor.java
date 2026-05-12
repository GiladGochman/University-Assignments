package com.assignment;
import java.io.*;
import java.util.*;
import java.util.zip.GZIPInputStream;
import opennlp.tools.stemmer.PorterStemmer;

public class CoOccurrenceProcessor {
    private static final String FILE_PATH = "path/to/google-syntactic-ngrams.gz";

    public static void main(String[] args) {
        Map<String, Map<String, Integer>> coOccurrence = new HashMap<>();
        PorterStemmer stemmer = new PorterStemmer();

        try (BufferedReader reader = new BufferedReader(new InputStreamReader(new GZIPInputStream(new FileInputStream(FILE_PATH))))) {
            String line;
            while ((line = reader.readLine()) != null) {
                String[] parts = line.split("\t");
                if (parts.length < 3) continue;

                String headWord = stemmer.stem(parts[0]);
                String depWord = stemmer.stem(parts[1]);
                String relation = parts[2];

                String feature = depWord + "-" + relation;

                coOccurrence.putIfAbsent(headWord, new HashMap<>());
                coOccurrence.get(headWord).put(feature, coOccurrence.get(headWord).getOrDefault(feature, 0) + 1);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }

        // הצגת דוגמאות
        coOccurrence.entrySet().stream().limit(5).forEach(entry -> {
            System.out.println(entry.getKey() + ": " + entry.getValue());
        });
    }
}
