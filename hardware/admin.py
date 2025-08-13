from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Sale

# Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "current_stock", "reorder_level", "colored_reorder_status")
    list_filter = ("current_stock",)

    def colored_reorder_status(self, obj):
        if obj.current_stock <= obj.reorder_level:
            return format_html('<span style="color: red; font-weight: bold;">⚠️ Low stock! ({} left)</span>', obj.current_stock)
        return format_html('<span style="color: green; font-weight: bold;">✅ OK</span>')
    colored_reorder_status.short_description = "Stock Status"

# Sale Admin
@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("product", "quantity_sold", "total_price", "date_sold")
    list_filter = ("date_sold",)
