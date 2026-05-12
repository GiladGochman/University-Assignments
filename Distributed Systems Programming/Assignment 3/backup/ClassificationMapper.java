package com.assignment;

import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;
import java.io.IOException;

public class ClassificationMapper extends Mapper<Object, Text, Text, Text> {
    // Prepare word pair feature vectors for classification
    @Override
    protected void map(Object key, Text value, Context context)
            throws IOException, InterruptedException {
        // Read word-relatedness.txt
        // Generate 24-dimensional feature vectors
    }
}