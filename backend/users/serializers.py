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
    languages = serializers.DictField()
    class Meta:
        model = GitHubProject
        fields = ['id', 'project_name', 'description', 'user', 'languages', 'github_projects_languages']

    def get_languages(self, obj):
        # Assuming GitHubProjectLanguage has a foreign key to GitHubProject
        # and contains fields 'language' and 'percentage'
        languages = GitHubProjectLanguage.objects.filter(project=obj)
        return GitHubProjectLanguageSerializer(languages, many=True).data

    def create(self, validated_data):
        print(validated_data['languages'])
        # Step 2: Extract languages data if present
        languages_data = validated_data.pop('languages', {})

        # Step 3: Create the GitHubProject instance
        github_project = GitHubProject.objects.create(
            user=validated_data['user'],
            project_name=validated_data['project_name'],
            description=validated_data['description']
        )

        print(languages_data)
        # Step 4 & 5: Iterate over languages data and create GitHubProjectLanguage instances
        if languages_data != []:
            for language, percentage in languages_data.items():
                GitHubProjectLanguage.objects.create(
                    project=github_project,
                    language=language,
                    percentage=percentage)

        # Step 6: Return the GitHubProject instance
        return github_project

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
