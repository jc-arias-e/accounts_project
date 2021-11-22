from django.db.models import Sum
from .models import Payee, Account, Transaction, Category, Subcategory



def sum_account(account, balance_date):
    total = account.initial_balance 
    result = Transaction.objects.filter(account=account, date__lte=balance_date).aggregate(Sum('amount'))
    if result['amount__sum']:
        total += result['amount__sum']
    return total


def add_account_totals(balance_date):
    account_list = Account.objects.all()
    for account in account_list:
        account.total = sum_account(account, balance_date)
    return account_list


def get_balance_summary(account_list):
    assets, liabilities = 0, 0
    for account in account_list:
        if account.type == 'A':
            assets += account.total
        if account.type == 'L':
            liabilities += account.total
    return assets, liabilities


def sum_category(category, balance_date):
    q = Account.objects.filter(transaction__alias__category=category, transaction__date__month=balance_date.month).annotate(total=Sum('transaction__amount'))
    total = 0
    if q:
        for account in q:
            if category.type == 'E' and account.type == 'A':
                account.total = -account.total
            total += account.total
    return total


def get_expenses_report(balance_date):
    category_list = Category.objects.all()
    income, expenses = 0, 0
    for category in category_list:
        category.total = sum_category(category, balance_date)
        if category.type == 'I':
            income += category.total
        if category.type == 'E':
            expenses += category.total
    return category_list, income, expenses


def sum_subcategory(subcategory, balance_date):
    q = Account.objects.filter(transaction__alias__subcategory=subcategory, transaction__date__month=balance_date.month).annotate(total=Sum('transaction__amount'))
    total = 0
    if q:
        for account in q:
            if subcategory.category.type == 'E' and account.type == 'A':
                account.total = -account.total
            total += account.total
    return total


def add_subcategory_totals(balance_date):
    subcategory_list = Subcategory.objects.all()
    for subcategory in subcategory_list:
        subcategory.total = sum_subcategory(subcategory, balance_date)
    return subcategory_list


def sum_alias(alias, balance_date):
    q = Account.objects.filter(transaction__alias=alias, transaction__date__month=balance_date.month).annotate(total=Sum('transaction_amount'))
    total = 0
    if q:
        for account in q:
            if alias.category.type == 'E' and account.type == 'A':
                account.total = -account.total
            total += account.total
    return total


def read_statement(statement, account_id):
    # return if the statement file is too large -> to review!
    if statement.multiple_chunks():
        return ['File too large', 'Choose a smaller one']

    statement_data = statement.read().decode("utf-8")
    lines = statement_data.strip().split("\n")
    
    transaction_list = []
    account = Account.objects.get(pk=account_id)
    for line in lines[1:]:
        fields = line.strip().split('\t')
        fields.append(account.name)
        transaction_list.append(fields)   
    return transaction_list


def assign_alias(transaction_list):
    new_payees = []
    for transaction in transaction_list:
        try:
            payee = Payee.objects.get(name=transaction[1])
            transaction[1] = payee.alias.name
        except Payee.DoesNotExist:
            if transaction[1] not in new_payees:
                new_payees.append(transaction[1])
    return transaction_list, new_payees
        

