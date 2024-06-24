from rest_framework import serializers
from .models import MyUser, CVLanguage, CVInformation, CVProject, CVProjectLanguage, GitHubProject, GitHubProjectLanguage

class CVLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVLanguage
        fields = ['id', 'language', 'proficiency']

class CVInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVInformation
        fields = ['id', 'headline', 'info']

class CVProjectLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVProjectLanguage
        fields = ['id', 'language']

class CVProjectSerializer(serializers.ModelSerializer):
    cv_projects_languages = CVProjectLanguageSerializer(many=True, read_only=True)

    class Meta:
        model = CVProject
        fields = ['id', 'project_name', 'description', 'cv_projects_languages']

class GitHubProjectLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GitHubProjectLanguage
        fields = ['id', 'language', 'percentage']

class GitHubProjectSerializer(serializers.ModelSerializer):
    github_projects_languages = GitHubProjectLanguageSerializer(many=True, read_only=True)

    class Meta:
        model = GitHubProject
        fields = ['id', 'project_name', 'description', 'github_projects_languages']

class UserSerializer(serializers.ModelSerializer):
    cv_languages = CVLanguageSerializer(many=True, read_only=True)
    cv_information = CVInformationSerializer(many=True, read_only=True)
    cv_projects = CVProjectSerializer(many=True, read_only=True)
    github_projects = GitHubProjectSerializer(many=True, read_only=True)

    class Meta:
        model = MyUser
        fields = ['id', 'email', 'name', 'location', 'phone', 'github_url', 'linkedin_url', 'cv_languages', 'cv_information', 'cv_projects', 'github_projects', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = MyUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name'],
            location=validated_data.get('location', ''),
            phone=validated_data.get('phone', ''),
            github_url=validated_data.get('github_url', ''),
            linkedin_url=validated_data.get('linkedin_url', '')
        )
        return user
