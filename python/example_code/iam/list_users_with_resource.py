# Copyright 2010-2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import boto3

# Create an IAM service resource
resource = boto3.resource('iam')

# Get an iterable of all users
users = resource.users.all()

# Print details for each user
for user in users:
    print("User {} created on {}".format(
        user.user_name,
        user.create_date
    )) 

#snippet-sourcedescription:[list_users_with_resource.py demonstrates how to list your IAM users.]
#snippet-keyword:[Python]
#snippet-keyword:[Code Sample]
#snippet-service:[<<ADD SERVICE>>]
#snippet-sourcetype:[full-example]
#snippet-sourcedate:[]
#snippet-sourceauthor:[AWS]

