from decimal import Decimal

from django.test import TestCase
from django.conf import settings

from core.models import User, Account


class AccountModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('test@test.com')
        self.account_data = {
            'currency': 'PEN',
            'name': 'Cuenta de ahorros',
            'description': 'Mi primera cuenta de ahorros',
            'type': Account.TYPE.SAVINGS
        }

    def test_create_account(self):
        """Testea creando una cuenta"""
        account_data = self.account_data.copy()
        account = self.user.add_account(**account_data)

        self.assertEqual(account.user, self.user)
        self.assertEqual(account.name, account_data['name'])
        self.assertEqual(account.description, account_data['description'])
        self.assertEqual(account.type, account_data['type'])

    def test_create_account_with_amount(self):
        """Testea creando una cuenta con una cantidad establecida"""
        account_data = self.account_data.copy()
        account_data['balance'] = Decimal('1000.0')

        account = self.user.add_account(**account_data)

        self.assertEqual(account.balance, account_data.get('balance'))

    def test_create_account_without_currency(self):
        """Testea crear una cuenta sin especificar una moneda"""
        account_data = self.account_data.copy()
        del account_data['currency']

        account = self.user.add_account(**account_data)

        self.assertEqual(account.currency, settings.DEFAULT_CURRENCY)

    def test_account_without_name(self):
        """Testea crear una cuenta sin especificar un nombre"""
        account_data = self.account_data.copy()
        del account_data['name']

        with self.assertRaises(ValueError):
            self.user.add_account(**account_data)

    def test_account_without_description(self):
        """Testea crear una nueva cuenta sin especificar descripcion"""
        account_data = self.account_data.copy()
        del account_data['description']

        account = self.user.add_account(**account_data)

        self.assertEqual(account.description, None)

    def test_account_without_type(self):
        """Testea crear una cuenta sin especificar un tipo"""
        account_data = self.account_data.copy()
        del account_data['type']

        with self.assertRaises(ValueError):
            self.user.add_account(**account_data)
