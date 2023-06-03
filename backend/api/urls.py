from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView, SpectacularRedocView
)
from rest_framework.routers import DefaultRouter

from .views import (DownloadShoppingCart, FavoriteApiView, RecipeViewSet, 
                    ShoppingView, IngredientView, TagView, FollowApiView,
                    FollowListApiView)

app_name = 'api'
router = DefaultRouter()

router.register('recipes', RecipeViewSet)
router.register(r'ingredients', IngredientView, basename='ingredients')
router.register('tags', TagView, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'schema/redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc'
    ),
    path(
        'recipes/download_shopping_cart/',
        DownloadShoppingCart.as_view(),
        name='download_shoppong_cart'
    ),
    path(
        'recipes/<int:favorite_id>/favorite/',
        FavoriteApiView.as_view(),
        name='favorite'
    ),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        ShoppingView.as_view(),
        name='shop_cart'
    ),
    path(
        'users/subscriptions/',
        FollowListApiView.as_view(),
        name='follow_list'
    ),
    path('auth/', include('djoser.urls.authtoken'), name='auth'),
    path(
        'users/<int:following_id>/subscribe/',
        FollowApiView.as_view(),
        name='follow_list'
    ),
    path('users/', include('djoser.urls')),
]
