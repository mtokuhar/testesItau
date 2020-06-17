/*
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

This file is licensed under the Apache License, Version 2.0 (the "License").
You may not use this file except in compliance with the License. A copy of
the License is located at http://aws.amazon.com/apache2.0/

This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

ABOUT THIS NODE.JS SAMPLE: This sample is part of the SDK for JavaScript Developer Guide topic
https://docs.aws.amazon.com/sdk-for-javascript/v2/developer-guide/sns-examples-managing-topics.html

Purpose:
sns_listtopics.js demonstrates how to retrieve a list of Amazon SNS topics.

Inputs:
- REGION (in commmand line input below)

Running the code:
node sns_listtopics.js REGION
 */
// snippet-start:[sns.JavaScript.topics.listTopics]
async function run() {
    try {
        const {SNS, ListTopicsCommand} = require("@aws-sdk/client-sns");
        const region = process.argv[2];
        const sns = new SNS(region);
        const data = await sns.send(new ListTopicsCommand({}));
        console.log(data.Topics);
    } catch (err) {
        console.error(err, err.stack);
    }
};
run();
// snippet-end:[sns.JavaScript.topics.listTopics]
exports.run = run;
