from django.db import models
from apps.geo.models import Commune


class Entreprise(models.Model):
    raison_sociale = models.CharField(max_length=200)
    contact_nom = models.CharField(max_length=150, blank=True)
    contact_tel = models.CharField(max_length=50, blank=True)
    contact_email = models.CharField(max_length=150, blank=True)
    adresse = models.TextField(blank=True)
    ice = models.CharField(max_length=20, blank=True)
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'entreprises'
        ordering = ['raison_sociale']
        verbose_name = 'Entreprise'

    def __str__(self):
        return self.raison_sociale


class OrganisationProfessionnelle(models.Model):
    TYPE_CHOICES = [
        ('cooperative', 'Coopérative'),
        ('association', 'Association'),
        ('gie', 'GIE'),
        ('autre', 'Autre'),
    ]
    nom = models.CharField(max_length=250)
    type_op = models.CharField(max_length=30, choices=TYPE_CHOICES, default='cooperative')
    commune = models.ForeignKey(Commune, on_delete=models.SET_NULL, null=True, blank=True)
    contact_nom = models.CharField(max_length=150, blank=True)
    contact_tel = models.CharField(max_length=50, blank=True)
    nbre_adherents = models.IntegerField(null=True, blank=True)
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'organisations_professionnelles'
        ordering = ['nom']
        verbose_name = 'Organisation Professionnelle'
        verbose_name_plural = 'Organisations Professionnelles'

    def __str__(self):
        return self.nom


class AssistanceTechnique(models.Model):
    raison_sociale = models.CharField(max_length=200)
    contact_nom = models.CharField(max_length=150, blank=True)
    contact_tel = models.CharField(max_length=50, blank=True)
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'assistances_techniques'
        ordering = ['raison_sociale']
        verbose_name = 'Assistance Technique'

    def __str__(self):
        return self.raison_sociale


class Beneficiaire(models.Model):
    SEXE_CHOICES = [('M', 'Masculin'), ('F', 'Féminin')]

    cin = models.CharField(max_length=15, unique=True, null=True, blank=True)
    nom_complet = models.CharField(max_length=200)
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES, null=True, blank=True)
    date_naissance = models.DateField(null=True, blank=True)
    telephone = models.CharField(max_length=50, blank=True)
    commune = models.ForeignKey(Commune, on_delete=models.SET_NULL, null=True, blank=True)
    douar = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'beneficiaires'
        ordering = ['nom_complet']
        verbose_name = 'Bénéficiaire'

    def __str__(self):
        return self.nom_complet

    @property
    def est_femme(self):
        return self.sexe == 'F'

    @property
    def est_jeune(self):
        if self.date_naissance:
            from django.utils import timezone
            age = (timezone.now().date() - self.date_naissance).days / 365.25
            return age < 40
        return None
