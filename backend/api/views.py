from django.contrib.auth import get_user_model
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import permissions
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    AllowAny,
)

from api.filters import IngredientSearchFilter, RecipeFilterSet
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    RecipeInputSerializer,
    RecipeOutputSerializer,
    IngredientSerializer,
    TagSerializer,
    UserListSerializer,
    UserDetailSerializer,
    PutAvatarSerializer,
    DeleteAvatarSerializer,
    SubscribeOutputSerializer,
    SubscribeInputSerializer,
    UnsubscribeSerializer,
    PostFavoriteSerializer,
    DeleteFavoriteSerializer,
    PostShoppingCartSerializer,
    DeleteShoppingCartSerializer,
)
from api.utils import (
    make_short_link,
    make_shopping_cart,
    response_200,
    response_201,
    response_204,
)
from ingredients.models import Ingredient
from recipes.models import Recipe
from tags.models import Tag


def post_cart_or_favorite(request, pk, SerializerClass):
    recipe = get_object_or_404(Recipe, pk=pk)
    user = request.user
    data = {'user': user.id, 'recipe': recipe.id}
    serializer = SerializerClass(data=data)
    serializer.is_valid(raise_exception=True)
    data = serializer.save()
    return response_201(data)


def delete_cart_or_favorite(request, pk, SerializerClass):
    recipe = get_object_or_404(Recipe, pk=pk)
    user = request.user
    data = {'user': user.id, 'recipe': recipe.id}
    serializer = SerializerClass(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return response_204()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = [IngredientSearchFilter, ]
    search_fields = ['^name']


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilterSet

    def get_serializer_class(self):
        if self.request.method not in permissions.SAFE_METHODS:
            return RecipeInputSerializer
        return RecipeOutputSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = False
        return super().update(request, *args, **kwargs)

    @action(detail=True, url_path='get-link')
    def get_link(self, request, pk=None):
        data = make_short_link(request, 'recipes', pk)
        return response_200(data)

    @action(detail=True,
            url_path='favorite',
            methods=['POST'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        return post_cart_or_favorite(request, pk,
                                     PostFavoriteSerializer)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        return delete_cart_or_favorite(request, pk,
                                       DeleteFavoriteSerializer)

    @action(detail=True,
            url_path='shopping_cart',
            methods=['POST'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        return post_cart_or_favorite(request, pk,
                                     PostShoppingCartSerializer)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        return delete_cart_or_favorite(request, pk,
                                       DeleteShoppingCartSerializer)

    @action(detail=False,
            url_path='download_shopping_cart',
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        stream = make_shopping_cart(request.user)
        return FileResponse(stream, filename='shopping_cart.txt')


class CustomUserViewSet(UserViewSet):
    queryset = get_user_model().objects.all()
    pagination_class = CustomPagination
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        if self.action == 'retrieve':
            return UserDetailSerializer
        if self.action == 'subscribe':
            return None
        if self.action == 'me_avatar':
            return PutAvatarSerializer

        return super().get_serializer_class()

    @action(detail=False,
            url_path='me',
            permission_classes=[IsAuthenticated])
    def me(self, request):
        return response_200(UserDetailSerializer(request.user).data)

    @action(detail=False,
            url_path='me/avatar',
            methods=['PUT'],
            permission_classes=[IsAuthenticated])
    def me_avatar(self, request):
        user = request.user
        data = request.data
        serializer = PutAvatarSerializer(user, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response_200(serializer.data)

    @me_avatar.mapping.delete
    def delete_avatar(self, request):
        serializer = DeleteAvatarSerializer(
            data={},
            context={'user': request.user}
        )
        serializer.is_valid()
        serializer.save()
        return response_204()

    @action(detail=True,
            url_path='subscribe',
            methods=['POST'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        me = request.user
        author = get_object_or_404(self.queryset, id=id)
        serializer = SubscribeInputSerializer(
            data={'author': author.id, 'follower': me.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return response_201(data)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id):
        me = request.user
        author = get_object_or_404(self.queryset, id=id)
        serializer = UnsubscribeSerializer(
            data={'author': author.id, 'follower': me.id},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response_204()

    @action(detail=False,
            url_path='subscriptions',
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        qs = request.user.followings.all()
        serializer = SubscribeOutputSerializer(
            [e.author for e in qs],
            context={'request': request},
            many=True
        )
        paginated_data = self.paginate_queryset(queryset=serializer.data)
        result = self.get_paginated_response(paginated_data)
        return result
