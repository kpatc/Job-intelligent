#!/usr/bin/env python3
"""
Load Jobs & Skills to Snowflake - Main Entry Point
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd

# Charger .env
PROJECT_ROOT = Path(__file__).parent.parent
env_file = PROJECT_ROOT / ".env"
load_dotenv(env_file)

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("load_snowflake.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DATA_DIR = PROJECT_ROOT / "data"

# Importer le loader
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from database.snowflake_loader import SnowflakeLoader

def main():
    """Charge les données dans Snowflake."""
    
    logger.info("="*70)
    logger.info("SNOWFLAKE DATA LOADER - Jobs + Skills")
    logger.info("="*70)
    
    # Récupérer les credentials
    account = os.getenv('SNOWFLAKE_ACCOUNT')
    user = os.getenv('SNOWFLAKE_USER')
    password = os.getenv('SNOWFLAKE_PASSWORD')
    warehouse = os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH')
    database = os.getenv('SNOWFLAKE_DATABASE', 'job_intelligent')
    schema = os.getenv('SNOWFLAKE_SCHEMA', 'public')
    
    # Vérifier les credentials
    if not all([account, user, password]):
        logger.error("❌ ERREUR: Credentials Snowflake manquantes dans .env")
        logger.error("   Ajoute: SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD")
        return False
    
    logger.info(f"Account: {account}")
    logger.info(f"User: {user}")
    logger.info(f"Warehouse: {warehouse}")
    logger.info(f"Database: {database}")
    logger.info(f"Schema: {schema}")
    
    # Charger les fichiers CSV
    jobs_csv = DATA_DIR / "jobs_cleaned.csv"
    skills_csv = DATA_DIR / "jobs_skills.csv"
    
    if not jobs_csv.exists():
        logger.error(f"❌ {jobs_csv} not found")
        return False
    
    if not skills_csv.exists():
        logger.error(f"❌ {skills_csv} not found")
        return False
    
    logger.info(f"\n[1/3] Chargement des CSV...")
    try:
        df_jobs = pd.read_csv(jobs_csv)
        logger.info(f"  ✓ {len(df_jobs)} jobs chargés")
    except Exception as e:
        logger.error(f"  ❌ Erreur: {e}")
        return False
    
    try:
        df_skills = pd.read_csv(skills_csv)
        logger.info(f"  ✓ {len(df_skills)} skills chargées")
    except Exception as e:
        logger.error(f"  ❌ Erreur: {e}")
        return False
    
    # Créer le loader
    logger.info(f"\n[2/3] Connexion à Snowflake...")
    try:
        loader = SnowflakeLoader(
            account=account,
            user=user,
            password=password,
            warehouse=warehouse,
            database=database,
            schema=schema
        )
    except Exception as e:
        logger.error(f"  ❌ Erreur création loader: {e}")
        return False
    
    # Charger les données
    logger.info(f"\n[3/3] Chargement des données...")
    try:
        success = loader.load_all(df_jobs, df_skills)
        if success:
            logger.info("\n" + "="*70)
            logger.info("✅ CHARGEMENT RÉUSSI!")
            logger.info("="*70)
            return True
        else:
            logger.error("❌ Erreur lors du chargement")
            return False
    except Exception as e:
        logger.error(f"  ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
