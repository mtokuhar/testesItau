// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0

package com.example.ecr.scenario;


import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.ecr.EcrClient;
import java.io.IOException;
import java.util.Scanner;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;

/**
 * Before running this Java V2 code example, set up your development
 * environment, including your credentials.
 *
 * For more information, see the following documentation topic:
 *
 * https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/get-started.html
 */
public class ECRScenario {
    public static final String DASHES = new String(new char[80]).replace("\0", "-");
    public static void main(String[] args) throws IOException, InterruptedException, ExecutionException {
        final String usage = """
                Usage: <iamRoleARN> <localImageName>

                Where:
                   iamRoleARN - The IAM role ARN that has the necessary permissions to access and manage the Amazon ECR repository.
                   localImageName - The local docker image to push into the ECR repository (ie, hello-world:latest). 
                """;

     //   if (args.length != 2) {
     //       System.out.println(usage);
     //       System.exit(1);
     //   }

        ECRActions ecrActions = new ECRActions();
        String iamRole = "arn:aws:iam::814548047983:role/Admin" ; //args[0];
        String localImageName = "hello-world-docker:latest" ; //args[1];
        String imageTag = "latest" ;

        Scanner scanner = new Scanner(System.in);
        System.out.println("""
            The Amazon Elastic Container Registry (ECR) is a fully-managed Docker container registry 
            service provided by AWS. It allows developers and organizations to securely 
            store, manage, and deploy Docker container images. 
            ECR provides a simple and scalable way to manage container images throughout their lifecycle, 
            from building and testing to production deployment.\s
                        
            The `EcrAsyncClient` interface in the AWS SDK provides a set of methods to 
            programmatically interact with the Amazon ECR service. This allows developers to 
            automate the storage, retrieval, and management of container images as part of their application 
            deployment pipelines. With ECR, teams can focus on building and deploying their 
            applications without having to worry about the underlying infrastructure required to 
            host and manage a container registry.
            
           This Getting Started scenario walks you through how to perform key operations for this service.  
           Let's get started...
          """);

        waitForInputToContinue(scanner);
        System.out.println(DASHES);

        System.out.println("""
           1. Create an ECR repository.
            
           An ECR repository is a private Docker container registry provided 
           by Amazon Web Services (AWS). It is a managed service that makes it easy to store, manage, and deploy Docker container images.\s
           
           Enter a repository name. 
           For example, 'ecr1'
           """ );
        String repoName;
        while (true) {
            repoName = scanner.nextLine().trim();
            if (!repoName.isEmpty()) {
                break;
            } else {
                System.out.println("Please enter a valid repository name:");
            }
        }

        String repoArn = String.valueOf(ecrActions.createECRRepository(repoName));
        System.out.println("The ARN of the ECR repository is " +repoArn);
        waitForInputToContinue(scanner);

        System.out.println(DASHES);
        System.out.println("""
        2. Set an ECR repository.
        
        Setting an ECR repository policy using the `setRepositoryPolicy` function is crucial for maintaining 
        the security and integrity of your container images. The repository policy allows you to 
        define specific rules and restrictions for accessing and managing the images stored within your ECR 
        repository.    
        """);
        waitForInputToContinue(scanner);
        ecrActions.setRepoPolicy(repoName, iamRole);
        waitForInputToContinue(scanner);

        System.out.println(DASHES);
        System.out.println("""
        3. Display ECR repository policy.
       
        Now we will retrieve the ECR policy to ensure it was successfully set.    
        """);
        waitForInputToContinue(scanner);
        String policyText = ecrActions.getRepoPolicy(repoName);
        System.out.println("Policy Text:");
        System.out.println(policyText);
        waitForInputToContinue(scanner);

        System.out.println(DASHES);
        System.out.println("""
        4. Retrieve an ECR authorization token.
       
        The `getAuthorizationToken` operation of the `ecrClient` is crucial for securely accessing 
        and interacting with an Amazon ECR repository. This operation is responsible for obtaining a valid 
        authorization token, which is required to authenticate your requests to the ECR service. 
        Without a valid authorization token, you would not be able to perform any operations on the ECR repository,
         such as pushing, pulling, or managing your Docker images.     
        """);
        waitForInputToContinue(scanner);
        ecrActions.getAuthToken();
        waitForInputToContinue(scanner);

        System.out.println(DASHES);
        System.out.println("""
        5. Get the ECR Repository URI.
                    
        The URI  of an Amazon ECR repository is important. When you want to deploy a container image to 
        a container orchestration platform like Amazon Elastic Kubernetes Service (EKS) 
        or Amazon Elastic Container Service (ECS), you need to specify the full image URI, 
        which includes the ECR repository URI. This allows the container runtime to pull the 
        correct container image from the ECR repository.    
       """);
        waitForInputToContinue(scanner);
        ecrActions.getRepositoryURI(repoName);
        waitForInputToContinue(scanner);

        System.out.println(DASHES);
        System.out.println("""
        6. Set an ECR Lifecycle Policy.
                    
       An ECR Lifecycle Policy is used to manage the lifecycle of Docker images stored in your ECR repositories. 
       These policies allow you to automatically remove old or unused Docker images from your repositories, 
       freeing up storage space and reducing costs.    
       """);
        waitForInputToContinue(scanner);
        ecrActions.setLifeCyclePolicy(repoName);
        waitForInputToContinue(scanner);

        System.out.println("""
            7. Push a docker image to the Amazon ECR Repository.
            
            The `pushDockerImage` method demonstrates the process of pushing a Docker image to the ECR repository, 
            including calculating the SHA-256 hash of the image, checking layer availability, 
            and completing the image upload.
            
            When pushing a docker image to an ECR repository, you calculate the SHA-256 hash of a given byte array. 
            This is used when uploading a Docker image to ECR because ECR requires the image digest 
            (a unique identifier based on the image content) to be provided during the image push operation.
                     
            """);

        waitForInputToContinue(scanner);
        ecrActions.pushDockerImage(repoName, localImageName);
        waitForInputToContinue(scanner);

        System.out.println(DASHES);
        System.out.println("8. Verify if the image is in the ECR Repository.");
        waitForInputToContinue(scanner);
        ecrActions.verifyImage(repoName, imageTag);
        waitForInputToContinue(scanner);

        System.out.println(DASHES);
        System.out.println("9. Delete the ECR Repository.");
        System.out.println("""
        If the repository isn't empty, you must either delete the contents of the repository 
        or use the force option (used in this scenario) to delete the repository and have Amazon ECR delete all of its contents 
        on your behalf.
        """);
        System.out.println("Would you like to delete the Amazon ECR Repository? (y/n)");
        String delAns = scanner.nextLine().trim();
        if (delAns.equalsIgnoreCase("y")) {
            System.out.println("You selected to delete the AWS ECR resources.");
            waitForInputToContinue(scanner);
            ecrActions.deleteECRRepository(repoName);
        }

        System.out.println(DASHES);
        System.out.println("This concludes the Amazon ECR SDK Getting Started scenario");
        System.out.println(DASHES);
    }

   private static void waitForInputToContinue(Scanner scanner) {
       while (true) {
           System.out.println("");
           System.out.println("Enter 'c' followed by <ENTER> to continue:");
           String input = scanner.nextLine();

           if (input.trim().equalsIgnoreCase("c")) {
               System.out.println("Continuing with the program...");
               System.out.println("");
               break;
           } else {
               // Handle invalid input.
               System.out.println("Invalid input. Please try again.");
          }
       }
   }
}