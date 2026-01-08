"""
Processing module - Nettoyage et normalisation des données
"""
import logging
import re
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class DataCleaner:
    """Nettoyage et normalisation des données d'offres d'emploi"""
    
    # Mapping des intitulés normalisés
    JOB_TITLE_MAPPING = {
        r'(?i)data.*scientist': 'Data Scientist',
        r'(?i)data.*engineer': 'Data Engineer',
        r'(?i)ml.*engineer|machine.*learning': 'ML Engineer',
        r'(?i)analytics.*engineer': 'Analytics Engineer',
        r'(?i)data.*analyst': 'Data Analyst',
        r'(?i)bi.*developer|business.*intelligence': 'BI Developer',
        r'(?i)python.*developer': 'Python Developer',
    }
    
    # Skills standardisés
    STANDARDIZED_SKILLS = {
        'python': 'Python',
        'sql': 'SQL',
        'spark': 'Apache Spark',
        'scala': 'Scala',
        'java': 'Java',
        'r': 'R',
        'pandas': 'Pandas',
        'numpy': 'NumPy',
        'sklearn': 'Scikit-Learn',
        'tensorflow': 'TensorFlow',
        'pytorch': 'PyTorch',
        'machine learning': 'Machine Learning',
        'deep learning': 'Deep Learning',
        'nlp': 'NLP',
        'computer vision': 'Computer Vision',
        'power bi': 'Power BI',
        'tableau': 'Tableau',
        'looker': 'Looker',
        'aws': 'AWS',
        'azure': 'Azure',
        'gcp': 'Google Cloud',
        'docker': 'Docker',
        'kubernetes': 'Kubernetes',
        'git': 'Git',
        'linux': 'Linux',
    }
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Nettoyer un texte"""
        if not text:
            return ''
        
        # Supprimer espaces superflus
        text = ' '.join(text.split())
        # Supprimer caractères spéciaux problématiques
        text = re.sub(r'[^\w\s\-\.]', '', text)
        return text.strip()
    
    @staticmethod
    def normalize_job_title(title: str) -> str:
        """Normaliser un intitulé de poste"""
        title = DataCleaner.clean_text(title)
        
        for pattern, normalized in DataCleaner.JOB_TITLE_MAPPING.items():
            if re.search(pattern, title, re.IGNORECASE):
                return normalized
        
        return title
    
    @staticmethod
    def extract_and_standardize_skills(text: str, provided_skills: List[str] = None) -> List[str]:
        """Extraire et standardiser les compétences"""
        skills = set()
        
        # Ajouter les skills fournis
        if provided_skills:
            for skill in provided_skills:
                standardized = DataCleaner.STANDARDIZED_SKILLS.get(skill.lower(), skill)
                skills.add(standardized)
        
        # Extraire du texte
        text_lower = text.lower()
        for skill_key, skill_name in DataCleaner.STANDARDIZED_SKILLS.items():
            if skill_key in text_lower:
                skills.add(skill_name)
        
        return list(skills)
    
    @staticmethod
    def clean_job(job: Dict[str, Any]) -> Dict[str, Any]:
        """Nettoyer une offre complète"""
        return {
            'job_title': DataCleaner.normalize_job_title(job.get('job_title', '')),
            'job_description': DataCleaner.clean_text(job.get('job_description', '')),
            'company_name': DataCleaner.clean_text(job.get('company_name', '')),
            'location': DataCleaner.clean_text(job.get('location', '')),
            'experience_level': job.get('experience_level', '').strip() or 'Non spécifié',
            'contract_type': job.get('contract_type', '').strip() or 'Non spécifié',
            'job_url': job.get('job_url', ''),
            'external_job_id': job.get('external_job_id', ''),
            'published_at': job.get('published_at'),
            'skills': DataCleaner.extract_and_standardize_skills(
                job.get('job_description', ''),
                job.get('skills', [])
            ),
            'salary_min': job.get('salary_min'),
            'salary_max': job.get('salary_max'),
            'salary_currency': job.get('salary_currency', 'EUR'),
        }
    
    @staticmethod
    def deduplicate_jobs(jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Supprimer les doublons basé sur job_url ou external_id"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            # Utiliser external_job_id comme clé unique
            key = job.get('external_job_id', job.get('job_url', ''))
            if key and key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        logger.info(f"✓ {len(jobs) - len(unique_jobs)} doublons supprimés")
        return unique_jobs


class DataProcessor:
    """Pipeline de traitement des données"""
    
    @staticmethod
    def process_jobs(raw_jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Pipeline complet de traitement"""
        logger.info("🔄 NETTOYAGE ET NORMALISATION")
        
        # 1. Dédupliquer
        deduplicated = DataCleaner.deduplicate_jobs(raw_jobs)
        logger.info(f"✓ {len(deduplicated)} offres après déduplication")
        
        # 2. Nettoyer
        cleaned_jobs = []
        for job in deduplicated:
            try:
                cleaned = DataCleaner.clean_job(job)
                cleaned_jobs.append(cleaned)
            except Exception as e:
                logger.warning(f"Erreur nettoyage: {e}")
        
        logger.info(f"✓ {len(cleaned_jobs)} offres nettoyées")
        
        # 3. Valider
        validated_jobs = [j for j in cleaned_jobs if j.get('job_title') and j.get('job_description')]
        logger.info(f"✓ {len(validated_jobs)} offres validées")
        
        return validated_jobs
