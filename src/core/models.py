from decimal import Decimal

from django.db import models
from django.utils import timezone

from django.conf import settings

from core.globals import CURRENCY
from users.models import AbstractUser


# User
class User(AbstractUser):
    favorite_currency = models.CharField(
        max_length=3,
        choices=CURRENCY.CHOICES,
        default=settings.DEFAULT_CURRENCY
    )

    def add_category(self, name=None, description=None, type=None, parent=None):
        if not name:
            raise ValueError('Categories must have a name')
        if not type:
            raise ValueError('Categories must have a type')

        category = Category(
            name=name,
            description=description,
            user=self,
            type=type,
            parent=parent
        )

        category.save()

        return category

    def add_account(self, name=None, description=None,
                    currency=None, balance=None, type=None):
        if not name:
            raise ValueError('Accounts must have a name')
        if not currency:
            currency = self.favorite_currency
        if not balance:
            balance = Decimal('0.00')
        if not type:
            raise ValueError('Accounts must have a type')

        account = Account(
            name=name,
            description=description,
            user=self,
            currency=currency,
            balance=balance,
            type=type
        )

        account.save()

        return account

    def add_budget(self, start_date=None, end_date=None):
        if not start_date:
            raise ValueError('Budgets must have a start date')
        if not end_date:
            raise ValueError('Budgets must have an end date')

        budget = Budget(
            start_date=start_date,
            end_date=end_date,
            user=self
        )

        budget.save()

        return budget


# Category
class Category(models.Model):
    """Modelo de categoria"""
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)

    user = models.ForeignKey(
        'User',
        related_name='categories',
        on_delete=models.CASCADE
    )
    parent = models.ForeignKey(
        'self',
        related_name='subcategories',
        on_delete=models.PROTECT,
        null=True
    )

    class TYPE:
        INCOME = 'I'
        EXPENSE = 'E'

        CHOICES = [
            (INCOME, 'Income'),
            (EXPENSE, 'Expense')
        ]

    type = models.CharField(max_length=1, choices=TYPE.CHOICES, default=TYPE.EXPENSE)

    def get_level(self):
        """Retorna el nivel de profundidad de la categoria"""
        if not self.parent:
            return 1

        return self.parent.get_level() + 1


class AccountLog(models.Model):
    """Modelo de log de cuenta"""
    account = models.ForeignKey('Account', related_name='logs', on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField(max_length=4, default=timezone.now().year)
    month = models.PositiveSmallIntegerField(max_length=2, default=timezone.now().month)
    balance = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        default=Decimal('0.00')
    )


# Account
class Account(models.Model):
    """Modelo de cuenta"""

    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(
        'User',
        related_name='accounts',
        on_delete=models.CASCADE
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY.CHOICES,
        default=settings.DEFAULT_CURRENCY
    )
    balance = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        default=Decimal('0.00')
    )

    class TYPE:
        CHECKING_ACCOUNT = 'C'
        SAVINGS = 'S'
        INVESTMENTS = 'I'
        WALLET = 'W'

        CHOICES = [
            (CHECKING_ACCOUNT, 'Checking Account'),
            (SAVINGS, 'Savings'),
            (INVESTMENTS, 'Investments'),
            (WALLET, 'Wallet'),
        ]
    type = models.CharField(
        max_length=1,
        choices=TYPE.CHOICES,
        default=TYPE.CHECKING_ACCOUNT
    )

    def __str__(self):
        return self.name

    def add_transaction(self, type=None, **kwargs):
        if not type:
            raise ValueError('Transaction requires a type')

        # El tipo de orden determina que funcion de modelo usara
        if type == Transaction.TYPE.TRANSFER:
            f = Transaction.objects.create_transfer
        elif type == Transaction.TYPE.INCOME:
            f = Transaction.objects.create_income
        elif type == Transaction.TYPE.EXPENSE:
            f = Transaction.objects.create_expense
        else:
            raise ValueError('Incorrect type for transaction')

        return f(account=self, **kwargs)

    def get_balance(self, year, month):
        if not year:
            year = timezone.now().year
        if not month:
            month = timezone.now().month

        account_log = self.logs.filter(year=year, month=month)
        if account_log.exists():
            balance = account_log.get().balance
        else:
            balance = self.balance

        return balance


