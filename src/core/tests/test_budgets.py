# from django.test import TestCase
#
# from core.models import Budget
# from core.tests import utils
#
#
# class BudgetModelTests(TestCase):
#
#     def test_create_budget(self):
#         """Test creating a new budget"""
#         start_date = '2020-11-02'
#         end_date = '2020-11-30'
#         budget = Budget.objects.create_budget(
#             start_date=start_date,
#             end_date=end_date
#         )
#
#         self.assertEqual(Budget.start_date, start_date)
#         self.assertEqual(Budget.end_date, end_date)
#
#     def test_get_totals_from_budget(self):
#         """Tests the budget properties based on spendings"""
#         budget = utils.get_test_budget()
#         budget.save()
#         budget.add_tag('Comida', 1000.0)
#         budget.add_spending(
#             name='Galletas',
#             amount=100.0
#         )
#         budget.add_spending(
#             name='Galletas',
#             amount=50.0
#         )
#         budget.add_spending(
#             name='Galletas',
#             amount=45.5
#         )
#
#         self.assertEqual(budget.total_to_pay, 1000.0)
#         self.assertEqual(budget.total_payed, 195.5)
#         self.assertEqual(budget.left_to_pay, 804.5)
#
#     def test_get_totals_by_tag(self):
#         """Tests getting the budget totals by tag"""
#         budget = utils.get_test_budget()
#         budget.save()
#
#         tag_name = 'Comida'
#         budget.add_tag(tag_name, 1000.0)
#         budget.add_spending(
#             name='Galletas',
#             amount=100.0,
#             tags=[tag_name]
#         )
#         budget.add_spending(
#             name='Galletas',
#             amount=50.0,
#             tags=[tag_name]
#         )
#         budget.add_spending(
#             name='Galletas',
#             amount=45.5,
#             tags=[tag_name]
#         )
#         budget.add_spending(
#             name='Otros',
#             amount=1000.0
#         )
#
#         self.assertEqual(budget.get_total_to_pay_by_tag(tag_name), 1000.0)
#         self.assertEqual(budget.get_total_payed_by_tag(tag_name), 195.5)
#         self.assertEqual(budget.get_left_to_pay_by_tag(tag_name), 804.5)
