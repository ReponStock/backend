import os
import json

import boto3
from botocore.exceptions import ClientError

from restock.db import get_conn
from restock.errors import get_client_error_response, create_base_error_response, get_python_error_response


def save_user_and_business(cognito_sub, nit, business_name):
    # Conexión a la base de datos
    conn = get_conn()
    with conn.cursor() as cursor:
        # Insertar la empresa
        insert_empresa_query = "INSERT INTO empresa (nit, name) VALUES (%s, %s) RETURNING id"
        cursor.execute(insert_empresa_query, (nit, business_name))
        empresa_id = cursor.fetchone()[0]

        # Insertar el usuario
        insert_usuario_query = "INSERT INTO usuario (cognito_sub, id_empresa) VALUES (%s, %s)"
        cursor.execute(insert_usuario_query, (cognito_sub, empresa_id))

        conn.commit()
    conn.close()

def signup(email: str, name: str, password: str, nit: int, business_name: str):
    client = boto3.client('cognito-idp')
    try:
        response = client.sign_up(
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

        cognito_sub = response['UserSub']

        client.admin_add_user_to_group(
            UserPoolId=os.environ['USER_POOL_ID'],
            Username=email,
            GroupName=os.environ["USER_GROUP_NAME"]
        )

        save_user_and_business(cognito_sub, nit, business_name)

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
    try:
        body = json.loads(event['body'])
        error = signup(
            body['email'],
            body["name"],
            body['password'],
            body['nit'],
            body['business_name']
        )

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
    except Exception as e:
        return get_python_error_response(e)
