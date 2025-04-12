# urls.py
from django.urls import path
from .views import (
    add_dog_to_profile,
    index,
    breeds,
    dogs_list,
    dog_create,
    dog_update,
    dog_delete,
    dog_read,
    all_dogs,
    remove_dog_from_profile
)

app_name = 'dogs'

urlpatterns = [
    path('', index, name='index'),
    path('breeds/', breeds, name='breeds'),
    path('dogs/', dogs_list, name='dogs_list'),
    path('dogs/all/', all_dogs, name='all_dogs'),
    path('dogs/create/', dog_create, name='dog_create'),
    path('dogs/<int:pk>/', dog_read, name='dog_read'),
    path('dogs/<int:pk>/update/', dog_update, name='dog_update'),
    path('dogs/<int:pk>/delete/', dog_delete, name='dog_delete'),
    path('dogs/<int:dog_id>/add_to_profile/', add_dog_to_profile, name='add_to_profile'),
    path('dogs/<int:dog_id>/remove_from_profile/', remove_dog_from_profile, name='remove_dog_from_profile'),
]