from core.models import User, Tag  # , Budget, Spending


def get_test_user():
    return User.objects.create_user('test@test.com')


def get_test_tag():
    return Tag(name='comida')


# def get_test_budget():
#     return Budget(
#         start_date='2020-11-02',
#         end_date='2020-11-30'
#     )
#
#
# def get_test_spending(budget):
#     return Spending(
#         budget=budget,
#         amount=10.0
#     )
