from rest_framework.routers import DefaultRouter
from .views import FiliereViewSet, StatutProjetViewSet, PhaseViewSet, ModePassationViewSet

router = DefaultRouter()
router.register('filieres', FiliereViewSet)
router.register('statuts-projet', StatutProjetViewSet)
router.register('phases', PhaseViewSet)
router.register('modes-passation', ModePassationViewSet)

urlpatterns = router.urls
