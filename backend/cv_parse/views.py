from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from .serializers import UserCVSerializer
from users.serializers import CVLanguageSerializer, CVInformationSerializer, CVExperienceSerializer, CVEducationSerializer, CVSkillSerializer, CVCertificationSerializer, CVProjectLanguageSerializer, CVProjectSerializer, GitHubProjectLanguageSerializer, GitHubProjectSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from backend.utils import ResponseFormatter
from users.models import CVLanguage, CVInformation, CVExperience, CVEducation, CVSkill, CVCertification, CVProject, CVProjectLanguage
import json
import boto3
from botocore.exceptions import ClientError
import os
from pathlib import Path
import environ
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# Initialize environment variables
env = environ.Env()
# Assuming your .env file is in the same directory as settings.py
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
from .cv_parser import cv_parser

bucket = env('AWS_STORAGE_BUCKET_NAME')

class UserCVUploadAPIView(APIView):
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
            try:
                # Save the CV data to the database
                s3_client = boto3.client('s3')
                # Define the S3 key for the file
                file_key = f"user_cvs/{user.id}/{file.name}"
                file_content = file.read()
                # Upload the file to S3
                s3_client.put_object(Bucket=bucket, Key=file_key, Body=file_content)
                
                # Save the CV data to the database
                self.createCVs(cv, user.id)
            except ClientError as e:
                return ResponseFormatter.format_response(None, http_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(e))
            except Exception as e:
                # Handle other exceptions
                return ResponseFormatter.format_response(None, http_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(e))

            
            return ResponseFormatter.format_response(cv, http_code=status.HTTP_200_OK)
        else:
            return ResponseFormatter.format_response(None , http_code=status.HTTP_400_BAD_REQUEST, message=serializer._errors)
        
    def createCVs(self, cv_json, user):
        CVLanguage.objects.filter(user=user).delete()
        CVExperience.objects.filter(user=user).delete()
        CVEducation.objects.filter(user=user).delete()
        CVSkill.objects.filter(user=user).delete()
        CVCertification.objects.filter(user=user).delete()
        CVProject.objects.filter(user=user).delete()
        CVInformation.objects.filter(user=user).delete()
        cv_info = {
            'user': user,
            'headline': "about",
            'info': cv_json['about']
        }
        cv_languages = cv_json['cv_language']
        cv_experiences = cv_json['cv_experience']
        cv_educations = cv_json['cv_education']
        cv_skills = cv_json['cv_skills']
        cv_certifications = cv_json['cv_certifications']
        cv_projects = cv_json['cv_projects']

        # Create CV Projects
        for cv_project in cv_projects:
            cv_project['user'] = user
            cv_project_serializer = CVProjectSerializer(data=cv_project)
            if cv_project_serializer.is_valid():
                cv_project_serializer.save()
            else:
                return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message=cv_project_serializer.errors)

        # Create CV Information
        cv_information_serializer = CVInformationSerializer(data=cv_info)
        if cv_information_serializer.is_valid():
            cv_information_serializer.save()
        else:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message=cv_information_serializer.errors)
            
        # Create CV Languages
        for cv_language in cv_languages:
            cv_language['user'] = user
            cv_language_serializer = CVLanguageSerializer(data=cv_language)
            if cv_language_serializer.is_valid():
                cv_language_serializer.save()
            else:
                return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message=cv_language_serializer.errors)
            
        # Create CV Experiences
        for cv_experience in cv_experiences:
            cv_experience['user'] = user
            cv_experience_serializer = CVExperienceSerializer(data=cv_experience)
            if cv_experience_serializer.is_valid():
                cv_experience_serializer.save()
            else:
                return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message=cv_experience_serializer.errors)
            
        # Create CV Educations
        for cv_education in cv_educations:
            cv_education['user'] = user
            cv_education_serializer = CVEducationSerializer(data=cv_education)
            if cv_education_serializer.is_valid():
                cv_education_serializer.save()
            else:
                return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message=cv_education_serializer.errors)
            
        # Create CV Skills
        for cv_skill in cv_skills:
            cv_skill['user'] = user
            cv_skill_serializer = CVSkillSerializer(data=cv_skill)
            if cv_skill_serializer.is_valid():
                cv_skill_serializer.save()
            else:
                return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message=cv_skill_serializer.errors)
            
        # Create CV Certifications
        for cv_certification in cv_certifications:
            cv_certification['user'] = user
            cv_certification_serializer = CVCertificationSerializer(data=cv_certification)
            if cv_certification_serializer.is_valid():
                cv_certification_serializer.save()
            else:
                return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message=cv_certification_serializer.errors)
            
class UserCVAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_401_UNAUTHORIZED, message="User is not authenticated.")
        
        cv_info = CVInformation.objects.filter(user=user)
        cv_languages = CVLanguage.objects.filter(user=user)
        cv_experiences = CVExperience.objects.filter(user=user)
        cv_educations = CVEducation.objects.filter(user=user)
        cv_skills = CVSkill.objects.filter(user=user)
        cv_certifications = CVCertification.objects.filter(user=user)
        cv_projects = CVProject.objects.filter(user=user)

        cv_info = CVInformationSerializer(cv_info, many=True)
        cv_languages = CVLanguageSerializer(cv_languages, many=True)
        cv_experiences = CVExperienceSerializer(cv_experiences, many=True)
        cv_educations = CVEducationSerializer(cv_educations, many=True)
        cv_skills = CVSkillSerializer(cv_skills, many=True)
        cv_certifications = CVCertificationSerializer(cv_certifications, many=True)
        cv_projects = CVProjectSerializer(cv_projects, many=True)

        cv = {
            'about': cv_info.data[0]["info"],
            'cv_languages': cv_languages.data,
            'cv_experiences': cv_experiences.data,
            'cv_educations': cv_educations.data,
            'cv_skills': cv_skills.data,
            'cv_certifications': cv_certifications.data,
            'cv_projects': cv_projects.data
        }

        return ResponseFormatter.format_response(cv, http_code=status.HTTP_200_OK)
    
class UserCVProjectEditAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_401_UNAUTHORIZED, message="User is not authenticated.")
        project_id = request.data.get('project_id')
        new_description = request.data.get('description')
        languages = request.data.get('languages')

        if not project_id or not (new_description or languages):
            return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="The 'project_id' and at least one of these field are required: 'description' or 'languages'")
        try:
            project = CVProject.objects.get(id=project_id, user=user)
        except Exception as e:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_404_NOT_FOUND, message="Project not found.")

        if new_description:
            project.description = new_description
        if languages:
            if not isinstance(languages, list):
                languages = [languages]
            for language in languages:
                CVProjectLanguage.objects.get_or_create(
                    project=project,
                    language=language
                )
        try:
            project.save()
        except Exception as e:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(e))
        
        return ResponseFormatter.format_response(CVProjectSerializer(project).data, http_code=status.HTTP_200_OK)
    
class UserCVProjectDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_401_UNAUTHORIZED, message="User is not authenticated.")
        project_id = request.data.get('project_id')
        languages = request.data.get('languages')
        if not project_id:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="The 'project_id' field is required. (languages is optional)")
        try:
            project = CVProject.objects.get(id=project_id, user=user)
        except Exception as e:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_404_NOT_FOUND, message="Project not found.")
        if languages:
            if not isinstance(languages, list):
                languages = [languages]
            for language in languages:
                object = CVProjectLanguage.objects.filter(
                    project=project,
                    language=language
                )
                if not object:
                    return ResponseFormatter.format_response(None, http_code=status.HTTP_404_NOT_FOUND, message=f"Language {language} not found in project {project_id}")
                object.delete()
        else:
            try:
                project.delete()
            except Exception as e:
                return ResponseFormatter.format_response(None, http_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(e))
        
        return ResponseFormatter.format_response(None, http_code=status.HTTP_200_OK)