# Transaction
class TransactionManager(models.Manager):
    """Manager del modelo de transaccion"""
    def create_transaction(self, amount=None, description=None, date=None, category=None,
                           account=None, type=None, logic_type=None, is_paid=False):
        if not amount:
            raise ValueError('Transaction must have an amount')
        if not date:
            raise ValueError('Transaction must have an date')
        if not account:
            raise ValueError('Transaction must have an account')
        if not type:
            raise ValueError('Transaction must have an type')

        transaction = Transaction(
            amount=amount,
            description=description,
            date=date,
            category=category,
            account=account,
            type=type,
            logic_type=logic_type
        )

        transaction.save()

        if is_paid:
            transaction.apply()

        return transaction

    def create_transfer(self, **kwargs):
        """Funcion de manager que crea transferencias"""

        account = kwargs.pop('account')
        destination_account = kwargs.pop('destination_account')

        transaction1 = self.create_transaction(
            **kwargs,
            account=account,
            description='Transfer output',
            type=Transaction.TYPE.TRANSFER,
            logic_type=Transaction.LOGIC_TYPE.EXPENSE
        )

        transaction2 = self.create_transaction(
            **kwargs,
            account=destination_account,
            description='Transfer input',
            type=Transaction.TYPE.TRANSFER,
            logic_type=Transaction.LOGIC_TYPE.INCOME
        )
        transaction1.linked_transaction = transaction2
        transaction2.linked_transaction = transaction1
        transaction1.save()
        transaction2.save()

        return transaction1

    def create_income(self, **kwargs):
        """Funcion de manager que crea ingresos"""
        logic_type = Transaction.LOGIC_TYPE.INCOME
        category = kwargs.get('category')
        if not category:
            raise ValueError('Income requires an income category')
        if category.type != logic_type:
            raise ValueError('Income must only have an income category')
        transaction = self.create_transaction(
            **kwargs,
            type=Transaction.TYPE.INCOME,
            logic_type=logic_type
        )

        return transaction

    def create_expense(self, **kwargs):
        """Funcion de manager que crea egresos"""
        logic_type = Transaction.LOGIC_TYPE.EXPENSE
        category = kwargs.get('category')
        if not category:
            raise ValueError('Expense requires an expense category')
        if category.type != logic_type:
            raise ValueError('Expense must only have an expense category')
        transaction = self.create_transaction(
            **kwargs,
            type=Transaction.TYPE.EXPENSE,
            logic_type=Transaction.LOGIC_TYPE.EXPENSE
        )

        return transaction


class Transaction(models.Model):
    """Modelo de transaccion"""
    amount = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        default=Decimal('0.00')
    )

    description = models.CharField(max_length=255, blank=True, null=True)

    def get_current_date(self):
        return timezone.localtime(timezone.now()).date()

    date = models.DateField(default=get_current_date)
    category = models.ForeignKey(
        'category',
        related_name='transactions',
        on_delete=models.PROTECT,
        null=True
    )
    account = models.ForeignKey(
        'Account',
        related_name='transactions',
        on_delete=models.CASCADE
    )
    linked_transaction = models.OneToOneField(
        'self',
        on_delete=models.CASCADE,
        null=True
    )

    class LOGIC_TYPE:
        INCOME = 'I'
        EXPENSE = 'E'

        CHOICES = [
            (INCOME, 'Income'),
            (EXPENSE, 'Expense')
        ]
    logic_type = models.CharField(max_length=1, choices=LOGIC_TYPE.CHOICES)

    class TYPE:
        TRANSFER = 'T'
        INCOME = 'I'
        EXPENSE = 'E'

        CHOICES = [
            (TRANSFER, 'Transfer'),
            (INCOME, 'Income'),
            (EXPENSE, 'Expense')
        ]
    type = models.CharField(max_length=1, choices=TYPE.CHOICES)
    is_paid = models.BooleanField(default=False)

    objects = TransactionManager()

    def apply(self):
        """Applies the changes in balance of an unpaid transaction"""
        if self.is_paid:
            raise ValueError('The transasction has been applied')

        amount = self.amount

        if self.logic_type == Transaction.LOGIC_TYPE.EXPENSE:
            amount *= -1

        self.account.balance += amount
        self.account.save()
        self.is_paid = True
        self.save()

    def unapply(self):
        """Undoes the changes in balance of a paid transaction"""
        if not self.is_paid:
            raise ValueError('The transasction has not been applied')

        amount = self.amount

        if self.type == Transaction.LOGIC_TYPE.INCOME:
            amount *= -1

        self.account.balance += amount
        self.account.save()
        self.is_paid = False
        self.save()


