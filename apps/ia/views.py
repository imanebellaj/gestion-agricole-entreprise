"""
Module IA — Intelligence Artificielle pour l'analyse prédictive agricole
Algorithmes: Risk Scoring, Détection d'anomalies, Prédiction de retards, Tendances
"""
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Avg, Sum, Count, Max, Min, StdDev, F, Q
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.marches.models import Marche, MarchePhase
from apps.projets.models import Projet, ProjetProgrammation
from apps.acteurs.models import Entreprise


# ─── Helpers ────────────────────────────────────────────────────────────────

def _safe_float(v, default=0.0):
    try:
        return float(v) if v is not None else default
    except (TypeError, ValueError):
        return default


def _risk_score(marche):
    """
    Calcule un score de risque [0-100] pour un marché.
    Basé sur: retard phases, ratio montant/superficie, pénalités, durée sans réception.
    """
    score = 0.0
    today = timezone.now().date()

    # Facteur 1: Phases en retard (poids 40%)
    phases = marche.phases.all()
    phases_retard = 0
    phases_total = phases.count()
    for p in phases:
        if p.date_reception_prevue and not p.date_reception_reelle:
            if p.date_reception_prevue < today:
                jours = (today - p.date_reception_prevue).days
                phases_retard += 1
                score += min(40, jours * 0.5)  # max 40 pts

    # Facteur 2: Pénalités (poids 25%)
    penalite = _safe_float(marche.penalite_retard_dh)
    montant = _safe_float(marche.montant_marche_dh or marche.montant_engage_dh) or 1
    ratio_penalite = penalite / montant if montant > 0 else 0
    score += min(25, ratio_penalite * 500)

    # Facteur 3: Taux de réalisation faible (poids 20%)
    sup_pot = _safe_float(marche.superficie_potentielle)
    sup_plant = _safe_float(marche.superficie_plantee)
    if sup_pot > 0:
        taux_real = sup_plant / sup_pot
        if taux_real < 0.5:
            score += (1 - taux_real) * 20
    elif marche.etat_avancement == 'en_cours':
        score += 10

    # Facteur 4: Pas de mise à jour récente (poids 15%)
    if marche.updated_at:
        jours_depuis_maj = (today - marche.updated_at.date()).days
        if jours_depuis_maj > 180:
            score += min(15, jours_depuis_maj * 0.03)

    return min(100, round(score, 1))


def _classify_risk(score):
    if score >= 70:
        return {'level': 'critique', 'label': 'Critique', 'color': '#ef4444'}
    elif score >= 40:
        return {'level': 'eleve', 'label': 'Élevé', 'color': '#f97316'}
    elif score >= 20:
        return {'level': 'modere', 'label': 'Modéré', 'color': '#eab308'}
    else:
        return {'level': 'faible', 'label': 'Faible', 'color': '#22c55e'}


# ─── Views ──────────────────────────────────────────────────────────────────

