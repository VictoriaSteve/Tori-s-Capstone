from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from users.serializers import UserSerializer


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Sign up successful"}, status=status.HTTP_201_CREATED)
    return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def signin(request):
    username = request.data.get("username")  
    password = request.data.get("password")

    user = authenticate(username=username, password=password)
    if user:
        access = AccessToken.for_user(user)
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Sign in successful",
            "access_token": str(access),
            "refresh_token": str(refresh)
        }, status=status.HTTP_200_OK)
    return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


# @api_view(["PUT"])
# @permission_classes([permissions.IsAuthenticated])
# def update_user(request):
#     user = request.user
#     serializer = UserSerializer(user, data=request.data, partial=True)
#     if serializer.is_valid():
#         serializer.save()
#         return Response({"message": "User updated", "user": serializer.data}, status=status.HTTP_200_OK)
#     return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# @api_view(["DELETE"])
# @permission_classes([permissions.IsAuthenticated])
# def delete_user(request):
#     user = request.user
#     user.delete()
#     return Response({"message": "User deleted"}, status=status.HTTP_204_NO_CONTENT)