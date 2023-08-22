import os
import json

import boto3
from botocore.exceptions import ClientError

from restock.errors import (
    get_client_error_response,
    get_python_error_response,
    create_base_error_response
)


def lambda_handler(event, context):
    body = json.loads(event["body"])

    username = body["email"]
    password = body["password"]

    cognito_client = boto3.client("cognito-idp")

    try:
        response = cognito_client.initiate_auth(
            AuthFlow = "USER_PASSWORD_AUTH",
            AuthParameters = {"USERNAME": username, "PASSWORD": password},
            ClientId = os.environ["APP_CLIENT_ID"]
        )
    except cognito_client.exceptions.NotAuthorizedException as e:
        return create_base_error_response(
            401,
            "INVALID_CREDENTIALS",
            "Invalid credential for this user"
        )
    except cognito_client.exceptions.UserNotFoundException as e:
        return create_base_error_response(
            404,
            "USER_NOT_FOUND",
            "This user was not found"
        )
    except ClientError as e:
        return get_client_error_response(e)
    except Exception as e:
        return get_python_error_response(e)

    return {
        'statusCode': 200,
        'body': json.dumps(
            {
                "access_token": response["AuthenticationResult"]["IdToken"],
                "refresh_token": response["AuthenticationResult"]["RefreshToken"],
                "expires_in": response["AuthenticationResult"]["ExpiresIn"],
                "token_type": response["AuthenticationResult"]["TokenType"],
            }
        )
    }
