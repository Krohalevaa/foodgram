from django.contrib import admin
from django.urls import path, include

# from django.conf import settings
# from djoser.views import TokenCreateView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),  # Подключаем API пользователей
    path('api/', include('recipes.urls')),  # API рецептов
    path('api/', include('favorites.urls')),  # API избранного
    path('api/auth/', include('djoser.urls')),  # Маршруты djoser
    path('api/auth/', include('djoser.urls.authtoken')),
    # path('signin/', TokenCreateView.as_view(), name='signin'),  # Эндпоинт для аутентификации
]
# Обработка медиа-файлов в режиме отладки
# if settings.DEBUG:
#     from django.conf import settings
#     from django.conf.urls.static import static

#     urlpatterns += static(settings.MEDIA_URL,
#                           document_root=settings.MEDIA_ROOT)
