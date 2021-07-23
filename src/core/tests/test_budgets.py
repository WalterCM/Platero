from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from core.models import User, Category, Transaction
from core.tests import utils


class BudgetModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('test@test.com')
        self.category = utils.get_test_category(
            user=self.user,
            name='Comida',
            type=Category.TYPE.EXPENSE
        )
        self.account = utils.get_test_account(user=self.user)
        self.budget = utils.get_test_budget(user=self.user)
        self.budget.add_category(self.category, 1000.0)
        self.category2 = utils.get_test_category(
            user=self.user,
            name='Juegos',
            type=Category.TYPE.EXPENSE
        )
        self.budget.add_category(self.category2, 2000.0)

    def test_create_budget(self):
        """Testea creando un nuevo presupuesto"""
        start_date = timezone.now()
        end_date = start_date + timedelta(days=30)
        budget = self.user.add_budget(
            start_date=start_date,
            end_date=end_date
        )

        self.assertEqual(budget.start_date, start_date)
        self.assertEqual(budget.end_date, end_date)

    def test_get_totals_from_budget(self):
        """Tests the budget properties based on expenses"""

        expense = utils.get_test_transaction(
            account=self.account,
            type=Transaction.TYPE.EXPENSE,
            amount=100.0,
            category=self.category
        )

        self.assertEqual(self.budget.total, 3000.0)
        self.assertEqual(self.budget.spent, expense.amount)
        self.assertEqual(self.budget.left, 2900.0)

    def test_get_totals_by_tag(self):
        """Tests getting the budget totals by category"""
        expense = utils.get_test_transaction(
            account=self.account,
            type=Transaction.TYPE.EXPENSE,
            amount=100.0,
            category=self.category
        )
        expense2 = utils.get_test_transaction(
            account=self.account,
            type=Transaction.TYPE.EXPENSE,
            amount=300.0,
            category=self.category2
        )

        self.assertEqual(self.budget.total, 3000.0)
        self.assertEqual(self.budget.spent, expense.amount + expense2.amount)
        self.assertEqual(self.budget.left, 2600.0)
        self.assertEqual(self.budget.get_total_by_category(self.category), 1000.0)
        self.assertEqual(self.budget.get_spent_by_category(self.category), expense.amount)
        self.assertEqual(self.budget.get_left_by_category(self.category), 900.0)
