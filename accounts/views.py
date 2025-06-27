# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .serializers import UserRegisterSerializer
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
User = get_user_model()
@csrf_exempt  # Disable CSRF for this view, not recommended for production


@api_view(['POST'])
@permission_classes([AllowAny])  # <-- This enables unauthenticated access
def register_user(request):
    serializer = UserRegisterSerializer(data=request.data)
    # print(serializer)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        print(token)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED)
    else:
        print(serializer.errors)  # 👈 add this line to see actual errors
        return Response(serializer.errors, status=400)



from django.contrib.auth import get_user_model, login
User = get_user_model()
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'Email and password required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user_obj = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    # Authenticate using username from user_obj
    user = authenticate(request, username=user_obj.username, password=password)

    if user is not None:
        login(request, user) 
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'message': 'Login successful!'})
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ProfileUpdateForm
@login_required

def user_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('user_profile')
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'my-account.html', {'form': form})