import json

from restock.db import get_conn
from restock.endpoints import admin_endpoint
from restock.errors import (
    get_client_error_response,
    get_python_error_response,
    create_base_error_response
)

@admin_endpoint
def lambda_handler(event, context):

    try:

        body = json.loads(event["body"])

        construction_name = body["construction_name"]
    except KeyError as e:
        return get_client_error_response(e)

    try:
        cognito_sub = event["requestContext"]["authorizer"]["claims"]["sub"]
    except Exception as e:
        print(event["requestContext"]["authorizer"])
        return get_python_error_response(e)

    try:
        with get_conn() as conn:
            with conn.cursor() as cursor:
                user_info_query = f"SELECT id, cognito_sub, id_empresa FROM usuario WHERE cognito_sub = '{cognito_sub}'"
                cursor.execute(user_info_query)
                user_id, _, id_empresa = cursor.fetchone()

                construction_insert = "INSERT INTO obra (name, id_empresa) VALUES (%s, %s) RETURNING id"
                cursor.execute(construction_insert, (construction_name, id_empresa))
                construction_id = cursor.fetchone()[0]

                user_x_construction_insert = "INSERT INTO usuario_x_obra (id_usuario, id_obra) VALUES (%s, %s)"
                cursor.execute(user_x_construction_insert, (user_id, construction_id))

                conn.commit()
    except Exception as e:
        return create_base_error_response(500, "DATABASE_ERROR", f"{e}")

    return {
        "statusCode": 201,
        "body": json.dumps({ "id": construction_id, "name": construction_name, "businees_id": id_empresa })
    }
