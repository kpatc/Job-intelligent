#!/usr/bin/env python3
"""
Indeed International Scraper - DATA jobs extraction with undetected-chromedriver.
Support: Indeed.com (Multiple regions) - Data Engineering, Data Science, Data Analysis, AI/ML
Approach: Anti-detection with undetected-chromedriver
"""

import logging
import pandas as pd
import os
import time
import re
from typing import List, Dict, Optional
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

# Configuration logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("indeed_full_ingest.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class IndeedScraper:
    """Scraper pour Indeed.com - Support multi-régional DATA jobs."""

    def __init__(self):
        self.offers = []
        self.driver = None

    def setup_driver(self):
        """Configure le driver undetected-chromedriver."""
        try:
            options = uc.ChromeOptions()
            options.add_argument("--incognito")
            options.add_argument('--disable-gpu')
            options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36')
            
            # Let undetected_chromedriver auto-detect the version
            self.driver = uc.Chrome(options=options)
        except Exception as e:
            logger.error(f"Failed to initialize undetected-chromedriver: {e}")
            raise

    def is_data_job(self, title: str, description: str) -> bool:
        """Vérifie si c'est une offre DATA/ML/AI."""
        data_patterns = [
            r'\bdata\b',
            r'\bmachine\s+learning\b',
            r'\bml\b',
            r'\bai\b',
            r'\bartificial\s+intelligence\b',
            r'\bdata\s+science\b',
            r'\bdata\s+engineer\b',
            r'\bdata\s+analyst\b',
            r'\bscientist\b',
        ]
        
        exclude_patterns = [
            r'\bsoftware\s+engineer\b', r'\bdeveloper\b', r'\bdéveloppeur\b',
            r'\bfrontend\b', r'\bbackend\b', r'\bfullstack\b',
            r'\bdevops\b', r'\bqa\b', r'\btest\b',
        ]
        
        text_lower = (title + " " + description).lower()
        
        # Hard exclude first
        for pattern in exclude_patterns:
            if re.search(pattern, text_lower):
                return False
        
        # Must match at least one data pattern
        return any(re.search(pattern, text_lower) for pattern in data_patterns)

    def search_and_get_links(self, region: str = "es", keyword: str = "data") -> List[str]:
        """Recherche et récupère les liens - URL directe."""
        
        logger.info(f"\n{'='*80}")
        logger.info(f"Searching in Indeed {region.upper()}: {keyword}")
        logger.info(f"{'='*80}\n")
        
        try:
            # URL directe avec le keyword
            search_url = f"https://{region}.indeed.com/jobs?q={keyword.replace(' ', '+')}"
            logger.info(f"Loading: {search_url}")
            
            self.driver.get(search_url)
            time.sleep(5)
            
            # Récupérer les liens avec pagination
            links = self._get_pagination_links()
            logger.info(f"✓ {len(links)} links found in {region.upper()}\n")
            return links
            
        except Exception as e:
            logger.error(f"Erreur recherche {region}: {str(e)[:80]}")
            return []

    def _get_pagination_links(self) -> List[str]:
        """Récupère les liens avec pagination."""
        wait = WebDriverWait(self.driver, 10)
        links = []
        page_num = 1
        
        while True:
            try:
                # Chercher les offres avec sélecteur Indeed standard
                try:
                    new_links = wait.until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[data-jk]"))
                    )
                except TimeoutException:
                    # Fallback: utiliser le sélecteur alternatif
                    new_links = self.driver.find_elements(By.CSS_SELECTOR, ".jobtitle.turnstileLink")
                
                href_list = [l.get_attribute("href") for l in new_links if l.get_attribute("href")]
                links.extend(href_list)
                logger.debug(f"  Page {page_num}: {len(href_list)} offers")
                
                # Chercher le bouton suivant
                try:
                    next_button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//a[contains(@aria-label, 'Next Page')]"))
                    )
                    ActionChains(self.driver).move_to_element(next_button).click().perform()
                    time.sleep(3)
                    page_num += 1
                except TimeoutException:
                    logger.info(f"  ✓ Pagination terminée ({page_num} pages)")
                    break
                    
            except Exception as e:
                logger.error(f"  Erreur pagination page {page_num}: {str(e)[:50]}")
                break
        
        return links

    def parse_job_details(self, link: str) -> Optional[Dict]:
        """Scrape les détails complets d'une offre Indeed."""
        try:
            self.driver.get(link)
            time.sleep(2)
            
            # Vérifier captcha
            if "verification" in self.driver.title.lower():
                logger.warning(f"  ⚠ Captcha detected on {link[:60]}")
                return None
            
            # Position (titre)
            try:
                position = self.driver.find_element(
                    By.XPATH, 
                    "//h1[contains(@class, 'JobInfoHeader-title')]"
                ).text
            except NoSuchElementException:
                try:
                    position = self.driver.find_element(By.TAG_NAME, "h1").text
                except:
                    logger.debug(f"  ✗ NO TITLE FOUND: {link[:60]}")
                    return None
            
            if not position or "verification" in position.lower():
                logger.debug(f"  ✗ INVALID TITLE: {position[:60] if position else 'empty'}")
                return None
            
            # Company
            try:
                company = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "[data-company-name]"
                ).text
            except NoSuchElementException:
                company = "Not specified"
            
            # Description complète
            description = ""
            try:
                desc_elem = self.driver.find_element(By.ID, "jobDescriptionText")
                description = desc_elem.text
            except NoSuchElementException:
                try:
                    desc_elem = self.driver.find_element(By.CSS_SELECTOR, ".jobsearch-jobDescriptionText")
                    description = desc_elem.text
                except:
                    logger.debug(f"  ✗ NO DESC FOUND: {position[:60]}")
                    description = ""
            
            # Filtrer les offres DATA
            is_data = self.is_data_job(position, description)
            if not is_data:
                logger.debug(f"  ✗ NOT DATA JOB: {position[:60]}")
                return None
            
            # Location
            try:
                location = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='job-location']").text
            except:
                location = "International"
            
            # Release date
            try:
                meta = self.driver.find_element(By.XPATH, "//div[contains(@class, 'jobMetadataFooter')]").text
                search = re.search(r"(\d+).*?(day|week|month|hour)", meta.lower())
                if search:
                    release_date = f"{search.group(1)} {search.group(2)}s ago"
                else:
                    release_date = "today/recently"
            except:
                release_date = "recently"
            
            logger.info(f"  ✓ {position[:60]} @ {company}")
            
            return {
                "job_id": f"indeed_{len(self.offers)+1:05d}",
                "title": position,
                "company": company,
                "location": location,
                "url": link,
                "description": description[:5000],
                "publish_date": release_date,
                "source": "indeed",
                "scrape_date": datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.warning(f"  ✗ PARSE ERROR: {str(e)[:50]}")
            return None

    def scrape(self, keyword: str = "data", regions: List[str] = None, 
               max_offers: int = 100) -> List[Dict]:
        """Lance le scraping complet Indeed."""
        
        if regions is None:
            regions = ["es", "fr", "uk"]
        
        logger.info(f"\n{'='*80}")
        logger.info(f"Indeed International Scraper - DATA JOBS ONLY")
        logger.info(f"Keyword: {keyword}")
        logger.info(f"Regions: {', '.join(regions)}")
        logger.info(f"Max offers: {max_offers}")
        logger.info(f"{'='*80}\n")
        
        self.setup_driver()
        all_links = []
        
        try:
            # Chercher les liens pour chaque région
            for region in regions:
                links = self.search_and_get_links(region=region, keyword=keyword)
                all_links.extend(links)
            
            if not all_links:
                logger.warning("❌ No links found!")
                return []
            
            logger.info(f"\nScraping {min(len(all_links), max_offers)} job details...\n")
            
            # Scraper les détails
            for i, link in enumerate(all_links[:max_offers]):
                if not link:
                    continue
                
                logger.info(f"[{i+1}/{min(len(all_links), max_offers)}] Parsing: {link[:80]}")
                offer = self.parse_job_details(link)
                
                if offer:
                    self.offers.append(offer)
                else:
                    logger.debug(f"  → Rejected or failed")
                
                # Pause respectueuse
                if (i + 1) % 5 == 0:
                    time.sleep(2)
        
        except Exception as e:
            logger.error(f"Erreur scraping: {str(e)}")
        
        finally:
            if self.driver:
                self.driver.quit()
        
        logger.info(f"\n{'='*80}")
        logger.info(f"Indeed International - DATA JOBS Summary")
        logger.info(f"  Total offers scraped: {len(self.offers)}")
        logger.info(f"{'='*80}\n")
        
        return self.offers

    def save_to_csv(self, filename: str = "indeed_jobs.csv", output_dir: str = "data") -> str:
        """Sauvegarde les offres en CSV."""
        if not self.offers:
            logger.warning("No offers to save")
            return None
        
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        try:
            df = pd.DataFrame(self.offers)
            df.to_csv(filepath, index=False, encoding='utf-8')
            logger.info(f"✓ Saved {len(self.offers)} offers to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving CSV: {e}")
            return None


def run(keyword: str = "data", regions: List[str] = None, 
        max_offers: int = 100, output_dir: str = "data"):
    """
    Lance le scraping complet d'Indeed.com (International).
    
    Args:
        keyword: Keyword de recherche (default: "data")
        regions: Régions à scraper ex: ["es", "fr", "uk"] (default: ["es", "fr", "uk"])
        max_offers: Nombre maximum d'offres à scraper (default: 100)
        output_dir: Répertoire de sortie (default: "data")
    
    Returns:
        Liste des offres scrapées
    """
    
    if regions is None:
        regions = ["es", "fr", "uk"]
    
    scraper = IndeedScraper()
    offers = scraper.scrape(keyword=keyword, regions=regions, max_offers=max_offers)
    filepath = scraper.save_to_csv(output_dir=output_dir)
    
    logger.info(f"\n{'='*80}")
    logger.info(f"Final Summary - Indeed International DATA JOBS:")
    logger.info(f"  - Total offers: {len(offers)}")
    if filepath:
        logger.info(f"  - File: {filepath}")
    logger.info(f"  - Categories: Data, Machine Learning, AI")
    logger.info(f"{'='*80}\n")
    
    return offers


if __name__ == "__main__":
    # Lance le scraping
    offers = run(
        keyword="data",
        regions=["es", "fr", "uk"],
        max_offers=100,
        output_dir="data"
    )
    logger.info(f"✅ Scraping completed! {len(offers)} offers saved.")
