#!/usr/bin/env python3
"""
ReKrute International Scraper - Multi-regional job extraction.
Supporte: ReKrute.com (Global) avec scraping des offres tech complètes.
"""

import requests
import csv
import time
import logging
import re
import os
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin

# Chemins absolus pour les données (stockage dans job-intelligent/data/)
PROJECT_ROOT = Path(__file__).parent.parent.parent  # Remonte vers job-intelligent/
DATA_DIR = PROJECT_ROOT / "data"

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("rekrute_full_ingest.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ReKruteScraper:
    """Scraper professionnel pour ReKrute.com - Support multi-régional."""

    def __init__(self):
        self.base_url = "https://www.rekrute.com"
        # URL filtrée pour les emplois en IT - meilleur pour trouver les offres DATA
        self.jobs_list_url = "https://www.rekrute.com/fr/offres-emploi-metiers-de-l-it.html"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        self.offers = []

    def fetch_page(self, url: str, timeout: int = 10) -> Optional[requests.Response]:
        """Récupère une page avec gestion des erreurs."""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            time.sleep(0.5)  # Respecter le serveur
            return response
        except requests.RequestException as e:
            logger.warning(f"Erreur accès {url}: {e}")
            return None

    def is_strictly_tech_job(self, title: str, description: str = "") -> bool:
        """Filtre - accepte les offres DATA, Machine Learning, AI."""
        
        # DATA/ML/AI KEYWORDS - PLUS SIMPLE ET FLEXIBLE
        data_patterns = [
            r'\bdata\b',
            r'\bmachine\s+learning\b',
            r'\bml\b',
            r'\bai\b',
            r'\bartificial\s+intelligence\b',
            r'\bdata\s+science\b',
            r'\bdata\s+engineer\b',
            r'\bdata\s+analyst\b',
            r'\banalyste\b',
            r'\bscientist\b',
        ]
        
        # HARD EXCLUDE - jobs clairement non-data/ml/ai
        exclude_patterns = [
            r'\bsoftware\s+engineer\b', r'\bdeveloper\b', r'\bdéveloppeur\b',
            r'\bfrontend\b', r'\bbackend\b', r'\bfullstack\b',
            r'\bdevops\b', r'\bsysadmin\b', r'\binfrastructure\b',
            r'\bsecurity\b', r'\bcybersecurity\b',
            r'\bqa\b', r'\btest\b', r'\bqa\s+automation\b',
            r'\breact\b', r'\bvue\b', r'\bangular\b', r'\bnode\b',
            r'\bcaissier\b', r'\bvend[e]?ur\b', r'\bcommercial\b', r'\bvente\b',
        ]
        
        text_lower = (title + " " + description).lower()
        
        # Hard exclude first
        for pattern in exclude_patterns:
            if re.search(pattern, text_lower):
                return False
        
        # MUST match at least ONE data/ml/ai pattern
        return any(re.search(pattern, text_lower) for pattern in data_patterns)

    def clean_text(self, text: str) -> str:
        """Nettoie le texte extrait."""
        if not text:
            return ""
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'&[a-z]+;', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def parse_job_listing(self, url: str) -> Optional[Dict]:
        """Scrape les détails complets d'une offre d'emploi."""
        try:
            response = self.fetch_page(url, timeout=8)
            if not response:
                return None
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extraire le titre
            title_elem = soup.find("h1")
            title = self.clean_text(title_elem.get_text()) if title_elem else ""
            
            if not title or len(title) < 5:
                return None
            
            # Filtrer strictement les offres data
            page_text = soup.get_text()[:3000]
            if not self.is_strictly_tech_job(title, page_text):
                logger.debug(f"  ✗ REJECTED (non-data): {title[:60]}")
                return None
            
            # ========== EXTRACTION COMPANY ==========
            # Chercher la section "Entreprise :"
            company = ""
            all_text = soup.get_text()
            
            # Chercher après "Entreprise :"
            if "Entreprise :" in all_text:
                start_idx = all_text.find("Entreprise :") + len("Entreprise :")
                # Prendre le texte jusqu'au prochain titre principal
                end_text = all_text[start_idx:start_idx + 500]
                lines = end_text.split('\n')
                for line in lines:
                    line = self.clean_text(line)
                    if line and len(line) > 3 and len(line) < 100:
                        company = line
                        break
            
            # Fallback: chercher dans les balises communes
            if not company:
                company_selectors = [
                    ("h2", {"class": lambda x: x and "company" in x.lower()}),
                    ("div", {"class": lambda x: x and "company" in x.lower()}),
                    ("span", {"class": "company-name"}),
                ]
                for tag, attrs in company_selectors:
                    elem = soup.find(tag, attrs)
                    if elem:
                        company = self.clean_text(elem.get_text())
                        break
            
            # Dernier fallback
            if not company:
                company = "Non spécifié"
            
            # ========== EXTRACTION LOCALISATION ==========
            location = "International"
            location_selectors = [
                ("span", {"class": lambda x: x and "location" in x.lower()}),
                ("div", {"data-testid": "job-location"}),
                ("div", {"class": lambda x: x and "lieu" in x.lower()}),
            ]
            for tag, attrs in location_selectors:
                elem = soup.find(tag, attrs)
                if elem:
                    location = self.clean_text(elem.get_text())
                    break
            
            # ========== EXTRACTION DESCRIPTION ==========
            # Extraire UNIQUEMENT "Poste" et "Profil recherché"
            description_parts = []
            text_lines = all_text.split('\n')
            
            in_poste_section = False
            in_profil_section = False
            in_unwanted_section = False
            
            for i, line in enumerate(text_lines):
                line_clean = self.clean_text(line)
                line_lower = line_clean.lower()
                
                # Détection des sections
                if 'poste' in line_lower and ':' in line_lower:
                    in_poste_section = True
                    in_profil_section = False
                    in_unwanted_section = False
                    continue
                elif 'profil' in line_lower and 'recherch' in line_lower and ':' in line_lower:
                    in_profil_section = True
                    in_poste_section = False
                    in_unwanted_section = False
                    continue
                elif any(section in line_lower for section in [
                    'entreprise', 'avantage', 'culture', 'candidature', 
                    'processus', 'contact', 'nos offres', 'emplois'
                ]):
                    in_poste_section = False
                    in_profil_section = False
                    in_unwanted_section = True
                    continue
                
                # Ajouter le texte des sections pertinentes
                if (in_poste_section or in_profil_section) and line_clean and len(line_clean) > 2:
                    description_parts.append(line_clean)
            
            description = " ".join(description_parts)[:2500]
            
            if not description:
                description = f"Titre: {title} | Localisation: {location}"
            
            logger.info(f"  ✓ {title[:60]} @ {company}")
            
            return {
                "job_id": f"rekrute_{len(self.offers)+1:05d}",
                "title": title,
                "company": company,
                "location": location,
                "url": url,
                "description": description,
                "source": "rekrute",
                "scrape_date": datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.debug(f"  Erreur scraping détails: {str(e)[:50]}")
            return None

    def scrape(self, num_pages: int = 25) -> List[Dict]:
        """Scrape ReKrute.com sur plusieurs pages - DATA JOBS UNIQUEMENT."""
        offers = []
        seen = set()
        
        logger.info(f"\n{'='*80}")
        logger.info(f"Scraping ReKrute.com IT Jobs Filter (International) - DATA JOBS ONLY")
        logger.info(f"URL: {self.jobs_list_url}")
        logger.info(f"Filtres: Toute offre avec 'data', 'machine learning', 'ai'")
        logger.info(f"Pages à scraper: {num_pages}")
        logger.info(f"{'='*80}\n")
        
        for page in range(1, num_pages + 1):
            try:
                # Utiliser l'URL filtrée IT avec pagination
                if page == 1:
                    url = self.jobs_list_url
                else:
                    url = f"{self.jobs_list_url}?p={page}"
                
                logger.info(f"Page {page}: {url}")
                
                response = self.fetch_page(url)
                if not response or response.status_code != 200:
                    logger.warning(f"  Status {response.status_code if response else 'None'}")
                    continue
                
                soup = BeautifulSoup(response.text, "html.parser")
                page_count = 0
                
                # Trouver TOUS les liens (plus flexible)
                all_links = soup.find_all("a", href=True)
                logger.debug(f"  Trouvé {len(all_links)} liens au total")
                
                for link in all_links:
                    href = link.get("href", "").strip()
                    if not href:
                        continue
                    
                    title = self.clean_text(link.get_text())
                    if not title or len(title) < 3:
                        continue
                    
                    # Filtre: liens d'offres d'emploi (pattern flexible)
                    if "offre-emploi" not in href and "offre_emploi" not in href:
                        continue
                    
                    # Éviter les doublons
                    if title in seen:
                        continue
                    seen.add(title)
                    
                    # Scraper les détails complets
                    if not href.startswith('http'):
                        job_url = urljoin(self.base_url, href)
                    else:
                        job_url = href
                    
                    offer = self.parse_job_listing(job_url)
                    
                    if offer:
                        offers.append(offer)
                        self.offers.append(offer)
                        page_count += 1
                        logger.debug(f"    ✓ Added: {offer['title'][:50]}")
                
                logger.info(f"  ✓ {page_count} data jobs trouvés en page {page}\n")
                
            except Exception as e:
                logger.error(f"Erreur page {page}: {str(e)[:50]}")
                continue
        
        logger.info(f"\n{'='*80}")
        logger.info(f"ReKrute International - IT Filter - DATA JOBS Summary")
        logger.info(f"  Total offres DATA scrapées: {len(offers)}")
        logger.info(f"{'='*80}\n")
        
        return offers

    def save_to_csv(self, filename: str = "rekrute_jobs.csv", output_dir: Optional[str] = None) -> str:
        """Sauvegarde les offres en CSV."""
        if not self.offers:
            logger.warning("Aucune offre à sauvegarder")
            return None
        
        # Utilise le répertoire data/ du projet racine si non spécifié
        if output_dir is None:
            output_dir = str(DATA_DIR)
        
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        try:
            df = pd.DataFrame(self.offers)
            df.to_csv(filepath, index=False, encoding='utf-8')
            logger.info(f"✓ Sauvegardé {len(self.offers)} offres dans {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Erreur sauvegarde CSV: {e}")
            return None


def run(num_pages: int = 25, output_dir: Optional[str] = None):
    """
    Lance le scraping complet de ReKrute.com (International).
    
    Args:
        num_pages: Nombre de pages à scraper (default: 25)
        output_dir: Répertoire de sortie pour les données (default: job-intelligent/data/)
    
    Returns:
        Liste des offres scrapées
    """
    scraper = ReKruteScraper()
    offers = scraper.scrape(num_pages=num_pages)
    filepath = scraper.save_to_csv(output_dir=output_dir)
    
    logger.info(f"\n{'='*80}")
    logger.info(f"Résumé final ReKrute International - DATA JOBS:")
    logger.info(f"  - Offres DATA scrapées: {len(offers)}")
    if filepath:
        logger.info(f"  - Fichier: {filepath}")
    logger.info(f"  - Catégories: Toute offre contenant 'data', 'machine learning', 'ai'")
    logger.info(f"{'='*80}\n")
    
    return offers


if __name__ == "__main__":
    # Lance le scraping avec 25 pages par défaut
    # Utilise le dossier data/ du projet racine (job-intelligent/data/)
    offers = run(num_pages=25, output_dir=str(DATA_DIR))
    logger.info(f"✅ Scraping terminé! {len(offers)} offres sauvegardées.")
