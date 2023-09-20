import json


def admin_endpoint(func):
    def wrapper(event, context):
        claims = event['requestContext']['authorizer']['claims']
        groups = claims.get('cognito:groups', [])

        if "administrator" not in groups:
            return {
                "statusCode": 401,
                "body": json.dumps({"error": "UNAUTHORIZED"})
            }
        return func(event, context)
    return wrapper
