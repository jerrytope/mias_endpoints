# yourapp/core.py
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def _wrap(data, http_status, message="Operation successful."):
    """Helper that builds the final enveloped response."""
    return Response(
        {
            "status": "success" if http_status < 400 else "error",
            "message": message,
            "data": data if data is not None else {},
        },
        status=http_status,
    )


def custom_exception_handler(exc, context):
    """
    Global exception handler – turns every error (4xx/5xx) into the same envelope.
    """
    # Let DRF generate the normal error response first
    response = exception_handler(exc, context)

    if response is not None:
        # DRF already gave us a response → turn it into our envelope
        custom_message = response.data.get("detail") or "An error occurred."
        if isinstance(response.data, dict) and "non_field_errors" in response.data:
            custom_message = response.data["non_field_errors"][0]

        return _wrap(
            data=response.data,
            http_status=response.status_code,
            message=custom_message,
        )

    # If DRF could not handle the exception → 500
    return _wrap(
        data={},
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message=str(exc),
    )


def wrap_response(view_func):
    """
    Decorator for class-based views (APIView, ViewSet actions, etc.)
    """
    def wrapped_view(self, request, *args, **kwargs):
        response = view_func(self, request, *args, **kwargs)

        # If the view already returned a Response → wrap it
        if isinstance(response, Response):
            # Preserve the original status code
            http_status = response.status_code
            # Use a friendly message for success cases
            default_msg = {
                200: "Record fetched successfully.",
                201: "Record created successfully.",
                202: "Record updated successfully.",
                204: "Record deleted successfully.",
            }.get(http_status, "Operation successful.")
            return _wrap(response.data, http_status, default_msg)

        # If the view returned raw data (rare), wrap it with 200
        return _wrap(response, status.HTTP_200_OK)
    return wrapped_view