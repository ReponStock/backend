import json
from typing import Dict

from botocore.exceptions import ClientError


def create_base_error_response(
    status_code: int,
    error_type: str,
    message: str
) -> Dict[str, str]:
    return {
        "statusCode": status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps({ "error": error_type, "message": message })
    }

def get_client_error_response(error) -> Dict[str, str]:
    error_type = error.response['Error']['Code']
    error_message = error.response['Error']['Message'].split(": ", 1)[-1]
    return {
        'statusCode': 400,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        'body': json.dumps({ "error": error_type, "message": error_message })
    }

def get_python_error_response(error) -> Dict[str, str]:
    return {
        'statusCode': 400,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        'body': json.dumps({ "error": type(error).__name__, "message": str(error) })
    }
