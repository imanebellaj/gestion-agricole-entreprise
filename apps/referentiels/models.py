from django.db import models


class Filiere(models.Model):
    CATEGORIE_CHOICES = [
        ('arboriculture', 'Arboriculture'),
        ('elevage', 'Élevage'),
        ('apiculture', 'Apiculture'),
        ('plantes_aromatiques', 'Plantes Aromatiques'),
        ('irrigation', 'Irrigation'),
        ('autre', 'Autre'),
    ]
    code = models.CharField(max_length=30, unique=True)
    libelle = models.CharField(max_length=100)
    categorie = models.CharField(max_length=50, choices=CATEGORIE_CHOICES)

    class Meta:
        db_table = 'filieres'
        ordering = ['libelle']
        verbose_name = 'Filière'

    def __str__(self):
        return self.libelle


class StatutProjet(models.Model):
    code = models.CharField(max_length=30, unique=True)
    libelle = models.CharField(max_length=100)

    class Meta:
        db_table = 'statuts_projet'
        verbose_name = 'Statut Projet'

    def __str__(self):
        return self.libelle


class Phase(models.Model):
    code = models.CharField(max_length=30, unique=True)
    libelle = models.CharField(max_length=150)
    ordre = models.SmallIntegerField(default=0)

    class Meta:
        db_table = 'phases'
        ordering = ['ordre']
        verbose_name = 'Phase'

    def __str__(self):
        return self.libelle


class ModePassation(models.Model):
    code = models.CharField(max_length=10, unique=True)
    libelle = models.CharField(max_length=100)

    class Meta:
        db_table = 'modes_passation'
        verbose_name = 'Mode de Passation'

    def __str__(self):
        return self.libelle
