from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.tests import utils
from core.models import Category, Account, Transaction
from core.globals import CURRENCY


LIST_CREATE_TRANSACTION_URL = reverse('transactions:transaction-list')


def get_retrieve_update_destroy_transaction_url(lookup=None):
    return reverse('transactions:transaction-detail', kwargs={'pk': lookup})


class PublicTests(TestCase):
    """Testea el API de transacciones (publico)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_list_url_forbidden(self):
        """Testea que necesita estar autenticado para usar el url de listado o creado"""
        res = self.client.get(LIST_CREATE_TRANSACTION_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        res = self.client.post(LIST_CREATE_TRANSACTION_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_update_delete_url_forbidden(self):
        """Testea que necesita autenticacion para usar el url de detalle"""
        res = self.client.get(get_retrieve_update_destroy_transaction_url())
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        res = self.client.put(get_retrieve_update_destroy_transaction_url())
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        res = self.client.delete(get_retrieve_update_destroy_transaction_url())
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateTests(TestCase):
    """Testea el API de transacciones (privado)"""

    def setUp(self):
        self.user = utils.get_test_user()

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.account = utils.get_test_account(
            user=self.user,
            currency=CURRENCY.PEN,
            balance=100.0,
            _type=Account.TYPE.SAVINGS
        )
        utils.get_test_transaction(self.account)
        utils.get_test_transaction(self.account)
        utils.get_test_transaction(self.account)

        other_account = utils.get_test_account(user=self.user)

        common_payload = {
            'amount': 10.0,
            'date': '2021-07-06',
            'is_paid': True,
            'account': self.account.id
        }

        self.transfer_payload = {
            **common_payload,
            'destination_account': other_account.id,
            'type': Transaction.TYPE.TRANSFER
        }

        common_payload['description'] = 'descripcion test'

        self.income_payload = {
            **common_payload,
            'category': utils.get_test_category(
                user=self.user,
                type=Category.TYPE.INCOME
            ).id,
            'type': Transaction.TYPE.INCOME
        }

        self.expense_payload = {
            **common_payload,
            'category': utils.get_test_category(
                user=self.user,
                type=Category.TYPE.EXPENSE
            ).id,
            'type': Transaction.TYPE.EXPENSE
        }

    def test_list_transactions(self):
        """Testea que un usuario pueda listar sus transacciones"""
        res = self.client.get(LIST_CREATE_TRANSACTION_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # self.assertEqual(len(res.data), self.account.transaction.count())

    def test_create_transfer(self):
        """Testea que un usuario pueda crear una transferencia"""
        payload = self.transfer_payload.copy()
        res = self.client.post(LIST_CREATE_TRANSACTION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_income(self):
        """Testea que un usuario pueda crear un ingreso"""
        payload = self.income_payload.copy()
        res = self.client.post(LIST_CREATE_TRANSACTION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_expense(self):
        """Testea que un usuario pueda crear un egreso"""
        payload = self.expense_payload.copy()
        res = self.client.post(LIST_CREATE_TRANSACTION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
