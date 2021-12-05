from django.test import TestCase
from decimal import Decimal
import datetime

from django.test.client import RequestFactory

from .views import upload_statement
from .models import Transaction, Payee, Alias, Category, Subcategory, Account, Parameters


class IndexViewsTest(TestCase):
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
        Transaction.objects.create(date=datetime.date(2021, 10, 30), alias=alias, amount=9.00, account=account2)
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
        self.assertEqual(response.context['account_list'][1].total, Decimal('46.50'))
        self.assertEqual(response.context['account_list'][2].name, 'Wallet')
        self.assertEqual(response.context['account_list'][2].total, Decimal('20.00'))
        self.assertEqual(response.context['assets'], Decimal('485.50'))
        self.assertEqual(response.context['liabilities'], Decimal('46.50'))
        self.assertEqual(response.context['capital'], Decimal('439.00'))
        self.assertEqual(response.context['balance_profit'], Decimal('-31.00'))
        # check income and expenses totals
        self.assertEqual(len(response.context['category_list']), 2)
        self.assertEqual(len(response.context['subcategory_list']), 1)
        self.assertEqual(response.context['category_list'][0].name, 'Food')
        self.assertEqual(response.context['category_list'][0].total, Decimal('20.00'))
        self.assertEqual(response.context['subcategory_list'][0].name, 'Meals')
        self.assertEqual(response.context['subcategory_list'][0].total, Decimal('20.00'))
        self.assertEqual(response.context['category_list'][1].name, 'Other')
        self.assertEqual(response.context['category_list'][1].total, Decimal('11.00'))
        self.assertEqual(response.context['income'], 0)
        self.assertEqual(response.context['expenses'], Decimal('31.00'))
        self.assertEqual(response.context['profit'], Decimal('-31.00'))


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

    
    def test_alias_transactions(self):
        # check alias.id = 1
        response = self.client.get('/accounts/1/alias')
        self.assertEqual(response.context['balance_date'], datetime.date(2021, 11, 11))
        self.assertEqual(response.context['transaction_list'].count(), 2)
        # check transactions
        self.assertEqual(response.context['transaction_list'][0].alias.name, 'CHIPOTLE')
        self.assertEqual(response.context['transaction_list'][0].amount, Decimal('-13.00'))
        self.assertEqual(response.context['transaction_list'][1].alias.name, 'CHIPOTLE')
        self.assertEqual(response.context['transaction_list'][1].amount, Decimal('7.00'))
        # check category total
        self.assertEqual(response.context['total'], Decimal('20.00'))


    def test_history_summary(self):
        Parameters.objects.create(date=datetime.date(2021, 10, 31))
        response = self.client.get('/accounts/history')
        self.assertEqual(response.status_code, 200)
        # check balance totals
        self.assertEqual(response.context['balance_date'], datetime.date(2021, 10, 31))
        self.assertEqual(response.context['account_list'].count(), 3)
        self.assertEqual(response.context['account_list'][0].name, 'BankAccount')
        self.assertEqual(response.context['account_list'][0].total, Decimal('489.50'))
        self.assertEqual(response.context['account_list'][1].name, 'CreditCard')
        self.assertEqual(response.context['account_list'][1].total, Decimal('39.50'))
        self.assertEqual(response.context['account_list'][2].name, 'Wallet')
        self.assertEqual(response.context['account_list'][2].total, Decimal('20.00'))
        self.assertEqual(response.context['assets'], Decimal('509.50'))
        self.assertEqual(response.context['liabilities'], Decimal('39.50'))
        self.assertEqual(response.context['capital'], Decimal('470.00'))
        self.assertEqual(response.context['balance_profit'], Decimal('-19.50'))
        # check income and expenses totals
        self.assertEqual(len(response.context['category_list']), 2)
        self.assertEqual(len(response.context['subcategory_list']), 1)
        self.assertEqual(response.context['category_list'][0].name, 'Food')
        self.assertEqual(response.context['category_list'][0].total, Decimal('9.00'))
        self.assertEqual(response.context['subcategory_list'][0].name, 'Meals')
        self.assertEqual(response.context['subcategory_list'][0].total, Decimal('9.00'))
        self.assertEqual(response.context['category_list'][1].name, 'Other')
        self.assertEqual(response.context['category_list'][1].total, Decimal('10.50'))
        self.assertEqual(response.context['income'], 0)
        self.assertEqual(response.context['expenses'], Decimal('19.50'))
        self.assertEqual(response.context['profit'], Decimal('-19.50'))


    def test_account_history(self):
        Parameters.objects.create(date=datetime.date(2021, 10, 31))
        # check account.id = 1
        response = self.client.get('/accounts/history/1/account')
        self.assertEqual(response.context['balance_date'], datetime.date(2021, 10, 31))
        self.assertEqual(response.context['transaction_list'].count(), 1)
        # check transactions
        self.assertEqual(response.context['transaction_list'][0].alias.name, 'CURZON CINEMA')
        self.assertEqual(response.context['transaction_list'][0].amount, Decimal('-10.50'))       
        # check account total and flag 'is_account'
        self.assertEqual(response.context['balance'], Decimal('489.50'))
        self.assertEqual(response.context['is_account'], True)


    def test_category_history(self):
        Parameters.objects.create(date=datetime.date(2021, 10, 31))
        # check category.id = 2
        response = self.client.get('/accounts/history/2/category')
        self.assertEqual(response.context['balance_date'], datetime.date(2021, 10, 31))
        self.assertEqual(response.context['transaction_list'].count(), 1)
        # check transactions
        self.assertEqual(response.context['transaction_list'][0].alias.name, 'CURZON CINEMA')
        self.assertEqual(response.context['transaction_list'][0].amount, Decimal('-10.50'))
        # check category total
        self.assertEqual(response.context['total'], Decimal('10.50'))
        

    def test_subcategory_history(self):
        Parameters.objects.create(date=datetime.date(2021, 10, 31))
        # check subcategory.id = 1
        response = self.client.get('/accounts/history/1/subcategory')
        self.assertEqual(response.context['balance_date'], datetime.date(2021, 10, 31))
        self.assertEqual(response.context['transaction_list'].count(), 1)
        # check transactions
        self.assertEqual(response.context['transaction_list'][0].alias.name, 'CHIPOTLE')
        self.assertEqual(response.context['transaction_list'][0].amount, Decimal('9.00'))
        # check category total
        self.assertEqual(response.context['total'], Decimal('9.00'))

    
    def test_alias_history(self):
        Parameters.objects.create(date=datetime.date(2021, 10, 31))
        # check alias.id = 1
        response = self.client.get('/accounts/history/2/alias')
        self.assertEqual(response.context['balance_date'], datetime.date(2021, 10, 31))
        self.assertEqual(response.context['transaction_list'].count(), 1)
        # check transactions
        self.assertEqual(response.context['transaction_list'][0].alias.name, 'CURZON CINEMA')
        self.assertEqual(response.context['transaction_list'][0].amount, Decimal('-10.50'))
        # check category total
        self.assertEqual(response.context['total'], Decimal('10.50'))


