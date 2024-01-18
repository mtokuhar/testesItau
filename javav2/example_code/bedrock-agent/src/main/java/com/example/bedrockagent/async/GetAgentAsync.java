// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0

package com.example.bedrockagent.async;

// snippet-start:[bedrock-agent.java2.get_agent_async.import]
import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.bedrockagent.BedrockAgentAsyncClient;
import software.amazon.awssdk.services.bedrockagent.model.Agent;
import software.amazon.awssdk.services.bedrockagent.model.GetAgentRequest;
import software.amazon.awssdk.services.bedrockagent.model.GetAgentResponse;

import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
// snippet-end:[bedrock-agent.java2.get_agent_async.import]

/**
 * Before running this Java V2 code example, set up your development
 * environment, including your credentials.
 *
 * For more information, see the following documentation topic:
 *
 * https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/get-started.html
 */
public class GetAgentAsync {
    public static void main(String[] args) {
        final String usage = """
            
            Usage:
                <agentId> [<region>]\s
                
            Where:
                agentId - The ID of an existing Agent in your AWS account
                region - (Optional) The AWS region where the Agent is located. Default is 'us-east-1'
        """;

        if (args.length < 1 || args.length > 2) {
            System.out.println(usage);
            System.exit(1);
        }

        String agentId = args[0];

        Region region = args.length == 2 ? Region.of(args[1]) : Region.US_EAST_1;

        System.out.println("Initializing the Amazon Bedrock Agent Client...");
        System.out.printf("Region: %s%n", region.toString());

        var client = BedrockAgentAsyncClient.builder()
                .region(region)
                .credentialsProvider(ProfileCredentialsProvider.create())
                .build();

        getAgent(client, agentId);
    }

    // snippet-start:[bedrock-agent.java2.get_agent_async.main]
    /**
     * Gets information about an agent.
     *
     * <p>This method retrieves agent details by making a call to the
     * GetAgent API operation and passing the agent ID. It prints out
     * basic information about the agent to the console for demonstration
     * purposes.</p>
     *
     * @param client  The client to manage Agents for Amazon Bedrock
     * @param agentId The unique identifier of the agent
     * @return The Agent object
     */
    public static Agent getAgent(BedrockAgentAsyncClient client, String agentId) {
        System.out.printf("Retrieving Amazon Bedrock Agent with ID: %s...%n", agentId);

        try {
            GetAgentRequest request = GetAgentRequest.builder()
                    .agentId(agentId)
                    .build();

            CompletableFuture<GetAgentResponse> future = client.getAgent(request)
                    .whenComplete((response, exception) -> {
                        if (exception != null) {
                            System.out.println(exception.getMessage());
                        }
                    });

            GetAgentResponse response = future.get();

            Agent agent = response.agent();

            System.out.println(" Agent ID : " + agent.agentId());
            System.out.println(" Name     : " + agent.agentName());
            System.out.println(" Model    : " + agent.foundationModel());
            System.out.println(" Status   : " + agent.agentStatus());
            System.out.println();

            return agent;

        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            System.err.println(e.getMessage());
            throw new RuntimeException(e);
        } catch (ExecutionException e) {
            System.err.println(e.getMessage());
            throw new RuntimeException(e);
        }
    }
    // snippet-end:[bedrock-agent.java2.get_agent_async.main]
}