from django.test import TestCase

from core.models import User


class BudgetModelTests(TestCase):

    def test_create_account(self):
        """Test creating a new account"""
        user = User.objects.create_user('test@test.com')

        account_data = {
            'name': 'Cuenta de ahorros',
            'description': 'Mi primera cuenta de ahorros',
            'type': 'savings'
        }
        account = user.add_account(**account_data)

        self.assertEqual(account.user, user)
        self.assertEqual(account.name, account_data['name'])
        self.assertEqual(account.description, account_data['description'])
        self.assertEqual(account.type, account_data['type'])
