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
from langchain.vector_lang import create_cv_data, delete_cv_language, add_cv_language, create_cv_certification, create_cv_education, create_cv_experience, create_cv_project, create_cv_skill, user_cv_project_delete,user_cv_project_update,delete_pgvector_experience,delete_cv_skill,delete_cv_certification, delete_cv_education
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
        file = request.FILES['cv']
        if not file:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="The 'cv' field is required.")
        serializer = UserCVSerializer(data=request.data)

        user = request.user
        if not user.is_authenticated:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_401_UNAUTHORIZED, message="User is not authenticated.")

        if serializer.is_valid():
            # Get the file from the request and parse it to extract the CV data
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
                #print("CV data saved successfully")
                db_cv = CV.getCVs(user)
                create_cv_data(db_cv, user.id)
            except ClientError as e:
                return ResponseFormatter.format_response(None, http_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(e))
            except Exception as e:
                # Handle other exceptions
                return ResponseFormatter.format_response(None, http_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(e))

            
            return ResponseFormatter.format_response(db_cv, http_code=status.HTTP_200_OK)
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
        print(cv_experiences)
        print(cv_educations)
        print(cv_skills)
        print(cv_certifications)
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
        
        cv = CV.getCVs(user)

        return ResponseFormatter.format_response(cv, http_code=status.HTTP_200_OK)
    

class CV():
    def getCVs(user):
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

        info = ""
        if cv_info.data:
            info = cv_info.data[0].get("info", "")
        cv = {
            'about': info,
            'cv_languages': cv_languages.data,
            'cv_experiences': cv_experiences.data,
            'cv_educations': cv_educations.data,
            'cv_skills': cv_skills.data,
            'cv_certifications': cv_certifications.data,
            'cv_projects': cv_projects.data
        }
        return cv

#edit function for update cv project is added inside vector_lang
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
            serializer = CVProjectSerializer(project)
            x= user_cv_project_update(user.id, project_id, serializer.data)
            print(x)
        except Exception as e:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(e))
        
        return ResponseFormatter.format_response(CVProjectSerializer(project).data, http_code=status.HTTP_200_OK)
    
#delete function for delete cv project is added inside vector_lang
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
                x= user_cv_project_delete(user.id, project_id)
                print(x)
            except Exception as e:
                return ResponseFormatter.format_response(None, http_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(e))
        
        return ResponseFormatter.format_response(None, http_code=status.HTTP_200_OK)

class UserCVProjectAddAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_401_UNAUTHORIZED, message="User is not authenticated.")
        project_name = request.data.get('project_name')
        description = request.data.get('description')
        languages = request.data.get('languages')
        if not project_name or not description or not languages:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="The 'project_name', 'description' and 'languages' fields are required.")
        try:
            project = CVProject.objects.create(
                user=user,
                project_name=project_name,
                description=description
            )
            project_data = {"project_name": project_name, "description": description, "languages": languages}
            create_cv_project(project_data=project_data, user_id=user.id)
            if not isinstance(languages, list):
                languages = [languages]
            for language in languages:
                CVProjectLanguage.objects.get_or_create(
                    project=project,
                    language=language
                )
        except Exception as e:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(e))
        
        return ResponseFormatter.format_response(CVProjectSerializer(project).data, http_code=status.HTTP_200_OK)

#deleting cv language inside pgvector is added to vector_lang and in here also
class UserAddorDeleteCVLanguageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_401_UNAUTHORIZED, message="User is not authenticated.")
        language = request.data.get('language')
        if not language:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="The 'language' field is required.")
        try:
            lang = CVLanguage.objects.get_or_create(
                user=user,
                language=language
            )
            ser = CVLanguageSerializer(lang, many=False)
            add_cv_language(user.id, ser)
        except Exception as e:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(e))
        
        return ResponseFormatter.format_response(None, http_code=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_401_UNAUTHORIZED, message="User is not authenticated.")
        language = request.data.get('language')
        if not language:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="The 'language' field is required.")
        try:
            object = CVLanguage.objects.get(
                user=user,
                language=language
            )
            object.delete()
            delete_cv_language(user.id, language)
        except Exception as e:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_404_NOT_FOUND, message=f"Language {language} not found.")
        
        return ResponseFormatter.format_response(None, http_code=status.HTTP_200_OK)
    
