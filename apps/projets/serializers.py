from rest_framework import serializers
from .models import Projet, ProjetProgrammation


class ProjetProgrammationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjetProgrammation
        fields = '__all__'


class ProjetSerializer(serializers.ModelSerializer):
    filiere_libelle = serializers.CharField(source='filiere.libelle', read_only=True)
    filiere_categorie = serializers.CharField(source='filiere.categorie', read_only=True)
    statut_libelle = serializers.CharField(source='statut.libelle', read_only=True)
    province_libelle = serializers.CharField(source='province.libelle', read_only=True)
    programmations = ProjetProgrammationSerializer(many=True, read_only=True)

    class Meta:
        model = Projet
        fields = '__all__'


class ProjetListSerializer(serializers.ModelSerializer):
    filiere_libelle = serializers.CharField(source='filiere.libelle', read_only=True)
    statut_libelle = serializers.CharField(source='statut.libelle', read_only=True)
    province_libelle = serializers.CharField(source='province.libelle', read_only=True)

    class Meta:
        model = Projet
        fields = [
            'id', 'intitule', 'filiere', 'filiere_libelle', 'filiere_categorie',
            'statut', 'statut_libelle', 'province', 'province_libelle',
            'date_demarrage', 'superficie_programmee', 'cout_global_kdh',
        ]

    filiere_categorie = serializers.CharField(source='filiere.categorie', read_only=True)
