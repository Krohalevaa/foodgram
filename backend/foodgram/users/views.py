# from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import User
from .forms import SubscribeForm
from .validators import validate_not_self_follow
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

class UserProfileView(View):
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        recipes = user.recipes.all()
        return render(request, 'users/profile.html', {'user': user, 'recipes': recipes})

class SubscribeView(View):
    def post(self, request, user_id):
        target_user = get_object_or_404(User, id=user_id)
        validate_not_self_follow(request.user, target_user)
        if request.user.is_authenticated:
            # Логика подписки/отписки
            # ...
            return redirect('user_profile', username=target_user.username)
        return redirect('login')
