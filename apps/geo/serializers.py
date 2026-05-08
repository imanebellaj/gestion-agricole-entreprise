from rest_framework import serializers
from .models import Province, Cercle, Commune


class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = '__all__'


class CercleSerializer(serializers.ModelSerializer):
    province_libelle = serializers.CharField(source='province.libelle', read_only=True)

    class Meta:
        model = Cercle
        fields = '__all__'


class CommuneSerializer(serializers.ModelSerializer):
    cercle_libelle = serializers.CharField(source='cercle.libelle', read_only=True)
    province_libelle = serializers.CharField(source='province.libelle', read_only=True)

    class Meta:
        model = Commune
        fields = '__all__'
