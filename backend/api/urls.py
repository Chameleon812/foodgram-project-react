from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (RecipeViewSet,
                    IngredientView, TagView, UserViewSet)

app_name = 'api'
router = DefaultRouter()

router.register(r'recipes', RecipeViewSet,  basename='recipes')
router.register(r'ingredients', IngredientView, basename='ingredients')
router.register('tags', TagView, basename='tags')
router.register(r'users', UserViewSet, basename='users')
urlpatterns = [
    path('auth/', include('djoser.urls.authtoken'), name='auth'),
    path('', include(router.urls)),
    path('', include('djoser.urls'))
]
