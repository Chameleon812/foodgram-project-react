from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView, SpectacularRedocView
)
from rest_framework.routers import DefaultRouter

from .views import (RecipeViewSet,
                    IngredientView, TagView, FollowApiView,
                    FollowListApiView)

app_name = 'api'
router = DefaultRouter()

router.register(r'recipes', RecipeViewSet,  basename='recipes')
router.register(r'ingredients', IngredientView, basename='ingredients')
router.register('tags', TagView, basename='tags')
urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'schema/redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc'
    ),
    path('auth/', include('djoser.urls.authtoken'), name='auth'),
    path(
        'users/<int:following_id>/subscribe/',
        FollowApiView.as_view(),
        name='following'
    ),
    path(
        'users/subscriptions/',
        FollowListApiView.as_view({'get': 'list'}),
        name='follow_list'
    ),
    path('', include(router.urls)),
    path('', include('djoser.urls'))
]
