from rest_framework.routers import DefaultRouter
from .views import (
    EntrepriseViewSet, OrganisationProfessionnelleViewSet,
    AssistanceTechniqueViewSet, BeneficiaireViewSet,
)

router = DefaultRouter()
router.register('entreprises', EntrepriseViewSet)
router.register('organisations-professionnelles', OrganisationProfessionnelleViewSet)
router.register('assistances-techniques', AssistanceTechniqueViewSet)
router.register('beneficiaires', BeneficiaireViewSet)

urlpatterns = router.urls
