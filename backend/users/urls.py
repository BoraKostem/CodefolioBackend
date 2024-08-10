from django.urls import path
from .views import UserCreate, LoginView, WhoAmIView, ProfileView, PublicProfileView, PublicSearchView
from github_parse.views import GithubRepoView
from langchain.views import ChatView
from cv_parse.views import UserCVUploadAPIView, UserCVAPIView, UserCVProjectEditAPIView, UserCVProjectDeleteAPIView, UserCVProjectAddAPIView, UserAddorDeleteCVSkillAPIView, UserAddorDeleteCVCertificationAPIView, UserAddorDeleteCVEducationAPIView, UserAddorDeleteCVExperienceAPIView, UserAddorDeleteCVLanguageAPIView
urlpatterns = [
    path('register', UserCreate.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('profile/github', GithubRepoView.as_view(), name='github'),
    path('profile/cv/upload', UserCVUploadAPIView.as_view(), name='cv'),
    path('profile/cv', UserCVAPIView.as_view(), name='cv'),
    path('profile/cv/project/edit', UserCVProjectEditAPIView.as_view(), name='cv_project_edit'),
    path('profile/cv/project/delete', UserCVProjectDeleteAPIView.as_view(), name='cv_project_delete'),
    path('profile/cv/project/add', UserCVProjectAddAPIView.as_view(), name='cv_project_add'),
    path('profile/cv/skill', UserAddorDeleteCVSkillAPIView.as_view(), name='cv_skill'),
    path('profile/cv/certification', UserAddorDeleteCVCertificationAPIView.as_view(), name='cv_certification'),
    path('profile/cv/education', UserAddorDeleteCVEducationAPIView.as_view(), name='cv_education'),
    path('profile/cv/experience', UserAddorDeleteCVExperienceAPIView.as_view(), name='cv_experience'),
    path('profile/cv/language', UserAddorDeleteCVLanguageAPIView.as_view(), name='cv_language'),
    path('profile/photo', ProfileView.as_view(), name='profile_photo'),
    path('profile/public', PublicProfileView.as_view(), name='public_profile'),
    path('search', PublicSearchView.as_view(), name='search'),
    path('whoami', WhoAmIView.as_view(), name='whoami'),
    path('chat', ChatView.as_view(), name='chat'),
]
