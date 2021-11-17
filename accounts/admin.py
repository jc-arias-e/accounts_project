from django.contrib import admin

from .models import Category, Subcategory, Account, Alias

admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Account)
admin.site.register(Alias)
