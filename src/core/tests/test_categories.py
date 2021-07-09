from django.test import TestCase

from core.models import User, Category


class CategoryModelTests(TestCase):
    def setUp(self):
        self.data = {
            'name': 'My test category',
            'description': 'Test description',
            'type': Category.TYPE.EXPENSE
        }

        self.user = User.objects.create_user('test@test.com')

    def test_create_category(self):
        """Testea creando una nueva categoria"""
        data = self.data.copy()
        category = self.user.add_category(**data)

        self.assertEqual(category.name, data.get('name'))
        self.assertEqual(category.description, data.get('description'))

    def test_subcategory(self):
        """Testea creando una categoria dentro de otra"""
        data = self.data.copy()
        category = self.user.add_category(**data)

        data['name'] = 'My second test category'
        data['parent'] = category

        subcategory = self.user.add_category(**data)

        self.assertEqual(subcategory.name, data.get('name'))
        self.assertEqual(subcategory.parent, category)

    def test_ncategory(self):
        """Testea que se pueden crear varios niveles de cateogiras """
        data = self.data.copy()
        times = 6
        category = None
        for i in range(times):
            data['name'] = 'Category {}'.format(i)
            category = self.user.add_category(**data)
            data['parent'] = category

        self.assertEqual(category.get_level(), times)

    def test_create_category_no_name(self):
        """Testea que no se pueda crear una categoria sin nombre"""
        data = self.data.copy()
        del data['name']

        with self.assertRaises(ValueError):
            self.user.add_category(**data)

    def test_Create_category_no_description(self):
        """Testea que se pueda crear una categoria sin descripcion"""
        data = self.data.copy()
        del data['description']

        category = self.user.add_category(**data)

        self.assertEqual(category.name, data.get('name'))

    def test_create_category_no_type(self):
        """Testea que no se pueda crear una cateogir asin tipo"""
        data = self.data.copy()
        del data['type']

        with self.assertRaises(ValueError):
            self.user.add_category(**data)
