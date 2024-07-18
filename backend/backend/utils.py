from django.utils.timezone import now
from rest_framework.response import Response
from rest_framework import status

class ResponseFormatter:
    @staticmethod
    def format_response(data, http_code=status.HTTP_200_OK, message="Success"):
        response_data = {
            "status": http_code,
            "creation_datetime": now().isoformat(),
            "message": message,
            "content": data
        }
        return Response(response_data, status=http_code)