from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Sum, Count, Avg
from .models import Projet, ProjetProgrammation
from .serializers import ProjetSerializer, ProjetListSerializer, ProjetProgrammationSerializer


class ProjetViewSet(viewsets.ModelViewSet):
    queryset = Projet.objects.select_related('filiere', 'statut', 'province').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['filiere', 'statut', 'province']
    search_fields = ['intitule', 'observations']
    ordering_fields = ['intitule', 'date_demarrage', 'superficie_programmee', 'cout_global_kdh']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjetListSerializer
        return ProjetSerializer

    @action(detail=True, methods=['get'])
    def synthese(self, request, pk=None):
        projet = self.get_object()
        from apps.marches.models import Marche
        marches = Marche.objects.filter(projet=projet)
        stats = marches.aggregate(
            nb_marches=Count('id'),
            superficie_realisee=Sum('superficie_realisee'),
            superficie_plantee=Sum('superficie_plantee'),
            montant_engage=Sum('montant_engage_dh'),
            montant_emis=Sum('montant_emis_dh'),
            total_penalites=Sum('penalite_retard_dh'),
        )
        taux = None
        if projet.superficie_programmee and stats['superficie_realisee']:
            taux = round(float(stats['superficie_realisee']) / float(projet.superficie_programmee) * 100, 2)
        stats['taux_realisation_pct'] = taux
        return Response(stats)

    @action(detail=False, methods=['get'])
    def par_filiere(self, request):
        data = (
            Projet.objects
            .values('filiere__libelle', 'filiere__categorie')
            .annotate(nb=Count('id'), superficie=Sum('superficie_programmee'))
            .order_by('-nb')
        )
        return Response(list(data))

    @action(detail=False, methods=['get'])
    def par_statut(self, request):
        data = (
            Projet.objects
            .values('statut__libelle', 'statut__code')
            .annotate(nb=Count('id'))
            .order_by('-nb')
        )
        return Response(list(data))


class ProjetProgrammationViewSet(viewsets.ModelViewSet):
    queryset = ProjetProgrammation.objects.select_related('projet').all()
    serializer_class = ProjetProgrammationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['projet', 'annee']
