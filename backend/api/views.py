from django.db import IntegrityError
from django.db.models import Sum
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import HttpResponse, get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import action

from users.models import CustomUser, Follow
from recipes.models import (
    Tag, Ingredient, Recipe,
    Favorite, ShoppingCart, RecipeIngredient
)

from .serializers import (
    TagSerializer, IngredientSerializer,
    RecipeSerializer, RecipeFullSerializer,
    UserFollowSerializer,
    CurrentUserSerializer,
    RecipeShortSerializer, FollowListSerializer
)
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsOwnerOrReadOnly


User = get_user_model()


class IngredientView(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny, ]
    queryset = Ingredient.objects.all()
    filter_backends = [DjangoFilterBackend, ]
    filter_class = IngredientFilter
    pagination_class = None


class TagView(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = [AllowAny, ]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrReadOnly, ]
    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination
    pagination_class.page_size = 6
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method not in ('POST', 'PUT', 'PATCH'):
            return RecipeSerializer
        return RecipeFullSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    def add_to_favorite(self, request, recipe):
        try:
            Favorite.objects.create(user=request.user, recipe=recipe)
        except IntegrityError:
            return Response(
                {'error'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = RecipeShortSerializer(recipe)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def delete_from_favorite(self, request, recipe):
        favorite = Favorite.objects.filter(user=request.user, recipe=recipe)
        if not favorite.exists():
            return Response(
                {'error'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('post', 'delete',),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            return self.add_to_favorite(request, recipe)
        return self.delete_from_favorite(request, recipe)

    def generate_shopping_cart_data(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__in_shopping_cart__user=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        print(ingredients)
        return ingredients

    def generate_ingredients_content(self, ingredients):
        content = 'Shopping list:'
        for ingredient in ingredients:
            content += (
                f"\n{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) - "
                f"{ingredient['amount']}")
        return content

    @action(detail=False)
    def download_shopping_cart(self, request):
        try:
            ingredients = self.generate_shopping_cart_data(request)
        except ShoppingCart.DoesNotExist:
            return Response(
                {'SHOPPING_CART_DOES_NOT_EXISTS'},
                status=status.HTTP_400_BAD_REQUEST
            )
        content = self.generate_ingredients_content(ingredients)
        response = HttpResponse(
            content, content_type='text/plain,charset=utf8'
        )
        response['Content-Disposition'] = 'attachment; filename=shopping_cart.txt'
        return response

    def add_to_shopping_cart(self, request, recipe, shopping_cart):
        if shopping_cart.recipes.filter(pk__in=(recipe.pk,)).exists():
            return Response(
                {'RECIPE_CANNOT_ADDED_TWICE'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        shopping_cart.recipes.add(recipe)
        serializer = self.get_serializer(recipe)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def remove_from_shopping_cart(self, request, recipe, shopping_cart):
        if not shopping_cart.recipes.filter(pk__in=(recipe.pk,)).exists():
            return Response(
                {'RECIPE_CANNOT_DELETE'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        shopping_cart.recipes.remove(recipe)
        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(methods=('post', 'delete',), detail=True)
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        shopping_cart = (
            ShoppingCart.objects.get_or_create(user=request.user)[0]
        )
        if request.method == 'POST':
            return self.add_to_shopping_cart(request, recipe, shopping_cart)
        return self.remove_from_shopping_cart(request, recipe, shopping_cart)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CurrentUserSerializer
    permission_classes = [AllowAny, ]

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated, )
    )
    def me(self, request):
        serializer = self.get_serializer(self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, pk):
        user = request.user
        following = get_object_or_404(CustomUser, id=pk)

        if request.method == 'POST':
            data = {
                'following': pk,
                'user': user.id
            }
            serializer = UserFollowSerializer(data=data,
                                            context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            Follow.objects.filter(user=user, following=following).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowListSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
