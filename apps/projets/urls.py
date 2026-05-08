from rest_framework.routers import DefaultRouter
from .views import ProjetViewSet, ProjetProgrammationViewSet

router = DefaultRouter()
router.register('projets', ProjetViewSet)
router.register('programmations', ProjetProgrammationViewSet)

urlpatterns = router.urls
