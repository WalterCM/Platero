from core.models import Tag, Term


def get_test_tag():
    return Tag(name='comida')


def get_test_term():
    return Term(
        start_date='2020-11-02',
        end_date='2020-11-30'
    )
