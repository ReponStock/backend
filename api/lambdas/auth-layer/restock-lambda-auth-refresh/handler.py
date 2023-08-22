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

    refresh_token = body["refresh_token"]
    cognito = boto3.client('cognito-idp')

    try:
        response = cognito.initiate_auth(
            AuthFlow='REFRESH_TOKEN_AUTH',
            AuthParameters = { "REFRESH_TOKEN": refresh_token },
            ClientId = os.environ["APP_CLIENT_ID"]
        )
    except cognito.exceptions.NotAuthorizedException as e:
        return create_base_error_response(
            401,
            "INVALID_REFRESH_TOKEN",
            "Invalid refresh token"
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
                "expires_in": response["AuthenticationResult"]["ExpiresIn"],
            }
        )
    }
