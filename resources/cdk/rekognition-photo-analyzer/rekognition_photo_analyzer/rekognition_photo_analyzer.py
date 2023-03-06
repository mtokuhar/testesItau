# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from aws_cdk import (
    aws_apigateway as apigateway,
    aws_cognito as cognito,
    aws_dynamodb as ddb,
    aws_iam as iam,
    aws_lambda as lambda_cdk,
    aws_s3 as s3,
    aws_s3_notifications as s3_notifications,
    aws_s3_deployment as s3_deployment,
    Stack
)
from constructs import Construct
from pathlib import Path


ELROS_PATH = "./website"


Lambdas = dict[str, lambda_cdk.Function]


class RekognitionPhotoAnalyzerStack(Stack):
    def __init__(self, scope: Construct, lang: str, name="", email="", **kwargs) -> None:
        self.email = email

        id = f"{name}-{lang}-PAM"

        super().__init__(scope, id, **kwargs)

        (user, group) = self._iam()
        self.user = user
        self.group = group

        (storage_bucket, working_bucket) = self._s3()
        self.storage_bucket = storage_bucket
        self.working_bucket = working_bucket

        (labels_table, jobs_table) = self._dynamodb()
        self.labels_table = labels_table
        self.jobs_table = jobs_table

        (cognito_pool, cognito_user, app_client) = self._cognito()
        self.cognito_pool = cognito_pool
        self.cognito_user = cognito_user

        lambdas = self._lambdas()

        gateway = self._api_gateway(lambdas, cognito_pool)
        self._s3_website(gateway, app_client)

    def _iam(self):
        # create new IAM group and user
        group = iam.Group(self, f"AppGroup")
        user = iam.User(self, f"AppUser")

        # add IAM user to the new group
        user.add_to_group(group)

        return (user, group)

    def _s3(self) -> tuple[s3.Bucket, s3.Bucket]:
        # give new user access to the bucket
        storage_bucket = s3.Bucket(
            self, f"storage-bucket")
        storage_bucket.grant_read_write(self.user)

        # TODO: Policy for Glacier storage class for objects with tag rekognition: complete

        working_bucket = s3.Bucket(
            self, f"working-bucket")
        working_bucket.grant_read_write(self.user)

        # TODO: Add 24-hour deletion policy

        return (storage_bucket, working_bucket)

    def _dynamodb(self) -> tuple[ddb.Table, ddb.Table]:
        # create DynamoDB table to hold Rekognition results
        labels_table = ddb.Table(
            self, f"LabelsTable",
            partition_key=ddb.Attribute(
                name='Label', type=ddb.AttributeType.STRING)
        )

        jobs_table = ddb.Table(
            self, f"JobsTable",
            partition_key=ddb.Attribute(
                name='JobId', type=ddb.AttributeType.STRING)
        )

        return (labels_table, jobs_table)

    def _cognito(self) -> tuple[cognito.UserPool, cognito.CfnUserPoolClient, cognito.UserPoolClient]:
        cognito_pool = cognito.UserPool(
            self, f"UserPool",
            password_policy=cognito.PasswordPolicy(
                # Password is 6 characters minimum length and no complexity requirements,
                min_length=6,
                require_digits=False,
                require_lowercase=False,
                require_symbols=False,
                require_uppercase=False,
            ),
            mfa=cognito.Mfa.OFF,  # no MFA,
            # no self-service account recovery,
            account_recovery=cognito.AccountRecovery.NONE,
            self_sign_up_enabled=False,  # no self-registration,
            # no assisted verification,
            # no required or custom attributes,
            # send email with cognito.
        )
        cognito_app_client = cognito_pool.add_client(
            f"AppClient")
        cognito_user = cognito.CfnUserPoolUser(
            self, f"UserPool-DefaultUser",
            user_pool_id=cognito_pool.user_pool_id,
            user_attributes=[cognito.CfnUserPoolUser.AttributeTypeProperty(
                name="email",
                value=self.email
            )],
            username=self.email,
        )
        return (cognito_pool, cognito_user, cognito_app_client)

    def _s3_website(self, gateway: apigateway.RestApi, app_client: cognito.UserPoolClient):
        website_bucket = s3.Bucket(
            self, f"website",
            # public_read_access=True,
            website_index_document="index.html"
        )
        deployment = s3_deployment.BucketDeployment(
            self, f"Website",
            sources=[
                s3_deployment.Source.asset(ELROS_PATH)],
            destination_bucket=website_bucket
        )

        # TODO: Embed app client id & gateway endpoint.

        return (website_bucket, deployment)

    def _api_gateway(self, lambdas: Lambdas, cognito_pool: cognito.UserPool) -> None:
        api = apigateway.RestApi(
            self, f"RestApi",
            rest_api_name=self.stack_name,
            default_cors_preflight_options=apigateway.CorsOptions(
                # TODO: Limit this to the s3Deployment bucket domain?
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_credentials=True
            )
        )

        auth = apigateway.CognitoUserPoolsAuthorizer(
            self, f"Authorizer",
            cognito_user_pools=[cognito_pool]
        )

        self._api_gateway_route(api, 'labels', lambdas['Labels'], 'GET', auth)
        # self._api_gateway_route(api, 'upload', lambdas['Upload'], 'PUT', auth)
        # self._api_gateway_route(api, 's3_copy', lambdas['Copy'], 'PUT', auth)
        # self._api_gateway_route(
        #     api, 'download', lambdas['Download'], 'PUT', auth)
        # self._api_gateway_route(
        #     api, 'archive', lambdas['Archive'], 'PUT', auth)

    def _api_gateway_route(self, api: apigateway.RestApi, resource: str, lambda_fn: lambda_cdk.Function, method: str, auth: apigateway.CognitoUserPoolsAuthorizer) -> None:
        resource = api.root.add_resource(resource)
        resource.add_method(
            method,
            apigateway.LambdaIntegration(lambda_fn),
            authorizer=auth,
            authorization_type=apigateway.AuthorizationType.COGNITO,
        )

    def _lambdas(self) -> Lambdas:
        self.layer = lambda_cdk.LayerVersion(
            self, f"LibraryLayer", code=self.lambda_code_asset())
        lambda_DetectLabels = self._lambda_DetectLabels(
            self.storage_bucket, self.labels_table)
        lambda_ZipArchive = self._lambda_ZipArchive(
            self.working_bucket, self.jobs_table)
        lambda_Labels = self._lambda_Labels(self.labels_table)
        return dict(
            DetectLabels=lambda_DetectLabels,
            ZipArchive=lambda_ZipArchive,
            Labels=lambda_Labels,
            # TODO
            Upload=None,
            Copy=None,
            Download=None,
            Archive=None,
        )

    def lambda_runtime(self) -> lambda_cdk.Runtime:
        raise NotImplementedError()

    def lambda_code_asset(self) -> lambda_cdk.Code:
        raise NotImplementedError()

    def lambda_DetectLabels_handler(self) -> str:
        raise NotImplementedError()

    def lambda_Labels_handler(self) -> str:
        raise NotImplementedError()

    def lambda_ZipArchive_handler(self) -> str:
        raise NotImplementedError()

    def lambda_Upload_handler(self) -> str:
        raise NotImplementedError()

    def lambda_Copy_handler(self) -> str:
        raise NotImplementedError()

    def lambda_Download_handler(self) -> str:
        raise NotImplementedError()

    def lambda_Archive_handler(self) -> str:
        raise NotImplementedError()

    def _lambda_DetectLabels(self, storage_bucket: s3.Bucket, labels_table: ddb.Table):
        # create Lambda function
        lambda_function = lambda_cdk.Function(
            self, f'DetectLabelsFn',
            runtime=self.lambda_runtime(),
            # layers=self._layers()
            handler=self.lambda_DetectLabels_handler(),
            code=self.lambda_code_asset(),
            environment={
                'STORAGE_BUCKET_NAME': storage_bucket.bucket_name,
                'LABELS_TABLE_NAME': labels_table.table_name
            }
        )

        # add Rekognition permissions for Lambda function
        statement = iam.PolicyStatement()
        statement.add_actions("rekognition:DetectLabels")
        # statement.add_resources(lambda_function.function_arn)
        # lambda_function.role.add_to_principal_policy(iam.PolicyStatement(
        #     actions=["rekognition:DetectLabels"],
        #     # resources=[lambda_function.function_arn]
        #     resources=[
        #         self.format_arn(
        #             service="lambda",
        #             resource="function",
        #             resource_name=lambda_function.function_name
        #         )
        #     ]
        # ))

        # create trigger for Lambda function with image type suffixes
        # notification = s3_notifications.LambdaDestination(lambda_function)
        # storage_bucket.add_object_created_notification(
        #     notification, s3.NotificationKeyFilter(suffix='.jpg'))
        # storage_bucket.add_object_created_notification(
        #     notification, s3.NotificationKeyFilter(suffix='.jpeg'))

        # grant permissions for lambda to read/write to DynamoDB table and bucket
        labels_table.grant_read_write_data(lambda_function)
        storage_bucket.grant_read_write(lambda_function)

        return lambda_function

    def _lambda_ZipArchive(self, working_bucket: s3.Bucket, jobs_table: ddb.Table):
        # create Lambda function
        lambda_function = lambda_cdk.Function(
            self, f'ZipArchiveFn',
            runtime=self.lambda_runtime(),
            handler=self.lambda_ZipArchive_handler(),
            code=self.lambda_code_asset(),
            environment={
                'WORKING_BUCKET_NAME': working_bucket.bucket_name,
                'JOBS_TABLE_NAME': jobs_table.table_name
            }
        )

        # create trigger for Lambda function on job report suffix
        notification = s3_notifications.LambdaDestination(lambda_function)
        notification.bind(self, working_bucket)
        working_bucket.add_object_created_notification(
            notification, s3.NotificationKeyFilter(prefix='job-', suffix='/report.csv'))

        # grant permissions for lambda to read/write to DynamoDB table and bucket
        jobs_table.grant_read_write_data(lambda_function)
        working_bucket.grant_read_write(lambda_function)

        return lambda_function

    def _lambda_Labels(self, labels_table: ddb.Table):
        # create Lambda function
        lambda_function = lambda_cdk.Function(
            self, f'LabelsFn',
            runtime=self.lambda_runtime(),
            handler=self.lambda_Labels_handler(),
            code=self.lambda_code_asset(),
            environment={
                'LABELS_TABLE_NAME': labels_table.table_name
            }
        )

        labels_table.grant_read_data(lambda_function)
        return lambda_function


