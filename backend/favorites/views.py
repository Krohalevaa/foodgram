from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAuthenticated

from .models import FavoriteRecipe
from .serializers import FavoriteSerializer


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.user or request.user.is_staff:
            return True
        return False


class FavoriteViewSet(viewsets.ModelViewSet):
    """Вьюсет для избранного"""
    queryset = FavoriteRecipe.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    @action(detail=False, methods=['post'], url_path='add_to_favorites')
    def add_to_favorites(self, request):
        user = request.user
        recipe_id = request.data.get('recipe_id')
        recipe = FavoriteRecipe.objects.get(id=recipe_id)
        favorite, created = FavoriteRecipe.objects.get_or_create(user=user,
                                                                 recipe=recipe)
        if created:
            return Response({"status": "added to favorites"})
        return Response({"status": "already in favorites"})

    @action(detail=False, methods=['get'], url_path='user_favorites')
    def user_favorites(self, request):
        user = request.user
        favorites = FavoriteRecipe.objects.filter(user=user)
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data)