class RiskScoringView(APIView):
    """
    Scoring de risque pour tous les marchés actifs.
    Algorithme multi-critères: retards, pénalités, taux de réalisation, inactivité.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        marches = Marche.objects.filter(
            etat_avancement__in=['en_cours', 'programme']
        ).prefetch_related('phases').select_related('projet', 'projet__filiere', 'commune', 'entreprise')

        results = []
        for m in marches:
            score = _risk_score(m)
            risk = _classify_risk(score)
            results.append({
                'id': m.id,
                'numero_marche': m.numero_marche,
                'annee': m.annee,
                'projet': m.projet.intitule if m.projet else '—',
                'filiere': m.projet.filiere.libelle if m.projet and m.projet.filiere else '—',
                'commune': m.commune.libelle if m.commune else '—',
                'entreprise': m.entreprise.raison_sociale if m.entreprise else '—',
                'score_risque': score,
                'niveau_risque': risk['level'],
                'label_risque': risk['label'],
                'couleur_risque': risk['color'],
                'montant_dh': _safe_float(m.montant_engage_dh),
                'penalite_dh': _safe_float(m.penalite_retard_dh),
                'taux_realisation': round(
                    (_safe_float(m.superficie_plantee) / _safe_float(m.superficie_potentielle) * 100)
                    if _safe_float(m.superficie_potentielle) > 0 else 0, 1
                ),
            })

        results.sort(key=lambda x: x['score_risque'], reverse=True)

        # Statistiques globales
        scores = [r['score_risque'] for r in results]
        critique = sum(1 for r in results if r['niveau_risque'] == 'critique')
        eleve = sum(1 for r in results if r['niveau_risque'] == 'eleve')
        modere = sum(1 for r in results if r['niveau_risque'] == 'modere')
        faible = sum(1 for r in results if r['niveau_risque'] == 'faible')

        return Response({
            'marches': results,
            'resume': {
                'total': len(results),
                'score_moyen': round(sum(scores) / len(scores), 1) if scores else 0,
                'critique': critique,
                'eleve': eleve,
                'modere': modere,
                'faible': faible,
                'distribution': [
                    {'label': 'Critique', 'value': critique, 'color': '#ef4444'},
                    {'label': 'Élevé', 'value': eleve, 'color': '#f97316'},
                    {'label': 'Modéré', 'value': modere, 'color': '#eab308'},
                    {'label': 'Faible', 'value': faible, 'color': '#22c55e'},
                ]
            }
        })


class PredictionRetardView(APIView):
    """
    Prédiction de probabilité de retard pour les marchés en cours.
    Modèle: scoring bayésien basé sur historique entreprise, filière, montant.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        marches_actifs = Marche.objects.filter(
            etat_avancement='en_cours'
        ).prefetch_related('phases').select_related('projet__filiere', 'entreprise')

        # Statistiques historiques par entreprise
        stats_entreprise = {}
        for m in Marche.objects.filter(etat_avancement__in=['receptionne', 'cloture']):
            eid = m.entreprise_id
            if eid not in stats_entreprise:
                stats_entreprise[eid] = {'total': 0, 'retards': 0}
            stats_entreprise[eid]['total'] += 1
            has_retard = m.phases.filter(
                date_reception_prevue__isnull=False,
                date_reception_reelle__isnull=False
            ).filter(
                date_reception_reelle__gt=F('date_reception_prevue')
            ).exists()
            if has_retard:
                stats_entreprise[eid]['retards'] += 1

        # Taux de retard global historique (a priori)
        total_hist = Marche.objects.filter(etat_avancement__in=['receptionne', 'cloture']).count()
        retards_hist = MarchePhase.objects.filter(
            date_reception_prevue__isnull=False,
            date_reception_reelle__isnull=False
        ).filter(date_reception_reelle__gt=F('date_reception_prevue')).count()
        taux_global = retards_hist / total_hist if total_hist > 0 else 0.3

        predictions = []
        for m in marches_actifs:
            # Probabilité de base
            prob = taux_global

            # Ajustement entreprise (si historique)
            eid = m.entreprise_id
            if eid and eid in stats_entreprise and stats_entreprise[eid]['total'] > 0:
                taux_ent = stats_entreprise[eid]['retards'] / stats_entreprise[eid]['total']
                # Moyenne pondérée avec la base
                n = stats_entreprise[eid]['total']
                prob = (n * taux_ent + 3 * taux_global) / (n + 3)

            # Ajustement montant élevé (+risque)
            montant = _safe_float(m.montant_engage_dh)
            if montant > 5_000_000:
                prob = min(0.95, prob * 1.2)
            elif montant > 2_000_000:
                prob = min(0.95, prob * 1.1)

            # Ajustement phase proche de la date prévue
            phase_urgente = False
            jours_avant_echeance = None
            for p in m.phases.all():
                if p.date_reception_prevue and not p.date_reception_reelle:
                    jours = (p.date_reception_prevue - today).days
                    if 0 <= jours <= 60:
                        phase_urgente = True
                        jours_avant_echeance = jours
                        prob = min(0.95, prob * 1.3)
                    elif jours < 0:
                        prob = min(0.99, prob * 1.5)

            # Ajustement pénalités existantes
            if _safe_float(m.penalite_retard_dh) > 0:
                prob = min(0.99, prob * 1.4)

            pct = round(prob * 100, 1)
            predictions.append({
                'id': m.id,
                'numero_marche': m.numero_marche,
                'annee': m.annee,
                'projet': m.projet.intitule[:50] if m.projet else '—',
                'filiere': m.projet.filiere.libelle if m.projet and m.projet.filiere else '—',
                'entreprise': m.entreprise.raison_sociale if m.entreprise else '—',
                'prob_retard_pct': pct,
                'risque': 'Très élevé' if pct >= 70 else 'Élevé' if pct >= 50 else 'Modéré' if pct >= 30 else 'Faible',
                'couleur': '#ef4444' if pct >= 70 else '#f97316' if pct >= 50 else '#eab308' if pct >= 30 else '#22c55e',
                'phase_urgente': phase_urgente,
                'jours_avant_echeance': jours_avant_echeance,
                'montant_dh': montant,
            })

        predictions.sort(key=lambda x: x['prob_retard_pct'], reverse=True)

        return Response({
            'predictions': predictions,
            'taux_retard_historique': round(taux_global * 100, 1),
            'nb_marchés_analyses': len(predictions),
            'nb_a_risque': sum(1 for p in predictions if p['prob_retard_pct'] >= 50),
        })


