from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.db.models import Sum
from rest_framework import status
from rest_framework.response import Response

from recipes.models import RecipeIngredient


def base_url(request):
    scheme = request.scheme
    host = request.get_host()
    url = f'{scheme}://{host}'
    return url


def delete_avatar(avatar):
    if avatar:
        path = Path(settings.MEDIA_ROOT) / avatar.path
        if path.exists():
            path.unlink()


def remove_file(file):
    if file:
        path = Path(file)
        if path.exists():
            path.unlink()


def make_short_link(request, route, pk):
    url = f'{base_url(request)}/{route}/{pk}'
    return {'short-link': url}


def make_shopping_cart(me):
    qs = RecipeIngredient.objects.filter(
        recipe__in=me.shopping_cart.values('recipe')
    ).values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).order_by(
        'ingredient__name'
    ).annotate(total=Sum('amount'))

    data = ''
    for e in qs:
        name = e['ingredient__name']
        total = e['total']
        mu = e['ingredient__measurement_unit']
        data += f'{name} - {total} {mu}\n'

    return BytesIO(data.encode())


def response_200(data):
    return Response(data, status=status.HTTP_200_OK)


def response_201(data):
    return Response(data, status=status.HTTP_201_CREATED)


def response_204():
    return Response(None, status=status.HTTP_204_NO_CONTENT)


def response_400(msg):
    detail = {'detail': msg}
    return Response(detail, status=status.HTTP_400_BAD_REQUEST)
