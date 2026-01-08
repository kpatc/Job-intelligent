"""
Module d'ingestion - Base pour tous les connecteurs de sources
"""
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseIngester(ABC):
    """Classe abstraite pour tous les ingesteurs de données"""
    
    def __init__(self, source_name: str, source_type: str):
        self.source_name = source_name
        self.source_type = source_type  # 'api', 'scraping', 'csv'
        self.jobs = []
        self.errors = []
    
    @abstractmethod
    def fetch_jobs(self) -> List[Dict[str, Any]]:
        """
        Récupérer les offres depuis la source
        Doit retourner une liste de dictionnaires avec les données brutes
        """
        pass
    
    @abstractmethod
    def validate_job(self, job: Dict[str, Any]) -> bool:
        """Valider si une offre a tous les champs requis"""
        pass
    
    def normalize_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliser les données d'une offre (à override si besoin)"""
        return {
            'job_title': job.get('job_title', '').strip(),
            'job_description': job.get('job_description', '').strip(),
            'company_name': job.get('company_name', '').strip(),
            'location': job.get('location', '').strip(),
            'experience_level': job.get('experience_level', '').strip(),
            'contract_type': job.get('contract_type', '').strip(),
            'job_url': job.get('job_url', ''),
            'external_job_id': job.get('external_job_id', f"{self.source_name}_{job.get('id', '')}"),
            'published_at': job.get('published_at', datetime.now().date()),
            'skills': job.get('skills', []),
            'salary_min': job.get('salary_min'),
            'salary_max': job.get('salary_max'),
            'salary_currency': job.get('salary_currency'),
        }
    
    def ingest(self) -> Dict[str, Any]:
        """Processus d'ingestion complet"""
        logger.info(f"🔄 Démarrage ingestion: {self.source_name}")
        start_time = datetime.now()
        
        try:
            # Récupérer les jobs
            raw_jobs = self.fetch_jobs()
            logger.info(f"✓ {len(raw_jobs)} offres récupérées de {self.source_name}")
            
            # Valider et normaliser
            for raw_job in raw_jobs:
                try:
                    if self.validate_job(raw_job):
                        normalized = self.normalize_job(raw_job)
                        self.jobs.append(normalized)
                    else:
                        self.errors.append(f"Job invalide: {raw_job.get('id', 'Unknown')}")
                except Exception as e:
                    self.errors.append(f"Erreur normalisation: {str(e)}")
            
            logger.info(f"✓ {len(self.jobs)} offres valides, {len(self.errors)} erreurs")
            
            return {
                'source': self.source_name,
                'status': 'success',
                'jobs_count': len(self.jobs),
                'errors_count': len(self.errors),
                'started_at': start_time,
                'ended_at': datetime.now(),
                'data': self.jobs,
                'errors': self.errors
            }
            
        except Exception as e:
            logger.error(f"✗ Erreur ingestion {self.source_name}: {str(e)}")
            return {
                'source': self.source_name,
                'status': 'error',
                'jobs_count': 0,
                'errors_count': 1,
                'started_at': start_time,
                'ended_at': datetime.now(),
                'data': [],
                'error_message': str(e)
            }
