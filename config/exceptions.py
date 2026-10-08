from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    # Let Django/DRF handle unexpected server errors normally.
    if response is None:
        return response

    # If an error is already in our standard format, keep it unchanged.
    if isinstance(response.data, dict) and "error" in response.data:
        return response

    if isinstance(response.data, dict):
        response.data = {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request.",
                "details": response.data,
            }
        }

    elif isinstance(response.data, list):
        response.data = {
            "error": {
                "code": "ERROR",
                "message": "Request failed.",
                "details": response.data,
            }
        }

    else:
        response.data = {
            "error": {
                "code": "ERROR",
                "message": str(response.data),
            }
        }

    return response