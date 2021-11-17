from django.forms.formsets import formset_factory
from django.views import generic
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import datetime

from .models import Transaction, Account, Alias, Category, Subcategory
from .forms import UploadFileForm, PayeeForm, DateForm
from . import modules
                
    
class IndexView(generic.ListView):
    template_name = 'accounts/index.html'
    assets = 0
    liabilities = 0
    income = 0
    expenses = 0
    
    
    def get_queryset(self):
        """ Check balance date """
        if 'balance_date' in self.request.session:
            balance_date = self.request.session['balance_date']
        else:
            balance_date = Transaction.objects.all().order_by('-date').first().date
            self.request.session['balance_date'] = balance_date.isoformat()

        """ Calculate balance for each account """    
        account_list, self.assets, self.liabilities = modules.create_balance(balance_date)
        return account_list
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['balance_date'] = self.request.session['balance_date']
        context['assets'] = self.assets
        context['liabilities'] = self.liabilities
        context['capital'] = self.assets - self.liabilities

        """ Calculate profit compared to previous balance """
        balance_date = datetime.date.fromisoformat(self.request.session['balance_date'])
        prev_date = datetime.date(balance_date.year, balance_date.month, 1) - datetime.timedelta(days=1)
        prev_list, prev_assets, prev_liabilities = modules.create_balance(prev_date)
        context['balance_profit'] = (self.assets - self.liabilities) - (prev_assets - prev_liabilities)
        
        """ Calculate total for each category """
        category_list = Category.objects.all()
        balance_month = datetime.date.fromisoformat(self.request.session['balance_date']).month
        for category in category_list:
            for transaction in Transaction.objects.filter(alias__category=category, date__month=balance_month):
                if transaction.account.type == 'A' and transaction.alias.category.type == 'E':
                    transaction.amount = -transaction.amount
                category.total += transaction.amount
            if category.type == 'I':
                self.income += category.total
            if category.type == 'E':
                self.expenses += category.total
                
        """ Calculate total for each subcategory """
        subcategory_list = Subcategory.objects.all()
        balance_month = datetime.date.fromisoformat(self.request.session['balance_date']).month
        for subcategory in subcategory_list:
            for transaction in Transaction.objects.filter(alias__subcategory=subcategory, date__month=balance_month):
                if transaction.account.type == 'A' and transaction.alias.subcategory.category.type == 'E':
                    transaction.amount = -transaction.amount
                subcategory.total += transaction.amount
               
        context['category_list'] = category_list
        context['subcategory_list'] = subcategory_list
        context['income'] = self.income
        context['expenses'] = self.expenses
        context['profit'] = self.income - self.expenses
        return context

    
class AccountView(generic.ListView):
    template_name = 'accounts/transactions.html'
    balance = 0
    
    def get_queryset(self):
        balance_date = self.request.session['balance_date']
        transaction_list = Transaction.objects.filter(account__id=self.kwargs['pk'], date__lte=balance_date)
        account = Account.objects.get(pk=self.kwargs['pk'])
        self.balance = account.initial_balance
        for transaction in transaction_list:
            self.balance += transaction.amount
        return transaction_list
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['balance'] = self.balance
        context['is_account'] = True
        context['balance_date'] = datetime.date.fromisoformat(self.request.session['balance_date'])
        return context
    
    
class CategoryView(generic.ListView):
    template_name = 'accounts/transactions.html'
    total = 0
    
    def get_queryset(self):
        balance_month = datetime.date.fromisoformat(self.request.session['balance_date']).month
        transaction_list = Transaction.objects.filter(alias__category__id=self.kwargs['pk'], date__month=balance_month)
        for transaction in transaction_list:
            if transaction.account.type == 'A' and transaction.alias.category.type == 'E':
                transaction.amount = -transaction.amount
            self.total += transaction.amount
        return transaction_list
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total'] = self.total
        context['balance_date'] = datetime.date.fromisoformat(self.request.session['balance_date'])
        return context
    
    
