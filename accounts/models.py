from django.db import models


class Account(models.Model):
    name = models.CharField(max_length=30)
    ASSET = 'A'
    LIABILITY = 'L'
    ACCOUNT_TYPE_CHOICES = [
        (ASSET, 'Asset'),
        (LIABILITY, 'Liability'),
    ]
    type = models.CharField(max_length=1, choices=ACCOUNT_TYPE_CHOICES, default=ASSET)
    initial_balance = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    balance = 0

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=30)
    INCOME = 'I'
    EXPENSE = 'E'
    CATEGORY_TYPE_CHOICES = [
        (INCOME, 'Income'),
        (EXPENSE, 'Expense'),
    ]
    type = models.CharField(max_length=1, choices=CATEGORY_TYPE_CHOICES, default=EXPENSE)
    total = 0

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'


class Subcategory(models.Model):
    name = models.CharField(max_length=30)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    total = 0

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'subcategories'


class Alias(models.Model):
    name = models.CharField(max_length=30)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return '{} {} {}'.format(self.name, self.category, self.subcategory)

    class Meta:
        verbose_name_plural = 'aliases'


class Transaction(models.Model):
    date = models.DateField()
    alias = models.ForeignKey(Alias, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    
    def __str__(self):
        return '{} {} {} {}'.format(self.account, self.date, self.alias, self.amount)


class Payee(models.Model):
    name = models.CharField(max_length=50)
    alias = models.ForeignKey(Alias, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class DoubleEntry(models.Model):
    alias = models.ForeignKey(Alias, on_delete=models.CASCADE)
    account_A = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='+')
    account_B = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='+')

