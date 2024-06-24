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

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

class CVLanguage(models.Model):
    user = models.ForeignKey(MyUser, related_name='cv_languages', on_delete=models.CASCADE)
    language = models.CharField(max_length=255)
    proficiency = models.CharField(max_length=255)

class CVInformation(models.Model):
    user = models.ForeignKey(MyUser, related_name='cv_information', on_delete=models.CASCADE)
    headline = models.CharField(max_length=255)
    info = models.TextField()

class CVProjectLanguage(models.Model):
    language = models.CharField(max_length=255)
    project = models.ForeignKey('CVProject', related_name='cv_projects_languages', on_delete=models.CASCADE)

class CVProject(models.Model):
    user = models.ForeignKey(MyUser, related_name='cv_projects', on_delete=models.CASCADE)
    project_name = models.CharField(max_length=255)
    description = models.TextField()

class GitHubProjectLanguage(models.Model):
    language = models.CharField(max_length=255)
    percentage = models.FloatField()
    project = models.ForeignKey('GitHubProject', related_name='github_projects_languages', on_delete=models.CASCADE)

class GitHubProject(models.Model):
    user = models.ForeignKey(MyUser, related_name='github_projects', on_delete=models.CASCADE)
    project_name = models.CharField(max_length=255)
    description = models.TextField()
