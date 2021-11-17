from django.test import TestCase, RequestFactory
from decimal import Decimal
import datetime

from .models import Transaction, Alias, Category, Subcategory, Account
from .views import IndexView, AccountView, CategoryView


class TransactionModelTest(TestCase):
    def setUp(self):
        Category.objects.create(name='Other', type='E')
        categ = Category.objects.get(pk=1)
        Subcategory.objects.create(name='Leisure', category=categ)
        subcateg = Subcategory.objects.get(pk=1)
        Alias.objects.create(name='CURZON CINEMA', category=categ, subcategory=subcateg)
        Account.objects.create(name='Mastercard', type='L', initial_balance=170.50)
            
    def test_category_created(self):
        categ = Category.objects.get(pk=1)
        self.assertEqual(categ.name, 'Other')
        self.assertEqual(categ.INCOME, 'I')
        self.assertEqual(categ.EXPENSE, 'E')
        self.assertEqual(categ.type, 'E')
        self.assertEqual(categ.total, 0)
        
    def test_subcategory_created(self):
        subcateg = Subcategory.objects.get(pk=1)
        categ = Category.objects.get(pk=1)
        self.assertEqual(subcateg.name, 'Leisure')
        self.assertEqual(subcateg.category, categ)
        self.assertEqual(subcateg.total, 0)
        
    def test_alias_created(self):
        alias = Alias.objects.get(pk=1)
        categ = Category.objects.get(pk=1)
        subcateg = Subcategory.objects.get(pk=1)
        self.assertEqual(alias.name, 'CURZON CINEMA')
        self.assertEqual(alias.category, categ)
        self.assertEqual(alias.subcategory, subcateg)
        
    def test_account_created(self):
        account = Account.objects.get(pk=1)
        self.assertEqual(account.name, 'Mastercard')
        self.assertEqual(account.ASSET, 'A')
        self.assertEqual(account.LIABILITY, 'L')
        self.assertEqual(account.type, 'L')
        self.assertEqual(account.initial_balance, Decimal('170.50'))
        self.assertEqual(account.balance, 0)
    
    def test_transaction_created(self):
        alias = Alias.objects.get(pk=1)
        account = Account.objects.get(pk=1)
        Transaction.objects.create(date=datetime.date(2021, 10, 25), alias=alias, amount=-23.45, account=account)
        transaction = Transaction.objects.get(pk=1)
        self.assertEqual(transaction.date, datetime.date(2021, 10, 25))
        self.assertEqual(transaction.alias, alias)
        self.assertEqual(transaction.amount, Decimal('-23.45'))
        self.assertEqual(transaction.account, account)
        

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
        self.assertEqual(response.context['income'], 0)
        self.assertEqual(response.context['expenses'], Decimal('10.50'))
        self.assertEqual(response.context['profit'], Decimal('-10.50'))
        
    def test_index_session(self):
        request = self.factory.get('/accounts/')
        # create request.session as the Middelwareis that creates it is not activated
        request.session = {}
        response = IndexView.as_view()(request)
        self.assertEqual(request.session['balance_month'], 11)
        
    def test_account_transactions(self):
        request = self.factory.get('/accounts/1/account')
        # create request.session
        request.session = {'balance_date': '2021-11-3' }
        view = AccountView()
        view.setup(request)
        # check account.id = 1
        view.kwargs['pk'] = 1
        queryset = view.get_queryset()
        self.assertEqual(queryset.count(), 2)
        # check first transaction
        self.assertEqual(queryset[:1][0].alias.name, 'CURZON CINEMA')
        self.assertEqual(queryset[:1][0].amount, Decimal('10.50'))       
        # check account total and the flag 'is_account' passed in context
        view.object_list = []
        context = view.get_context_data()
        self.assertEqual(context['balance'], Decimal('47.60'))
        self.assertEqual(context['is_account'], True)
        
    def test_category_transactions(self):
        request = self.factory.get('/accounts/1/category')
        # create request.session
        request.session = {'balance_month': 11 }
        view = CategoryView()
        view.setup(request)
        # check category.id = 1
        view.kwargs['pk'] = 1
        queryset = view.get_queryset()
        self.assertEqual(queryset.count(), 1)
        # check first transaction
        self.assertEqual(queryset[:1][0].alias.category.name, 'Other')
        # check category total in context
        view.object_list = []
        context = view.get_context_data()
        self.assertEqual(context['total'], Decimal('10.50'))
        

        