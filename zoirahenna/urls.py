
from django.contrib import admin
from django.urls import path ,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.purchase.urls')), 
    path('', include('apps.ui.urls')), 
]
