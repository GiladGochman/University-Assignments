package org.example;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Partitioner;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.MultipleInputs;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class Step4 {




    /////////////test of first job///////////////

    private static class BigramMapper extends Mapper<LongWritable, Text, Text, Text> {
        @Override
        public void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {

            String[] keyValue = value.toString().split("\t");
            String[] words = keyValue[0].split(" ");
            String word1 = words[0];
            String occurrences = keyValue[1];

            Text outKey = new Text(String.format("%s",word1));

            if(words.length > 1) {

                String word2 = words[1];
                Text outKey2 = new Text(String.format("%s",word2));
                Text outVal = new Text(String.format("%s %s %s",word1,word2,occurrences));

                context.write(outKey, outVal);
                context.write(outKey2, outVal);

            }
            else if(!word1.equals("*"))
                context.write(outKey, new Text(occurrences));

        }
    }

    public static class firstJobReducer extends Reducer<Text, Text, Text, Text> {
        @Override
        protected void reduce(Text key, Iterable<Text> values, Context context) throws IOException, InterruptedException {


            List<String> valuesList = new ArrayList<>();

            int singleOccurrence = 0;
            String[] words = key.toString().split(" ");
            String word1 = words[0];

            boolean found = false;

            for(Text value : values) {

                String[] vs = value.toString().split(" ");

                if(!found){

                    if(vs.length!=1)
                        valuesList.add(value.toString());
                    else {

                        singleOccurrence = Integer.parseInt(vs[0]);

                        for(String pair : valuesList) {

                            String[] extractedPair = pair.split(" ");
                            Text outKey = new Text(String.format("%s %s",extractedPair[0],extractedPair[1]));
                            Text outValue = new Text(String.format("%s %s %d", extractedPair[2],word1,singleOccurrence));
                            context.write(outKey, outValue);

                        }

                        valuesList.clear();
                        found = true;

                    }
                }
                else if(vs.length!=1) {

                    String[] extractedPair = value.toString().split(" ");
                    Text outKey = new Text(String.format("%s %s",extractedPair[0],extractedPair[1]));
                    Text outValue = new Text(String.format("%s %s %d", extractedPair[2],word1,singleOccurrence));
                    context.write(outKey, outValue);


                }
            }
        }
    }

    private static class firstJobPartitioner extends Partitioner<Text, Text> {
        @Override
        public int getPartition(Text key, Text value, int numPartitions) {
            return Math.abs(key.hashCode()) % numPartitions;
        }
    }

    ////////////////////////////////////////////



    //////////////test of second job/////////////

    private static class TrigramMapper extends Mapper<LongWritable, Text, Text, Text> {
        @Override
        public void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {

            String[] keyValue = value.toString().split("\t");
            String[] words = keyValue[0].split(" ");
            String word1 = words[0];
            String word2 = words[1];


            String[] vals = keyValue[1].split(" ");
            String pairOccurrences = vals[0];

            Text outKey = new Text(String.format("%s %s", word1, word2));

            if (words.length > 2) {

                String word3 = words[2];

                Text outKey2 = new Text(String.format("%s %s", word2, word3));
                Text outVal = new Text(String.format("%s %s %s %s", word1, word2, word3, keyValue[1]));

                context.write(outKey, outVal);
                context.write(outKey2, outVal);

            } else {
                String[] values = keyValue[1].split(" ");
                String eitherWord = values[1];
                String singleOccurrence = values[2];
                context.write(outKey, new Text(String.format("%s %s %s", pairOccurrences,eitherWord,singleOccurrence)));
            }
        }
    }

    public static class AggregationReducer extends Reducer<Text, Text, Text, Text> {
        @Override
        protected void reduce(Text key, Iterable<Text> values, Context context) throws IOException, InterruptedException {

            List<String> valuesList = new ArrayList<>();

            int pairOccurences = 0;
            String[] words = key.toString().split(" ");
            String word1 = words[0];
            String word2 = words[1];

            int word1Occurrences = -1;
            int word2Occurrences = -1;

            boolean found = false;

            for (Text value : values) {

                String[] vs = value.toString().split(" ");

                if (!found) {

                    if (vs.length != 3)
                        valuesList.add(value.toString());
                    else {

                        pairOccurences = Integer.parseInt(vs[0]);
                        String eitherWord = vs[1];
                        String eitherWordOccurrences = vs[2];

                        if (eitherWord.equals(word1))
                            word1Occurrences = Integer.parseInt(eitherWordOccurrences);
                        else if (eitherWord.equals(word2))
                            word2Occurrences = Integer.parseInt(eitherWordOccurrences);

                        if (word1Occurrences != -1 && word2Occurrences != -1) {
                            for (String triplet : valuesList) {

                                String[] extractedTriplet = triplet.split(" ");
                                Text outKey = new Text(String.format("%s %s %s", extractedTriplet[0], extractedTriplet[1], extractedTriplet[2]));
                                Text outValue1 = new Text(String.format("%s %s %s %s %s %s", extractedTriplet[3], word1, word2, pairOccurences, word1, word1Occurrences));
                                Text outValue2 = new Text(String.format("%s %s %s %s %s %s", extractedTriplet[3], word1, word2, pairOccurences, word2, word2Occurrences));
                                context.write(outKey, outValue1);
                                context.write(outKey, outValue2);

                            }

                            valuesList.clear();
                            found = true;
                        }

                    }
                } else if (vs.length != 3) {

                    String[] extractedTriplet = value.toString().split(" ");
                    Text outKey = new Text(String.format("%s %s %s", extractedTriplet[0], extractedTriplet[1], extractedTriplet[2]));
                    Text outValue1 = new Text(String.format("%s %s %s %s %s %s", extractedTriplet[3], word1, word2, pairOccurences, word1, word1Occurrences));
                    Text outValue2 = new Text(String.format("%s %s %s %s %s %s", extractedTriplet[3], word1, word2, pairOccurences, word2, word2Occurrences));
                    context.write(outKey, outValue1);
                    context.write(outKey, outValue2);
                }


            }
        }
    }

        private static class CustomPartitioner extends Partitioner<Text, Text> {
            @Override
            public int getPartition(Text key, Text value, int numPartitions) {
                return Math.abs(key.hashCode()) % numPartitions;
            }
        }


        /// ///////////////////////////

    public static void main(String[] args) throws Exception {

            System.out.println("running step 4");

            ////////// first job ///////////////////



            System.out.println("starting first job....");

            Configuration config = new Configuration();
            Job job = Job.getInstance(config, "Word Pair Aggregation");
            job.setJarByClass(Step4.class);

            job.setMapperClass(BigramMapper.class);
            job.setReducerClass(firstJobReducer.class);

            job.setOutputKeyClass(Text.class);
            job.setOutputValueClass(Text.class);
            job.setPartitionerClass(firstJobPartitioner.class);

            job.setOutputFormatClass(TextOutputFormat.class);
            MultipleInputs.addInputPath(job, new Path("s3://lielaytoutputs/step1/"), TextInputFormat.class);
            MultipleInputs.addInputPath(job, new Path("s3://lielaytoutputs/step2/"), TextInputFormat.class);
            FileOutputFormat.setOutputPath(job, new Path("s3://lielaytoutputs/step4job1/"));

            job.waitForCompletion(true);


            System.out.println("finished first job!");

            ////////////////////////////////////////////


            ///////////second job////////////////////

            System.out.println("starting second job....");


            config = new Configuration();
            Job job2 = Job.getInstance(config, "Word Pair Aggregation");
            job2.setJarByClass(Step4.class);

            job2.setMapperClass(TrigramMapper.class);
            job2.setReducerClass(AggregationReducer.class);

            job2.setOutputKeyClass(Text.class);
            job2.setOutputValueClass(Text.class);
            job2.setPartitionerClass(CustomPartitioner.class);

            job2.setOutputFormatClass(TextOutputFormat.class);
            MultipleInputs.addInputPath(job2, new Path("s3://lielaytoutputs/step4job1/"), TextInputFormat.class);
            MultipleInputs.addInputPath(job2, new Path("s3://lielaytoutputs/step3/"), TextInputFormat.class);
            FileOutputFormat.setOutputPath(job2, new Path("s3://lielaytoutputs/step4/"));

            job2.waitForCompletion(true);

            System.out.println("finished second job!");
            //////////////////////////////////////////




    }
}

