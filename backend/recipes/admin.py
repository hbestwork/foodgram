from django.contrib import admin

from recipes.models import (
    Recipe,
    RecipeTag,
    RecipeIngredient,
    Favorite,
    ShoppingCart
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'favorited_by'
    )
    list_filter = ('tags',)
    search_fields = ('name', 'author__username', 'author__email',)
    # filter_vertical = ('tags',)
    inlines = (RecipeTagInline, RecipeIngredientInline,)

    @admin.display(description='В избранном')
    def favorited_by(self, obj):
        return obj.favorites.count()


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'recipe',
        'ingredient',
        'amount'
    )


@admin.register(RecipeTag)
class RecipeTagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'recipe',
        'tag',
    )


@admin.register(Favorite)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
    )
