from django.urls import path
from .views import dashboard
from .views import materials_list, add_material, add_purchased_batch
from.views import *
from .views import sales_and_customers, delete_sale, delete_customer ,create_customer ,create_sale
urlpatterns = [
    path('', dashboard, name='dashboard'),


    path('materials/', materials_list, name='materials_list'),
    path('materials/add/', add_material, name='add_material'),
    path('batches/add/', add_purchased_batch, name='add_purchased_batch'),



   path('sales-and-customers/', sales_and_customers, name='sales_and_customers'),
    path('create-customer/', create_customer, name='create_customer'),
    path('create-sale/', create_sale, name='create_sale'),
    
    path('create-henna-type/', create_henna_type, name='create_henna_type'),
    path('delete-sale/<int:sale_id>/', delete_sale, name='delete_sale'),
    path('delete-customer/<int:customer_id>/', delete_customer, name='delete_customer'),
    path('delete-henna-type/<int:henna_id>/', delete_henna_type, name='delete_henna_type'),

]