from django.core.exceptions import ValidationError

def validate_not_self_follow(user, target_user):
    if user == target_user:
        raise ValidationError("Вы не можете подписаться на себя.")