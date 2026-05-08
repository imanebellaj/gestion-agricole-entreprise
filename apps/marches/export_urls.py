from django.urls import path
from .export_views import ExportMarchesExcel, ExportBeneficiairesExcel, ExportProjetsPDF

urlpatterns = [
    path('marches/excel/', ExportMarchesExcel.as_view(), name='export-marches-excel'),
    path('beneficiaires/excel/', ExportBeneficiairesExcel.as_view(), name='export-beneficiaires-excel'),
    path('marches/pdf/', ExportProjetsPDF.as_view(), name='export-marches-pdf'),
]
