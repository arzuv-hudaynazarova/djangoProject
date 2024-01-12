from django.contrib import admin
from .models import *


# Custom admin view for Product
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'digital')  # Fields to be displayed in the list view
    list_filter = ('category', 'digital')  # Filters to be added to the sidebar
    search_fields = ('name', 'category__name')  # Fields to be searchable


# Register your models here
admin.site.register(Customer)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(Category)
