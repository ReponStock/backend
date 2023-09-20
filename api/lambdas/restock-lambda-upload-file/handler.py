import os
import json
import base64
from uuid import uuid4
from datetime import datetime

import boto3
from pytz import timezone

from restock.errors import (
    get_client_error_response,
    get_python_error_response,
    create_base_error_response
)
from restock.db import get_conn


def set_name(name: str) -> str:
    return name.translate({ ord(" "): "_" })


def lambda_handler(event, context):

    try:
        construction_id = event["pathParameters"]["construction_id"]
        cognito_sub = event["requestContext"]["authorizer"]["claims"]["sub"]
    except KeyError as e:
        return get_client_error_response(e)

    try:
        with get_conn() as conn:
            with conn.cursor() as cursor:
                query = (
                    "SELECT e.name, o.name FROM obra o INNER JOIN usuario u on (o.id_empresa = u.id_empresa) "
                    "INNER JOIN empresa e on (o.id_empresa = e.id) WHERE o.id = %s AND u.cognito_sub = %s"
                )
                cursor.execute(query, (construction_id, cognito_sub))
                result = cursor.fetchone()
                business_name, construction_name = result if result else (None, None)
                if not business_name:
                    return create_base_error_response(401, "UNAUTHORIZED", "invalid business id or unauthorized user")
    except Exception as e:
        return create_base_error_response(500, "DATABASE_ERROR", f"{e}")

    # Extraer los datos binarios del evento
    file_content = base64.b64decode(event['body'])

    # Extraer el tipo MIME del encabezado
    content_type = event['headers'].get('Content-Type', '')

    # Validar el tipo MIME
    valid_content_types = [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel'
    ]

    if content_type not in valid_content_types:
        return create_base_error_response(
            400,
            "INVALID_FILE_TYPE",
            f"'{content_type}' content-type is not allowed"
        )


    now = datetime.now(timezone("America/Bogota"))
    filename = f"{uuid4()}.xlsx"
    key = f"file-uploads/{set_name(business_name)}/{set_name(construction_name)}/{cognito_sub}/{now.year}/{now.month}/{now.day}/{filename}"

    try:
        s3 = boto3.client('s3')
        s3.put_object(Body=file_content, Bucket=os.environ['BUCKET_NAME'], Key=key)
    except Exception as e:
        return get_python_error_response(e)

    return {
        'statusCode': 200,
        'body': json.dumps({ "filename": filename })
    }
