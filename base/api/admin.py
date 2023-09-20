from django.contrib import admin
from .models import *


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'parent_cat', 'updated_at', 'total_views']
    ordering = ('name',)
    search_fields = ("name", "id", )  # "parent_cat_id", )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'url', 'sale']
    ordering = ('-sale',)
    search_fields = ("name", "id", )  # 'category')  🔥


@admin.register(Visitors)
class VisitorsAdmin(admin.ModelAdmin):
    list_display = ['id', 'ip', 'count', 'last_visit']
    ordering = ('-count',)
    search_fields = ("ip", "id", )


@admin.register(Constants)
class ConstantsAdmin(admin.ModelAdmin):
    list_display = ['sale', 'paginate', 'pages']
