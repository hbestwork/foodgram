from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from ingredients.models import Ingredient
from recipes.constants import (
    MAX_NAME,
    MIN_COOKING_TIME,
    MAX_COOKING_TIME,
    MIN_AMOUNT,
    MAX_AMOUNT,
    MAX_AMOUNT_ERROR,
    MIN_AMOUNT_ERROR,
    MAX_COOKING_TIME_ERROR,
    MIN_COOKING_TIME_ERROR,
)
from tags.models import Tag


class Recipe(models.Model):
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes',
    )

    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_NAME
    )

    image = models.ImageField(
        verbose_name='Изображение',
        upload_to=settings.IMAGE_FOLDER,
    )

    text = models.TextField(
        verbose_name='Описание',
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Инредиенты',
        through='RecipeIngredient'
    )

    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        through='RecipeTag'
    )

    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=(
            MinValueValidator(
                MIN_COOKING_TIME,
                message=MIN_COOKING_TIME_ERROR
            ),
            MaxValueValidator(
                MAX_COOKING_TIME,
                message=MAX_COOKING_TIME_ERROR
            ),
        )
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-id',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='recipe_ingredients',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=(
            MinValueValidator(
                MIN_AMOUNT,
                message=MIN_AMOUNT_ERROR
            ),
            MaxValueValidator(
                MAX_AMOUNT,
                message=MAX_AMOUNT_ERROR
            ),
        )
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient'
            ),
        ]

    def __str__(self):
        return (f'{self.recipe.name}: {self.ingredient.name} - '
                f'{self.amount} {self.ingredient.measurement_unit}')


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_tags',
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег',
        related_name='recipe_tags',
    )

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'tag',),
                name='unique_recipe_tag',
            )
        ]

    def __str__(self):
        return f'{self.recipe.name} - {self.tag.name}'


class Favorite(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorites'
    )

    recipe = models.ForeignKey(
        'recipes.Recipe',
        on_delete=models.CASCADE,
        related_name='favorites'
    )

    class Meta:
        verbose_name = 'Избранный'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_favorite',
            ),
        ]

    def __str__(self):
        return f'{self.user.username} likes {self.recipe.name}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_cart'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_cart'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_shopping_cart',
            ),
        ]

    def __str__(self):
        return f'{self.user.username} wants {self.recipe.name}'
