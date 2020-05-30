from django.contrib import admin
from .models import Item, Orderitem, Order
# Register your models here.
admin.site.register(Item)
admin.site.register(Orderitem)
admin.site.register(Order)
