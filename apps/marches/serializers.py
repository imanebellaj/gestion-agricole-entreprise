from rest_framework import serializers
from .models import Marche, MarchePhase, MarchesBeneficiaire, MarchePaiement, AppelOffre


class MarchePhaseSerializer(serializers.ModelSerializer):
    phase_libelle = serializers.CharField(source='phase.libelle', read_only=True)
    en_retard = serializers.BooleanField(read_only=True)
    jours_retard = serializers.IntegerField(read_only=True)

    class Meta:
        model = MarchePhase
        fields = '__all__'


class MarchesBeneficiaireSerializer(serializers.ModelSerializer):
    beneficiaire_nom = serializers.CharField(source='beneficiaire.nom_complet', read_only=True)
    beneficiaire_cin = serializers.CharField(source='beneficiaire.cin', read_only=True)

    class Meta:
        model = MarchesBeneficiaire
        fields = '__all__'


class MarchePaiementSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarchePaiement
        fields = '__all__'


class MarcheSerializer(serializers.ModelSerializer):
    projet_intitule = serializers.CharField(source='projet.intitule', read_only=True)
    filiere_libelle = serializers.CharField(source='projet.filiere.libelle', read_only=True)
    entreprise_nom = serializers.CharField(source='entreprise.raison_sociale', read_only=True)
    op_nom = serializers.CharField(source='op.nom', read_only=True)
    commune_libelle = serializers.CharField(source='commune.libelle', read_only=True)
    phases = MarchePhaseSerializer(many=True, read_only=True)
    paiements = MarchePaiementSerializer(many=True, read_only=True)

    class Meta:
        model = Marche
        fields = '__all__'


class MarcheListSerializer(serializers.ModelSerializer):
    projet_intitule = serializers.CharField(source='projet.intitule', read_only=True)
    filiere_libelle = serializers.CharField(source='projet.filiere.libelle', read_only=True)
    entreprise_nom = serializers.CharField(source='entreprise.raison_sociale', read_only=True)
    commune_libelle = serializers.CharField(source='commune.libelle', read_only=True)
    etat_avancement_display = serializers.CharField(source='get_etat_avancement_display', read_only=True)

    class Meta:
        model = Marche
        fields = [
            'id', 'numero_marche', 'annee', 'projet', 'projet_intitule',
            'filiere_libelle', 'commune', 'commune_libelle',
            'entreprise', 'entreprise_nom', 'etat_avancement',
            'etat_avancement_display', 'montant_engage_dh', 'montant_emis_dh',
            'superficie_potentielle', 'superficie_plantee', 'penalite_retard_dh',
        ]


class AppelOffreSerializer(serializers.ModelSerializer):
    projet_intitule = serializers.CharField(source='projet.intitule', read_only=True)

    class Meta:
        model = AppelOffre
        fields = '__all__'
