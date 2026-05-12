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

public class Step3 {

    private static class TrigramMapper extends Mapper<LongWritable, Text, Text, Text> {

        private static final Pattern HEBREW_MATCHER = Pattern.compile("[\\u05D0-\\u05EA]+");
        @Override
        public void map(LongWritable lineOffset, Text record, Context context) throws IOException, InterruptedException {
            String[] columns = record.toString().split("\t");
            String[] wordTriple = columns[0].split(" ");

            for(String word : wordTriple) {
                if(!HEBREW_MATCHER.matcher(word).matches())
                    return;
            }

            if (wordTriple.length > 2) {
                String firstWord = wordTriple[0];
                String secondWord = wordTriple[1];
                String thirdWord = wordTriple[2];
                Text trigramKey = new Text(String.format("%s %s %s", firstWord, secondWord, thirdWord));
                Text occurrenceValue = new Text(columns[2]);
                context.write(trigramKey, occurrenceValue);
            }
        }
    }

    public static class CountAggregatorReducer extends Reducer<Text, Text, Text, Text> {

        @Override
        protected void reduce(Text wordTriple, Iterable<Text> occurrences, Context context) throws IOException, InterruptedException {
            int totalOccurrences = 0;
            for (Text occurrence : occurrences) {
                totalOccurrences += Long.parseLong(occurrence.toString());
            }

            Text result = new Text(String.format("%d", totalOccurrences));
            context.write(wordTriple, result);
        }
    }

    private static class CustomPartitioner extends Partitioner<Text, Text> {

        @Override
        public int getPartition(Text key, Text value, int numberOfPartitions) {
            return Math.abs(key.hashCode()) % numberOfPartitions;
        }
    }

    public static void main(String[] args) throws Exception {
        System.out.println("running step 3");
        Configuration configuration = new Configuration();
        Job job = Job.getInstance(configuration, "Trigram Count");
        job.setJarByClass(Step3.class);

        job.setMapperClass(TrigramMapper.class);
        job.setCombinerClass(CountAggregatorReducer.class);
        job.setReducerClass(CountAggregatorReducer.class);

        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);
        job.setPartitionerClass(CustomPartitioner.class);

        job.setOutputFormatClass(TextOutputFormat.class);
        job.setInputFormatClass(SequenceFileInputFormat.class);

        SequenceFileInputFormat.addInputPath(job, new Path("s3://datasets.elasticmapreduce/ngrams/books/20090715/heb-all/3gram/data"));
        FileOutputFormat.setOutputPath(job, new Path("s3://lielaytoutputs/step3/"));

        job.waitForCompletion(true);
    }
}

