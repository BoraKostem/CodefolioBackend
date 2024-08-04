from django.shortcuts import render
from .github_parser import GithubRepo
# Create your views here.
from rest_framework import generics
from users.serializers import UserSerializer, GitHubProjectSerializer
from users.models import MyUser, GitHubProject
from rest_framework import status
from langchain.vector_lang import add_documents, delete_github_project
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from backend.utils import ResponseFormatter

class GithubRepoView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_401_UNAUTHORIZED, message="User is not authenticated.")

        try:
            user_projects = GitHubProject.objects.filter(user=user)
        except GitHubProject.DoesNotExist:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_404_NOT_FOUND, message="No projects found for the user.")

        projects_serializer = GitHubProjectSerializer(user_projects, many=True)
        return ResponseFormatter.format_response(projects_serializer.data, http_code=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        url = request.data.get('github_url')
        if not url:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="The 'github_url' field is required.")
        data_for_update = {'github_url': url}
        user_serializer = UserSerializer(user, data=data_for_update, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
        else:
            return ResponseFormatter.format_response(user_serializer.errors, http_code=status.HTTP_400_BAD_REQUEST)
        
        GitHubProject.objects.filter(user=user).delete()
        delete_github_project(user.id)
        
        username = url.split('/')[-1]
        repos = GithubRepo.fetch_github_repos(username)
        if type(repos) == ValueError:
            # Here you return an HTTP error response if a ValueError is caught
            return ResponseFormatter.format_response(str(repos), http_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Failed to fetch GitHub repositories.")
        
        for repo in repos:
            languages = []
            for language, percentage in repo['languages'].items():
                languages.append({'language': language, 'percentage': percentage})
            description = repo.get('description') or '-'
            project_data = {
                'user': user_serializer.data["id"],
                'project_name': repo['name'],
                'description': description,
                'github_project_languages': languages,
            }
            x = add_documents(project_data)
            print(x)
            #print(project_data['languages'])
            project_serializer = GitHubProjectSerializer(data=project_data)
            if project_serializer.is_valid():
                project_serializer.save()
            else:
                return ResponseFormatter.format_response(project_serializer.errors, http_code=status.HTTP_400_BAD_REQUEST)

        return ResponseFormatter.format_response(repos)
    def patch(self, request, *args, **kwargs):
        user = request.user
        project_id = request.data.get('project_id')
        new_description = request.data.get('description')

        if not project_id:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="The 'project_id' field is required.")
        if new_description is None:  # Explicitly checking for None allows empty strings as valid descriptions
            return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="The 'description' field is required.")

        try:
            project = GitHubProject.objects.get(id=project_id, user=user)
        except GitHubProject.DoesNotExist:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_404_NOT_FOUND, message="Project not found.")

        try:
            project.description = new_description
            project.save()
        except Exception as e:
            print(e)
            return ResponseFormatter.format_response(None, http_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Failed to update project description.")

        return ResponseFormatter.format_response(GitHubProjectSerializer(project).data, http_code=status.HTTP_200_OK)
    def delete(self, request):
        project_ids = request.data.get('project_ids')
        if not project_ids:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message="The 'project_ids' field is required.")

        if not isinstance(project_ids, list):
            project_ids = [project_ids]

        user = request.user
        try:
            GitHubProject.objects.filter(id__in=project_ids, user=user).delete()
            return ResponseFormatter.format_response(None, http_code=status.HTTP_200_OK, message="Project(s) deleted successfully.")
        except Exception as e:
            return ResponseFormatter.format_response(None, http_code=status.HTTP_400_BAD_REQUEST, message=str(e))