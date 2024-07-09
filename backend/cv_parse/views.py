from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from .serializers import UserCVSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from backend.utils import ResponseFormatter
import json
import boto3
from .cv_parser import cv_parser

class UserCVUploadAPIView(APIView):
    parser_classes = (MultiPartParser, JSONParser)  # To support both JSON and multipart/form-data requests
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = UserCVSerializer(data=request.data)

        user = request.user
        if not user.is_authenticated:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_401_UNAUTHORIZED, message="User is not authenticated.")

        if serializer.is_valid():
            # Get the file from the request and parse it to extract the CV data
            file = request.FILES['cv']
            cv = cv_parser(file)
            #todo save cv data to the s3 bucket

            
            return ResponseFormatter.format_response(cv, http_code=status.HTTP_200_OK)
        else:
            return ResponseFormatter.format_response(None , http_code=status.HTTP_400_BAD_REQUEST, message=serializer._errors)