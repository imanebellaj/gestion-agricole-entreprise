# DPA Agricole — Guide d'installation

## Prérequis
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ avec la base `dpa` restaurée (fichier `datta.sql`)

## 1. Restaurer la base de données

```bash
psql -U postgres -c "CREATE DATABASE dpa;"
psql -U postgres dpa < datta.sql
```

## 2. Configurer le backend Django

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt

# Renseigner le mot de passe PostgreSQL dans .env
notepad .env
```

Modifier dans `.env` :
```
DB_PASSWORD=votre_mot_de_passe_postgres
```

Puis :
```bash
python manage.py migrate --run-syncdb
python manage.py createsuperuser
python manage.py runserver
```

## 3. Démarrer le frontend React

```bash
cd frontend
npm install
npm run dev
```

## 4. Accès à l'application

| URL | Description |
|-----|-------------|
| http://localhost:5173 | Application web (React) |
| http://localhost:8000/api/docs/ | Documentation API (Swagger) |
| http://localhost:8000/admin/ | Interface d'administration Django |

## Structure du projet

```
dev_app_agricole/
├── backend/                  # Django + DRF
│   ├── apps/
│   │   ├── geo/              # Provinces, Cercles, Communes
│   │   ├── referentiels/     # Filières, Phases, Modes, Statuts
│   │   ├── acteurs/          # Entreprises, OPs, Bénéficiaires
│   │   ├── projets/          # Projets + Programmation annuelle
│   │   ├── marches/          # Marchés + Phases + Paiements
│   │   └── dashboard/        # KPIs et agrégats
│   ├── config/               # Settings Django
│   ├── .env                  # Configuration (DB, secrets)
│   └── requirements.txt
└── frontend/                 # React + Vite + Tailwind
    ├── src/
    │   ├── api/              # Client HTTP + endpoints
    │   ├── components/       # UI réutilisables
    │   ├── context/          # Auth context
    │   └── pages/            # Dashboard, Projets, Marchés...
    └── package.json
```

## Endpoints API principaux

```
GET  /api/dashboard/kpi/                    → KPIs globaux
GET  /api/projets/projets/                  → Liste des projets
GET  /api/marches/marches/en_retard/        → Marchés en retard
GET  /api/acteurs/beneficiaires/doublons/   → Doublons CIN
GET  /api/dashboard/evolution-annuelle/     → Courbes temporelles
```
