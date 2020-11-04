from django.test import TestCase

from core.models import Term
from core.tests import utils


class TermModelTests(TestCase):

    def test_create_term(self):
        """Test creating a new term"""
        start_date = '2020-11-02'
        end_date = '2020-11-30'
        term = Term.objects.create_term(
            start_date=start_date,
            end_date=end_date
        )

        self.assertEqual(term.start_date, start_date)
        self.assertEqual(term.end_date, end_date)

    def test_get_totals_from_term(self):
        """Tests the term properties based on spendings"""
        term = utils.get_test_term()
        term.save()
        term.add_tag('Comida', 1000.0)
        term.add_spending(
            name='Galletas',
            amount=100.0
        )
        term.add_spending(
            name='Galletas',
            amount=50.0
        )
        term.add_spending(
            name='Galletas',
            amount=45.5
        )

        self.assertEqual(term.total_to_pay, 1000.0)
        self.assertEqual(term.total_payed, 195.5)
        self.assertEqual(term.left_to_pay, 804.5)

    def test_get_totals_by_tag(self):
        """Tests getting the term totals by tag"""
        term = utils.get_test_term()
        term.save()

        tag_name = 'Comida'
        term.add_tag(tag_name, 1000.0)
        term.add_spending(
            name='Galletas',
            amount=100.0,
            tags=[tag_name]
        )
        term.add_spending(
            name='Galletas',
            amount=50.0,
            tags=[tag_name]
        )
        term.add_spending(
            name='Galletas',
            amount=45.5,
            tags=[tag_name]
        )
        term.add_spending(
            name='Otros',
            amount=1000.0
        )

        self.assertEqual(term.get_total_to_pay_by_tag(tag_name), 1000.0)
        self.assertEqual(term.get_total_payed_by_tag(tag_name), 195.5)
        self.assertEqual(term.get_left_to_pay_by_tag(tag_name), 804.5)
