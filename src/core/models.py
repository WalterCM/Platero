from decimal import Decimal

from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin


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


# Term
class TermManager(models.Manager):
    """Manager of the term model"""
    def create_term(self, start_date, end_date):
        if not start_date:
            raise ValueError('Terms must have a start date')
        if not end_date:
            raise ValueError('Terms must have an end date')
        term = self.model(start_date=start_date, end_date=end_date)
        term.save()

        return term


class Term(models.Model):
    """Term model"""

    start_date = models.DateField()
    end_date = models.DateField()

    objects = TermManager()

    def add_spending(self, name, total_to_pay, total_payed=0.0, tags=None):
        if not name:
            raise ValueError('Spendings must have a name')
        if not total_to_pay:
            raise ValueError('Spending must have a total to pay')
        spending = Spending(
            name=name,
            term=self,
            total_to_pay=total_to_pay,
            total_payed=total_payed
        )
        spending.save()

        if tags:
            for tag in tags:
                spending.add_tag(tag)

        return spending

    @property
    def total_to_pay(self):
        return self.spendings.aggregate(
            total=models.Sum('total_to_pay')
        ).get('total')

    @property
    def total_payed(self):
        return self.spendings.aggregate(
            total=models.Sum('total_payed')
        ).get('total')

    @property
    def left_to_pay(self):
        return self.spendings.annotate(
            left_to_pay=models.F('total_to_pay') - models.F('total_payed')
        ).aggregate(
            total=models.Sum('left_to_pay')
        ).get('total')


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

        return tag


class Tag(models.Model):
    """Tag model"""
    name = models.CharField(max_length=255)

    objects = TagManager()


# Spending
class Spending(models.Model):
    """Spending model"""
    name = models.CharField(max_length=255)
    tags = models.ManyToManyField('Tag', related_name='Spendings')
    term = models.ForeignKey(
        'Term',
        related_name='spendings',
        on_delete=models.CASCADE
    )
    total_to_pay = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )
    total_payed = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.00')
    )

    def add_tag(self, name):
        if not name:
            raise ValueError('Tags must have a name')
        self.tags.add(Tag.objects.get_or_create_tag(name=name))

    @property
    def left_to_pay(self):
        return self.total_to_pay - self.total_payed
