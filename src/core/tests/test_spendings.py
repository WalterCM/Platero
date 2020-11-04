from django.test import TestCase

from core.tests import utils


class SpendingModelTests(TestCase):

    def test_create_spending(self):
        """Tests creating a new spending"""
        tag = utils.get_test_tag()
        tag.save()

        term = utils.get_test_term()
        term.save()

        name = 'Galleta'
        total_to_pay = 1000.0
        spending = term.add_spending(
            name=name,
            tags=[tag.name],
            total_to_pay=total_to_pay
        )

        self.assertEqual(spending.name, name)
        self.assertEqual(float(spending.total_to_pay), total_to_pay)
        self.assertEqual(spending.tags.get(), tag)
        self.assertEqual(spending.left_to_pay, total_to_pay)

    def test_create_spending_with_payed_amoaunt(self):
        """Tests creating a spending with total_payed"""
        term = utils.get_test_term()
        term.save()

        name = 'Galleta'
        total_to_pay = 1000.0
        total_payed = 500.0
        spending = term.add_spending(
            name=name,
            total_to_pay=total_to_pay,
            total_payed=total_payed
        )

        self.assertEqual(spending.name, name)
        self.assertEqual(spending.total_to_pay, total_to_pay)
        self.assertEqual(spending.total_payed, total_payed)
        # Coincidence. Change if necessary
        self.assertEqual(spending.left_to_pay, total_payed)

    def test_add_tag_to_spending(self):
        """Tests adding tags to a spending"""
        term = utils.get_test_term()
        term.save()
        spending = utils.get_test_spending(term)
        spending.save()

        name = 'comida'
        spending.add_tag(name=name)

        self.assertEqual(spending.tags.get().name, name)
