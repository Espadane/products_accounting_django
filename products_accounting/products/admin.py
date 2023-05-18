from django.contrib import admin
from .models import Product, Store, Inventory, Transfer


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']
    
@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'store', 'quantity']
    list_filter = ['store']
    search_fields = ['product__name']
    ordering = ['store', 'product']
    
@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ['product', 'store', 'difference', 'date', 'user', 'comment']
    list_filter = ['store', 'date']
    date_hierarchy = 'date'
    search_fields = ['product__name']
    ordering = ['date', 'product']