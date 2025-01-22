from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class User(AbstractUser):
    """Модель для пользователя, расширяющая стандартную модель AbstractUser."""
    nickname: models.CharField = models.CharField(
        max_length=150, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    bio: models.TextField = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',
        blank=True,
    )

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель для подписки, которая связывает пользователей друг с другом."""
    user: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions')
    subscribed_to: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers')

    class Meta:
        unique_together = ('user', 'subscribed_to')

    def __str__(self):
        return f"{self.user.username} -> {self.subscribed_to.username}"