# Tag
class TagManager(models.Manager):
    """Manager de etiqueta"""
    def create_tag(self, name):
        if not name:
            raise ValueError('Tags must have a name')
        tag = self.model(name=name)
        tag.save()

        return tag

    def get_or_create_tag(self, name):
        if not name:
            raise ValueError('Tags must have a name')
        try:
            tag = Tag.objects.get(name=name)
        except Tag.DoesNotExist:
            tag = self.create_tag(name)
        tag.save()
        return tag


class Tag(models.Model):
    """Modelo de etiquetas"""
    name = models.CharField(max_length=255)

    objects = TagManager()

    def __str__(self):
        return self.name


# # Budget
# class BudgetManager(models.Manager):
#     """Manager of the budget model"""
#     def create_budget(self, start_date, end_date):
#         if not start_date:
#             raise ValueError('Budgets must have a start date')
#         if not end_date:
#             raise ValueError('Budgets must have an end date')
#         budget = self.model(start_date=start_date, end_date=end_date)
#         budget.save()
#
#         return budget


class Budget(models.Model):
    """Budget model"""

    start_date = models.DateField()
    end_date = models.DateField()
    user = models.ForeignKey('User', related_name='budgets', on_delete=models.CASCADE)

    # objects = BudgetManager()

    def __str__(self):
        return '{start_date} - {end_date}'.format(
            start_date=self.start_date,
            end_date=self.end_date
        )

    def add_category(self, category=None, planned_spending=None):
        budget_tag = BudgetCategory(
            budget=self,
            category=category,
            planned_spending=planned_spending
        )
        budget_tag.save()

        return budget_tag

    def get_total_by_category(self, category=None):
        """Returns the planned spending of the category"""
        if not category:
            raise ValueError('Category is required')

        try:
            category = self.categories.get(category=category)
        except Category.DoesNotExist:
            raise ValueError(
                'That category doesn\'t exist in the budget'
            )

        return category.planned_spending

    def get_spent_by_category(self, category=None):
        """Returns the total payed in spendings by category"""
        if not category:
            raise ValueError('Category is required')

        transactions = Transaction.objects.filter(
            account__in=self.user.accounts.all(),
            category=category,
            type=Transaction.TYPE.EXPENSE
        )
        return transactions.aggregate(
            total=models.Sum('amount')
        ).get('total')

    def get_left_by_category(self, name):
        """Returns the left to pay amount by category"""
        total = self.get_total_by_category(name)
        spent = self.get_spent_by_category(name)
        return total - spent

    @property
    def total(self):
        return self.categories.aggregate(
            total=models.Sum('planned_spending')
        ).get('total')

    @property
    def spent(self):
        transactions = Transaction.objects.filter(
            account__in=self.user.accounts.all(),
            type=Transaction.TYPE.EXPENSE
        )
        return transactions.aggregate(
            total=models.Sum('amount')
        ).get('total')

    @property
    def left(self):
        return self.total - self.spent


class BudgetCategory(models.Model):
    budget = models.ForeignKey(
        'Budget',
        related_name='categories',
        on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        'Category',
        related_name='budgets',
        on_delete=models.CASCADE
    )
    planned_spending = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )
