"""
Vantura Admin Panel Configuration
Full CRUD for products, categories, orders, reviews, and messages.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Category, SubCategory, Product, Order, OrderItem, Review, ContactMessage


class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 1
    fields = ('name', 'slug', 'is_active')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'product_count', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [SubCategoryInline]

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'slug', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'category__name')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'name', 'category', 'subcategory', 'price', 'stock', 'is_active', 'is_featured', 'is_founder_choice')
    list_display_links = ('image_preview', 'name')
    list_filter = ('category', 'subcategory', 'is_active', 'is_featured', 'is_founder_choice', 'is_new')
    search_fields = ('name', 'sku', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('price', 'stock', 'is_active', 'is_featured', 'is_founder_choice')
    readonly_fields = ('image_preview', 'created_at', 'updated_at')
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'slug', 'sku', 'category', 'subcategory')
        }),
        ('Description', {
            'fields': ('description', 'short_description', 'weight')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'compare_price', 'stock')
        }),
        ('Images', {
            'fields': ('image', 'image2', 'image3', 'image_preview')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured', 'is_founder_choice', 'is_new')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:50px;border-radius:4px;" />', obj.image.url)
        return '—'
    image_preview.short_description = 'Image'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'product_price', 'quantity', 'subtotal')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'full_name', 'email', 'status', 'total', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method', 'payment_status')
    search_fields = ('order_number', 'full_name', 'email', 'phone')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    list_editable = ('status',)
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'user', 'status', 'notes')
        }),
        ('Customer', {
            'fields': ('full_name', 'email', 'phone')
        }),
        ('Shipping Address', {
            'fields': ('address', 'city', 'state', 'country', 'zip_code')
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_status', 'subtotal', 'shipping_cost', 'total')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'title', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved')
    search_fields = ('user__username', 'product__name', 'title')
    list_editable = ('is_approved',)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read',)
    search_fields = ('name', 'email', 'subject')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    list_editable = ('is_read',)
