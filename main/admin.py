from django.contrib import admin

from .models import Category, Order, OrderItem, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'description', 'created_at')
	search_fields = ('name',)


class OrderItemInline(admin.TabularInline):
	model = OrderItem
	extra = 0
	readonly_fields = ('product', 'price', 'quantity', 'line_total')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ('name', 'category', 'price', 'stock', 'is_active', 'featured')
	list_filter = ('category', 'is_active', 'featured')
	search_fields = ('name', 'category__name')
	prepopulated_fields = {'slug': ('name',)}


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ('id', 'customer_name', 'status', 'total', 'created_at')
	list_filter = ('status', 'created_at')
	search_fields = ('customer_name', 'email')
	inlines = [OrderItemInline]
