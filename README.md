# 🌱 Application de Gestion Agricole

Application web complète développée durant mon stage en entreprise pour la gestion et le suivi des projets agricoles, marchés, bénéficiaires et acteurs du secteur agricole.

---

## 🚀 Technologies utilisées

**Backend**
- Python / Django 5 + Django REST Framework
- PostgreSQL
- JWT Authentication (djangorestframework-simplejwt)
- Pandas & NumPy (analyse de données)
- API Documentation avec Swagger (drf-spectacular)

**Frontend**
- React 19 + Vite
- Tailwind CSS
- Leaflet (cartes interactives)
- Recharts (graphiques et statistiques)
- React Query + Axios

---

## ✨ Fonctionnalités principales

- 📊 **Dashboard** — KPIs globaux, évolution annuelle, statistiques en temps réel
- 🗺️ **Carte interactive** — Visualisation géographique des projets (provinces, cercles, communes)
- 📁 **Gestion des projets** — Suivi complet avec programmation annuelle
- 🤝 **Marchés** — Gestion des marchés, phases et paiements, alertes retard
- 👥 **Acteurs** — Entreprises, organisations professionnelles, bénéficiaires
- 🤖 **Module IA** — Analyse intelligente des données agricoles
- 📤 **Export** — Export des données en Excel et PDF

---

## 🗂️ Structure du projet

```
dev_app_agricole/
├── backend/                  # Django + DRF
│   ├── apps/
│   │   ├── geo/              # Provinces, Cercles, Communes
│   │   ├── referentiels/     # Filières, Phases, Modes, Statuts
│   │   ├── acteurs/          # Entreprises, OPs, Bénéficiaires
│   │   ├── projets/          # Projets + Programmation annuelle
│   │   ├── marches/          # Marchés + Phases + Paiements
│   │   ├── ia/               # Module intelligence artificielle
│   │   └── dashboard/        # KPIs et agrégats
│   └── requirements.txt
└── frontend/                 # React + Vite + Tailwind
    └── src/
        ├── api/              # Client HTTP + endpoints
        ├── components/       # Composants UI réutilisables
        ├── context/          # Auth context (JWT)
        └── pages/            # Dashboard, Projets, Marchés...
```

---

## ⚙️ Installation

### Prérequis
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt

# Configurer la base de données dans .env
cp .env.example .env
# Modifier DB_PASSWORD dans .env

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Accès

| URL | Description |
|-----|-------------|
| http://localhost:5173 | Application React |
| http://localhost:8000/api/docs/ | Documentation Swagger |
| http://localhost:8000/admin/ | Administration Django |

---

## 📡 API Endpoints principaux

```
GET  /api/dashboard/kpi/                  → KPIs globaux
GET  /api/projets/projets/                → Liste des projets
GET  /api/marches/marches/en_retard/      → Marchés en retard
GET  /api/acteurs/beneficiaires/doublons/ → Détection doublons
GET  /api/dashboard/evolution-annuelle/  → Évolution temporelle
```

---

## 👩‍💻 Auteure

**Bellaj Imane**
Étudiante en Génie Informatique — Option Intelligence Artificielle
DUT — École Supérieure de Technologie

[![GitHub](https://img.shields.io/badge/GitHub-imanebellaj-black?logo=github)](https://github.com/imanebellaj)
