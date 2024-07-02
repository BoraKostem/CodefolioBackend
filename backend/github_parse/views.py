from django.shortcuts import render
from .github_parser import GithubRepo
# Create your views here.
from rest_framework import generics
from users.serializers import UserSerializer, GitHubProjectSerializer
from users.models import MyUser, GitHubProject
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from backend.utils import ResponseFormatter

class GithubRepoView(APIView):
    permission_classes = [IsAuthenticated]

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

        username = url.split('/')[-1]
        repos = GithubRepo.fetch_github_repos(username)
        if type(repos) == ValueError:
            # Here you return an HTTP error response if a ValueError is caught
            return ResponseFormatter.format_response(str(repos), http_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Failed to fetch GitHub repositories.")
        
        for repo in repos:
            description = repo.get('description') or '-'
            project_data = {
                'user': user_serializer.data["id"],
                'project_name': repo['name'],
                'description': description,
                'languages': repo['languages'],
            }
            #print(project_data['languages'])
            project_serializer = GitHubProjectSerializer(data=project_data)
            if project_serializer.is_valid():
                project_serializer.save()
            else:
                return ResponseFormatter.format_response(project_serializer.errors, http_code=status.HTTP_400_BAD_REQUEST)

        return ResponseFormatter.format_response(repos)