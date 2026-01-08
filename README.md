# Job Intelligent - Dashboard Power BI

Plateforme data-driven pour l'analyse et la recommandation d'offres d'emploi Data.

## 🏗️ Architecture

```
[ Job Boards ] → [ Ingestion ] → [ Nettoyage ] → [ Stockage ] 
                                                      ↓
                                              [ NLP & Recommandation ]
                                                      ↓
                                              [ Data Mart BI ]
                                                      ↓
                                              [ Power BI Dashboard ]
```

## 📦 Structure du projet

```
job-intelligent/
├── src/
│   ├── ingestion/          # Collecte depuis Job Boards
│   ├── processing/         # Nettoyage & Normalisation
│   ├── nlp/               # Analyse sémantique & Embeddings
│   ├── recommandation/    # Système de matching
│   └── database/          # Connexion & schéma DB
├── config/                # Configuration (env vars)
├── data/                  # Raw data & exports
├── scripts/               # Orchestration & utilitaires
├── requirements.txt       # Dépendances Python
└── README.md
```

## 🚀 Installation

1. **Cloner le repo**
```bash
cd /home/josh/PowerBi
```

2. **Créer l'environnement virtuel**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer la base de données PostgreSQL**
```bash
# Voir scripts/setup_database.sql
psql -U postgres -f scripts/setup_database.sql
```

5. **Configuration ENV**
```bash
cp .env.example .env
# Éditer .env avec vos paramètres
```

## 🎯 Phases du projet

- [ ] Phase 1 : Architecture & BD (en cours)
- [ ] Phase 2 : Ingestion données
- [ ] Phase 3 : Nettoyage & Normalisation
- [ ] Phase 4 : NLP & Recommandation
- [ ] Phase 5 : Data Mart BI
- [ ] Phase 6 : Dashboard Power BI

## 📝 Livrables

- Base de données centralisée
- Pipeline data documentée
- Système de recommandation
- Dashboard Power BI
- Rapport final
