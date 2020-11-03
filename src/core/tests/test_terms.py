from django.test import TestCase

from core.models import Term


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
