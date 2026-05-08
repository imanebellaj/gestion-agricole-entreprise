from rest_framework import serializers
from .models import Entreprise, OrganisationProfessionnelle, AssistanceTechnique, Beneficiaire


class EntrepriseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entreprise
        fields = '__all__'


class OrganisationProfessionnelleSerializer(serializers.ModelSerializer):
    commune_libelle = serializers.CharField(source='commune.libelle', read_only=True)

    class Meta:
        model = OrganisationProfessionnelle
        fields = '__all__'


class AssistanceTechniqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistanceTechnique
        fields = '__all__'


class BeneficiaireSerializer(serializers.ModelSerializer):
    commune_libelle = serializers.CharField(source='commune.libelle', read_only=True)
    est_femme = serializers.SerializerMethodField()
    est_jeune = serializers.SerializerMethodField()

    class Meta:
        model = Beneficiaire
        fields = [
            'id', 'cin', 'nom_complet', 'sexe', 'date_naissance',
            'telephone', 'commune', 'commune_libelle', 'douar',
            'created_at', 'updated_at', 'est_femme', 'est_jeune',
        ]

    def get_est_femme(self, obj) -> bool:
        return obj.est_femme

    def get_est_jeune(self, obj) -> bool | None:
        return obj.est_jeune
