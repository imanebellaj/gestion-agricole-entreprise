from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Sum, Count, Q
from django.utils import timezone
from .models import Marche, MarchePhase, MarchesBeneficiaire, MarchePaiement, AppelOffre
from .serializers import (
    MarcheSerializer, MarcheListSerializer, MarchePhaseSerializer,
    MarchesBeneficiaireSerializer, MarchePaiementSerializer, AppelOffreSerializer,
)


class MarcheViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['projet', 'entreprise', 'etat_avancement', 'annee', 'commune']
    search_fields = ['numero_marche', 'objet']
    ordering_fields = ['annee', 'numero_marche', 'montant_engage_dh', 'superficie_plantee']

    def get_queryset(self):
        qs = Marche.objects.select_related(
            'projet__filiere', 'entreprise', 'commune', 'op'
        ).prefetch_related('phases', 'paiements')
        # Filtre filière (via projet__filiere__libelle)
        filiere = self.request.query_params.get('filiere')
        if filiere:
            qs = qs.filter(projet__filiere__libelle__icontains=filiere)
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return MarcheListSerializer
        return MarcheSerializer

    @action(detail=False, methods=['get'])
    def en_retard(self, request):
        today = timezone.now().date()
        phases_retard = MarchePhase.objects.filter(
            date_reception_prevue__lt=today,
            date_reception_reelle__isnull=True
        ).select_related('marche__projet', 'marche__entreprise', 'phase')
        data = [{
            'marche_id': p.marche.id,
            'numero_marche': p.marche.numero_marche,
            'projet': p.marche.projet.intitule,
            'entreprise': p.marche.entreprise.raison_sociale if p.marche.entreprise else None,
            'phase': p.phase.libelle,
            'date_reception_prevue': p.date_reception_prevue,
            'jours_retard': (today - p.date_reception_prevue).days,
        } for p in phases_retard]
        data.sort(key=lambda x: x['jours_retard'], reverse=True)
        return Response(data)

    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        qs = Marche.objects.all()
        agg = qs.aggregate(
            montant_engage=Sum('montant_engage_dh'),
            montant_emis=Sum('montant_emis_dh'),
            superficie=Sum('superficie_plantee'),
            penalites=Sum('penalite_retard_dh'),
        )
        return Response({
            'total':                    qs.count(),
            'en_cours':                 qs.filter(etat_avancement='en_cours').count(),
            'receptionne':              qs.filter(etat_avancement='receptionne').count(),
            'par_etat':                 list(qs.values('etat_avancement').annotate(nb=Count('id'))),
            'montant_total_engage':     agg['montant_engage'],
            'montant_total_emis':       agg['montant_emis'],
            'superficie_plantee_totale':agg['superficie'],
            'total_penalites':          agg['penalites'],
        })


class MarchePhaseViewSet(viewsets.ModelViewSet):
    queryset = MarchePhase.objects.select_related('marche', 'phase').all()
    serializer_class = MarchePhaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['marche', 'phase']


class MarchesBeneficiaireViewSet(viewsets.ModelViewSet):
    queryset = MarchesBeneficiaire.objects.select_related('marche', 'beneficiaire').all()
    serializer_class = MarchesBeneficiaireSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['marche', 'beneficiaire']


class MarchePaiementViewSet(viewsets.ModelViewSet):
    queryset = MarchePaiement.objects.select_related('marche').all()
    serializer_class = MarchePaiementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['marche']


class AppelOffreViewSet(viewsets.ModelViewSet):
    queryset = AppelOffre.objects.select_related('projet').all()
    serializer_class = AppelOffreSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['projet', 'statut']
    search_fields = ['objet']
