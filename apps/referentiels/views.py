from rest_framework import viewsets, permissions
from .models import Filiere, StatutProjet, Phase, ModePassation
from .serializers import FiliereSerializer, StatutProjetSerializer, PhaseSerializer, ModePassationSerializer


class FiliereViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Filiere.objects.all()
    serializer_class = FiliereSerializer
    permission_classes = [permissions.IsAuthenticated]


class StatutProjetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StatutProjet.objects.all()
    serializer_class = StatutProjetSerializer
    permission_classes = [permissions.IsAuthenticated]


class PhaseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Phase.objects.all()
    serializer_class = PhaseSerializer
    permission_classes = [permissions.IsAuthenticated]


class ModePassationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ModePassation.objects.all()
    serializer_class = ModePassationSerializer
    permission_classes = [permissions.IsAuthenticated]
