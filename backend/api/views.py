import datetime
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

from .serializers import (
    TagSerializer, IngredientSerializer,
    RecipeSerializer, RecipeFullSerializer,
    FollowListSerializer, UserFollowSerializer,
    CurrentUserSerializer, RecipeImageSerializer
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
                status=HTTP_400_BAD_REQUEST,
            )
        serializer = RecipeImageSerializer(recipe)
        return Response(
            serializer.data,
            status=HTTP_201_CREATED,
        )

    def delete_from_favorite(self, request, recipe):
        favorite = Favorite.objects.filter(user=request.user, recipe=recipe)
        if not favorite.exists():
            return Response(
                {'error'},
                status=HTTP_400_BAD_REQUEST,
            )
        favorite.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        methods=('get', 'delete',),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'GET':
            return self.add_to_favorite(request, recipe)
        return self.delete_from_favorite(request, recipe)

class ShoppingListViewSet(viewsets.GenericViewSet):
    NAME = 'ingredients__ingredient__name'
    MEASUREMENT_UNIT = 'ingredients__ingredient__measurement_unit'
    permission_classes = (IsAuthenticated,)
    serializer_class = RecipeImageSerializer
    queryset = ShoppingList.objects.all()
    http_method_names = ('get', 'delete',)

    def generate_shopping_list_data(self, request):
        recipes = (
            request.user.shopping_list.recipes.prefetch_related('ingredients')
        )
        return (
            recipes.order_by(self.NAME)
            .values(self.NAME, self.MEASUREMENT_UNIT)
            .annotate(total=Sum('ingredients__amount'))
        )

    def generate_ingredients_content(self, ingredients):
        content = ''
        for ingredient in ingredients:
            content += (
                f'{ingredient[self.NAME]}'
                f' ({ingredient[self.MEASUREMENT_UNIT]})'
                f' — {ingredient["total"]}\r\n'
            )
        return content

    @action(detail=False)
    def download_shopping_list(self, request):
        try:
            ingredients = self.generate_shopping_list_data(request)
        except ShoppingList.DoesNotExist:
            return Response(
                {'Shopping list doesnt exist'},
                status=HTTP_400_BAD_REQUEST
            )
        content = self.generate_ingredients_content(ingredients)
        response = HttpResponse(
            content, content_type='text/plain,charset=utf8'
        )
        response['Content-Disposition'] = f'attachment; filename={FILE_NAME}'
        return response

    def add_to_shopping_list(self, request, recipe, shopping_list):
        if shopping_list.recipes.filter(pk__in=(recipe.pk,)).exists():
            return Response(
                {'Cannot added twice'},
                status=HTTP_400_BAD_REQUEST,
            )
        shopping_list.recipes.add(recipe)
        serializer = self.get_serializer(recipe)
        return Response(
            serializer.data,
            status=HTTP_201_CREATED,
        )

    def remove_from_shopping_list(self, request, recipe, shopping_list):
        if not shopping_list.recipes.filter(pk__in=(recipe.pk,)).exists():
            return Response(
                {'Cannot delete'},
                status=HTTP_400_BAD_REQUEST,
            )
        shopping_list.recipes.remove(recipe)
        return Response(
            status=HTTP_204_NO_CONTENT,
        )

    @action(methods=('get', 'delete',), detail=True)
    def shopping_list(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        shopping_list = (
            ShoppingList.objects.get_or_create(user=request.user)[0]
        )
        if request.method == 'GET':
            return self.add_to_shopping_list(request, recipe, shopping_list)
        return self.remove_from_shopping_list(request, recipe, shopping_list)


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

    def post(self, request, following_id):
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
