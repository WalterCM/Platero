from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.utils.timezone import now


# User
class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self.db)

        return user

    def create_superuser(self, email, password=None):
        """Creates and saves a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self.db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


# Tag
class TagManager(models.Manager):
    """Manager of the tag model"""
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
    """Tag model"""
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
#     tags = models.ManyToManyField('Tag', related_name='Spendings', blank=True)
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
