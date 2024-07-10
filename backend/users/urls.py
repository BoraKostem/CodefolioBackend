from django.urls import path
from .views import UserCreate, LoginView, WhoAmIView
from github_parse.views import GithubRepoView
from cv_parse.views import UserCVUploadAPIView, UserCVAPIView
urlpatterns = [
    path('register', UserCreate.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('profile/github', GithubRepoView.as_view(), name='github'),
    path('profile/cv/upload', UserCVUploadAPIView.as_view(), name='cv'),
    path('profile/cv', UserCVAPIView.as_view(), name='cv'),
    path('whoami/', WhoAmIView.as_view(), name='whoami'),
]
