from rest_framework import routers

from transactions.views import TransactionViewSet

router = routers.SimpleRouter()
router.register(r'', TransactionViewSet, basename='transaction')

app_name = 'transactions'

urlpatterns = router.urls
