from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer, UserAvatarSerializer
from .permissions import IsOwnerOrReadOnly


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления пользователями. Поддерживает CRUD."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrReadOnly]

    @action(detail=True,
            methods=['post'],
            serializer_class=UserAvatarSerializer)
    def change_avatar(self, request, pk=None):
        """Кастомное действие для изменения фото пользователя."""
        user = self.get_object()
        serializer = UserAvatarSerializer(data=request.data)
        if serializer.is_valid():
            user.avatar = serializer.validated_data['avatar']
            user.save()
            return Response({"status": "avatar updated"})
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        """Кастомное действие для подписки на пользователя."""
        user_to_subscribe = self.get_object()
        user = request.user
        if user == user_to_subscribe:
            return Response({"error": "Cannot subscribe to yourself"},
                            status=400)
        user.subscriptions.add(user_to_subscribe)
        return Response({"status": "subscribed successfully"})

    @action(detail=True, methods=['post'])
    def unsubscribe(self, request, pk=None):
        """Кастомное действие для отписки от пользователя."""
        user_to_unsubscribe = self.get_object()
        user = request.user
        user.subscriptions.remove(user_to_unsubscribe)
        return Response({"status": "unsubscribed successfully"})
