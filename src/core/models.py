from decimal import Decimal

from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone

from django.conf import settings

from core.globals import CURRENCY


# User
class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Crea y guarda un nuevo usuario"""
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self.db)

        return user

    def create_superuser(self, email, password=None):
        """Crea y guarda y nuevo superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self.db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Usuario personalizado que usa email en vez de username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    favorite_currency = models.CharField(
        max_length=3,
        choices=CURRENCY.CHOICES,
        default=settings.DEFAULT_CURRENCY
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'

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
#
#
# class Budget(models.Model):
#     """Budget model"""
#
#     start_date = models.DateField()
#     end_date = models.DateField()
#
#     objects = BudgetManager()
#
#     def __str__(self):
#         return '{start_date} - {end_date}'.format(
#             start_date=self.start_date,
#             end_date=self.end_date
#         )
#
#     def add_tag(self, name, planned_spending):
#         tag = Tag.objects.get_or_create_tag(name)
#         tag.save()
#
#         budget_tag = BudgetTag(
#             budget=self,
#             tag=tag,
#             planned_spending=planned_spending
#         )
#         budget_tag.save()
#
#         return budget_tag
#
#     def get_total_to_pay_by_tag(self, name):
#         """Returns the planned spending of the tag"""
#         try:
#             tag = self.tags.get(tag__name=name)
#         except Tag.DoesNotExist:
#             raise ValueError(
#                 'A tag with that name doesn\'t exist in this budget'
#             )
#
#         return tag.planned_spending
#
#     def get_total_payed_by_tag(self, name):
#         """Returns the total payed in spendings by tag"""
#         return self.spendings.filter(tags__name=name).aggregate(
#             total=models.Sum('amount')
#         ).get('total')
#
#     def get_left_to_pay_by_tag(self, name):
#         """Returns the left to pay amount by tag"""
#         total_to_pay = self.get_total_to_pay_by_tag(name)
#         total_payed = self.get_total_payed_by_tag(name)
#         return total_to_pay - total_payed
#
#     @property
#     def total_to_pay(self):
#         return self.tags.aggregate(
#             total=models.Sum('planned_spending')
#         ).get('total')
#
#     @property
#     def total_payed(self):
#         return self.spendings.aggregate(
#             total=models.Sum('amount')
#         ).get('total')
#
#     @property
#     def left_to_pay(self):
#         return self.total_to_pay - self.total_payed
#
#
# class BudgetTag(models.Model):
#     budget = models.ForeignKey(
#         'Budget',
#         related_name='tags',
#         on_delete=models.CASCADE
#     )
#     tag = models.ForeignKey(
#         'Tag',
#         related_name='budgets',
#         on_delete=models.CASCADE
#     )
#     planned_spending = models.DecimalField(
#         max_digits=6,
#         decimal_places=2
#     )


# # Spending
# class Spending(models.Model):
#     """Spending model"""
#     name = models.CharField(max_length=255)
#     tags = models.ManyToManyField('Tag', related_name='Spendings', blank=True
#     )
#     budget = models.ForeignKey(
#         'Budget',
#         related_name='spendings',
#         on_delete=models.CASCADE
#     )
#     amount = models.DecimalField(
#         max_digits=6,
#         decimal_places=2
#     )
#     created_at = models.DateField(default=now)
#
#     def __str__(self):
#         return self.name
#
#     def add_tag(self, name):
#         if not name:
#             raise ValueError('Tags must have a name')
#         self.tags.add(Tag.objects.get_or_create_tag(name=name))
