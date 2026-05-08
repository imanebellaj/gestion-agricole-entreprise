from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.TableauBordIAView.as_view(), name='ia-dashboard'),
    path('risk-scoring/', views.RiskScoringView.as_view(), name='ia-risk-scoring'),
    path('predictions-retard/', views.PredictionRetardView.as_view(), name='ia-predictions'),
    path('tendances/', views.TendancesView.as_view(), name='ia-tendances'),
    path('anomalies/', views.AnomaliesView.as_view(), name='ia-anomalies'),
    path('recommandations/', views.RecommandationsView.as_view(), name='ia-recommandations'),
]
