from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from users.serializers import UserSerializer
from rest_framework import serializers as drf_serializers
from drf_spectacular.utils import extend_schema, inline_serializer
from users import serializers


SignInRequest = inline_serializer(
    name="SignInRequest",
    fields={
        "email": drf_serializers.EmailField(),
        "password": drf_serializers.CharField(),
    }
)
SignInResponse = inline_serializer(
    name="SignInResponcse",
    fields={
        "message": drf_serializers.CharField(),
        "access_token": drf_serializers.CharField(),
        "refresh": drf_serializers.CharField(),
    }
)

SignupSuccess = inline_serializer(
    name="SignupSuccess",
    fields={"message": drf_serializers.CharField()},
)
# Validation or other errors: { "error": { ... } }
SignupError = inline_serializer(
    name="SignupError",
    fields={"error": drf_serializers.DictField()},
)

SignInUnauthorized = inline_serializer(
    name="SignInUnauthorized",
    fields={"error": drf_serializers.CharField()},
)

@extend_schema(
        summary="Register user",
        description="Create a new user account.",
        tags=["Authentication"],
        request=serializers.UserSerializer,
        responses={
            201: SignupSuccess,
            400: SignupError,
        }
)    


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Sign up successful"}, status=status.HTTP_201_CREATED)
    return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
        summary="Sign in",
        description="Obtain JWT access and refresh tokens using email and passord.",
        tags=["Authentication"],
        request=SignInRequest,
        responses={
            200: SignInResponse,
            401: SignInUnauthorized,
        }

)

@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def signin(request):
    email = request.data.get("email")  
    password = request.data.get("password")

    user = authenticate(email=email, password=password)
    if user:
        access = AccessToken.for_user(user)
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Sign in successful",
            "access_token": str(access),
            "refresh_token": str(refresh)
        }, status=status.HTTP_200_OK)
    return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["PUT"])
@permission_classes([permissions.IsAuthenticated])
def update_user(request, id):
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User updated", "user": serializer.data})
    
    return Response(serializer.errors, status=400)


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def delete_user(request, id):
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    user.delete()
    return Response({"message": "User deleted"}, status=204)