"""Модуль URL для работы проекта."""

from django.urls import path, include

from django.contrib import admin
from django.conf import settings
from rest_framework.routers import DefaultRouter

from .views import (RecipeViewSet, TagViewSet, IngredientViewSet,
                    UserViewSet, FavoriteViewSet, ShopListViewSet,
                    UserAvatarUpdateView)


router = DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'favorites', FavoriteViewSet)
router.register(r'users', UserViewSet)
router.register(r'shopping_cart', ShopListViewSet, basename='shopping_cart')

app_name = 'api'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/me/', UserViewSet.as_view({'get': 'retrieve'}),
         name='user-me'),
    path('users/me/avatar/', UserAvatarUpdateView.as_view(),
         name='user-avatar-update'),
]

# if settings.DEBUG:
#     from django.conf import settings
#     from django.conf.urls.static import static

#     urlpatterns += static(settings.MEDIA_URL,
#                           document_root=settings.MEDIA_ROOT)
