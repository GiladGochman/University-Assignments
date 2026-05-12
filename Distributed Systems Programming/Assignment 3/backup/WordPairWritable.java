package com.assignment;

import org.apache.hadoop.io.Writable;
import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;

public class WordPairWritable implements Writable {
    private String word1;
    private String word2;

    // Default constructor (required for Hadoop)
    public WordPairWritable() {
    }

    // Parameterized constructor
    public WordPairWritable(String word1, String word2) {
        this.word1 = word1;
        this.word2 = word2;
    }

    // Implement the write method
    @Override
    public void write(DataOutput out) throws IOException {
        out.writeUTF(word1);
        out.writeUTF(word2);
    }

    // Implement the readFields method
    @Override
    public void readFields(DataInput in) throws IOException {
        word1 = in.readUTF();
        word2 = in.readUTF();
    }

    // Getters and setters
    public String getWord1() {
        return word1;
    }

    public void setWord1(String word1) {
        this.word1 = word1;
    }

    public String getWord2() {
        return word2;
    }

    public void setWord2(String word2) {
        this.word2 = word2;
    }

    @Override
    public String toString() {
        return word1 + "\t" + word2;
    }
}