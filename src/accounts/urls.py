from django.urls import path
from rest_framework import routers

from accounts.views import AccountViewSet

router = routers.SimpleRouter()
router.register(r'', AccountViewSet, basename='account')

app_name = 'accounts'

urlpatterns = router.urls
