package com.assignment;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.fs.Path;

public class MapReduceJob {
    public static void main(String[] args) throws Exception {
        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf, "Semantic Similarity");

        // Configure job: set mapper, reducer, input/output paths
        // Handle 10% and 100% corpus runs
    }
}