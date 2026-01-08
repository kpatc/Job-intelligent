"""
Script principal - Lancer l'ingestion et le traitement
"""
import sys
import logging
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/josh/PowerBi/job-intelligent/data/ingestion.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

from config.settings import DATABASE_URL
from src.database import db
from src.database.models import Base
from src.ingestion.orchestrator import IngestionOrchestrator
from src.processing import DataProcessor


def setup_database():
    """Initialiser la base de données"""
    logger.info("🗄️  Initialisation base de données...")
    
    try:
        # Connecter à la BD
        if not db.connect():
            logger.error("Impossible de se connecter à la base de données")
            return False
        
        # Créer les tables (si needed)
        # Base.metadata.create_all(db.engine)
        # logger.info("✓ Tables créées")
        
        return True
    except Exception as e:
        logger.error(f"Erreur init BD: {e}")
        return False


def main():
    """Fonction principale"""
    
    logger.info("🚀 DÉMARRAGE PIPELINE JOB INTELLIGENT")
    logger.info(f"Database: {DATABASE_URL}")
    
    # 1. Setup BD
    if not setup_database():
        logger.error("Échec initialisation BD")
        return
    
    # 2. Ingestion
    orchestrator = IngestionOrchestrator()
    ingestion_result = orchestrator.run_all()
    
    # Récupérer tous les jobs
    all_jobs = orchestrator.get_all_jobs()
    logger.info(f"\n📦 Total jobs à traiter: {len(all_jobs)}")
    
    # 3. Traitement (nettoyage)
    processed_jobs = DataProcessor.process_jobs(all_jobs)
    
    # 4. Sauvegarder
    logger.info("\n💾 SAUVEGARDE DES DONNÉES")
    _save_jobs(processed_jobs)
    
    logger.info("\n✅ PIPELINE TERMINÉ AVEC SUCCÈS!")
    logger.info("=" * 60)
    
    # Fermer BD
    db.disconnect()


def _save_jobs(jobs):
    """Sauvegarder les jobs (pour développement)"""
    import json
    from config.settings import PROCESSED_DATA_DIR
    
    output_file = f"{PROCESSED_DATA_DIR}/jobs_processed.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False, default=str)
    
    logger.info(f"✓ {len(jobs)} offres sauvegardées dans {output_file}")


if __name__ == '__main__':
    main()
