from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class MyUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    profile_photo = models.URLField(blank=True, null=True)
    profile_background = models.URLField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

class CVLanguage(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False)
    user = models.ForeignKey(MyUser, related_name='cv_languages', on_delete=models.CASCADE)
    language = models.CharField(max_length=255)
    is_manual_added = models.BooleanField(default=True)
    class Meta:
        unique_together = ('user', 'language',)

class CVInformation(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False)
    user = models.ForeignKey(MyUser, related_name='cv_information', on_delete=models.CASCADE)
    headline = models.CharField(max_length=255)
    info = models.TextField()
    class Meta:
        unique_together = ('user', 'headline',)

class CVExperience(models.Model):
    user = models.ForeignKey(MyUser, related_name='cv_experiences', on_delete=models.CASCADE)
    company_name = models.TextField()
    description = models.TextField()
    position = models.TextField()
    location = models.TextField()
    start_date = models.CharField(max_length=57)  # Format: MM/YYYY
    end_date = models.CharField(max_length=57, null=True, blank=True)  # Format: MM/YYYY
    is_manual_added = models.BooleanField(default=True)

class CVEducation(models.Model):
    user = models.ForeignKey(MyUser, related_name='cv_education', on_delete=models.CASCADE)
    degree = models.TextField()
    school = models.TextField()
    location = models.TextField()
    start_date = models.CharField(max_length=57)  # Format: MM/YYYY
    end_date = models.CharField(max_length=57, null=True, blank=True)  # Format: MM/YYYY
    is_manual_added = models.BooleanField(default=True)

class CVSkill(models.Model):
    user = models.ForeignKey(MyUser, related_name='cv_skills', on_delete=models.CASCADE)
    skill = models.TextField()
    is_manual_added = models.BooleanField(default=True)
    class Meta:
        unique_together = ('user', 'skill',)

class CVCertification(models.Model):
    user = models.ForeignKey(MyUser, related_name='cv_certifications', on_delete=models.CASCADE)
    certification_name = models.TextField()
    description = models.TextField(null=True, blank=True)  # Optional
    url = models.URLField(null=True, blank=True)  # Optional
    date = models.CharField(max_length=58)
    is_manual_added = models.BooleanField(default=True)

class CVProjectLanguage(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False)
    language = models.TextField()
    project = models.ForeignKey('CVProject', related_name='cv_project_languages', on_delete=models.CASCADE)
    class Meta:
        unique_together = ('language', 'project',)

class CVProject(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False)
    user = models.ForeignKey(MyUser, related_name='cv_projects', on_delete=models.CASCADE)
    project_name = models.TextField()
    description = models.TextField()
    is_manual_added = models.BooleanField(default=True)

class GitHubProjectLanguage(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False)
    language = models.CharField(max_length=255)
    percentage = models.FloatField()
    project = models.ForeignKey('GitHubProject', related_name='github_project_languages', on_delete=models.CASCADE)
    class Meta:
        unique_together = ('language', 'project',)

class GitHubProject(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False)
    user = models.ForeignKey(MyUser, related_name='github_projects', on_delete=models.CASCADE)
    project_name = models.CharField(max_length=255)
    description = models.TextField()
