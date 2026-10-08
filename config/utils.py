from rest_framework import status
from rest_framework.response import Response


def validation_error_response(errors):
    return Response(
        {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request.",
                "details": errors,
            }
        },
        status=status.HTTP_400_BAD_REQUEST,
    )