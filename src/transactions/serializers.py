from rest_framework import serializers

from core.models import Transaction, Account


class TransactionSerializer(serializers.ModelSerializer):
    pass


class TransferSerializer(TransactionSerializer):
    """Serializer para el modelo Transaction tipo Transfer"""
    destination_account = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all(),
        required=True,
        write_only=True
    )
    type = serializers.CharField(required=True)

    class Meta:
        model = Transaction
        fields = (
            'id', 'amount', 'description', 'date', 'account', 'destination_account',
            'type', 'is_paid'
        )
        extra_kwargs = {
            'amount': {'required': True},
            'date': {'required': True}
        }

    def create(self, validated_data):
        account = validated_data.pop('account')
        transaction = account.add_transaction(**validated_data)

        return transaction


class IncomeExpenseSerializer(TransactionSerializer):
    """Serializer para el modelo Transaction tipo Income y Expense"""

    class Meta:
        model = Transaction
        fields = (
            'id', 'amount', 'description', 'date', 'category',
            'account', 'type', 'is_paid'
        )
        extra_kwargs = {
            'amount': {'required': True},
            'date': {'required': True},
            'account': {'required': True},
            'type': {'required': True}
        }

    def create(self, validated_data):
        account = validated_data.pop('account')
        transaction = account.add_transaction(**validated_data)

        return transaction
