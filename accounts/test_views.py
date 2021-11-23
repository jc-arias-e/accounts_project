from django.test import TestCase
from decimal import Decimal
import datetime

from .models import Transaction, Alias, Category, Subcategory, Account


class IndexViewTest(TestCase):
    def setUp(self):
        account = Account.objects.create(name='BankAccount', type='A', initial_balance=500)
        account2 = Account.objects.create(name='CreditCard', type='L', initial_balance=30.50)
        Account.objects.create(name='Wallet', type='A', initial_balance=20)
        categ = Category.objects.create(name='Food', type='E')
        subcateg = Subcategory.objects.create(name='Meals', category=categ)
        categ2 = Category.objects.create(name='Other', type='E')
        alias = Alias.objects.create(name='CHIPOTLE', category=categ, subcategory=subcateg)
        alias2 = Alias.objects.create(name='CURZON CINEMA', category=categ2)
        Transaction.objects.create(date=datetime.date(2021, 11, 3), alias=alias, amount=-13, account=account)
        Transaction.objects.create(date=datetime.date(2021, 10, 27), alias=alias2, amount=-10.50, account=account)
        Transaction.objects.create(date=datetime.date(2021, 11, 11), alias=alias, amount=7, account=account2)
        Transaction.objects.create(date=datetime.date(2021, 11, 9), alias=alias2, amount=-11, account=account)
        
    def test_index(self):
        response = self.client.get('/accounts/')
        self.assertEqual(response.status_code, 200)
        # check balance totals
        self.assertEqual(response.context['balance_date'], datetime.date(2021, 11, 11))
        self.assertEqual(response.context['account_list'].count(), 3)
        self.assertEqual(response.context['account_list'][0].name, 'BankAccount')
        self.assertEqual(response.context['account_list'][0].total, Decimal('465.50'))
        self.assertEqual(response.context['account_list'][1].name, 'CreditCard')
        self.assertEqual(response.context['account_list'][1].total, Decimal('37.50'))
        self.assertEqual(response.context['account_list'][2].name, 'Wallet')
        self.assertEqual(response.context['account_list'][2].total, Decimal('20.00'))
        self.assertEqual(response.context['assets'], Decimal('485.50'))
        self.assertEqual(response.context['liabilities'], Decimal('37.50'))
        self.assertEqual(response.context['capital'], Decimal('448.00'))
        self.assertEqual(response.context['balance_profit'], Decimal('-31.00'))
        # check income and expenses totals
        self.assertEqual(response.context['category_list'].count(), 2)
        self.assertEqual(response.context['subcategory_list'].count(), 1)
        self.assertEqual(response.context['category_list'][0].name, 'Food')
        self.assertEqual(response.context['category_list'][0].total, Decimal('20.00'))
        self.assertEqual(response.context['subcategory_list'][0].name, 'Meals')
        self.assertEqual(response.context['subcategory_list'][0].total, Decimal('20.00'))
        self.assertEqual(response.context['category_list'][1].name, 'Other')
        self.assertEqual(response.context['category_list'][1].total, Decimal('11.00'))
        self.assertEqual(response.context['income'], 0)
        self.assertEqual(response.context['expenses'], Decimal('31.00'))
        self.assertEqual(response.context['profit'], Decimal('-31.00'))


class AccountViewTest(TestCase):
    def setUp(self):
        account = Account.objects.create(name='BankAccount', type='A', initial_balance=500)
        account2 = Account.objects.create(name='CreditCard', type='L', initial_balance=30.50)
        Account.objects.create(name='Wallet', type='A', initial_balance=20)
        categ = Category.objects.create(name='Food', type='E')
        subcateg = Subcategory.objects.create(name='Meals', category=categ)
        categ2 = Category.objects.create(name='Other', type='E')
        alias = Alias.objects.create(name='CHIPOTLE', category=categ, subcategory=subcateg)
        alias2 = Alias.objects.create(name='CURZON CINEMA', category=categ2)
        Transaction.objects.create(date=datetime.date(2021, 11, 3), alias=alias, amount=-13, account=account)
        Transaction.objects.create(date=datetime.date(2021, 10, 27), alias=alias2, amount=-10.50, account=account)
        Transaction.objects.create(date=datetime.date(2021, 11, 11), alias=alias, amount=7, account=account2)
        Transaction.objects.create(date=datetime.date(2021, 11, 9), alias=alias2, amount=-11, account=account)

    def test_account_transactions(self):
        # check account.id = 1
        response = self.client.get('/accounts/1/account')
        self.assertEqual(response.context['balance_date'], datetime.date(2021, 11, 11))
        self.assertEqual(response.context['transaction_list'].count(), 2)
        # check transactions
        self.assertEqual(response.context['transaction_list'][0].alias.name, 'CHIPOTLE')
        self.assertEqual(response.context['transaction_list'][0].amount, Decimal('-13.00')) 
        self.assertEqual(response.context['transaction_list'][1].alias.name, 'CURZON CINEMA')
        self.assertEqual(response.context['transaction_list'][1].amount, Decimal('-11.00'))       
        # check account total and flag 'is_account'
        self.assertEqual(response.context['balance'], Decimal('465.50'))
        self.assertEqual(response.context['is_account'], True)


