package org.example;

import com.amazonaws.auth.DefaultAWSCredentialsProviderChain;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.model.ListObjectsV2Request;
import com.amazonaws.services.s3.model.ListObjectsV2Result;
import com.amazonaws.services.s3.model.S3Object;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.*;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.io.WritableComparable;
import org.apache.hadoop.io.WritableComparator;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Partitioner;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.HashMap;

public class Step5 {

    private static class MyMapper extends Mapper<LongWritable, Text, Text, Text> {
        public void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
            String[] parts = value.toString().split("\t");
            context.write(new Text(parts[0]), new Text(parts[1]));
        }
    }

    public static class MyReducer extends Reducer<Text, Text, Text, Text> {
        private static long totalWords = 0L;

        public void setup(Context context) throws IOException {


            // Create an S3 client using the default credentials provider
            AmazonS3 s3Client = AmazonS3ClientBuilder.standard()
                    .withCredentials(new DefaultAWSCredentialsProviderChain())
                    .build();

            // Specify the bucket name and folder path (without "s3://")
            String bucketName = "lielaytoutputs";
            String folderPrefix = "step1/";

            // Create a request to list objects in the specified folder
            ListObjectsV2Request listObjects = new ListObjectsV2Request()
                    .withBucketName(bucketName)
                    .withPrefix(folderPrefix);

            // Get the list of objects in the folder
            ListObjectsV2Result result = s3Client.listObjectsV2(listObjects);

            // Iterate over the files in the folder
            for (S3ObjectSummary objectSummary : result.getObjectSummaries()) {
                String fileKey = objectSummary.getKey();
                System.out.println("Processing file: " + fileKey);

                // Retrieve the S3 object (file) content
                S3Object s3Object = s3Client.getObject(bucketName, fileKey);
                try (BufferedReader reader = new BufferedReader(new InputStreamReader(s3Object.getObjectContent()))) {
                    String line;
                    // Read the file line by line
                    String[] extracted;
                    while ((line = reader.readLine()) != null) {
                        extracted = line.split("\t");  // Process each line (e.g., print it)
                        if(extracted[0].equals("*")) {
                            totalWords = Integer.parseInt(extracted[1]);
                            return;
                        }
                    }
                } catch (IOException e) {
                    System.err.println("Error reading file " + fileKey + ": " + e.getMessage());
                }
            }


        }

        public void reduce(Text key, Iterable<Text> values, Context context) throws IOException, InterruptedException {
            try {


                String[] words = key.toString().split(" ");
                String word1 = words[0];
                String word2 = words[1];
                String word3 = words[2];

                double N1=0.0;
                double N2 = 0.0;
                double N3 = 0.0;
                double C0 = totalWords;
                double C1 = 0.0;
                double C2 = 0.0;
                double K2 = 0.0;
                double K3 = 0.0;

                for(Text value : values) {

                    String[] vs = value.toString().split(" ");

                    N3 = Double.parseDouble(vs[0]);

                    if(vs[1].equals(word1) && vs[2].equals(word2)) {
                        C2 = Double.parseDouble(vs[3]);
                        K3 = (Math.log(N3+1)+1)/(Math.log(N3+1)+2);
                    }

                    if(vs[1].equals(word2) && vs[2].equals(word3)) {
                        N2 = Double.parseDouble(vs[3]);
                        K2 = (Math.log(N2+1)+1)/(Math.log(N2+1)+2);
                    }

                    if(vs[4].equals(word2))
                        C1 = Double.parseDouble(vs[5]);

                    if(vs[4].equals(word3))
                        N1 = Double.parseDouble(vs[5]);

                }

                System.out.println(N1);
                System.out.println(N2);
                System.out.println(N3);
                System.out.println(C0);
                System.out.println(C1);
                System.out.println(C2);
                System.out.println(K2);
                System.out.println(K3);

                Double p = (K3) * (N3/C2) + (1-K3) * (K2) * (N2/C1) + (1-K3) * (1-K2) * (N1/C0);
                if(p>=0 && p<=1)
                    context.write(key,new Text(p.toString()));
                else
                    System.out.println("Probability is wrong!");

            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

    private static class MyPartitioner extends Partitioner<Text, Text> {
        public int getPartition(Text key, Text value, int numPartitions) {
            return Math.abs(key.hashCode()) % numPartitions;
        }
    }


    ////////////////////final MapReduce/////////////////////////////
    private static class SortMapper extends Mapper<LongWritable, Text, Text, Text> {
        public void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
            String[] parts = value.toString().split("\t");
            Text newKey = new Text(String.format("%s %s", parts[0], parts[1]));
            Text emptyValue = new Text("");
            context.write(newKey, emptyValue);
        }
    }

    private static class SortReducer extends Reducer<Text, Text, Text, Text> {
        @Override
        protected void reduce(Text key, Iterable<Text> values, Context context) throws IOException, InterruptedException {
            String keyString = key.toString();
            Text outputKey = new Text(keyString);
            Text emptyValue = new Text("");
            context.write(outputKey, emptyValue);
        }
    }

    private static class SortComparator extends WritableComparator {
        protected SortComparator() {
            super(Text.class, true);
        }

        @Override
        public int compare(WritableComparable key1, WritableComparable key2) {
            String[] parts1 = key1.toString().split(" ");
            String[] parts2 = key2.toString().split(" ");

            if (parts1[0].equals(parts2[0]) && parts1[1].equals(parts2[1])) {
                return Double.parseDouble(parts1[3]) > Double.parseDouble(parts2[3]) ? -1 : 1;
            }
            return key1.toString().compareTo(key2.toString());
        }
    }

    ///////////////////////////////////////////////////////////////




    public static void main(String[] args) throws Exception {

        System.out.println("running first job.....");
        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf, "Compute Probability");
        job.setJarByClass(Step5.class);
        job.setMapperClass(MyMapper.class);
        job.setReducerClass(MyReducer.class);
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);
        job.setPartitionerClass(MyPartitioner.class);
        job.setInputFormatClass(TextInputFormat.class);
        job.setOutputFormatClass(TextOutputFormat.class);

        FileInputFormat.addInputPath(job, new Path("s3://lielaytoutputs/step4/"));
        FileOutputFormat.setOutputPath(job, new Path("s3://lielaytoutputs/step5/"));

        job.waitForCompletion(true);
        System.out.println("first job is finished!");

        //////////// second job ///////////
        System.out.println("running second job and final....");
        Configuration conf2 = new Configuration();
        Job job2 = Job.getInstance(conf, "sorting");
        job2.setJarByClass(Step5.class);
        job2.setOutputKeyClass(Text.class);
        job2.setOutputValueClass(Text.class);
        job2.setMapperClass(SortMapper.class);
        job2.setSortComparatorClass(SortComparator.class);
        job2.setReducerClass(SortReducer.class);
        job2.setNumReduceTasks(1);
        job2.setInputFormatClass(TextInputFormat.class);
        job2.setOutputFormatClass(TextOutputFormat.class);

        FileInputFormat.addInputPath(job2, new Path("s3://lielaytoutputs/step5/"));
        FileOutputFormat.setOutputPath(job2, new Path("s3://lielaytoutputs/results"));
        System.out.println("second job is finished!");
        System.exit(job2.waitForCompletion(true) ? 0 : 1);
        //////////////////////////////////
    }
}

