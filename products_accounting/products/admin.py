from django.contrib import admin
from .models import Product, Store, Inventory, Transfer


admin.site.register(Product)
admin.site.register(Store)
admin.site.register(Inventory)
admin.site.register(Transfer)