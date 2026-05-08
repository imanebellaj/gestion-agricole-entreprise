from rest_framework.routers import DefaultRouter
from .views import ProvinceViewSet, CercleViewSet, CommuneViewSet

router = DefaultRouter()
router.register('provinces', ProvinceViewSet)
router.register('cercles', CercleViewSet)
router.register('communes', CommuneViewSet)

urlpatterns = router.urls
