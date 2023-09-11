from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView, SpectacularRedocView
)
from rest_framework.routers import DefaultRouter

from .views import (RecipeViewSet, 
                    ShoppingListViewSet, IngredientView, TagView, FollowApiView,
                    FollowListApiView)

app_name = 'api'
router = DefaultRouter()

router.register(r'recipes', RecipeViewSet,  basename='recipes')
router.register(r'recipes', ShoppingListViewSet, basename='shopping_cart')
router.register(r'ingredients', IngredientView, basename='ingredients')
router.register('tags', TagView, basename='tags')
urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'schema/redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc'
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
        name='following'
    ),
]
