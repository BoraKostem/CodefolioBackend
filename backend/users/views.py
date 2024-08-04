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
from botocore.exceptions import BotoCoreError, ClientError
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
    
class PublicProfileView(APIView):
    def get(self, request):
        try:
            user_id = request.query_params.get('id')
            if not user_id:
                return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="User ID is required")
            user = MyUser.objects.get(id=user_id)
        except MyUser.DoesNotExist:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_404_NOT_FOUND, message="User not found.")
        serializer = UserSerializer(user)
        data = serializer.data
        about = ''  # Initialize an empty string for 'about'
        if 'cv_information' in data:
            # Iterate over each item in 'cv_information'
            for cv_info in data['cv_information']:
                if cv_info.get('headline') == 'about':
                    about = cv_info.get('info', '')
                    break  # Exit the loop once the 'about' info is found
            # Remove 'cv_information' from data and add 'about'
            data.pop('cv_information', None)
            data['about'] = about
        return Response(data)

class PublicSearchView(APIView):
    def get(self, request):
        try:
            search_query = request.query_params.get('q')
            if not search_query:
                return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="Search query is required")
            users = MyUser.objects.filter(email__icontains=search_query)
        except MyUser.DoesNotExist:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_404_NOT_FOUND, message="No users found.")
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class WhoAmIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # The request.user will be set to the authenticated user by the JWTAuthentication class
        user = request.user
        serializer = UserSerializer(user)
        data = serializer.data
        about = ''  # Initialize an empty string for 'about'
        if 'cv_information' in data:
            # Iterate over each item in 'cv_information'
            for cv_info in data['cv_information']:
                if cv_info.get('headline') == 'about':
                    about = cv_info.get('info', '')
                    break  # Exit the loop once the 'about' info is found
            # Remove 'cv_information' from data and add 'about'
            data.pop('cv_information', None)
            data['about'] = about
        return Response(data)
    
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
            _, file_extension = os.path.splitext(file.name)
            file_name_without_extension = os.path.splitext(file.name)[0]
            datetime_string = datetime.now().strftime("%Y%m%d%H%M%S")
            file_name = f"{file_name_without_extension}{datetime_string}{file_extension}"
            file_key = f"user_profile/{user.id}/{file_name}"
            # Upload the file to S3
            try:
                s3_client.upload_fileobj(file, bucket_name, file_key)
                return f"https://{bucket_name}.s3.eu-central-1.amazonaws.com/{file_key}"
            except (BotoCoreError, ClientError) as error:
                # Handle the exception (log it, return it, etc.)
                return error

        # Update or create user profile with URLs
        user_profile = MyUser.objects.get(id=user.id)

        if profile_photo:
            profile_photo_url = upload_to_s3(profile_photo, bucket)
            user_profile.profile_photo = profile_photo_url
            if isinstance(profile_photo_url, (BotoCoreError,ClientError)):
                return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="Failed to upload profile photo.")
                
        if background_photo:
            background_photo_url = upload_to_s3(background_photo, bucket)
            user_profile.profile_background = background_photo_url
            if isinstance(background_photo_url, (BotoCoreError,ClientError)):
                return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="Failed to upload background photo.")
        try:
            user_profile.save()
        except:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="Failed to update user profile.")

        # Serialize and return the updated user profile
        serializer = UserSerializer(user_profile)

        return ResponseFormatter.format_response(serializer.data, http_code=status.HTTP_200_OK, message="User profile updated successfully.")
