package org.example;

import com.amazonaws.auth.AWSCredentialsProvider;
import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.services.ec2.AmazonEC2;
import com.amazonaws.services.ec2.AmazonEC2ClientBuilder;
import com.amazonaws.services.ec2.model.InstanceType;
import com.amazonaws.services.elasticmapreduce.AmazonElasticMapReduce;
import com.amazonaws.services.elasticmapreduce.AmazonElasticMapReduceClientBuilder;
import com.amazonaws.services.elasticmapreduce.model.*;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;

public class App {


    public static AWSCredentialsProvider credentialsProvider;
    public static AmazonS3 S3;
    public static AmazonEC2 ec2;
    public static AmazonElasticMapReduce emr;
    public static String bucketName = "lielaytstepjars";
    public static String logsBucketName = "lielaytlogs";

    public static int numberOfInstances = 4;

    public static void main(String[]args){
        System.out.println("[INFO] Connecting to aws");
        ec2 = AmazonEC2ClientBuilder.standard()
                .withRegion("us-east-1")
                .build();
        S3 = AmazonS3ClientBuilder.standard()
                .withRegion("us-east-1")
                .build();
        emr = AmazonElasticMapReduceClientBuilder.standard()
                .withRegion("us-east-1")
                .build();
        System.out.println( "list cluster");
        System.out.println( emr.listClusters());

        //steps

        //step1
        HadoopJarStepConfig step1 = new HadoopJarStepConfig()
                .withJar("s3://" + bucketName + "/step1.jar")
                .withMainClass("step1");

        StepConfig stepConfig1 = new StepConfig()
                .withName("step1")
                .withHadoopJarStep(step1)
                .withActionOnFailure("TERMINATE_JOB_FLOW");

        //step2
        HadoopJarStepConfig step2 = new HadoopJarStepConfig()
                .withJar("s3://" + bucketName + "/step2.jar")
                .withMainClass("step2");

        StepConfig stepConfig2 = new StepConfig()
                .withName("step2")
                .withHadoopJarStep(step2)
                .withActionOnFailure("TERMINATE_JOB_FLOW");

        //step3
        HadoopJarStepConfig step3 = new HadoopJarStepConfig()
                .withJar("s3://" + bucketName + "/step3.jar")
                .withMainClass("step3");

        StepConfig stepConfig3 = new StepConfig()
                .withName("step3")
                .withHadoopJarStep(step3)
                .withActionOnFailure("TERMINATE_JOB_FLOW");


        //step4
        HadoopJarStepConfig step4 = new HadoopJarStepConfig()
                .withJar("s3://" + bucketName + "/step4.jar")
                .withMainClass("step4");

        StepConfig stepConfig4 = new StepConfig()
                .withName("step4")
                .withHadoopJarStep(step4)
                .withActionOnFailure("TERMINATE_JOB_FLOW");


        //step5
        HadoopJarStepConfig step5 = new HadoopJarStepConfig()
                .withJar("s3://" + bucketName + "/step5.jar")
                .withMainClass("step5");

        StepConfig stepConfig5 = new StepConfig()
                .withName("step5")
                .withHadoopJarStep(step5)
                .withActionOnFailure("TERMINATE_JOB_FLOW");


        //step6
        HadoopJarStepConfig step6 = new HadoopJarStepConfig()
                .withJar("s3://" + bucketName + "/step6.jar")
                .withMainClass("step6");

        StepConfig stepConfig6 = new StepConfig()
                .withName("step6")
                .withHadoopJarStep(step6)
                .withActionOnFailure("TERMINATE_JOB_FLOW");


        //

        //Job flow
        JobFlowInstancesConfig instances = new JobFlowInstancesConfig()
                .withInstanceCount(numberOfInstances)
                .withMasterInstanceType(InstanceType.M4Large.toString())
                .withSlaveInstanceType(InstanceType.M4Large.toString())
                .withHadoopVersion("2.9.2")
                .withEc2KeyName("vockey")
                .withKeepJobFlowAliveWhenNoSteps(false)
                .withPlacement(new PlacementType("us-east-1a"));

        System.out.println("Set steps");
        RunJobFlowRequest runFlowRequest = new RunJobFlowRequest()
                .withName("Map reduce project")
                .withInstances(instances)
                .withSteps(stepConfig1,stepConfig2,stepConfig3,stepConfig4,stepConfig5)
                .withLogUri("s3://"+logsBucketName+"/logs/")
                .withServiceRole("EMR_DefaultRole")
                .withJobFlowRole("EMR_EC2_DefaultRole")
                .withReleaseLabel("emr-5.11.0");

        RunJobFlowResult runJobFlowResult = emr.runJobFlow(runFlowRequest);
        String jobFlowId = runJobFlowResult.getJobFlowId();
        System.out.println("Ran job flow with id: " + jobFlowId);
    }

}
