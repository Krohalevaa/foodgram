from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from favorites.views import FavoriteViewSet
from recipes.views import RecipeViewSet, TagViewSet, IngredientViewSet
from shoplist.views import ShopListViewSet
from users.views import UserViewSet

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'shoplist', ShopListViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/', include('djoser.urls')),  # Маршруты djoser
    path('api/auth/', include('djoser.urls.authtoken')),
]
# Обработка медиа-файлов в режиме отладки
# if settings.DEBUG:
#     from django.conf import settings
#     from django.conf.urls.static import static

#     urlpatterns += static(settings.MEDIA_URL,
#                           document_root=settings.MEDIA_ROOT)
