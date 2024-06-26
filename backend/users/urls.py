from django.urls import path
from .views import UserCreate, LoginView, WhoAmIView

urlpatterns = [
    path('register', UserCreate.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('whoami/', WhoAmIView.as_view(), name='whoami'),
]
