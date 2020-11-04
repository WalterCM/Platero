from core.models import Tag, Term, Spending


def get_test_tag():
    return Tag(name='comida')


def get_test_term():
    return Term(
        start_date='2020-11-02',
        end_date='2020-11-30'
    )


def get_test_spending(term):
    return Spending(
        term=term,
        total_to_pay=1000.0
    )
