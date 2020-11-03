from django.test import TestCase

from core.tests import utils


class SpendingModelTests(TestCase):

    def test_create_spending(self):
        """Test creating a new spending"""
        tag = utils.get_test_tag()
        tag.save()

        term = utils.get_test_term()
        term.save()

        name = 'Galleta'
        spending = term.add_spending(
            name=name,
            tags=[tag.name]
        )

        self.assertEqual(spending.tags.get(), tag)
