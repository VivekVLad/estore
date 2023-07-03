from typing import Any
from django.contrib import admin, messages
from django.db.models.query import QuerySet
from django.db.models.aggregates import Count
from django.urls import reverse
from django.utils.html import format_html, urlencode
from django.http.request import HttpRequest
from . import models


class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            ('<20', 'Low')
        ]

    def queryset(self, request, queryset: QuerySet):
        if self.value() == '<20':
            return queryset.filter(inventory__lt=20)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['collection']
    prepopulated_fields = {
        'slug': ['title']
    }
    actions = ['clear_inventory']
    list_display = ['title','unit_price','inventory_status','collection_title']
    list_editable = ['unit_price']
    list_select_related = ['collection']
    list_filter = ['collection','last_update',InventoryFilter]
    list_per_page = 10
    search_fields = ['title']

    def collection_title(self,product):
        return product.collection.title

    @admin.display(ordering='inventory')
    def inventory_status(self,product):
        if product.inventory < 20:
            return 'Low'
        return 'Enough'
    
    @admin.action(description='Clear inventory')
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{updated_count} products were successfully updated.',
            messages.INFO
        ) 


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name','last_name','membership']
    list_editable = ['membership']
    list_per_page = 10
    ordering = ['first_name','last_name']
    search_fields = ['first_name__istartswith','last_name__istartswith']



class OrderAdminInline(admin.TabularInline):
    autocomplete_fields = ['product']
    min_num = 1
    max_num = 10
    model = models.OrderItem
    extra = 0


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    inlines = [OrderAdminInline]
    list_display = ['id','placed_at','customer']


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title','products_count']
    search_fields = ['title']

    @admin.display(ordering='products_count')
    def products_count(self,collection):
        url = (
            reverse('admin:store_product_changelist')
            + '?'
            + urlencode({
                'collection__id': str(collection.id)
            }))
        return format_html('<a href="{}">{} Products</a>', url, collection.products_count)

    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count = Count('product')

        )


 