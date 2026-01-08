"""
Configuration centralisée du projet Job Intelligent
"""
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# ========== DATABASE ==========
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 5432),
    'database': os.getenv('DB_NAME', 'job_intelligent'),
    'user': os.getenv('DB_USER', 'job_user'),
    'password': os.getenv('DB_PASSWORD', ''),
}

# Connection string SQLAlchemy
DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

# ========== PATHS ==========
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')

# Créer les répertoires s'ils n'existent pas
for dir_path in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# ========== API KEYS ==========
API_KEYS = {
    'linkedin': os.getenv('LINKEDIN_API_KEY', ''),
    'indeed': os.getenv('INDEED_API_KEY', ''),
}

# ========== LOGGING ==========
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# ========== SOURCES DE DONNÉES ==========
DATA_SOURCES = {
    'indeed': {
        'enabled': True,
        'type': 'scraping',
    },
    'linkedin': {
        'enabled': True,
        'type': 'api',
    },
    'welcome_jungle': {
        'enabled': True,
        'type': 'api',
    },
    'france_travail': {
        'enabled': True,
        'type': 'api',
    },
}

# ========== NLP ==========
NLP_CONFIG = {
    'model': 'sentence-transformers/all-MiniLM-L6-v2',
    'language': 'fr',
}

# ========== RECOMMANDATION ==========
RECOMMENDATION_CONFIG = {
    'top_n': 10,
    'similarity_threshold': 0.5,
    'weights': {
        'semantic_similarity': 0.5,
        'skills_match': 0.3,
        'location_match': 0.2,
    }
}
