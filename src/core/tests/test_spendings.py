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
        amount = 1000.0
        spending = term.add_spending(
            name=name,
            tags=[tag.name],
            amount=amount
        )

        self.assertEqual(spending.name, name)
        self.assertEqual(spending.amount, amount)
        self.assertEqual(spending.tags.get(), tag)

    def test_create_spending_with_payed_amoaunt(self):
        """Tests creating a spending with total_payed"""
        term = utils.get_test_term()
        term.save()

        name = 'Galleta'
        amount = 10.0
        spending = term.add_spending(
            name=name,
            amount=amount,
        )

        self.assertEqual(spending.name, name)
        self.assertEqual(spending.amount, amount)

    def test_add_tag_to_spending(self):
        """Tests adding tags to a spending"""
        term = utils.get_test_term()
        term.save()
        spending = utils.get_test_spending(term)
        spending.save()

        name = 'comida'
        spending.add_tag(name=name)

        self.assertEqual(spending.tags.get().name, name)
