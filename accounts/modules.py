from .models import Payee, Account, Transaction


def create_balance(balance_date):
    account_list = Account.objects.all()
    assets = 0
    liabilities = 0
    for account in account_list:
        account.balance = account.initial_balance
        for transaction in Transaction.objects.filter(account=account, date__lte=balance_date):
            account.balance += transaction.amount
        if account.type == 'A':
            assets += account.balance
        if account.type == 'L':
            liabilities += account.balance
    return account_list, assets, liabilities


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
        

