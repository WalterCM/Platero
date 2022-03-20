from core.views import UserObjectViewSet
from categories.serializers import CategorySerializer


class CategoryViewSet(UserObjectViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return self.request.user.categories
