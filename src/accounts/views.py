from core.views import UserObjectViewSet
from accounts.serializers import AccountSerializer


class AccountViewSet(UserObjectViewSet):
    serializer_class = AccountSerializer

    def get_queryset(self):
        return self.request.user.accounts
