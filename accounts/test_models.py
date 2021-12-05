from django.test import TestCase
from decimal import Decimal
import datetime

from .models import Transaction, Alias, Category, Subcategory, Account, DoubleEntry


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
        
    def test_subcategory_created(self):
        subcateg = Subcategory.objects.get(pk=1)
        categ = Category.objects.get(pk=1)
        self.assertEqual(subcateg.name, 'Leisure')
        self.assertEqual(subcateg.category, categ)
        
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
    
    def test_transaction_created(self):
        alias = Alias.objects.get(pk=1)
        account = Account.objects.get(pk=1)
        Transaction.objects.create(date=datetime.date(2021, 10, 25), alias=alias, amount=-23.45, account=account)
        transaction = Transaction.objects.get(pk=1)
        self.assertEqual(transaction.date, datetime.date(2021, 10, 25))
        self.assertEqual(transaction.alias, alias)
        self.assertEqual(transaction.amount, Decimal('-23.45'))
        self.assertEqual(transaction.account, account)
        
    def test_double_entry_created(self):
        alias = Alias.objects.create(name='CREDIT CARD PAYMENT')
        account_a = Account.objects.create(name='BankAccount', type='A')
        account_b = Account.objects.get(name='Mastercard')
        double_entry = DoubleEntry.objects.create(alias=alias, account_a=account_a, account_b=account_b)
        self.assertEqual(double_entry.alias, alias)
        self.assertEqual(double_entry.alias.category, None)
        self.assertEqual(double_entry.alias.subcategory, None)
        self.assertEqual(double_entry.account_a, account_a)
        self.assertEqual(double_entry.account_b, account_b)
