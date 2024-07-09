from rest_framework import serializers
from .models import MyUser, CVLanguage, CVInformation, CVProject, CVProjectLanguage, GitHubProject, GitHubProjectLanguage, CVExperience, CVEducation, CVSkill, CVCertification

class CVLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVLanguage
        fields = ['id', 'language', 'user']

class CVInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVInformation
        fields = ['id', 'headline', 'user', 'info'] 

class CVExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVExperience
        fields = ['user', 'company_name', 'description', 'position', 'location', 'start_date', 'end_date']

class CVEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVEducation
        fields = ['user', 'degree', 'school', 'location', 'start_date', 'end_date']

class CVSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVSkill
        fields = ['user', 'skill']

class CVCertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVCertification
        fields = ['user', 'certification_name', 'description', 'url', 'date']

class CVProjectLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVProjectLanguage
        fields = ['id', 'language']

class CVProjectSerializer(serializers.ModelSerializer):
    cv_project_languages = CVProjectLanguageSerializer(many=True)

    class Meta:
        model = CVProject
        fields = ['id', 'project_name', 'description', 'user', 'cv_project_languages']
        extra_kwargs = {'user': {'write_only': True}}

    def create(self, validated_data):
        languages_data = validated_data.pop('cv_project_languages', [])
        cv_project = CVProject.objects.create(
            user=validated_data['user'],
            project_name=validated_data['project_name'],
            description=validated_data['description']
        )
    
        if languages_data != {}:
            for language_data in languages_data:
                CVProjectLanguage.objects.create(
                    project=cv_project,
                    language=language_data['language'])
    
        return cv_project

class GitHubProjectLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GitHubProjectLanguage
        fields = ['language', 'percentage']

class GitHubProjectSerializer(serializers.ModelSerializer):
    github_project_languages = GitHubProjectLanguageSerializer(many=True)

    class Meta:
        model = GitHubProject
        fields = ['id', 'project_name', 'description', 'user', 'github_project_languages']
        extra_kwargs = {'user': {'write_only': True}}

    def create(self, validated_data):

        languages_data = validated_data.pop('github_project_languages', [])

        github_project = GitHubProject.objects.create(
            user=validated_data['user'],
            project_name=validated_data['project_name'],
            description=validated_data['description']
        )
        print(languages_data)
        if languages_data != {}:
            for language_data in languages_data:
                GitHubProjectLanguage.objects.create(
                    project=github_project,
                    language=language_data['language'],
                    percentage=language_data['percentage'])

        return github_project

class UserSerializer(serializers.ModelSerializer):
    cv_languages = CVLanguageSerializer(many=True, read_only=True)
    cv_information = CVInformationSerializer(many=True, read_only=True)
    cv_experiences = CVExperienceSerializer(many=True, read_only=True)
    cv_education = CVEducationSerializer(many=True, read_only=True)
    cv_skills = CVSkillSerializer(many=True, read_only=True)
    cv_certifications = CVCertificationSerializer(many=True, read_only=True)
    cv_projects = CVProjectSerializer(many=True, read_only=True)
    github_projects = GitHubProjectSerializer(many=True, read_only=True)

    class Meta:
        model = MyUser
        fields = ['id', 'email', 'name', 'location', 'phone', 'github_url', 'linkedin_url', 'cv_languages', 'cv_information', 'cv_experiences', 'cv_education', 'cv_skills', 'cv_certifications', 'cv_projects', 'github_projects', 'password']
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
