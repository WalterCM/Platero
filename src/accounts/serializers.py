from rest_framework import serializers

from core.models import Account


class AccountSerializer(serializers.ModelSerializer):
    """Serializer para el modelo ACcount"""
    balance = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ('id', 'name', 'description', 'balance', 'currency', 'type')
        extra_kwargs = {
            'type': {'required': True}
        }

    def get_balance(self, account):
        filters = {
            'year': self.context.get('request').query_params.get('year'),
            'month': self.context.get('request').query_params.get('month')
        }
        return account.get_balance(**filters)

    def create(self, validated_data):
        """Crea una nueva cuenta y lo retorna"""
        request = self.context.get('request')
        account = request.user.add_account(**validated_data)

        return account
