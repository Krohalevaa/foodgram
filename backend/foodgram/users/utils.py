def get_user_recipes(user):
    return user.recipes.all()

def is_subscribed(user, target_user):
    return target_user in user.subscriptions.all()