class SubcategoryView(generic.ListView):
    template_name = 'accounts/transactions.html'
    total = 0
    
    def get_queryset(self):
        balance_month = datetime.date.fromisoformat(self.request.session['balance_date']).month
        transaction_list = Transaction.objects.filter(alias__subcategory__id=self.kwargs['pk'], date__month=balance_month)
        for transaction in transaction_list:
            if transaction.account.type == 'A' and transaction.alias.category.type == 'E':
                transaction.amount = -transaction.amount
            self.total += transaction.amount
        return transaction_list
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total'] = self.total
        context['balance_date'] = datetime.date.fromisoformat(self.request.session['balance_date'])
        return context
    
    
class AliasView(generic.ListView):
    template_name = 'accounts/transactions.html'
    total = 0
    
    def get_queryset(self):
        balance_month = datetime.date.fromisoformat(self.request.session['balance_date']).month
        transaction_list = Transaction.objects.filter(alias__id=self.kwargs['pk'], date__month=balance_month)
        for transaction in transaction_list:
            if transaction.account.type == 'A' and transaction.alias.category.type == 'E':
                transaction.amount = -transaction.amount
            self.total += transaction.amount
        return transaction_list
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total'] = self.total
        context['balance_date'] = datetime.date.fromisoformat(self.request.session['balance_date'])
        return context
    
    
# file upload
def upload_statement(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            transaction_list = modules.read_statement(request.FILES['statement'], request.POST['account'])
            transaction_list_updated, new_payees = modules.assign_alias(transaction_list)
            request.session['transaction_list'] = transaction_list_updated
            # choose the nex view
            if new_payees != []:
                request.session['new_payees'] = new_payees
                return HttpResponseRedirect(reverse('accounts:create_payees'))
            else:
                return HttpResponseRedirect(reverse('accounts:save_statement'))
    else:
        form = UploadFileForm()
    return render(request, 'accounts/upload.html', { 'form': form })
    

# display transactions to assign alias to new payees or create new aliases
def create_payees(request):
    transaction_list = request.session['transaction_list']  # review
    new_payees = request.session['new_payees']
    PayeeFormSet = formset_factory(PayeeForm, extra=0)
    
    if request.method == 'POST':
        formset = PayeeFormSet(request.POST)
        if formset.is_valid():
            # save data
            for form in formset:
                form.save()
            return HttpResponseRedirect(reverse('accounts:save_statement'))
    else:
        formset = PayeeFormSet(initial=[{'name': payee } for payee in new_payees])
    
    context = { 
        'transaction_list': transaction_list, 
        'formset': formset
    }
    return render(request, 'accounts/payees.html', context)



def save_statement(request):
    transaction_list = request.session['transaction_list']
    transaction_list_updated, new_payees = modules.assign_alias(transaction_list)

    if request.method == 'POST':
        # save data
        for transaction in transaction_list_updated:
            date_list = transaction[0].split('/')
            if date_list[0] != 4:
                date = date_list[2] + '-' + date_list[1] + '-' + date_list[0]
            else:
                date = date_list[0] + '-' + date_list[1] + '-' + date_list[2]
            alias = Alias.objects.get(name=transaction[1])
            account = Account.objects.get(name=transaction[3])
            full_transaction = Transaction(date=date, alias=alias, amount=transaction[2], account=account)
            full_transaction.save()
        return HttpResponseRedirect(reverse('accounts:index'))

    return render(request, 'accounts/statement.html', { 'transaction_list': transaction_list_updated })

    
def select_date(request):
    if request.method == 'POST':
        form = DateForm(request.POST)
        if form.is_valid():
            #change date
            request.session['balance_date'] = request.POST['date']
            return HttpResponseRedirect(reverse('accounts:index'))
    else:
        form = DateForm()
    return render(request, 'accounts/balance_date.html', { 'form': form })