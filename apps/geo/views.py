from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .models import Province, Cercle, Commune
from .serializers import ProvinceSerializer, CercleSerializer, CommuneSerializer


class ProvinceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer
    permission_classes = [permissions.IsAuthenticated]


class CercleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Cercle.objects.select_related('province').all()
    serializer_class = CercleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['province']


class CommuneViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Commune.objects.select_related('cercle', 'province').all()
    serializer_class = CommuneSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['province', 'cercle', 'type_commune']
    search_fields = ['libelle']
