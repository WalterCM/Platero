import random
import string
from decimal import Decimal

from django.contrib.auth import get_user_model

from core.globals import CURRENCY
from core.models import Account, Tag  # , Budget, Spending


class TestObjectException(Exception):
    pass


def get_test_user(email=None):
    letters = string.ascii_lowercase
    max_letters = 10
    name = ''.join(random.choice(letters) for i in range(max_letters))
    return get_user_model().objects.create_user(email or '{}@test.com'.format(name))


def get_test_account(user=None, name=None, description=None, currency=None, balance=None,
                     type=None):
    if not user:
        raise TestObjectException('Account creation requires a user')

    letters = string.ascii_lowercase
    max_letters = 10
    max_balance = 1000.0
    return user.add_account(
        name=name or ''.join(random.choice(letters) for i in range(max_letters)),
        description=description,
        currency=currency or random.choices(CURRENCY.CHOICES)[0][0],
        balance=balance or Decimal(str(round(random.uniform(0.0, max_balance), 2))),
        type=type or random.choices(Account.TYPE.CHOICES)[0][0]
    )


def get_test_tag():
    return Tag(name='comida')

# def get_test_budget():
#     return Budget(
#         start_date='2020-11-02',
#         end_date='2020-11-30'
#     )
#
#
# def get_test_spending(budget):
#     return Spending(
#         budget=budget,
#         amount=10.0
#     )
