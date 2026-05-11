package org.example;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Partitioner;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.SequenceFileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;

import java.io.IOException;
import java.util.regex.Pattern;

public class Step2 {

    private static class WordPairMapper extends Mapper<LongWritable, Text, Text, Text> {

        private static final Pattern HEBREW_MATCHER = Pattern.compile("[\\u05D0-\\u05EA]+");

        @Override
        public void map(LongWritable lineOffset, Text record, Context context) throws IOException, InterruptedException {
            String[] columns = record.toString().split("\t");
            String[] wordPair = columns[0].split(" ");

            for(String word : wordPair) {
                if(!HEBREW_MATCHER.matcher(word).matches())
                    return;
            }

            if (wordPair.length > 1) {
                String firstWord = wordPair[0];
                String secondWord = wordPair[1];
                Text pairKey = new Text(String.format("%s %s", firstWord, secondWord));
                Text occurrenceValue = new Text(columns[2]);
                context.write(pairKey, occurrenceValue);
            }
        }
    }

    public static class CountAggregatorReducer extends Reducer<Text, Text, Text, Text> {

        @Override
        protected void reduce(Text wordPair, Iterable<Text> occurrences, Context context) throws IOException, InterruptedException {
            int totalOccurrences = 0;
            for (Text occurrence : occurrences) {
                totalOccurrences += Long.parseLong(occurrence.toString());
            }

            Text result = new Text(String.format("%d", totalOccurrences));
            context.write(wordPair, result);
        }
    }

    private static class CustomPartitioner extends Partitioner<Text, Text> {

        @Override
        public int getPartition(Text key, Text value, int numberOfPartitions) {
            return Math.abs(key.hashCode()) % numberOfPartitions;
        }
    }

    public static void main(String[] args) throws Exception {
        System.out.println("running step 2");
        Configuration config = new Configuration();
        Job job = Job.getInstance(config, "Bigram Count");
        job.setJarByClass(Step2.class);

        job.setMapperClass(WordPairMapper.class);
        job.setCombinerClass(CountAggregatorReducer.class);
        job.setReducerClass(CountAggregatorReducer.class);

        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);
        job.setPartitionerClass(CustomPartitioner.class);

        job.setOutputFormatClass(TextOutputFormat.class);
        job.setInputFormatClass(SequenceFileInputFormat.class);

        SequenceFileInputFormat.addInputPath(job, new Path("s3://datasets.elasticmapreduce/ngrams/books/20090715/heb-all/2gram/data"));
        FileOutputFormat.setOutputPath(job, new Path("s3://lielaytoutputs/step2/"));

        job.waitForCompletion(true);
    }
}
