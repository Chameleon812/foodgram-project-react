from django.utils import timezone
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import HttpResponse, get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status, viewsets, generics
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import action

from users.models import CustomUser, Follow
from recipes.models import (
    Tag, Ingredient, Recipe,
    Favorite, RecipeIngredient, ShoppingList
)
from .mixins import FavoriteShopDelGetMixin
from .serializers import (
    TagSerializer, IngredientSerializer,
    RecipeSerializer, RecipeFullSerializer,
    FavoriteSerializer, ShoppingListSerializer,
    FollowListSerializer, UserFollowSerializer,
    CurrentUserSerializer
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
        print(self.action)
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeFullSerializer
        return RecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context


class FavoriteApiView(FavoriteShopDelGetMixin, APIView):
    permission_classes = [IsAuthenticated, ]
    model = Favorite
    serializer = FavoriteSerializer


class ShoppingView(FavoriteShopDelGetMixin, APIView):
    permission_classes = [IsAuthenticated, ]
    model = ShoppingList
    serializer = ShoppingListSerializer


class DownloadShoppingCart(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        shopping_list = {}
        ingredients = RecipeIngredient.objects.filter(
            recipe__purchases__user=request.user
            ).values(
                     'name',
                     'measurement_unit'
            ).annotate(
                      ing_amount=sum('amount')
            )
        for ingredient in ingredients:
            amount = ingredient.ing_amount
            name = ingredient.name
            measurement_unit = ingredient.measurement_unit
            if name not in shopping_list:
                shopping_list[name] = {
                    'measurement_unit': measurement_unit,
                    'amount': amount
                }
        main_list = ([f"* {item}:{value['amount']}"
                      f"{value['measurement_unit']}\n"
                      for item, value in shopping_list.items()])
        today = timezone.now()
        main_list.append(f'\n From FoodGram with love, {today.year}')
        response = HttpResponse(main_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="BuyList.txt"'
        return response


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


class FollowApiView(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, following_id):
        user = request.user
        data = {
            'following': following_id,
            'user': user.id
        }
        serializer = UserFollowSerializer(data=data,
                                          context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, following_id):
        user = request.user
        following = get_object_or_404(CustomUser, id=following_id)
        Follow.objects.filter(user=user, following=following).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowListApiView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = FollowListSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    def get_queryset(self):
        user = self.request.user
        return CustomUser.objects.filter(following__user=user)
