from django.contrib import admin

from .models import Client, FinancialCategory, Product, Sale, SaleItem


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "created_at")
    inlines = [SaleItemInline]


admin.site.register(Client)
admin.site.register(FinancialCategory)
admin.site.register(Product)
