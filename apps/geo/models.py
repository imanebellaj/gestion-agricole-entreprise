from django.db import models


class Province(models.Model):
    code = models.CharField(max_length=10, unique=True)
    libelle = models.CharField(max_length=100)
    region = models.CharField(max_length=100, default='Marrakech-Safi')

    class Meta:
        db_table = 'provinces'
        ordering = ['libelle']
        verbose_name = 'Province'
        verbose_name_plural = 'Provinces'

    def __str__(self):
        return self.libelle


class Cercle(models.Model):
    province = models.ForeignKey(Province, on_delete=models.PROTECT, related_name='cercles')
    libelle = models.CharField(max_length=100)

    class Meta:
        db_table = 'cercles'
        ordering = ['libelle']
        unique_together = [('province', 'libelle')]
        verbose_name = 'Cercle'

    def __str__(self):
        return self.libelle


class Commune(models.Model):
    TYPE_CHOICES = [('CT', 'Chef-lieu'), ('CR', 'Commune Rurale'), ('CU', 'Commune Urbaine')]

    cercle = models.ForeignKey(Cercle, on_delete=models.SET_NULL, null=True, blank=True, related_name='communes')
    province = models.ForeignKey(Province, on_delete=models.PROTECT, related_name='communes')
    libelle = models.CharField(max_length=150)
    type_commune = models.CharField(max_length=10, choices=TYPE_CHOICES, default='CT')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        db_table = 'communes'
        ordering = ['libelle']
        verbose_name = 'Commune'

    def __str__(self):
        return self.libelle
