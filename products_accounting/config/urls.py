from django.contrib import admin
from django.urls import path, include
from products import views as products

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include("products.urls")),
    path('',include("accounts.urls")),
]