class SelectDateViewTest(TestCase):
    def test_select_date_initial(self):
        response = self.client.get('/accounts/select/date')
        self.assertEqual(response.status_code, 200)

        # check date is created in Paramenters for the first time
        response_post = self.client.post('/accounts/select/date', { 'date': datetime.date(2021, 10, 7) })
        parameter = Parameters.objects.get(pk=1).date
        self.assertEqual(response_post.status_code, 302)
        self.assertEqual(parameter, datetime.date(2021, 10, 7))


    def test_select_date(self):
        response = self.client.get('/accounts/select/date')
        self.assertEqual(response.status_code, 200)

        # check date is set in Parameters if already exists
        Parameters.objects.create(date=datetime.date(2021, 9, 30))
        response_post = self.client.post('/accounts/select/date', { 'date': datetime.date(2021, 10, 29) })
        parameter = Parameters.objects.get(pk=1).date
        self.assertEqual(response_post.status_code, 302)
        self.assertEqual(parameter, datetime.date(2021, 10, 29))     


class UploadStatementViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.account = Account.objects.create(name='Creditcard')


    def test_upload_statement(self):
        with open('accounts/creditcard.csv') as file:
            request = self.factory.post('/accounts/upload/statement', {'account': self.account.id, 'statement': file })
        
        # create session normally created by middleware
        request.session = {}
        response_post = upload_statement(request)
        transaction_list = request.session['transaction_list']
        new_payees = request.session['new_payees']
        self.assertEqual(response_post.status_code, 302)
        # check some transactions
        self.assertEqual(len(transaction_list), 6)
        self.assertEqual(transaction_list[0], ['Creditcard', '23/11/2021', 'MORRISON STORE LONDON', 'New', '', '9.65' ])
        self.assertEqual(transaction_list[1], ['Creditcard', '29/11/2021', 'SAINSBURYS LONDON', 'New', '', '3.5'])
        self.assertEqual(transaction_list[2], ['Creditcard', '29/11/2021', 'MORRISON STORE LONDON', 'New', '', '4.5'])
        # check new payees
        self.assertEqual(len(new_payees), 5)
        self.assertEqual(new_payees[0], 'MORRISON STORE LONDON')
        self.assertEqual(new_payees[1], 'SAINSBURYS LONDON')
        self.assertEqual(new_payees[2], 'CAFFE NERO LONDON')
        #check initial names in create payees


    def test_asign_alias(self):
        # create existing alias
        category = Category.objects.create(name='Food', type='E')
        subcategory = Subcategory.objects.create(name='Groceries', category=category)
        alias = Alias.objects.create(name='MORRISON', category=category, subcategory=subcategory)
        Payee.objects.create(name='MORRISON STORE LONDON', alias=alias)

        with open('accounts/creditcard.csv') as file:
            request = self.factory.post('/accounts/upload/statement', {'account': self.account.id, 'statement': file })
        
        # create session normally created by middleware
        request.session = {}
        response_post = upload_statement(request)
        transaction_list = request.session['transaction_list']
        new_payees = request.session['new_payees']
        self.assertEqual(response_post.status_code, 302)
        # check some transactions
        self.assertEqual(len(transaction_list), 6)
        self.assertEqual(transaction_list[0], ['Creditcard', '23/11/2021', 'MORRISON', 'Food', 'Groceries', '9.65'])
        self.assertEqual(transaction_list[1], ['Creditcard', '29/11/2021', 'SAINSBURYS LONDON', 'New', '', '3.5'])
        self.assertEqual(transaction_list[2], ['Creditcard', '29/11/2021', 'MORRISON', 'Food', 'Groceries', '4.5'])
        # check new payees
        self.assertEqual(len(new_payees), 4)
        self.assertEqual(new_payees[0], 'SAINSBURYS LONDON')
        self.assertEqual(new_payees[1], 'CAFFE NERO LONDON')
        self.assertEqual(new_payees[2], 'CHIPOTLE GRILL')
        #check initial names in create payees