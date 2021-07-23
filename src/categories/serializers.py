from rest_framework import serializers

from core.models import Category


class CategorySerializer(serializers.ModelSerializer):
    """Serializer para el modelo ACcount"""

    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'type', 'parent')
        extra_kwargs = {
            'type': {'required': True},
            'parent': {'required': False}
        }

    def create(self, validated_data):
        """Crea una nueva cuenta y lo retorna"""
        request = self.context.get('request')
        category = request.user.add_category(**validated_data)

        return category
