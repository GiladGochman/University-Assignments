package com.assignment;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

/**
 * Hadoop MapReduce job to generate co-occurrence vectors for words
 * using syntactic dependencies from Google Syntactic N-Grams.
 */
public class CooccurrenceVector {

    /**
     * Mapper class: Extracts word dependencies and emits (word, dependency) key-value pairs.
     */
    public static class CooccurrenceMapper extends Mapper<LongWritable, Text, Text, Text> {
        public void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
            String line = value.toString();
            String[] tokens = line.split("\t");

            if (tokens.length < 3) return; // Ensure valid format

            String targetWord = tokens[0];  // Main word
            String contextWord = tokens[1]; // Co-occurring word
            String dependencyLabel = tokens[2]; // Dependency relation

            // Emit (target_word, context_word-dependency)
            context.write(new Text(targetWord), new Text(contextWord + "-" + dependencyLabel));
        }
    }

    /**
     * Reducer class: Aggregates dependencies to form a feature vector for each word.
     */
    public static class CooccurrenceReducer extends Reducer<Text, Text, Text, Text> {
        public void reduce(Text key, Iterable<Text> values, Context context) throws IOException, InterruptedException {
            Map<String, Integer> vector = new HashMap<>();

            // Count occurrences of each (context_word-dependency) pair
            for (Text val : values) {
                String feature = val.toString();
                vector.put(feature, vector.getOrDefault(feature, 0) + 1);
            }

            // Convert vector to string format: feature1:count, feature2:count, ...
            StringBuilder vectorStr = new StringBuilder();
            for (Map.Entry<String, Integer> entry : vector.entrySet()) {
                vectorStr.append(entry.getKey()).append(":").append(entry.getValue()).append(",");
            }

            // Remove last comma and write output
            if (vectorStr.length() > 0) vectorStr.setLength(vectorStr.length() - 1);
            context.write(key, new Text(vectorStr.toString()));
        }
    }

    /**
     * Main method: Configures and runs the Hadoop job.
     */
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("Usage: CooccurrenceVector <input path> <output path>");
            System.exit(-1);
        }

        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf, "Cooccurrence Vector Generator");

        job.setJarByClass(CooccurrenceVector.class);
        job.setMapperClass(CooccurrenceMapper.class);
        job.setReducerClass(CooccurrenceReducer.class);

        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);

        FileInputFormat.addInputPath(job, new Path(args[0]));
        FileOutputFormat.setOutputPath(job, new Path(args[1]));

        System.exit(job.waitForCompletion(true) ? 0 : 1);
    }
}