class TendancesView(APIView):
    """
    Analyse des tendances temporelles: superficies, budgets, marchés par année.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models.functions import ExtractYear

        # Évolution annuelle des marchés
        tendances_marches = list(
            Marche.objects.values('annee')
            .annotate(
                nb=Count('id'),
                montant_total=Sum('montant_engage_dh'),
                sup_plantee=Sum('superficie_plantee'),
                sup_potentielle=Sum('superficie_potentielle'),
                nb_benef=Sum('nb_beneficiaires'),
                nb_femmes=Sum('nb_beneficiaires_femmes'),
                nb_jeunes=Sum('nb_beneficiaires_jeunes'),
            )
            .order_by('annee')
        )

        # Taux de réalisation par année
        for t in tendances_marches:
            sp = _safe_float(t['sup_potentielle'])
            st = _safe_float(t['sup_plantee'])
            t['taux_realisation'] = round(st / sp * 100, 1) if sp > 0 else 0
            t['montant_total'] = _safe_float(t['montant_total'])
            t['sup_plantee'] = _safe_float(t['sup_plantee'])
            t['sup_potentielle'] = _safe_float(t['sup_potentielle'])
            t['nb_benef'] = t['nb_benef'] or 0
            t['nb_femmes'] = t['nb_femmes'] or 0
            t['nb_jeunes'] = t['nb_jeunes'] or 0
            if t['nb_benef'] > 0:
                t['taux_feminite'] = round(t['nb_femmes'] / t['nb_benef'] * 100, 1)
                t['taux_jeunesse'] = round(t['nb_jeunes'] / t['nb_benef'] * 100, 1)
            else:
                t['taux_feminite'] = 0
                t['taux_jeunesse'] = 0

        # Projection simple (régression linéaire sur sup_plantee)
        annees = [t['annee'] for t in tendances_marches if t['sup_plantee'] > 0]
        sups = [t['sup_plantee'] for t in tendances_marches if t['sup_plantee'] > 0]

        projection = None
        if len(annees) >= 3:
            try:
                import numpy as np
                x = np.array(annees)
                y = np.array(sups)
                coeffs = np.polyfit(x, y, 1)
                next_year = max(annees) + 1
                proj_val = max(0, float(np.polyval(coeffs, next_year)))
                r2 = float(1 - np.var(y - np.polyval(coeffs, x)) / np.var(y)) if np.var(y) > 0 else 0
                projection = {
                    'annee': next_year,
                    'sup_projetee': round(proj_val, 1),
                    'coefficient_directeur': round(float(coeffs[0]), 2),
                    'r2': round(r2, 3),
                    'tendance': 'hausse' if coeffs[0] > 0 else 'baisse',
                    'confiance': 'élevée' if r2 > 0.7 else 'modérée' if r2 > 0.4 else 'faible',
                }
            except ImportError:
                pass

        # Performance par filière
        perf_filiere = list(
            Marche.objects.values('projet__filiere__libelle')
            .annotate(
                nb_marches=Count('id'),
                sup_plantee=Sum('superficie_plantee'),
                sup_potentielle=Sum('superficie_potentielle'),
                montant=Sum('montant_engage_dh'),
                nb_benef=Sum('nb_beneficiaires'),
                penalites=Sum('penalite_retard_dh'),
            )
            .order_by('-sup_plantee')
        )

        for f in perf_filiere:
            sp = _safe_float(f['sup_potentielle'])
            st = _safe_float(f['sup_plantee'])
            f['taux_realisation'] = round(st / sp * 100, 1) if sp > 0 else 0
            f['montant'] = _safe_float(f['montant'])
            f['sup_plantee'] = _safe_float(f['sup_plantee'])
            f['nb_benef'] = f['nb_benef'] or 0
            f['penalites'] = _safe_float(f['penalites'])
            f['filiere'] = f.pop('projet__filiere__libelle') or 'N/A'

        return Response({
            'tendances_annuelles': tendances_marches,
            'projection': projection,
            'performance_filieres': perf_filiere,
        })


class AnomaliesView(APIView):
    """
    Détection d'anomalies statistiques: montants aberrants, taux de réalisation atypiques,
    marchés sans activité, doublons potentiels.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        anomalies = []
        today = timezone.now().date()

        # 1. Marchés avec montant aberrant (z-score > 2)
        stats = Marche.objects.aggregate(
            moy=Avg('montant_engage_dh'),
            std=StdDev('montant_engage_dh'),
        )
        moy = _safe_float(stats['moy'])
        std = _safe_float(stats['std']) or 1

        for m in Marche.objects.filter(montant_engage_dh__isnull=False):
            z = abs((_safe_float(m.montant_engage_dh) - moy) / std)
            if z > 2.5:
                anomalies.append({
                    'type': 'montant_aberrant',
                    'label': 'Montant statistiquement aberrant',
                    'severity': 'warning',
                    'icon': '💰',
                    'marche': m.numero_marche,
                    'detail': f"Montant {float(m.montant_engage_dh):,.0f} DH (z-score={z:.1f}, moyenne={moy:,.0f} DH)",
                    'valeur': float(m.montant_engage_dh),
                    'z_score': round(z, 2),
                })

        # 2. Superficies réalisées > potentielles (incohérence)
        for m in Marche.objects.filter(superficie_plantee__isnull=False, superficie_potentielle__isnull=False):
            pot = _safe_float(m.superficie_potentielle)
            plant = _safe_float(m.superficie_plantee)
            if pot > 0 and plant > pot * 1.05:
                anomalies.append({
                    'type': 'superficie_incoherente',
                    'label': 'Superficie plantée > superficie potentielle',
                    'severity': 'error',
                    'icon': '🌿',
                    'marche': m.numero_marche,
                    'detail': f"Plantée: {plant} ha > Potentielle: {pot} ha (+{((plant/pot-1)*100):.0f}%)",
                    'valeur': plant - pot,
                })

        # 3. Marchés en cours sans aucune phase documentée
        for m in Marche.objects.filter(etat_avancement='en_cours').annotate(nb_phases=Count('phases')):
            if m.nb_phases == 0:
                anomalies.append({
                    'type': 'sans_phase',
                    'label': 'Marché en cours sans phase documentée',
                    'severity': 'info',
                    'icon': '📋',
                    'marche': m.numero_marche,
                    'detail': f"Année {m.annee} — Aucune ODS enregistrée",
                    'valeur': None,
                })

        # 4. Pénalités élevées (> 5% du montant)
        for m in Marche.objects.filter(penalite_retard_dh__gt=0, montant_marche_dh__gt=0):
            ratio = _safe_float(m.penalite_retard_dh) / _safe_float(m.montant_marche_dh)
            if ratio > 0.05:
                anomalies.append({
                    'type': 'penalite_elevee',
                    'label': 'Pénalité > 5% du montant marché',
                    'severity': 'error',
                    'icon': '⚠️',
                    'marche': m.numero_marche,
                    'detail': f"Pénalité: {float(m.penalite_retard_dh):,.0f} DH ({ratio*100:.1f}% du marché)",
                    'valeur': ratio * 100,
                })

        # 5. Taux de réalisation très faible pour marchés terminés
        for m in Marche.objects.filter(etat_avancement__in=['receptionne', 'cloture']):
            pot = _safe_float(m.superficie_potentielle)
            plant = _safe_float(m.superficie_plantee)
            if pot > 0 and plant / pot < 0.5:
                anomalies.append({
                    'type': 'realisation_faible',
                    'label': 'Marché réceptionné avec taux < 50%',
                    'severity': 'warning',
                    'icon': '📉',
                    'marche': m.numero_marche,
                    'detail': f"Réalisé {plant} ha / {pot} ha ({plant/pot*100:.0f}%)",
                    'valeur': round(plant / pot * 100, 1),
                })

        severity_order = {'error': 0, 'warning': 1, 'info': 2}
        anomalies.sort(key=lambda x: severity_order.get(x['severity'], 3))

        return Response({
            'anomalies': anomalies,
            'total': len(anomalies),
            'erreurs': sum(1 for a in anomalies if a['severity'] == 'error'),
            'avertissements': sum(1 for a in anomalies if a['severity'] == 'warning'),
            'informations': sum(1 for a in anomalies if a['severity'] == 'info'),
        })


