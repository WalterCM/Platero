from rest_framework import serializers

from core.models import Account


class AccountSerializer(serializers.ModelSerializer):
    """Serializer para el modelo ACcount"""

    class Meta:
        model = Account
        fields = ('id', 'name', 'description', 'balance', 'currency', 'type')

    def create(self, validated_data):
        """Crea una nueva cuenta y lo retorna"""
        request = self.context.get('request')
        account = request.user.add_account(**validated_data)

        return account
