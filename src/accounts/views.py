from django.core.exceptions import PermissionDenied

from rest_framework import viewsets, permissions

from accounts.serializers import AccountSerializer
from core.models import Account


class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.accounts

    def get_object(self):
        queryset = self.get_queryset()
        try:
            obj = queryset.get(pk=self.kwargs.get('pk'))
        except Account.DoesNotExist:
            raise PermissionDenied('You don\'t have access to that account')

        return obj
