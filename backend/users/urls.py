from django.urls import path
from .views import UserCreate, LoginView, WhoAmIView
from github_parse.views import GithubRepoView
urlpatterns = [
    path('register', UserCreate.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('profile/github', GithubRepoView.as_view(), name='github'),
    path('whoami/', WhoAmIView.as_view(), name='whoami'),
]
