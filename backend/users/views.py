from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from .models import MyUser
from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate

class UserCreate(generics.CreateAPIView):
    queryset = MyUser.objects.all()
    serializer_class = UserSerializer

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': 'Invalid Credentials'}, status=400)
    
class WhoAmIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # The request.user will be set to the authenticated user by the JWTAuthentication class
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)