class CategoryViewTest(TestCase):
    def setUp(self):
        account = Account.objects.create(name='BankAccount', type='A', initial_balance=500)
        account2 = Account.objects.create(name='CreditCard', type='L', initial_balance=30.50)
        Account.objects.create(name='Wallet', type='A', initial_balance=20)
        categ = Category.objects.create(name='Food', type='E')
        subcateg = Subcategory.objects.create(name='Meals', category=categ)
        categ2 = Category.objects.create(name='Other', type='E')
        alias = Alias.objects.create(name='CHIPOTLE', category=categ, subcategory=subcateg)
        alias2 = Alias.objects.create(name='CURZON CINEMA', category=categ2)
        Transaction.objects.create(date=datetime.date(2021, 11, 3), alias=alias, amount=-13, account=account)
        Transaction.objects.create(date=datetime.date(2021, 10, 27), alias=alias2, amount=-10.50, account=account)
        Transaction.objects.create(date=datetime.date(2021, 11, 11), alias=alias, amount=7, account=account2)
        Transaction.objects.create(date=datetime.date(2021, 11, 9), alias=alias2, amount=-11, account=account)

    def test_category_transactions(self):
        # check category.id = 1
        response = self.client.get('/accounts/1/category')
        self.assertEqual(response.context['balance_date'], datetime.date(2021, 11, 11))
        self.assertEqual(response.context['transaction_list'].count(), 2)
        # check transactions
        self.assertEqual(response.context['transaction_list'][0].alias.name, 'CHIPOTLE')
        self.assertEqual(response.context['transaction_list'][0].amount, Decimal('-13.00'))
        self.assertEqual(response.context['transaction_list'][1].alias.name, 'CHIPOTLE')
        self.assertEqual(response.context['transaction_list'][1].amount, Decimal('7.00'))
        # check category total
        self.assertEqual(response.context['total'], Decimal('20.00'))
        

class SubcategoryViewTest(TestCase):
    def setUp(self):
        account = Account.objects.create(name='BankAccount', type='A', initial_balance=500)
        account2 = Account.objects.create(name='CreditCard', type='L', initial_balance=30.50)
        Account.objects.create(name='Wallet', type='A', initial_balance=20)
        categ = Category.objects.create(name='Food', type='E')
        subcateg = Subcategory.objects.create(name='Meals', category=categ)
        categ2 = Category.objects.create(name='Other', type='E')
        alias = Alias.objects.create(name='CHIPOTLE', category=categ, subcategory=subcateg)
        alias2 = Alias.objects.create(name='CURZON CINEMA', category=categ2)
        Transaction.objects.create(date=datetime.date(2021, 11, 3), alias=alias, amount=-13, account=account)
        Transaction.objects.create(date=datetime.date(2021, 10, 27), alias=alias2, amount=-10.50, account=account)
        Transaction.objects.create(date=datetime.date(2021, 11, 11), alias=alias, amount=7, account=account2)
        Transaction.objects.create(date=datetime.date(2021, 11, 9), alias=alias2, amount=-11, account=account)

    def test_subcategory_transactions(self):
        # check subcategory.id = 1
        response = self.client.get('/accounts/1/subcategory')
        self.assertEqual(response.context['balance_date'], datetime.date(2021, 11, 11))
        self.assertEqual(response.context['transaction_list'].count(), 2)
        # check transactions
        self.assertEqual(response.context['transaction_list'][0].alias.name, 'CHIPOTLE')
        self.assertEqual(response.context['transaction_list'][0].amount, Decimal('-13.00'))
        self.assertEqual(response.context['transaction_list'][1].alias.name, 'CHIPOTLE')
        self.assertEqual(response.context['transaction_list'][1].amount, Decimal('7.00'))
        # check category total
        self.assertEqual(response.context['total'], Decimal('20.00'))

    