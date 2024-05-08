# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import boto3
import logging


def delete_selected_public_ecr_repos():
    # Initialize logging
    logging.basicConfig(level=logging.INFO)

    # Create an ECR public client
    client = boto3.client("ecr")

    # Paginate through all public repositories
    paginator = client.get_paginator("describe_repositories")
    for page in paginator.paginate():
        for repo in page["repositories"]:
            repo_name = repo["repositoryName"]
            logging.info(f"Found repository {repo_name}")
            # Check if 'examples' is in the repository name
            if "examples" in repo_name:
                try:
                    # Attempt to delete the repository
                    response = client.delete_repository(repositoryName=repo_name)
                    logging.info(f"Deleted repository {repo_name}: {response}")
                except Exception as e:
                    logging.error(f"Failed to delete repository {repo_name}: {e}")


if __name__ == "__main__":
    delete_selected_public_ecr_repos()
