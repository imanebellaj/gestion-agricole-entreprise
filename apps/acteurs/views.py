from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from .models import Entreprise, OrganisationProfessionnelle, AssistanceTechnique, Beneficiaire
from .serializers import (
    EntrepriseSerializer, OrganisationProfessionnelleSerializer,
    AssistanceTechniqueSerializer, BeneficiaireSerializer,
)


class EntrepriseViewSet(viewsets.ModelViewSet):
    queryset = Entreprise.objects.all()
    serializer_class = EntrepriseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['actif']
    search_fields = ['raison_sociale', 'ice']
    ordering_fields = ['raison_sociale', 'created_at']

    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        entreprise = self.get_object()
        from apps.marches.models import Marche
        stats = Marche.objects.filter(entreprise=entreprise).aggregate(
            nb_marches=Count('id'),
            total_engage=Sum('montant_engage_dh'),
            total_emis=Sum('montant_emis_dh'),
            total_penalites=Sum('penalite_retard_dh'),
        )
        return Response(stats)


class OrganisationProfessionnelleViewSet(viewsets.ModelViewSet):
    queryset = OrganisationProfessionnelle.objects.select_related('commune').all()
    serializer_class = OrganisationProfessionnelleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['type_op', 'actif', 'commune']
    search_fields = ['nom', 'contact_nom']


class AssistanceTechniqueViewSet(viewsets.ModelViewSet):
    queryset = AssistanceTechnique.objects.all()
    serializer_class = AssistanceTechniqueSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['raison_sociale']


class BeneficiaireViewSet(viewsets.ModelViewSet):
    queryset = Beneficiaire.objects.select_related('commune').all()
    serializer_class = BeneficiaireSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['sexe', 'commune']
    search_fields = ['nom_complet', 'cin', 'douar']
    ordering_fields = ['nom_complet', 'created_at']

    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        qs = self.get_queryset()
        total = qs.count()
        femmes = qs.filter(sexe='F').count()
        from django.utils import timezone
        from datetime import date
        cutoff = date(timezone.now().year - 40, timezone.now().month, timezone.now().day)
        jeunes = qs.filter(date_naissance__gte=cutoff).count()
        return Response({
            'total': total,
            'femmes': femmes,
            'hommes': total - femmes,
            'jeunes': jeunes,
            'taux_femmes': round(femmes / total * 100, 1) if total else 0,
            'taux_jeunes': round(jeunes / total * 100, 1) if total else 0,
        })

    @action(detail=False, methods=['get'])
    def doublons(self, request):
        doublons = (
            Beneficiaire.objects
            .values('cin')
            .annotate(nb=Count('id'))
            .filter(nb__gt=1, cin__isnull=False)
            .order_by('-nb')
        )
        return Response(list(doublons))


# Import nécessaire pour EntrepriseViewSet
from django.db.models import Sum
