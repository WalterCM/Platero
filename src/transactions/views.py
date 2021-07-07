from django.core.exceptions import PermissionDenied

from rest_framework import viewsets, permissions

from transactions.serializers import TransferSerializer, IncomeExpenseSerializer
from core.models import Transaction


class TransactionViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Transaction.objects.filter(account__user=self.request.user)

    def get_object(self):
        queryset = self.get_queryset()
        try:
            obj = queryset.get(pk=self.kwargs.get('pk'))
        except Transaction.DoesNotExist:
            raise PermissionDenied('You don\'t have access to that account')

        return obj

    def get_serializer_class(self):
        type = self.request.data.get('type')

        if type == Transaction.CREATION_TYPE.TRANSFER:
            return TransferSerializer

        return IncomeExpenseSerializer
