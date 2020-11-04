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
        term.add_spending(
            name='Galletas',
            total_to_pay=100.0,
            total_payed=25.5
        )
        term.add_spending(
            name='Deuda',
            total_to_pay=700.0,
            total_payed=620.0
        )
        term.add_spending(
            name='Emergencia',
            total_to_pay=100.0,
            total_payed=0.0
        )

        self.assertEqual(term.total_to_pay, 900.0)
        self.assertEqual(term.total_payed, 645.5)
        self.assertEqual(term.left_to_pay, 254.5)
