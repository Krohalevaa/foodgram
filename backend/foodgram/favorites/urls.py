from django.urls import path
from . import views

app_name = 'favorites'

urlpatterns = [
    path('add/<int:recipe_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('remove/<int:recipe_id>/', views.remove_from_favorites, name='remove_from_favorites'),
    path('', views.FavoritesListView.as_view(), name='favorites_list'),
]