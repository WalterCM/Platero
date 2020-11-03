from django.test import TestCase

from core.models import Tag


class TagModelTests(TestCase):

    def test_create_tag(self):
        """Tests creating a new tag"""
        name = 'comida'
        tag = Tag.objects.create_tag(
            name=name
        )

        self.assertEqual(tag.name, name)

    def test_get_existing_tag(self):
        """Tests that gets a tag instead of creating a new one"""
        name = 'comida'
        old_tag = Tag(name=name)
        old_tag.save()

        tag = Tag.objects.get_or_create_tag(name=name)

        self.assertEqual(tag.name, name)
        self.assertEqual(tag.id, old_tag.id)

    def test_get_created_tag(self):
        """Tests getting a new tag when a tag with that name doesn't exist"""
        name = 'comida'

        self.assertEqual(Tag.objects.count(), 0)
        tag = Tag.objects.get_or_create_tag(name=name)
        tag.save()
        self.assertEqual(Tag.objects.count(), 1)
        self.assertEqual(tag.name, name)
