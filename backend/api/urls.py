from django.urls import path, include
from rest_framework.routers import SimpleRouter

from api.views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    CustomUserViewSet,
)

app_name = 'api'

api_router = SimpleRouter()
api_router.register('users', CustomUserViewSet)
api_router.register('ingredients', IngredientViewSet, basename='ingredient')
api_router.register('tags', TagViewSet)
api_router.register('recipes', RecipeViewSet, basename='recipe')

urlpatterns = [
    path('', include(api_router.urls)),
]
