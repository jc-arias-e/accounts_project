from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/account', views.AccountView.as_view(), name='account_transactions'),
    path('<int:pk>/category', views.CategoryView.as_view(), name='category_transactions'),
    path('<int:pk>/subcategory', views.SubcategoryView.as_view(), name='subcategory_transactions'),
    path('<int:pk>/alias', views.AliasView.as_view(), name='alias_transactions'),
    path('upload/statement', views.upload_statement, name='upload_statement'),
    path('create/payees', views.create_payees, name='create_payees'),
    path('save/statement', views.save_statement, name='save_statement'),
    path('select/date', views.select_date, name='select_date'),
]
