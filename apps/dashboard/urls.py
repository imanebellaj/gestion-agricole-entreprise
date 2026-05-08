from django.urls import path
from .views import (
    KpiGlobalView, SuperficiesParFiliereView, EvolutionAnnuelleView,
    PerformanceEntreprisesView, RepartitionBudgetView, AlertesView,
)

urlpatterns = [
    path('kpi/', KpiGlobalView.as_view(), name='kpi-global'),
    path('superficies-par-filiere/', SuperficiesParFiliereView.as_view()),
    path('evolution-annuelle/', EvolutionAnnuelleView.as_view()),
    path('performance-entreprises/', PerformanceEntreprisesView.as_view()),
    path('repartition-budget/', RepartitionBudgetView.as_view()),
    path('alertes/', AlertesView.as_view()),
]
