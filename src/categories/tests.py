from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.tests import utils
from core.models import Category

LIST_CREATE_CATEGORY_URL = reverse('categories:category-list')


def get_retrieve_update_destroy_category_url(lookup=None):
    return reverse('categories:category-detail', kwargs={'pk': lookup})


class PublicTests(TestCase):
    """Testea el API de categorias (publico)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_list_url_unauthorized(self):
        """Testea que necesita estar autenticado para usar el url de listado o creado"""
        res = self.client.get(LIST_CREATE_CATEGORY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        res = self.client.post(LIST_CREATE_CATEGORY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_update_delete_url_unauthorized(self):
        """Testea que necesita autenticacion para usar el url de detalle"""
        res = self.client.get(get_retrieve_update_destroy_category_url())
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        res = self.client.put(get_retrieve_update_destroy_category_url())
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        res = self.client.delete(get_retrieve_update_destroy_category_url())
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTests(TestCase):
    """Testea el API de categorias (privado)"""

    def setUp(self):
        self.user = utils.get_test_user()

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.category = utils.get_test_category(user=self.user, type=Category.TYPE.EXPENSE)

        self.payload = {
            'name': 'Cuenta de ahorros 1',
            'description': 'descripcion test',
            'type': Category.TYPE.EXPENSE,
            'parent': self.category.id
        }

        user2 = utils.get_test_user()
        self.another_user_category = utils.get_test_category(user=user2)

    def test_list_categories(self):
        """Testea que un usuario pueda listar sus categorias"""
        res = self.client.get(LIST_CREATE_CATEGORY_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), self.user.categories.count())

    def test_create_category(self):
        """Testea que un usuario pueda crear una categoria"""
        payload = self.payload.copy()
        res = self.client.post(LIST_CREATE_CATEGORY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data.get('name'), payload.get('name'))
        self.assertEqual(res.data.get('description'), payload.get('description'))
        self.assertEqual(res.data.get('type'), payload.get('type'))

    def test_create_category_no_name(self):
        """Testea que un usuario no pueda crear una categoria sin nombre"""
        payload = self.payload.copy()
        del payload['name']

        res = self.client.post(LIST_CREATE_CATEGORY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_category_no_description(self):
        """Testea que un usuario si pueda crear una categoria sin description"""
        payload = self.payload.copy()
        del payload['description']

        res = self.client.post(LIST_CREATE_CATEGORY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_category_no_parent(self):
        """Testea que un usuario pueda crear una categoria sin padre"""
        payload = self.payload.copy()
        del payload['parent']

        res = self.client.post(LIST_CREATE_CATEGORY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_category_no_type(self):
        """Testea que un usuario no pueda crear una categoria sin tipo"""
        payload = self.payload.copy()
        del payload['type']

        res = self.client.post(LIST_CREATE_CATEGORY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_category(self):
        """Testea que un usuario pueda obtener informacion de una categoria especifica"""
        res = self.client.get(get_retrieve_update_destroy_category_url(self.category.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get('id'), self.category.id)
        self.assertEqual(res.data.get('name'), self.category.name)
        self.assertEqual(res.data.get('description'), self.category.description)
        self.assertEqual(res.data.get('type'), self.category.type)

    def test_retrieve_category_from_another_user(self):
        """Testea que un usuario no pueda obtener info de una cuenta que no es suya"""
        res = self.client.get(
            get_retrieve_update_destroy_category_url(self.another_user_category.id)
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_category(self):
        """Testea que un usuario pueda actualizar su propia categoria"""
        payload = {
            'name': 'New account name',
            'description': 'New description',
            'type': Category.TYPE.INCOME
        }
        self.assertNotEqual(self.category.name, payload.get('name'))
        self.assertNotEqual(self.category.description, payload.get('description'))
        self.assertNotEqual(self.category.type, payload.get('type'))

        res = self.client.put(
            get_retrieve_update_destroy_category_url(self.category.id),
            payload
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, payload.get('name'))
        self.assertEqual(self.category.description, payload.get('description'))
        self.assertEqual(self.category.type, payload.get('type'))

    def test_partial_update_category(self):
        """Testea que un usuario pueda actualizar parcialmente una cuenta suya"""
        payload = {
            'name': 'New account name',
            'description': 'New description'
        }
        self.assertNotEqual(self.category.name, payload.get('name'))
        res = self.client.patch(
            get_retrieve_update_destroy_category_url(self.category.id),
            payload
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, payload.get('name'))

    def test_update_category_from_another_user(self):
        """Testea que un usuario no pueda actualizar una categoria que no es suya"""
        payload = {
            'name': 'New account name',
            'description': 'New description',
            'type': Category.TYPE.INCOME
        }
        res = self.client.put(
            get_retrieve_update_destroy_category_url(self.another_user_category.id),
            payload
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_destroy_category(self):
        """Testea que un usuario pueda eliminar una categoria"""
        self.assertEqual(self.user.categories.count(), 1)
        res = self.client.delete(
            get_retrieve_update_destroy_category_url(self.category.id)
        )

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.user.categories.count(), 0)

    def test_destroy_category_From_another_user(self):
        """Testea que un usuario no pueda eliminar una categoria que no es suya"""
        res = self.client.delete(
            get_retrieve_update_destroy_category_url(self.another_user_category.id)
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
