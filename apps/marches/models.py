from django.db import models
from apps.geo.models import Commune
from apps.referentiels.models import Phase, ModePassation
from apps.projets.models import Projet
from apps.acteurs.models import Entreprise, OrganisationProfessionnelle, AssistanceTechnique, Beneficiaire


class Marche(models.Model):
    ETAT_CHOICES = [
        ('programme', 'Programmé'),
        ('en_cours', 'En cours'),
        ('suspendu', 'Suspendu'),
        ('resilie', 'Résilié'),
        ('receptionne', 'Réceptionné'),
        ('cede', 'Cédé'),
        ('cloture', 'Clôturé'),
    ]

    numero_marche = models.CharField(max_length=100)
    annee = models.SmallIntegerField()
    projet = models.ForeignKey(Projet, on_delete=models.PROTECT, related_name='marches')
    commune = models.ForeignKey(Commune, on_delete=models.SET_NULL, null=True, blank=True)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.SET_NULL, null=True, blank=True)
    op = models.ForeignKey(OrganisationProfessionnelle, on_delete=models.SET_NULL, null=True, blank=True)
    assistance_tech = models.ForeignKey(AssistanceTechnique, on_delete=models.SET_NULL, null=True, blank=True)
    mode_passation = models.ForeignKey(ModePassation, on_delete=models.SET_NULL, null=True, blank=True)
    objet = models.TextField()
    montant_engage_dh = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    montant_marche_dh = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    montant_emis_dh = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    penalite_retard_dh = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    nb_jours_penalite = models.IntegerField(default=0)
    superficie_potentielle = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    superficie_realisee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    superficie_travaillee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    superficie_plantee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    etat_avancement = models.CharField(max_length=50, choices=ETAT_CHOICES, default='en_cours')
    nb_beneficiaires = models.IntegerField(null=True, blank=True)
    nb_beneficiaires_jeunes = models.IntegerField(null=True, blank=True)
    nb_beneficiaires_femmes = models.IntegerField(null=True, blank=True)
    observations = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'marches'
        ordering = ['-annee', 'numero_marche']
        verbose_name = 'Marché'

    def __str__(self):
        return f"{self.numero_marche} — {self.projet}"


class MarchePhase(models.Model):
    marche = models.ForeignKey(Marche, on_delete=models.CASCADE, related_name='phases')
    phase = models.ForeignKey(Phase, on_delete=models.PROTECT)
    duree_prevue_mois = models.SmallIntegerField(null=True, blank=True)
    date_ods_notification = models.DateField(null=True, blank=True)
    date_ods_commencement = models.DateField(null=True, blank=True)
    date_ods_commencement_reel = models.DateField(null=True, blank=True)
    date_ordre_arret = models.DateField(null=True, blank=True)
    date_ordre_reprise = models.DateField(null=True, blank=True)
    date_reception_prevue = models.DateField(null=True, blank=True)
    date_reception_reelle = models.DateField(null=True, blank=True)
    superficie_travaillee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    superficie_plantee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    montant_emis_dh = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    observations = models.TextField(blank=True)

    class Meta:
        db_table = 'marche_phases'
        verbose_name = 'Phase de Marché'

    def __str__(self):
        return f"{self.marche} / {self.phase}"

    @property
    def en_retard(self):
        from django.utils import timezone
        if self.date_reception_prevue and not self.date_reception_reelle:
            return self.date_reception_prevue < timezone.now().date()
        return False

    @property
    def jours_retard(self):
        from django.utils import timezone
        if self.en_retard:
            return (timezone.now().date() - self.date_reception_prevue).days
        return 0


class MarchesBeneficiaire(models.Model):
    marche = models.ForeignKey(Marche, on_delete=models.CASCADE, related_name='beneficiaires_marche')
    beneficiaire = models.ForeignKey(Beneficiaire, on_delete=models.PROTECT)
    superficie_cedee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    date_cession = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'marche_beneficiaires'
        unique_together = [('marche', 'beneficiaire')]
        verbose_name = 'Bénéficiaire du Marché'


class MarchePaiement(models.Model):
    marche = models.ForeignKey(Marche, on_delete=models.CASCADE, related_name='paiements')
    numero_dp = models.CharField(max_length=20, blank=True)
    montant_dh = models.DecimalField(max_digits=14, decimal_places=2)
    date_paiement = models.DateField(null=True, blank=True)
    observations = models.TextField(blank=True)

    class Meta:
        db_table = 'marche_paiements'
        ordering = ['date_paiement']
        verbose_name = 'Paiement de Marché'

    def __str__(self):
        return f"DP {self.numero_dp} — {self.montant_dh} DH"


class AppelOffre(models.Model):
    STATUT_CHOICES = [
        ('prevu', 'Prévu'),
        ('publie', 'Publié'),
        ('attribue', 'Attribué'),
        ('infructueux', 'Infructueux'),
        ('annule', 'Annulé'),
    ]
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='appels_offres')
    objet = models.TextField()
    lieu_execution = models.CharField(max_length=250, blank=True)
    mode_passation = models.ForeignKey(ModePassation, on_delete=models.SET_NULL, null=True, blank=True)
    periode_publication = models.CharField(max_length=50, blank=True)
    service_concerne = models.CharField(max_length=100, blank=True)
    statut = models.CharField(max_length=30, choices=STATUT_CHOICES, default='prevu')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'appels_offres'
        verbose_name = "Appel d'Offres"
