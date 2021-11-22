from django.test import TestCase, RequestFactory
from decimal import Decimal
import datetime

from .models import Transaction, Alias, Category, Subcategory, Account
from .views import AccountView, CategoryView


class IndexViewTest(TestCase):
    def setUp(self):
        account = Account.objects.create(name='Mastercard', type='L', initial_balance=30.10)
        account2 = Account.objects.create(name='Natwest', type='A', initial_balance=500)
        categ = Category.objects.create(name='Other', type='E')
        categ2 = Category.objects.create(name='Food', type='E')
        subcateg = Subcategory.objects.create(name='Meals', category=categ2)
        alias = Alias.objects.create(name='CURZON CINEMA', category=categ)
        alias2 = Alias.objects.create(name='CHIPOTLE', category=categ2, subcategory=subcateg)
        transaction = Transaction.objects.create(date=datetime.date(2021, 11, 3), alias=alias, amount=10.50, account=account)
        transaction2 = Transaction.objects.create(date=datetime.date(2021, 10, 27), alias=alias2, amount=7.00, account=account)
        self.factory = RequestFactory()
        
    def test_index(self):
        response = self.client.get('/accounts/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['balance_date'], datetime.date(2021, 11, 3))
        self.assertEqual(response.context['assets'], Decimal('500'))
        self.assertEqual(response.context['liabilities'], Decimal('47.60'))
        self.assertEqual(response.context['capital'], Decimal('452.40'))
        self.assertEqual(response.context['balance_profit'], Decimal('-10.50'))
        self.assertEqual(response.context['income'], 0)
        self.assertEqual(response.context['expenses'], Decimal('10.50'))
        self.assertEqual(response.context['profit'], Decimal('-10.50'))
        
    def test_account_transactions(self):
        request = self.factory.get('/accounts/1/account')
        view = AccountView()
        view.setup(request)
        # check account.id = 1
        view.kwargs['pk'] = 1
        view.object_list = []
        context = view.get_context_data()
        self.assertEqual(context['transaction_list'].count(), 2)
        # check first transaction
        self.assertEqual(context['transaction_list'][0].alias.name, 'CURZON CINEMA')
        self.assertEqual(context['transaction_list'][0].amount, Decimal('10.50'))       
        # check account total and flag 'is_account'
        self.assertEqual(context['balance'], Decimal('47.60'))
        self.assertEqual(context['is_account'], True)
        
    def test_category_transactions(self):
        request = self.factory.get('/accounts/1/category')
        view = CategoryView()
        view.setup(request)
        # check category.id = 1
        view.kwargs['pk'] = 1       
        view.object_list = []
        context = view.get_context_data()
        self.assertEqual(context['transaction_list'].count(), 1)
        # check first transaction
        self.assertEqual(context['transaction_list'][0].alias.name, 'CURZON CINEMA')
        self.assertEqual(context['transaction_list'][0].amount, Decimal('10.50'))
        # check category total
        self.assertEqual(context['total'], Decimal('10.50'))
        

        