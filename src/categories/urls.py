from rest_framework import routers

from categories.views import CategoryViewSet

router = routers.SimpleRouter()
router.register(r'', CategoryViewSet, basename='category')

app_name = 'categories'

urlpatterns = router.urls
