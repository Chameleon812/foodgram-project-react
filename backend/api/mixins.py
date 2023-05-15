from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status

from recipes.models import Recipe


class FavoriteShopDelGetMixin:

    def delete(self, request, obj_id):
        mod = self.model
        user = request.user
        recipe = get_object_or_404(Recipe, id=obj_id)
        mod.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get(self, request, obj_id):
        user = request.user
        data = {
            'recipe': obj_id,
            'user': user.id
        }
        serializer = self.serializer(data=data,
                                     context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
