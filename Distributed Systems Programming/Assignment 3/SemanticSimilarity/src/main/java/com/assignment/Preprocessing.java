package com.assignment;
import java.io.*;
import java.util.*;
import java.util.regex.*;

public class Preprocessing {

    private static final Set<String> STOP_WORDS = new HashSet<>(Arrays.asList(
        "a", "an", "the", "and", "but", "if", "or", "as", "is", "to", "of", "for", "on", "with", "in", "at", "by", "from", "about"
    ));

    /**
     * Tokenizes the input text into words, removing non-alphabetic characters.
     * @param text The input text.
     * @return A list of tokens (words).
     */
    public static List<String> tokenize(String text) {
        // Convert to lowercase and split on non-word characters
        String[] words = text.toLowerCase().split("\\W+");
        List<String> tokens = new ArrayList<>();
        for (String word : words) {
            if (!word.isEmpty()) {
                tokens.add(word);
            }
        }
        return tokens;
    }

    /**
     * Stems the input word. (Basic stemming algorithm)
     * @param word The word to stem.
     * @return The stemmed word.
     */
    public static String stem(String word) {
        // Basic suffix stripping (could be extended with Porter Stemmer or another algorithm)
        if (word.endsWith("ing")) {
            return word.substring(0, word.length() - 3);
        } else if (word.endsWith("ed")) {
            return word.substring(0, word.length() - 2);
        } else if (word.endsWith("s")) {
            return word.substring(0, word.length() - 1);
        }
        return word;
    }

    /**
     * Filters out stop words from the list of tokens.
     * @param tokens The list of tokens.
     * @return A list of tokens without stop words.
     */
    public static List<String> filterStopWords(List<String> tokens) {
        List<String> filteredTokens = new ArrayList<>();
        for (String token : tokens) {
            if (!STOP_WORDS.contains(token)) {
                filteredTokens.add(token);
            }
        }
        return filteredTokens;
    }

    /**
     * Preprocesses the input text by tokenizing, stemming, and filtering stop words.
     * @param text The input text.
     * @return A list of preprocessed tokens.
     */
    public static List<String> preprocess(String text) {
        List<String> tokens = tokenize(text);
        tokens = filterStopWords(tokens);
        List<String> stemmedTokens = new ArrayList<>();
        for (String token : tokens) {
            stemmedTokens.add(stem(token));
        }
        return stemmedTokens;
    }

    /**
     * Reads the input file and applies preprocessing on each line.
     * @param inputFile The file to read.
     * @param outputFile The file to write the preprocessed data.
     * @throws IOException If file I/O fails.
     */
    public static void preprocessFile(String inputFile, String outputFile) throws IOException {
        BufferedReader reader = new BufferedReader(new FileReader(inputFile));
        BufferedWriter writer = new BufferedWriter(new FileWriter(outputFile));

        String line;
        while ((line = reader.readLine()) != null) {
            List<String> preprocessedTokens = preprocess(line);
            writer.write(String.join(" ", preprocessedTokens));
            writer.newLine();
        }

        reader.close();
        writer.close();
    }

    public static void main(String[] args) {
        if (args.length < 2) {
            System.err.println("Usage: java Preprocessing <input file> <output file>");
            System.exit(-1);
        }

        try {
            preprocessFile(args[0], args[1]);
            System.out.println("Preprocessing completed and saved to " + args[1]);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