#deleting cv experience inside pgvector is added to vector_lang and in here also
class UserAddorDeleteCVExperienceAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_401_UNAUTHORIZED, message="User is not authenticated.")
        company_name = request.data.get('company_name')
        description = request.data.get('description')
        position = request.data.get('position')
        location = request.data.get('location')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        if not company_name or not description or not position or not location or not start_date:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="The 'company_name', 'description', 'position', 'location' and 'start_date' fields are required | 'end_date' is optional. Format: MM/YYYY")
        try:
            exp = CVExperience.objects.create(
                user=user,
                company_name=company_name,
                description=description,
                position=position,
                location=location,
                start_date=start_date,
                end_date=end_date
            )
            ser = CVExperienceSerializer(exp, many=False)
            create_cv_experience(ser, user.id)
        except Exception as e:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(e))
        
        return ResponseFormatter.format_response(None, http_code=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_401_UNAUTHORIZED, message="User is not authenticated.")
        experience_id = request.data.get('experience_id')
        if not experience_id:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="The 'experience_id' field is required.")
        try:
            object = CVExperience.objects.get(
                user=user,
                id=experience_id
            ) 
            object.delete()
            x = delete_pgvector_experience(experience_id, user.id)  # Use experience_id and user.id
            print(x)
        except Exception as e:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_404_NOT_FOUND, message=f"Experience not found.")
        
        return ResponseFormatter.format_response(None, http_code=status.HTTP_200_OK)
    
# it is not complete
class UserAddorDeleteCVEducationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_401_UNAUTHORIZED, message="User is not authenticated.")
        degree = request.data.get('degree')
        school = request.data.get('school')
        location = request.data.get('location')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        if not degree or not school or not location or not start_date:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="The 'degree', 'school', 'location' and 'start_date' fields are required | 'end_date' is optional. Format: MM/YYYY")
        try:
            edu = CVEducation.objects.create(
                user=user,
                degree=degree,
                school=school,
                location=location,
                start_date=start_date,
                end_date=end_date
            )
            ser = CVEducationSerializer(edu, many=False)
            create_cv_education(ser, user.id)
        except Exception as e:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(e))
        
        return ResponseFormatter.format_response(None, http_code=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_401_UNAUTHORIZED, message="User is not authenticated.")
        education_id = request.data.get('education_id')
        if not education_id:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="The 'education_id' field is required.")
        try:
            object = CVEducation.objects.get(
                user=user,
                id=education_id
            )
            object.delete()
            delete_cv_education(education_id=education_id, user_id=user.id)
        except Exception as e:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_404_NOT_FOUND, message=f"Education not found.")
        
        return ResponseFormatter.format_response(None, http_code=status.HTTP_200_OK)

# delete operation of pgvector insdie AddOrDeleteCVskill is created and added in here  
class UserAddorDeleteCVSkillAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_401_UNAUTHORIZED, message="User is not authenticated.")
        skill = request.data.get('skill')
        if not skill:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="The 'skill' field is required.")
        try:
            skill = CVSkill.objects.get_or_create(
                user=user,
                skill=skill
            )
            ser = CVSkillSerializer(skill, many=False)
            create_cv_skill(skill_data=ser, user_id=user.id)
        except Exception as e:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(e))
        
        return ResponseFormatter.format_response(None, http_code=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_401_UNAUTHORIZED, message="User is not authenticated.")
        skill = request.data.get('skill')
        if not skill:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="The 'skill' field is required.")
        try:
            object = CVSkill.objects.get(
                user=user,
                skill=skill
            )
            object.delete()
            delete_cv_skill(user.id, skill)
        except Exception as e:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_404_NOT_FOUND, message=f"Skill {skill} not found.")
        
        return ResponseFormatter.format_response(None, http_code=status.HTTP_200_OK)

#delete operation is created for cv_certification.
class UserAddorDeleteCVCertificationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_401_UNAUTHORIZED, message="User is not authenticated.")
        certification_name = request.data.get('certification_name')
        description = request.data.get('description')
        url = request.data.get('url')
        date = request.data.get('date')
        if not certification_name or not description or not url or not date:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="The 'certification_name', 'description', 'url' and 'date' fields are required.")
        try:
            cer = CVCertification.objects.create(
                user=user,
                certification_name=certification_name,
                description=description,
                url=url,
                date=date
            )
            ser = CVCertificationSerializer(cer, many=False)
            create_cv_certification(ser, user.id)
        except Exception as e:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(e))
        
        return ResponseFormatter.format_response(None, http_code=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_401_UNAUTHORIZED, message="User is not authenticated.")
        certification_id = request.data.get('certification_id')
        if not certification_id:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="The 'certification_id' field is required.")
        try:
            object = CVCertification.objects.get(
                user=user,
                id=certification_id
            )  
            object.delete()
                    # Call the function to delete the corresponding vector from pgvector
            delete_cv_certification(user.id, certification_id)
        except Exception as e:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_404_NOT_FOUND, message=f"Certification not found.")
        
        return ResponseFormatter.format_response(None, http_code=status.HTTP_200_OK)