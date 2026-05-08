from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Sum, Count, Avg, F, Q
from django.utils import timezone


class KpiGlobalView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from apps.projets.models import Projet
        from apps.marches.models import Marche, MarchePhase
        from apps.acteurs.models import Beneficiaire, Entreprise

        from apps.projets.models import ProjetProgrammation

        projets_qs = Projet.objects.all()
        marches_qs = Marche.objects.all()
        today = timezone.now().date()

        # KPIs principaux — superficie
        # On utilise ProjetProgrammation pour avoir programmée et réalisée cohérentes
        pp_agg = ProjetProgrammation.objects.aggregate(
            prog=Sum('superficie_programmee'),
            real=Sum('superficie_realisee'),
        )
        total_sup_programmee_pp = float(pp_agg['prog'] or 0)
        total_sup_realisee_pp   = float(pp_agg['real'] or 0)

        # Fallback : Projet.superficie_programmee si ProjetProgrammation vide
        total_sup_programmee_proj = float(projets_qs.aggregate(t=Sum('superficie_programmee'))['t'] or 0)

        # Superficie affichée dans les KPIs : réalisée depuis ProjetProgrammation
        total_sup_plantee = total_sup_realisee_pp if total_sup_realisee_pp > 0 else float(marches_qs.aggregate(t=Sum('superficie_plantee'))['t'] or 0)

        # Dénominateur : ProjetProgrammation si disponible, sinon Projet
        denom = total_sup_programmee_pp if total_sup_programmee_pp > 0 else total_sup_programmee_proj

        # Calcul du taux, plafonné à 100 %
        if denom > 0 and total_sup_plantee > 0:
            taux_realisation = min(round(total_sup_plantee / denom * 100, 1), 100.0)
        else:
            taux_realisation = 0.0

        total_sup_programmee = denom

        total_engage = marches_qs.aggregate(t=Sum('montant_engage_dh'))['t'] or 0
        total_emis = marches_qs.aggregate(t=Sum('montant_emis_dh'))['t'] or 0

        nb_marches_retard = MarchePhase.objects.filter(
            date_reception_prevue__lt=today,
            date_reception_reelle__isnull=True
        ).count()

        nb_beneficiaires = Beneficiaire.objects.count()
        nb_femmes = Beneficiaire.objects.filter(sexe='F').count()

        cutoff = today.replace(year=today.year - 40)
        nb_jeunes = Beneficiaire.objects.filter(date_naissance__gte=cutoff).count()

        return Response({
            'projets': {
                'total': projets_qs.count(),
                'superficie_programmee_ha': total_sup_programmee,
                'superficie_plantee_ha': total_sup_plantee,
                'taux_realisation_pct': taux_realisation,
            },
            'marches': {
                'total': marches_qs.count(),
                'en_retard': nb_marches_retard,
                'en_cours':    marches_qs.filter(etat_avancement='en_cours').count(),
                'programme':   marches_qs.filter(etat_avancement='programme').count(),
                'receptionne': marches_qs.filter(etat_avancement='receptionne').count(),
                'cloture':     marches_qs.filter(etat_avancement='cloture').count(),
                'suspendu':    marches_qs.filter(etat_avancement='suspendu').count(),
                'montant_engage_dh': float(total_engage),
                'montant_emis_dh': float(total_emis),
                'taux_consommation_pct': round(float(total_emis) / float(total_engage) * 100, 1) if total_engage else 0,
            },
            'beneficiaires': {
                'total': nb_beneficiaires,
                'femmes': nb_femmes,
                'jeunes': nb_jeunes,
                'taux_femmes_pct': round(nb_femmes / nb_beneficiaires * 100, 1) if nb_beneficiaires else 0,
            },
            'entreprises': {
                'total': Entreprise.objects.filter(actif=True).count(),
            },
        })


class SuperficiesParFiliereView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from apps.marches.models import Marche
        data = (
            Marche.objects
            .values(filiere=F('projet__filiere__libelle'))
            .annotate(
                superficie_programmee=Sum('superficie_potentielle'),
                superficie_plantee=Sum('superficie_plantee'),
                nb_marches=Count('id'),
            )
            .order_by('-superficie_plantee')
        )
        return Response(list(data))


class EvolutionAnnuelleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from apps.projets.models import ProjetProgrammation
        data = (
            ProjetProgrammation.objects
            .values('annee')
            .annotate(
                superficie_programmee=Sum('superficie_programmee'),
                superficie_realisee=Sum('superficie_realisee'),
                budget_programme=Sum('budget_programme_kdh'),
                budget_engage=Sum('budget_engage_kdh'),
            )
            .order_by('annee')
        )
        return Response(list(data))


class PerformanceEntreprisesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from apps.marches.models import Marche
        data = (
            Marche.objects
            .filter(entreprise__isnull=False)
            .values(entreprise=F('entreprise__raison_sociale'))
            .annotate(
                nb_marches=Count('id'),
                total_marche_dh=Sum('montant_marche_dh'),
                total_penalites_dh=Sum('penalite_retard_dh'),
                superficie_plantee=Sum('superficie_plantee'),
            )
            .order_by('-total_marche_dh')[:10]
        )
        return Response(list(data))


class RepartitionBudgetView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from apps.projets.models import Projet
        from apps.marches.models import Marche
        data = (
            Projet.objects
            .values('intitule', filiere=F('filiere__libelle'))
            .annotate(
                budget_global=Sum('cout_global_kdh'),
                engage=Sum('marches__montant_engage_dh'),
                emis=Sum('marches__montant_emis_dh'),
            )
            .order_by('-budget_global')
        )
        return Response(list(data))


class AlertesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from apps.marches.models import Marche, MarchePhase
        today = timezone.now().date()
        j15 = today.replace(day=today.day + 15) if today.day <= 16 else today

        # Marchés en retard
        retards = MarchePhase.objects.filter(
            date_reception_prevue__lt=today,
            date_reception_reelle__isnull=True
        ).select_related('marche__projet').count()

        # Réceptions prochaines (dans 15 jours)
        prochaines = MarchePhase.objects.filter(
            date_reception_prevue__gte=today,
            date_reception_prevue__lte=today.replace(day=min(today.day + 15, 28)),
            date_reception_reelle__isnull=True
        ).count()

        # Marchés avec pénalités
        avec_penalites = Marche.objects.filter(penalite_retard_dh__gt=0).count()

        return Response({
            'marches_en_retard': retards,
            'receptions_prochaines_15j': prochaines,
            'marches_avec_penalites': avec_penalites,
        })
