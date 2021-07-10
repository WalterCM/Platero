from decimal import Decimal

from django.test import TestCase

from core import globals
from core.tests import utils
from core.models import Category, Account, Transaction


class TransactionTests(TestCase):
    def setUp(self):
        user = utils.get_test_user()
        self.account_data = {
            'currency': globals.CURRENCY.PEN,
            'balance': Decimal('1000.0'),
            'name': 'Cuenta corriente',
            'description': 'Mi primera cuenta corriente',
            'type': Account.TYPE.CHECKING_ACCOUNT
        }
        self.account = user.add_account(**self.account_data)
        self.transaction_data = {
            'amount': Decimal('10.00'),
            'description': 'Transaccion de prueba',
            'is_paid': True,
            'date': '2021-06-02',
            'account': self.account
        }


class TransactionModelTests(TransactionTests):
    def setUp(self):
        super().setUp()
        self.transaction_data['type'] = Transaction.TYPE.EXPENSE
        self.transaction_data['logic_type'] = Transaction.TYPE.EXPENSE

    def test_create_transaction(self):
        """Testea creando un nuevo transaccion"""
        transaction_data = self.transaction_data.copy()
        transaction = Transaction.objects.create_transaction(
            **transaction_data
        )

        self.assertEqual(transaction.amount, transaction_data.get('amount'))
        self.assertEqual(transaction.is_paid, transaction_data.get('is_paid'))
        self.assertEqual(transaction.date, transaction_data.get('date'))
        self.assertEqual(transaction.account, transaction_data.get('account'))

    def test_transaction_without_amount(self):
        """Testea creacion de transaccion sin especificar cantidad"""
        transaction_data = self.transaction_data.copy()
        del transaction_data['amount']

        with self.assertRaises(ValueError):
            Transaction.objects.create_transaction(**transaction_data)

    def test_transaction_without_description(self):
        """Testea creacion de transaccion sin especificar descripccion"""
        transaction_data = self.transaction_data.copy()
        del transaction_data['description']

        transaction = Transaction.objects.create_transaction(
            **transaction_data
        )

        self.assertEqual(transaction.description, None)

    def test_transaction_without_is_paid(self):
        """Testea creacion de transaccion sin especificar is_paid"""
        transaction_data = self.transaction_data.copy()
        del transaction_data['is_paid']
        transaction = Transaction.objects.create_transaction(
            **transaction_data
        )

        self.assertEqual(transaction.is_paid, False)

    def test_transaction_without_date(self):
        """Testea creacion de transaccion sin especificar fecha"""
        transaction_data = self.transaction_data.copy()
        del transaction_data['date']

        with self.assertRaises(ValueError):
            Transaction.objects.create_transaction(**transaction_data)

    def test_transaction_without_account(self):
        """Testea creacion de transaccion sin especificar cuenta"""
        transaction_data = self.transaction_data.copy()
        del transaction_data['account']

        with self.assertRaises(ValueError):
            Transaction.objects.create_transaction(**transaction_data)

    def test_transaction_without_type(self):
        """Testea de de creacion de transaccion sin especificar tipo"""
        transaction_data = self.transaction_data.copy()
        del transaction_data['type']

        with self.assertRaises(ValueError):
            Transaction.objects.create_transaction(**transaction_data)

    def test_create_two_transactions(self):
        """Testea creacion de una transaccion despues de la otra"""
        transaction_data = self.transaction_data.copy()
        transaction1 = Transaction.objects.create_transaction(
            **transaction_data
        )
        transaction2 = Transaction.objects.create_transaction(
            **transaction_data
        )

        self.assertEqual(transaction1.amount, transaction_data.get('amount'))
        self.assertEqual(transaction2.amount, transaction_data.get('amount'))

    def test_apply_transaction(self):
        """Testea la aplicacion de una transaccion sin pagar"""
        transaction_data = self.transaction_data.copy()
        transaction_data['is_paid'] = False
        transaction = Transaction.objects.create_transaction(
            **transaction_data
        )

        self.assertEqual(transaction.is_paid, False)
        self.assertEqual(self.account.balance, Decimal('1000.0'))

        transaction.apply()

        self.assertEqual(transaction.is_paid, True)
        self.assertEqual(self.account.balance, Decimal('990.0'))

    def test_unapply_transaction(self):
        """Testea la desaplicacion de una transaccion pagada"""
        transaction_data = self.transaction_data.copy()
        transaction_data['is_paid'] = True
        transaction = Transaction.objects.create_transaction(
            **transaction_data
        )

        self.assertEqual(transaction.is_paid, True)
        self.assertEqual(self.account.balance, Decimal('990.0'))

        transaction.unapply()

        self.assertEqual(transaction.is_paid, False)
        self.assertEqual(self.account.balance, Decimal('1000.0'))

    def test_apply_paid_transaction(self):
        """Testea que una transaccion pagada no pueda ser aplicada nuevamente"""
        transaction_data = self.transaction_data.copy()
        transaction_data['is_paid'] = True
        transaction = Transaction.objects.create_transaction(
            **transaction_data
        )

        with self.assertRaises(ValueError):
            transaction.apply()

    def test_unapply_unpaid_transaction(self):
        """Testea que una transaccion sin pagar pueda ser desaplicada"""
        transaction_data = self.transaction_data.copy()
        transaction_data['is_paid'] = False
        transaction = Transaction.objects.create_transaction(
            **transaction_data
        )

        with self.assertRaises(ValueError):
            transaction.unapply()


class TransferTests(TransactionTests):
    def setUp(self):
        super().setUp()
        self.account2 = self.account.user.add_account(**self.account_data)
        del self.transaction_data['account']
        del self.transaction_data['description']
        self.transaction_data['account'] = self.account
        self.transaction_data['destination_account'] = self.account2

    def test_create_new_transfer(self):
        """Testea crear una nueva transferencia"""
        transaction_data = self.transaction_data.copy()
        transaction = Transaction.objects.create_transfer(
            **transaction_data
        )
        self.assertEqual(self.account.balance, Decimal('990.0'))
        self.assertEqual(self.account2.balance, Decimal('1010.0'))
        self.assertEqual(transaction.linked_transaction.account, self.account2)
        self.assertEqual(
            self.account2.transactions.get().linked_transaction,
            transaction
        )


class IncomeTests(TransactionTests):
    def test_create_new_income(self):
        """Testea crear una nueva ingreso"""
        transaction_data = self.transaction_data.copy()
        transaction_data['category'] = utils.get_test_category(
            user=self.account.user,
            type=Category.TYPE.INCOME
        )
        Transaction.objects.create_income(
            **transaction_data
        )

        self.assertEqual(self.account.balance, Decimal('1010.0'))


class ExpenseTests(TransactionTests):
    def test_create_new_expense(self):
        """Testea crear un nuevo egreso"""
        transaction_data = self.transaction_data.copy()
        transaction_data['category'] = utils.get_test_category(
            user=self.account.user,
            type=Category.TYPE.EXPENSE
        )
        Transaction.objects.create_expense(
            **transaction_data
        )

        self.assertEqual(self.account.balance, Decimal('990.0'))
