from django.test import TestCase

from core.models import Tag


class TagModelTests(TestCase):

    def test_create_tag(self):
        """Test creating a new tag"""
        name = 'comida'
        tag = Tag.objects.create_tag(
            name=name
        )

        self.assertEqual(tag.name, name)
