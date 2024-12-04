from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser
from rest_framework.generics import CreateAPIView
from .serializers import CustomUserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate


# base views below
class HomeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        user_data = {
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_number": user.phone_number  
        }
        serializer = CustomUserSerializer(user)
        return Response({"user": serializer.data})

# authentication below
class CreateUserView(APIView): 
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)      
        if serializer.is_valid():
            serializer.save()
            # or get token immediately  
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response({"error":"All fields are required"}, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(username=username, password=password)
        if not user:
            return Response({"error":"Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        refresh = RefreshToken.for_user(user)
        # res = {"refresh": str(refresh), "access": str(refresh.access_token)}
        response = Response({"response": "You're logged in!"}, status=status.HTTP_200_OK)
        response.set_cookie(
            key="access_token",
            value=str(refresh.access_token),
            httponly=True,  # Makes it only accessible via HTTP, not JavaScript
            secure=True,  # Set to True for production to ensure cookie is sent over HTTPS
            samesite='Lax',  # Helps prevent CSRF attacks
            max_age=60*60*24*7
        )
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=60*60*24*30
        )
        return response
class LogoutView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        response = Response({"response": "You're logged out!"}, status=status.HTTP_200_OK)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response
class RefreshTokenView(APIView):
    permission_classes = [AllowAny] 
    def get(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            response = Response({"error":"Refresh token was not provided"}, status=status.HTTP_400_BAD_REQUEST)
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")
            return response
        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            response = Response({"message":"Access token is updated"}, status=status.HTTP_200_OK)
            response.set_cookie(
                key="access_token",
                value=new_access_token,
                httponly=True,
                secure=True,
                samesite='Lax',
                max_age=60*60*24*7,
            )
            return response
        except Exception as e:
            response = Response({"error":"Refresh token is invalid"}, status=status.HTTP_400_BAD_REQUEST) 
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")
            return response
# for the front end
class CheckAuthenticationView(APIView):
    #Checking is authenticated or not(for the front end to show pages)
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"is_authenticated":request.user.is_authenticated}, status=status.HTTP_200_OK)            