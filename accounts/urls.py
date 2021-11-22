from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('', views.IndexView.as_view(template_name='accounts/index.html'), name='index'),
    path('history', views.IndexView.as_view(template_name='accounts/history.html'), name='history'),
    path('<int:pk>/account', views.AccountView.as_view(template_name='accounts/transactions.html'), name='account_transactions'),
    path('history/<int:pk>/account', views.AccountView.as_view(template_name='accounts/transactions_history.html'), name='account_history'),
    path('<int:pk>/category', views.CategoryView.as_view(template_name = 'accounts/transactions.html'), name='category_transactions'),
    path('history/<int:pk>/category', views.CategoryView.as_view(template_name='accounts/transactions_history.html'), name='category_history'),
    path('<int:pk>/subcategory', views.SubcategoryView.as_view(template_name='accounts/transactions.html'), name='subcategory_transactions'),
    path('history/<int:pk>/subcategory', views.SubcategoryView.as_view(template_name = 'accounts/transactions_history.html'), name='subcategory_history'),
    path('<int:pk>/alias', views.AliasView.as_view(template_name = 'accounts/transactions.html'), name='alias_transactions'),
    path('history/<int:pk>/alias', views.AliasView.as_view(template_name='accounts/transactions_history.html'), name='alias_history'),
    path('upload/statement', views.upload_statement, name='upload_statement'),
    path('create/payees', views.create_payees, name='create_payees'),
    path('save/statement', views.save_statement, name='save_statement'),
    path('select/date', views.select_date, name='select_date'),
]
