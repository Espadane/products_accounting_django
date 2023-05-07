from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('stores/', views.stores, name='stores'),
    path('stores_detail/<int:store_id>', views.stores_detail, name='stores_detail'),
    path('product_detail/<int:product_id>/', views.product_detail, name='product_detail'),
    path('create_transfer/<int:product_id>/', views.create_transfer, 
         name='create_transfer'),
    path('upload_sales', views.upload_sales, name='upload_sales'),
    path('report_sales', views.report_sales, name='report_sales'),
    path('upload_receipt', views.upload_receipt, name='upload_receipt'),
    path('report_receipt', views.report_receipt, name='report_receipt'),
    path('upload_stock_products', views.upload_stock_products, name='upload_stock_products'),
    path('report_stock_products', views.report_stock_products, name='report_stock_products'),
    path('compare_products', views.compare_products, name='compare_products'),
    path('report_compare_products', views.report_compare_products, name='report_compare_products'),
]