class PythonRekognitionPhotoAnalyzerStack(RekognitionPhotoAnalyzerStack):
    def __init__(self, scope: Construct, name, email, **kwargs) -> None:
        super().__init__(scope, "Python", name, email, **kwargs)

    def lambda_runtime(self):
        return lambda_cdk.Runtime.PYTHON_3_8

    def lambda_code_asset(self):
        return lambda_cdk.Code.from_asset('rekognition_photo_analyzer/lambda')

    def lambda_DetectLabels_handler(self):
        return 'rekfunction.handler'

    def lambda_Labels_handler(self):
        return "rek.func"

    def lambda_ZipArchive_handler(self):
        return "rek.func"

    def lambda_Upload_handler(self):
        return "rek.func"

    def lambda_Copy_handler(self):
        return "rek.func"

    def lambda_Download_handler(self):
        return "rek.func"

    def lambda_Archive_handler(self):
        return "rek.func"


class JavaRekognitionPhotoAnalyzerStack(RekognitionPhotoAnalyzerStack):
    def __init__(self, scope: Construct,  name, email, **kwargs) -> None:
        super().__init__(scope, "Java", name, email, **kwargs)

    def lambda_runtime(self):
        return lambda_cdk.Runtime.JAVA_11

    def lambda_code_asset(self):
        return lambda_cdk.Code.from_asset(str(Path(__file__) / '../../../../../javav2/usecases/pam_source_files/'))

    def lambda_DetectLabels_handler(self):
        return 'com.example.photo.handlers.S3Trigger.handleRequest'

    def lambda_Labels_handler(self):
        return "rek.func"

    def lambda_ZipArchive_handler(self):
        return "rek.func"

    def lambda_Upload_handler(self):
        return "rek.func"

    def lambda_Copy_handler(self):
        return "rek.func"

    def lambda_Download_handler(self):
        return "rek.func"

    def lambda_Archive_handler(self):
        return "rek.func"
