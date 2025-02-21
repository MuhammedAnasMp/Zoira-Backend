from django.urls import path
from .views import dashboard
from .views import materials_list, add_material, add_purchased_batch
urlpatterns = [
    path('', dashboard, name='dashboard'),


    path('materials/', materials_list, name='materials_list'),
    path('materials/add/', add_material, name='add_material'),
    path('batches/add/', add_purchased_batch, name='add_purchased_batch'),
]
