import json

from restock.db import get_conn
from restock.endpoints import admin_endpoint
from restock.errors import (
    get_client_error_response,
    get_python_error_response,
    create_base_error_response
)


def lambda_handler(event, context):
    try:
        cognito_sub = event["requestContext"]["authorizer"]["claims"]["sub"]
    except Exception as e:
        print(event["requestContext"]["authorizer"])
        return get_python_error_response(e)

    try:
        with get_conn() as conn:
            with conn.cursor() as cursor:
                query = "SELECT o.id, o.name FROM obra o INNER JOIN usuario u on (o.id_empresa = u.id_empresa) WHERE u.cognito_sub = %s"
                cursor.execute(query, (cognito_sub,))

                constructions = list(map(lambda x: { "id": x[0], "name": x[1] }, cursor.fetchall()))
    except Exception as e:
        return create_base_error_response(500, "DATABASE_ERROR", f"{e}")

    return {
        "statusCode": 200,
        "body": json.dumps({ "constructions": constructions })
    }
