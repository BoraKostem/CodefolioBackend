from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from .models import MyUser
from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from backend.utils import ResponseFormatter
from rest_framework import status
from datetime import datetime
from PIL import Image
import boto3
import os
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# Initialize environment variables
env = environ.Env()
# Assuming your .env file is in the same directory as settings.py
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

bucket = env('AWS_STORAGE_BUCKET_NAME')
class UserCreate(generics.CreateAPIView):
    queryset = MyUser.objects.all()
    serializer_class = UserSerializer

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': 'Invalid Credentials'}, status=400)
    
class WhoAmIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # The request.user will be set to the authenticated user by the JWTAuthentication class
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
''' Profile Photo upload -- Test It --
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_401_UNAUTHORIZED, message="User is not authenticated.")
        # Extract files from request
        profile_photo = request.FILES.get('profile_photo')
        if profile_photo:
            image = Image.open(profile_photo)
            width, height = image.size
            if not (width >= 200 and height >= 200):
                return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="Profile photo must be at least 200x200 pixels.")
        background_photo = request.FILES.get('background_photo')
        if background_photo:
            image = Image.open(background_photo)
            width, height = image.size
            if not (width >= 1920 and height >= 1080):
                return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="Background photo must be at least 1920x1080 pixels.")
        if not profile_photo and not background_photo:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="No files were uploaded. (profile_photo or background_photo)")

        # Initialize S3 client
        s3_client = boto3.client('s3')
        
        # Function to upload to S3 and return file URL
        def upload_to_s3(file, bucket_name, object_name=None):
            if object_name is None:
                object_name = file.name
            response = s3_client.upload_fileobj(file, bucket_name, object_name)
            file_name = file.name + datetime.now().strftime("%Y%m%d%H%M%S")
            file_key = f"user_profile/{user.id}/{file_name}"
            file_content = file.read()
            # Upload the file to S3
            s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=file_content)
            if response is None:
                return None
            return f"https://{bucket_name}.s3.eu-central-1.amazonaws.com/{file_key}"
        
        # Update or create user profile with URLs
        user_profile = MyUser.objects.get(id=user)

        if profile_photo:
            profile_photo_url = upload_to_s3(profile_photo, bucket)
            user_profile.profile_photo = profile_photo_url
        if background_photo:
            background_photo_url = upload_to_s3(background_photo, bucket)
            user_profile.profile_background = background_photo_url
        try:
            user_profile.save()
        except:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="Failed to update user profile.")

        # Serialize and return the updated user profile
        serializer = UserSerializer(data=user_profile)
        return ResponseFormatter.format_response(serializer.data, http_code=status.HTTP_200_OK, message="User profile updated successfully.")

'''