from django.urls import path
from .views import UserProfileView, SubscribeView
from djoser import views as djoser_views

urlpatterns = [
    path('<str:username>/', UserProfileView.as_view(), name='user_profile'),
    path('subscribe/<int:user_id>/', SubscribeView.as_view(), name='subscribe'),
    # path('register/', djoser_views.UserCreate.as_view(), name='user-create'),
    # path('login/', djoser_views.TokenCreate.as_view(), name='token-create'),
    # path('logout/', djoser_views.TokenDestroy.as_view(), name='token-destroy'),

]