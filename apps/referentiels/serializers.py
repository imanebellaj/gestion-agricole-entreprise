from rest_framework import serializers
from .models import Filiere, StatutProjet, Phase, ModePassation


class FiliereSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filiere
        fields = '__all__'


class StatutProjetSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatutProjet
        fields = '__all__'


class PhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phase
        fields = '__all__'


class ModePassationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModePassation
        fields = '__all__'
