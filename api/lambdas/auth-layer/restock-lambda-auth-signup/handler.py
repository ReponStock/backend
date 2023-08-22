import os
import json

import boto3
from botocore.exceptions import ClientError

from restock.errors import get_client_error_response, create_base_error_response


def signup(email: str, name: str, password: str):
    client = boto3.client('cognito-idp')
    try:
        client.sign_up(
            ClientId=os.environ['APP_CLIENT_ID'],
            Username=email,
            Password=password,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': email
                },
                {
                    "Name": "name",
                    "Value": name
                }
            ]
        )
        client.admin_add_user_to_group(
            UserPoolId=os.environ['USER_POOL_ID'],
            Username=email,
            GroupName=os.environ["USER_GROUP_NAME"]
        )
        return None
    except client.exceptions.UsernameExistsException as e:
        return create_base_error_response(
            400,
            "USER_ALREADY_EXISTS",
            "Email already exists"
        )
    except ClientError as e:
        return get_client_error_response(e)

def lambda_handler(event, context):
    body = json.loads(event['body'])
    error = signup(body['email'], body["name"], body['password'])

    if error:
        return error

    return {
        "statusCode": 201,
        "body": json.dumps(
            {
                "email": body['email'],
                "status": "SUCCESS",
                "message": f"user was successfully registered"
            }
        )
    }
