# from django.db import models

# # Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class User(AbstractUser):
    nickname = models.CharField(max_length=150, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)
    # Если нужно, можно добавить дополнительные поля для пользователя
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',  # Уникальное имя для реверса
        blank=True,
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',  # Уникальное имя для реверса
        blank=True,
    )

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    subscribed_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscribers')

    class Meta:
        unique_together = ('user', 'subscribed_to')

    def __str__(self):
        return f"{self.user.username} -> {self.subscribed_to.username}"


# class CustomUser(AbstractUser):
#     email = models.EmailField(unique=True)

#     def __str__(self):
#         return self.username