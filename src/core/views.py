from django.core.exceptions import PermissionDenied

from rest_framework import viewsets, permissions


class UserObjectViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.categories

    def get_object(self):
        queryset = self.get_queryset()
        try:
            obj = queryset.get(pk=self.kwargs.get('pk'))
        except queryset.model.DoesNotExist:
            raise PermissionDenied('You don\'t have access to that account')

        return obj
