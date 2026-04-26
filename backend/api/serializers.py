from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from api.utils import remove_file, delete_avatar
from api.validators import (
    non_empty_list_validator,
    non_blank_validator,
    non_repeating_validator,
    self_subscribe_validator,
    no_subscription_validator,
    need_subscription_validator,
    no_relation_validator,
    need_relation_validator,
)
from ingredients.models import Ingredient
from recipes.constants import (
    MAX_NAME,
    MIN_COOKING_TIME,
    MAX_COOKING_TIME,
    MIN_AMOUNT,
    MAX_AMOUNT,
    MIN_AMOUNT_ERROR,
    MAX_AMOUNT_ERROR,
    MIN_COOKING_TIME_ERROR,
    MAX_COOKING_TIME_ERROR
)
from recipes.models import Recipe, RecipeIngredient, ShoppingCart, Favorite
from tags.models import Tag
from users.models import Subscription


class RecipeBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class UserListSerializer(UserSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'avatar'
        )


class UserDetailSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        is_subscribed = False
        if 'request' in self.context:
            me = self.context['request'].user
            if me.is_authenticated:
                is_subscribed = me.followings.filter(author=obj).exists()

        return is_subscribed


class SubscribeOutputSerializer(UserDetailSerializer):
    recipes = RecipeBriefSerializer(many=True, read_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
            'recipes',
        )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context['request']

        qs = instance.recipes.all()
        if 'recipes_limit' in request.query_params:
            recipes_limit = int(request.query_params['recipes_limit'])
            qs = qs[:recipes_limit]

        ret['recipes'] = RecipeBriefSerializer(
            qs, many=True, context=self.context
        ).data
        ret['recipes_count'] = qs.count()

        return ret


class SubscribeInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('author', 'follower')

    def validate(self, data):
        author = data['author']
        follower = data['follower']
        self_subscribe_validator(author, follower)
        subscription = follower.followings.filter(author=author).first()
        no_subscription_validator(subscription)
        return data

    def save(self):
        author = self.validated_data['author']
        follower = self.validated_data['follower']
        author.followers.create(follower=follower)
        context = {'request': self.context['request']}
        return SubscribeOutputSerializer(author, context=context).data


class UnsubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('author', 'follower')

    def validate(self, data):
        author = data['author']
        follower = data['follower']
        subscription = follower.followings.filter(author=author).first()
        need_subscription_validator(subscription)
        return {'subscription': subscription}

    def save(self):
        subscription = self.validated_data['subscription']
        subscription.delete()


class PutAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = get_user_model()
        fields = ('avatar',)

    def save(self):
        old_avatar = self.instance.avatar
        self.instance.avatar = self.validated_data['avatar']
        self.instance.save()
        delete_avatar(old_avatar)

    def to_representation(self, instance):
        return {'avatar': instance.avatar.url}


class DeleteAvatarSerializer(serializers.Serializer):
    def validate(self, data):
        return self.context

    def save(self):
        user = self.validated_data['user']
        old_avatar = user.avatar
        user.avatar = None
        user.save()
        delete_avatar(old_avatar)


class PostCartOrFavoriteBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = None
        fields = ('user', 'recipe')

    def validate(self, data):
        relation = self.Meta.model.objects.filter(
            user=data['user'],
            recipe=data['recipe']
        ).first()
        no_relation_validator(relation)
        return data

    def save(self):
        self.Meta.model.objects.create(
            user=self.validated_data['user'],
            recipe=self.validated_data['recipe']
        )
        return RecipeBriefSerializer(self.validated_data['recipe']).data


class DeleteCartOrFavoriteBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = None
        fields = ('user', 'recipe')

    def validate(self, data):
        relation = self.Meta.model.objects.filter(
            user=data['user'],
            recipe=data['recipe']
        ).first()
        need_relation_validator(relation)
        return {'relation': relation}

    def save(self):
        relation = self.validated_data['relation']
        relation.delete()


class PostShoppingCartSerializer(PostCartOrFavoriteBaseSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')


class PostFavoriteSerializer(PostCartOrFavoriteBaseSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')


class DeleteShoppingCartSerializer(DeleteCartOrFavoriteBaseSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')


class DeleteFavoriteSerializer(DeleteCartOrFavoriteBaseSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    name = serializers.CharField(required=False)
    measurement_unit = serializers.CharField(required=False)
    amount = serializers.IntegerField(
        max_value=MAX_AMOUNT,
        min_value=MIN_AMOUNT,
        error_messages={
            'max_value': MAX_AMOUNT_ERROR,
            'min_value': MIN_AMOUNT_ERROR
        }
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)

    def to_representation(self, instance):
        data = IngredientSerializer(instance.ingredient).data
        data['amount'] = instance.amount
        return data


class RecipeOutputSerializer(serializers.ModelSerializer):
    author = UserDetailSerializer(default=serializers.CurrentUserDefault())

    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients',
        many=True,
    )

    tags = TagSerializer(
        many=True
    )

    image = Base64ImageField(validators=[non_blank_validator])

    is_favorited = serializers.SerializerMethodField()

    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'name', 'image', 'text', 'ingredients',
            'tags', 'cooking_time', 'is_favorited', 'is_in_shopping_cart'
        )
        read_only_fields = ('__all__',)

    def get_is_favorited(self, obj):
        if self.context:
            me = self.context['request'].user
            if me.is_authenticated:
                return me.favorites.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        if self.context:
            me = self.context['request'].user
            if me.is_authenticated:
                return me.shopping_cart.filter(recipe=obj).exists()
        return False


class RecipeInputSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=MAX_NAME)

    image = Base64ImageField(validators=[non_blank_validator])

    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients',
        many=True,
    )

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )

    cooking_time = serializers.IntegerField(
        max_value=MAX_COOKING_TIME,
        min_value=MIN_COOKING_TIME,
        error_messages={
            'max_value': MAX_COOKING_TIME_ERROR,
            'min_value': MIN_COOKING_TIME_ERROR
        }
    )

    class Meta:
        model = Recipe
        fields = (
            'name', 'image', 'text', 'ingredients',
            'tags', 'cooking_time',
        )

    def validate_ingredients(self, value):
        non_empty_list_validator(value)
        non_repeating_validator({i['id'] for i in value}, value)
        return value

    def validate_tags(self, value):
        non_empty_list_validator(value)
        non_repeating_validator(set(value), value)
        return value

    def create_ingredients(self, ingredients, recipe):
        recipe.recipe_ingredients.all().delete()
        recipeingredients = []
        for ingredient in ingredients:
            item = RecipeIngredient(
                ingredient=ingredient['id'],
                recipe=recipe,
                amount=ingredient['amount']
            )
            recipeingredients.append(item)
        RecipeIngredient.objects.bulk_create(recipeingredients)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        old_image = instance.image.path
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
        super().update(instance, validated_data)
        remove_file(old_image)
        instance.tags.set(tags)
        self.create_ingredients(ingredients, instance)
        return instance

    def to_representation(self, instance):
        data = RecipeOutputSerializer(instance).data
        return data
