package org.example;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.*;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;
import org.apache.hadoop.mapreduce.lib.input.SequenceFileInputFormat;
import java.io.IOException;
import java.util.regex.Pattern;

public class Step1 {

    private static class TokenizerMapper extends Mapper<LongWritable, Text, Text, Text> {

        private static final Pattern HEBREW_MATCHER = Pattern.compile("[\\u05D0-\\u05EA]+");

        @Override
        public void map(LongWritable lineOffset, Text record, Context context) throws IOException, InterruptedException {
            String[] columns = record.toString().split("\t");
            String word = columns[0];

            if(!HEBREW_MATCHER.matcher(word).matches())
                return;

            Text wordKey = new Text(word);
            Text occurrenceValue = new Text(columns[2]);
            Text totalKey = new Text("*");

            context.write(wordKey, occurrenceValue);
            context.write(totalKey, occurrenceValue);
        }
    }

    private static class AggregatorReducer extends Reducer<Text, Text, Text, Text> {

        @Override
        protected void reduce(Text word, Iterable<Text> occurrences, Context context) throws IOException, InterruptedException {
            int totalOccurrences = 0;

            for (Text occurrence : occurrences) {
                totalOccurrences += Long.parseLong(occurrence.toString());
            }

            Text result = new Text(String.format("%d", totalOccurrences));
            context.write(word, result);
        }
    }

    private static class CustomPartitioner extends Partitioner<Text, Text> {

        @Override
        public int getPartition(Text key, Text value, int numberOfPartitions) {
            return Math.abs(key.hashCode()) % numberOfPartitions;
        }
    }

    public static void main(String[] args) throws Exception {
        System.out.println("running step 1");
        Configuration configuration = new Configuration();
        Job job = Job.getInstance(configuration, "Word Count Aggregator");
        job.setJarByClass(Step1.class);

        job.setMapperClass(TokenizerMapper.class);
        job.setCombinerClass(AggregatorReducer.class);
        job.setReducerClass(AggregatorReducer.class);

        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);
        job.setPartitionerClass(CustomPartitioner.class);

        job.setOutputFormatClass(TextOutputFormat.class);
        job.setInputFormatClass(SequenceFileInputFormat.class);

        SequenceFileInputFormat.addInputPath(job, new Path("s3://datasets.elasticmapreduce/ngrams/books/20090715/heb-all/1gram/data"));
        FileOutputFormat.setOutputPath(job, new Path("s3://lielaytoutputs/step1/"));

        job.waitForCompletion(true);
    }
}
