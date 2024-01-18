// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0

import com.example.bedrockagent.async.ListAgentsAsync;
import com.example.bedrockagent.async.GetAgentAsync;
import org.junit.jupiter.api.*;
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.bedrockagent.BedrockAgentAsyncClient;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertNotNull;

@TestInstance(TestInstance.Lifecycle.PER_METHOD)
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
class AsyncBedrockAgentTests {

    private static BedrockAgentAsyncClient client;
    private static String agentId = "";

    @BeforeAll
    static void setup() {
        Region region = Region.US_EAST_1;
        client = BedrockAgentAsyncClient.builder()
                .region(region)
                .credentialsProvider(DefaultCredentialsProvider.create())
                .build();

        try (InputStream input = AsyncBedrockAgentTests.class
                .getClassLoader()
                .getResourceAsStream("config.properties")) {
            var prop = new Properties();
            prop.load(input);
            agentId = prop.getProperty("agentId");
        } catch (IOException ex) {
            ex.printStackTrace();
        }
    }

    @Test
    @Order(0)
    @Tag("IntegrationTest")
    void listAgents() {
        var agents = ListAgentsAsync.listAgents(client);
        assertNotNull(agents);
        System.out.println("Test ListAgentsAsync passed.");
    }

    @Test
    @Order(2)
    @Tag("IntegrationTest")
    void getAgent() {
        assertDoesNotThrow(() -> GetAgentAsync.getAgent(client, agentId));
        System.out.println("Test GetAgentAsync passed.");
    }
}
