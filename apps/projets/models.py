from django.db import models
from apps.geo.models import Province
from apps.referentiels.models import Filiere, StatutProjet


class Projet(models.Model):
    intitule = models.CharField(max_length=400)
    filiere = models.ForeignKey(Filiere, on_delete=models.PROTECT, related_name='projets')
    province = models.ForeignKey(Province, on_delete=models.SET_NULL, null=True, blank=True)
    statut = models.ForeignKey(StatutProjet, on_delete=models.PROTECT, related_name='projets')
    date_demarrage = models.DateField(null=True, blank=True)
    duree_annees = models.SmallIntegerField(null=True, blank=True)
    superficie_programmee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cout_global_kdh = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    nbre_benef_potentiel = models.IntegerField(null=True, blank=True)
    unites_valorisation = models.SmallIntegerField(default=0)
    observations = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projets'
        ordering = ['-created_at']
        verbose_name = 'Projet'

    def __str__(self):
        return self.intitule


class ProjetProgrammation(models.Model):
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='programmations')
    annee = models.SmallIntegerField()
    superficie_programmee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    superficie_realisee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    budget_programme_kdh = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    budget_engage_kdh = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    observations = models.TextField(blank=True)

    class Meta:
        db_table = 'projets_programmation'
        ordering = ['annee']
        unique_together = [('projet', 'annee')]
        verbose_name = 'Programmation Annuelle'

    def __str__(self):
        return f"{self.projet} — {self.annee}"
