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
    client = boto3.client("cognito-idp")

    body = json.loads(event["body"])
    try:
        client.confirm_sign_up(
            ClientId=os.environ["APP_CLIENT_ID"],
            Username=body["email"],
            ConfirmationCode=body["confirmation_code"]
        )
    except client.exceptions.CodeMismatchException as e:
        return create_base_error_response(
            400,
            "INVALID_CODE",
            "invalid confirmation code"
        )
    except ClientError as e:
        return get_client_error_response(e)
    except Exception as e:
        return get_python_error_response(e)

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "User confirmed successfully", "status": "SUCCESS"})
    }
