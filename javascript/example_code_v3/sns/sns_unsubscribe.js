/*
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

This file is licensed under the Apache License, Version 2.0 (the "License").
You may not use this file except in compliance with the License. A copy of
the License is located at http://aws.amazon.com/apache2.0/

This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

ABOUT THIS NODE.JS SAMPLE: This sample is part of the SDK for JavaScript Developer Guide topic
https://docs.aws.amazon.com/sdk-for-javascript/v2/developer-guide/sns-examples-subscribing-unubscribing-topics.html

Purpose:
sns_unsubscribe.js demonstrates how to delete a subscription to an Amazon SNS topic.

Inputs:
- REGION (in commmand line input below)
- TOPIC_SUBSCRIPTION_ARN (in commmand line input below)

Running the code:
node sns_subscribeapp.js  REGION TOPIC_SUBSCRIPTION_ARN
 */
// snippet-start:[sns.JavaScript.subscriptions.unsubscribe]
async function run() {
    try {
        const {SNS, UnsubscribeCommand} = require("@aws-sdk/client-sns");
        const region = process.argv[2];
        const sns = new SNS(region);
        const params = {SubscriptionArn : process.argv[3]};
        const data = await sns.send(new UnsubscribeCommand(params));
        console.log("Subscription ARN is " + data.SubscriptionArn);
    } catch (err) {
        console.error(err, err.stack);
    }
};
run();
// snippet-end:[sns.JavaScript.subscriptions.unsubscribe]
exports.run = run;
