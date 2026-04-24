from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy

from .models import MyUser, Subscription

admin.site.unregister(Group)
admin.site.unregister(TokenProxy)


@admin.register(MyUser)
class UserAdmin(UserAdmin):
    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
        'followers',
        'recipes',
    )
    search_fields = ('email', 'username',)

    @admin.display(description='Подписчики')
    def followers(self, obj):
        return obj.followers.count()

    @admin.display(description='Рецепты')
    def recipes(self, obj):
        return obj.recipes.count()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'follower',
    )
