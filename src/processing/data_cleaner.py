#!/usr/bin/env python3
"""
Data Cleaner: Harmonize, clean, and normalize job data from multiple sources
"""

import pandas as pd
import re
import os
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

class DataCleaner:
    def __init__(self):
        self.df_combined = None
        self.data_dir = DATA_DIR
        
    def load_data(self):
        """Load Indeed and ReKrute CSV files"""
        logger.info("Loading data files...")
        
        indeed_file = self.data_dir / "indeed_jobs.csv"
        rekrute_file = self.data_dir / "rekrute_jobs.csv"
        
        if not indeed_file.exists():
            logger.warning(f"Indeed file not found: {indeed_file}")
            df_indeed = pd.DataFrame()
        else:
            df_indeed = pd.read_csv(indeed_file)
            logger.info(f"✓ Loaded {len(df_indeed)} Indeed jobs")
        
        if not rekrute_file.exists():
            logger.warning(f"ReKrute file not found: {rekrute_file}")
            df_rekrute = pd.DataFrame()
        else:
            df_rekrute = pd.read_csv(rekrute_file)
            logger.info(f"✓ Loaded {len(df_rekrute)} ReKrute jobs")
        
        return df_indeed, df_rekrute
    
    def harmonize_columns(self, df_indeed, df_rekrute):
        """Harmonize columns between Indeed and ReKrute"""
        logger.info("Harmonizing columns...")
        
        # ReKrute columns: job_id, title, company, location, url, description, source, scrape_date
        # Indeed columns: job_id, title, company, location, url, description, publish_date, source, scrape_date
        
        # Add missing publish_date to ReKrute (use scrape_date as fallback)
        if 'publish_date' not in df_rekrute.columns:
            df_rekrute['publish_date'] = df_rekrute.get('scrape_date', None)
        
        # Add missing publish_date to Indeed if needed
        if 'publish_date' not in df_indeed.columns:
            df_indeed['publish_date'] = df_indeed.get('scrape_date', None)
        
        # Standardize column order
        standard_columns = ['job_id', 'title', 'company', 'location', 'url', 
                           'description', 'publish_date', 'source', 'scrape_date']
        
        # Keep only standard columns (that exist)
        df_indeed = df_indeed[[col for col in standard_columns if col in df_indeed.columns]]
        df_rekrute = df_rekrute[[col for col in standard_columns if col in df_rekrute.columns]]
        
        # Combine
        df_combined = pd.concat([df_indeed, df_rekrute], ignore_index=True)
        logger.info(f"✓ Combined: {len(df_combined)} total jobs")
        
        return df_combined
    
    def clean_text(self, text):
        """Clean text: normalize whitespace, encoding"""
        if pd.isna(text) or not isinstance(text, str):
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char == '\n')
        
        return text
    
    def normalize_title(self, title):
        """Normalize job titles (capitalize words, standardize keywords)"""
        if pd.isna(title):
            return ""
        
        title = str(title).strip()
        
        # Standardize common titles
        replacements = {
            r'\bdata scientist\b': 'Data Scientist',
            r'\bdata analyst\b': 'Data Analyst',
            r'\bdata engineer\b': 'Data Engineer',
            r'\bmachine learning\s+engineer\b': 'Machine Learning Engineer',
            r'\bml engineer\b': 'Machine Learning Engineer',
            r'\bai engineer\b': 'AI Engineer',
            r'\bartificial intelligence\s+engineer\b': 'AI Engineer',
        }
        
        normalized = title
        for pattern, replacement in replacements.items():
            normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
        
        # Capitalize each word if no standardization matched
        if normalized == title:
            normalized = ' '.join(word.capitalize() for word in title.split())
        
        return normalized
    
    def remove_duplicates(self, df):
        """Remove duplicate jobs (by URL)"""
        logger.info("Removing duplicates...")
        
        initial_count = len(df)
        
        # Remove rows where URL is duplicated
        df = df.drop_duplicates(subset=['url'], keep='first')
        
        # Remove rows where title + company are duplicated (likely same job)
        df = df.drop_duplicates(subset=['title', 'company'], keep='first')
        
        removed = initial_count - len(df)
        logger.info(f"✓ Removed {removed} duplicates → {len(df)} unique jobs")
        
        return df
    
    def clean_descriptions(self, df):
        """Clean job descriptions"""
        logger.info("Cleaning descriptions...")
        
        df['description'] = df['description'].apply(self.clean_text)
        
        # Truncate to 5000 chars
        df['description'] = df['description'].str[:5000]
        
        logger.info("✓ Descriptions cleaned")
        
        return df
    
    def normalize_titles(self, df):
        """Normalize job titles"""
        logger.info("Normalizing job titles...")
        
        df['title'] = df['title'].apply(self.normalize_title)
        
        logger.info("✓ Titles normalized")
        
        return df
    
    def standardize_companies(self, df):
        """Standardize company names"""
        logger.info("Standardizing company names...")
        
        # Clean company names
        df['company'] = df['company'].apply(lambda x: self.clean_text(x) if isinstance(x, str) else x)
        
        # Replace "Non spécifié" with "Not specified"
        df['company'] = df['company'].replace(['Non spécifié', 'non spécifié', 'N/A', 'nan'], 'Not specified')
        
        logger.info("✓ Company names standardized")
        
        return df
    
    def clean(self):
        """Main cleaning pipeline"""
        logger.info("="*80)
        logger.info("Starting Data Cleaning Pipeline")
        logger.info("="*80)
        
        # Load
        df_indeed, df_rekrute = self.load_data()
        
        if df_indeed.empty and df_rekrute.empty:
            logger.error("No data files found!")
            return None
        
        # Harmonize columns
        self.df_combined = self.harmonize_columns(df_indeed, df_rekrute)
        
        # Clean descriptions
        self.df_combined = self.clean_descriptions(self.df_combined)
        
        # Normalize titles
        self.df_combined = self.normalize_titles(self.df_combined)
        
        # Standardize companies
        self.df_combined = self.standardize_companies(self.df_combined)
        
        # Remove duplicates
        self.df_combined = self.remove_duplicates(self.df_combined)
        
        logger.info("="*80)
        logger.info(f"Cleaning complete! Final count: {len(self.df_combined)} unique jobs")
        logger.info("="*80)
        
        return self.df_combined
    
    def save(self, filename="jobs_cleaned.csv"):
        """Save cleaned data to CSV"""
        if self.df_combined is None:
            logger.error("No data to save. Run clean() first.")
            return
        
        output_path = self.data_dir / filename
        
        logger.info(f"Saving to {output_path}...")
        self.df_combined.to_csv(output_path, index=False)
        logger.info(f"✓ Saved {len(self.df_combined)} jobs to {filename}")
        
        return output_path
    
    def summary(self):
        """Print summary statistics"""
        if self.df_combined is None:
            logger.error("No data to summarize.")
            return
        
        logger.info("\n" + "="*80)
        logger.info("DATA SUMMARY")
        logger.info("="*80)
        
        logger.info(f"Total jobs: {len(self.df_combined)}")
        logger.info(f"By source:")
        logger.info(self.df_combined['source'].value_counts().to_string())
        
        logger.info(f"\nTop 10 companies:")
        logger.info(self.df_combined['company'].value_counts().head(10).to_string())
        
        logger.info(f"\nTop 10 job titles:")
        logger.info(self.df_combined['title'].value_counts().head(10).to_string())
        
        logger.info(f"\nLocations:")
        logger.info(self.df_combined['location'].value_counts().to_string())
        
        logger.info("="*80 + "\n")


if __name__ == "__main__":
    cleaner = DataCleaner()
    
    # Run cleaning pipeline
    cleaner.clean()
    
    # Save cleaned data
    cleaner.save("jobs_cleaned.csv")
    
    # Print summary
    cleaner.summary()
