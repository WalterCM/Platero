from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.tests import utils
from core.models import Account, Transaction
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
            'type': Transaction.CREATION_TYPE.TRANSFER
        }

        common_payload['description'] = 'descripcion test'

        self.income_payload = {
            **common_payload,
            'type': Transaction.CREATION_TYPE.INCOME
        }

        self.expense_payload = {
            **common_payload,
            'type': Transaction.CREATION_TYPE.EXPENSE
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

    # def test_create_account_no_name(self):
    #     """Testea que un usuario no pueda crear una cuenta sin nombre"""
    #     payload = self.payload.copy()
    #     del payload['name']
    #
    #     res = self.client.post(LIST_CREATE_ACCOUNT_URL, payload)
    #     self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    #
    # def test_create_account_no_description(self):
    #     """Testea que un usuario si pueda crear una cuenta sin description"""
    #     payload = self.payload.copy()
    #     del payload['description']
    #
    #     res = self.client.post(LIST_CREATE_ACCOUNT_URL, payload)
    #     self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    #
    # def test_create_account_no_currency(self):
    #     """Testea que un usuario no pueda crear una cuenta sin moneda"""
    #     payload = self.payload.copy()
    #     del payload['currency']
    #
    #     res = self.client.post(LIST_CREATE_ACCOUNT_URL, payload)
    #     self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(res.data.get('currency'), self.user.favorite_currency)
    #
    # def test_create_account_no_type(self):
    #     """Testea que un usuario no pueda crear una cuenta sin tipo"""
    #     payload = self.payload.copy()
    #     del payload['type']
    #
    #     res = self.client.post(LIST_CREATE_ACCOUNT_URL, payload)
    #     self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_retrieve_account(self):
    #     """Testea que un usuario pueda obtener informacion de una cuenta especifica"""
    #     res = self.client.get(get_retrieve_update_destroy_account_url(self.account.id))
    #
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertEqual(res.data.get('id'), self.account.id)
    #     self.assertEqual(res.data.get('name'), self.account.name)
    #     self.assertEqual(res.data.get('description'), self.account.description)
    #     self.assertEqual(res.data.get('currency'), self.account.currency)
    #     self.assertEqual(res.data.get('balance'), str(self.account.balance))
    #     self.assertEqual(res.data.get('type'), self.account.type)
    #
    # def test_retrieve_account_from_another_user(self):
    #     """Testea que un usuario no pueda obtener info de una cuenta que no es suya"""
    #     res = self.client.get(
    #         get_retrieve_update_destroy_account_url(self.another_user_account.id)
    #     )
    #
    #     self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
    #
    # def test_update_account(self):
    #     """Testea que un usuario pueda actualizar su propia cuenta"""
    #     payload = {
    #         'name': 'New account name',
    #         'description': 'New description',
    #         'currency': CURRENCY.USD,
    #         'type': Account.TYPE.CHECKING_ACCOUNT
    #     }
    #     self.assertNotEqual(self.account.name, payload.get('name'))
    #     self.assertNotEqual(self.account.description, payload.get('description'))
    #     self.assertNotEqual(self.account.currency, payload.get('currency'))
    #     self.assertNotEqual(self.account.type, payload.get('type'))
    #
    #     res = self.client.put(
    #         get_retrieve_update_destroy_account_url(self.account.id),
    #         payload
    #     )
    #
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.account.refresh_from_db()
    #     self.assertEqual(self.account.name, payload.get('name'))
    #     self.assertEqual(self.account.description, payload.get('description'))
    #     self.assertEqual(self.account.currency, payload.get('currency'))
    #     self.assertEqual(self.account.type, payload.get('type'))
    #
    # def test_partial_update_account(self):
    #     """Testea que un usuario pueda actualizar parcialmente una cuenta suya"""
    #     payload = {
    #         'name': 'New account name',
    #         'description': 'New description'
    #     }
    #     self.assertNotEqual(self.account.name, payload.get('name'))
    #     res = self.client.patch(
    #         get_retrieve_update_destroy_account_url(self.account.id),
    #         payload
    #     )
    #
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.account.refresh_from_db()
    #     self.assertEqual(self.account.name, payload.get('name'))
    #
    # def test_update_account_from_another_user(self):
    #     """Testea que un usuario no pueda actualizar una cuenta que no es suya"""
    #     payload = {
    #         'name': 'New account name',
    #         'description': 'New description',
    #         'currency': CURRENCY.USD,
    #         'type': Account.TYPE.CHECKING_ACCOUNT
    #     }
    #     res = self.client.put(
    #         get_retrieve_update_destroy_account_url(self.another_user_account.id),
    #         payload
    #     )
    #     self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
