from rest_framework.routers import DefaultRouter
from .views import (
    MarcheViewSet, MarchePhaseViewSet, MarchesBeneficiaireViewSet,
    MarchePaiementViewSet, AppelOffreViewSet,
)

router = DefaultRouter()
router.register('marches', MarcheViewSet, basename='marche')
router.register('phases', MarchePhaseViewSet)
router.register('beneficiaires-marche', MarchesBeneficiaireViewSet)
router.register('paiements', MarchePaiementViewSet)
router.register('appels-offres', AppelOffreViewSet)

urlpatterns = router.urls