class RecommandationsView(APIView):
    """
    Recommandations intelligentes basées sur l'analyse des données.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        recommandations = []

        # Marchés urgents à traiter
        phases_urgentes = MarchePhase.objects.filter(
            date_reception_prevue__isnull=False,
            date_reception_reelle__isnull=False,
            date_reception_prevue__gte=today,
            date_reception_prevue__lte=today + timedelta(days=30),
        ).select_related('marche', 'phase')

        if phases_urgentes.exists():
            recommandations.append({
                'priorite': 1,
                'type': 'urgence',
                'titre': f'{phases_urgentes.count()} réception(s) dans les 30 jours',
                'description': 'Des marchés arrivent à échéance. Planifiez les visites de réception.',
                'action': 'Voir les marchés en retard',
                'icon': '🚨',
                'couleur': '#ef4444',
                'items': [f"{p.marche.numero_marche} — {p.date_reception_prevue}" for p in phases_urgentes[:5]],
            })

        # Entreprises avec beaucoup de retards
        from django.db.models import FloatField, ExpressionWrapper
        entreprises_retard = []
        for e in Entreprise.objects.filter(marches__isnull=False).distinct():
            total = e.marches.count()
            retards = e.marches.filter(
                phases__date_reception_prevue__lt=today,
                phases__date_reception_reelle__isnull=True
            ).distinct().count()
            if total >= 2 and retards / total > 0.5:
                entreprises_retard.append({
                    'nom': e.raison_sociale,
                    'taux_retard': round(retards / total * 100)
                })

        if entreprises_retard:
            recommandations.append({
                'priorite': 2,
                'type': 'performance',
                'titre': f'{len(entreprises_retard)} entreprise(s) à faible performance',
                'description': 'Ces entreprises ont un taux de retard > 50%. Envisager un audit ou des pénalités.',
                'action': 'Voir le scoring de risque',
                'icon': '🏗️',
                'couleur': '#f97316',
                'items': [f"{e['nom']} ({e['taux_retard']}% de retard)" for e in entreprises_retard[:5]],
            })

        # Filieres sous-performantes
        from django.db.models import FloatField, Value
        for filiere_data in Marche.objects.values('projet__filiere__libelle').annotate(
            sp=Sum('superficie_potentielle'), st=Sum('superficie_plantee')
        ):
            sp = _safe_float(filiere_data['sp'])
            st = _safe_float(filiere_data['st'])
            if sp > 0 and st / sp < 0.6 and filiere_data['projet__filiere__libelle']:
                recommandations.append({
                    'priorite': 3,
                    'type': 'amelioration',
                    'titre': f"Filière {filiere_data['projet__filiere__libelle']}: taux {st/sp*100:.0f}%",
                    'description': f"Superficie plantée ({st:.0f} ha) loin de l'objectif ({sp:.0f} ha). Analyser les blocages.",
                    'action': 'Voir les marchés de la filière',
                    'icon': '🌿',
                    'couleur': '#eab308',
                    'items': [],
                })

        # Marchés sans entreprise assignée
        sans_entreprise = Marche.objects.filter(
            entreprise__isnull=True,
            etat_avancement='en_cours'
        ).count()
        if sans_entreprise > 0:
            recommandations.append({
                'priorite': 4,
                'type': 'donnees',
                'titre': f'{sans_entreprise} marché(s) sans entreprise assignée',
                'description': 'Compléter les données pour un suivi complet des marchés.',
                'action': 'Compléter les données',
                'icon': '📝',
                'couleur': '#6366f1',
                'items': [],
            })

        recommandations.sort(key=lambda x: x['priorite'])

        return Response({
            'recommandations': recommandations,
            'total': len(recommandations),
            'generees_le': today.isoformat(),
        })


class TableauBordIAView(APIView):
    """Vue agrégée pour le tableau de bord IA — données combinées pour affichage synthétique."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()

        marches_actifs = Marche.objects.filter(etat_avancement__in=['en_cours', 'programme'])
        scores = []
        for m in marches_actifs.prefetch_related('phases'):
            scores.append(_risk_score(m))

        score_moyen = round(sum(scores) / len(scores), 1) if scores else 0
        nb_critique = sum(1 for s in scores if s >= 70)
        nb_eleve = sum(1 for s in scores if 40 <= s < 70)

        # KPIs rapides
        total_marches = Marche.objects.count()
        en_retard = MarchePhase.objects.filter(
            date_reception_prevue__lt=today,
            date_reception_reelle__isnull=True
        ).values('marche').distinct().count()

        stats_benef = Marche.objects.aggregate(
            total=Sum('nb_beneficiaires'),
            femmes=Sum('nb_beneficiaires_femmes'),
            jeunes=Sum('nb_beneficiaires_jeunes'),
        )

        # Anomalies rapides
        nb_anomalies = 0
        for m in Marche.objects.filter(superficie_plantee__isnull=False, superficie_potentielle__isnull=False):
            if _safe_float(m.superficie_potentielle) > 0:
                if _safe_float(m.superficie_plantee) > _safe_float(m.superficie_potentielle) * 1.05:
                    nb_anomalies += 1
        nb_anomalies += Marche.objects.filter(penalite_retard_dh__gt=0).count()

        return Response({
            'score_risque_global': score_moyen,
            'nb_marchés_critiques': nb_critique,
            'nb_marchés_risque_eleve': nb_eleve,
            'nb_anomalies_detectees': nb_anomalies,
            'nb_retards_actifs': en_retard,
            'total_marches_analyses': total_marches,
            'beneficiaires_ia': {
                'total': stats_benef['total'] or 0,
                'femmes': stats_benef['femmes'] or 0,
                'jeunes': stats_benef['jeunes'] or 0,
                'taux_feminite': round(
                    (stats_benef['femmes'] or 0) / (stats_benef['total'] or 1) * 100, 1
                ),
                'taux_jeunesse': round(
                    (stats_benef['jeunes'] or 0) / (stats_benef['total'] or 1) * 100, 1
                ),
            },
            'modeles_utilises': [
                'Risk Scoring Multi-critères',
                'Scoring Bayésien (prédiction retards)',
                'Détection d\'anomalies (z-score)',
                'Régression Linéaire (tendances)',
            ],
        })
