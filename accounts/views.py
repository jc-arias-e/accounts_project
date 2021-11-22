from django.forms.formsets import formset_factory
from django.views.generic import ListView
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import datetime

from .models import Parameters, Transaction, Account, Alias, Category, Subcategory
from .forms import UploadFileForm, PayeeForm, DateForm
from . import modules
                
    
class IndexView(ListView):
    model = Account
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Check if called from index or history path
        if self.template_name == 'accounts/index.html':
            balance_date = Transaction.objects.all().order_by('-date').first().date
        else:
            balance_date = Parameters.objects.get(pk=1).date
        
        # Calculate balance summary
        account_list = modules.add_account_totals(balance_date)
        assets, liabilities = modules.get_balance_summary(account_list)
        context['balance_date'] = balance_date
        context['account_list'] = account_list
        context['assets'] = assets
        context['liabilities'] = liabilities
        context['capital'] = assets - liabilities

        # Calculate profit comparing with previous balance
        prev_date = datetime.date(balance_date.year, balance_date.month, 1) - datetime.timedelta(days=1)
        prev_account_list = modules.add_account_totals(prev_date)
        prev_assets, prev_liabilities = modules.get_balance_summary(prev_account_list)
        context['balance_profit'] = (assets - liabilities) - (prev_assets - prev_liabilities)
               
        # Calculate category totals
        category_list, income, expenses = modules.get_expenses_report(balance_date)
        context['category_list'] = category_list
        context['income'] = income
        context['expenses'] = expenses
        context['profit'] = income - expenses
                
        # Calculate subcategory totals              
        context['subcategory_list'] = modules.add_subcategory_totals(balance_date)
        
        return context

    
class AccountView(ListView):
    model = Transaction
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Check if called from account_transactions or account_history path
        if self.template_name == 'accounts/transactions.html':
            balance_date = Transaction.objects.all().order_by('-date').first().date
        else:
            balance_date = Parameters.objects.get(pk=1).date

        account = Account.objects.get(pk=self.kwargs['pk'])
        context['balance_date'] = balance_date
        context['transaction_list'] = Transaction.objects.filter(account=account, date__month=balance_date.month)
        context['balance'] = modules.sum_account(account, balance_date)
        context['is_account'] = True      
        return context
    
    
class CategoryView(ListView):
    model = Transaction
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Check if called from category_transactions or category_history path
        if self.template_name == 'accounts/transactions.html':
            balance_date = Transaction.objects.all().order_by('-date').first().date
        else:
            balance_date = Parameters.objects.get(pk=1).date

        category = Category.objects.get(pk=self.kwargs['pk'])
        context['balance_date'] = balance_date
        context['transaction_list'] = Transaction.objects.filter(alias__category=category, date__month=balance_date.month)
        context['total'] = modules.sum_category(category, balance_date)
        return context
    
    
class SubcategoryView(ListView):
    model = Transaction
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Check if called from subcategory_transactions or subcategory_history path
        if self.template_name == 'accounts/transactions.html':
            balance_date = Transaction.objects.all().order_by('-date').first().date
        else:
            balance_date = Parameters.objects.get(pk=1).date
        
        subcategory = Subcategory.objects.get(pk=self.kwargs['pk'])
        context['balance_date'] = balance_date
        context['transaction_list'] = Transaction.objects.filter(alias__subcategory=subcategory, date__month=balance_date.month)
        context['total'] = modules.sum_subcategory(subcategory, balance_date)
        return context
    
    
class AliasView(ListView):
    model = Transaction
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

                # Check if called from subcategory_transactions or subcategory_history path
        if self.template_name == 'accounts/transactions.html':
            balance_date = Transaction.objects.all().order_by('-date').first().date
        else:
            balance_date = Parameters.objects.get(pk=1).date

        alias = Alias.objects.get(pk=self.kwargs['pk'])
        context['balance_date'] = balance_date
        context['transaction_list'] = Transaction.objects.filter(alias=alias, date__month=balance_date.month)
        context['total'] = modules.sum_alias(alias, balance_date)
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
            #save date
            if Parameters.objects.all().count() == 0:
                Parameters.objects.create(date=request.POST['date'])
            else:
                parameter = Parameters.objects.get(pk=1)
                parameter.date = request.POST['date']
                parameter.save()
            return HttpResponseRedirect(reverse('accounts:history'))
    else:
        form = DateForm()
    return render(request, 'accounts/balance_date.html', { 'form': form })


