"""
Skills Extraction Module - NLP-based skill extraction from job descriptions
Uses both rule-based (regex) and semantic methods (Sentence-BERT)
"""

import re
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Set
import logging
from pathlib import Path
import json
from datetime import datetime

try:
    from sentence_transformers import SentenceTransformer, util
    BERT_AVAILABLE = True
except ImportError:
    BERT_AVAILABLE = False
    print("⚠️  sentence-transformers not installed. Will use regex only.")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('skills_extraction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================
# SKILL DEFINITIONS & PATTERNS
# ============================================================

TECH_SKILLS = {
    # Programming Languages
    'python': ['python', 'py3', 'python3'],
    'sql': ['sql', 'tsql', 'plsql', 'mysql', 'postgresql', 'sqlite'],
    'java': ['java(?!script)', r'\bjava\b'],
    'javascript': ['javascript', 'js', 'node.js', 'node', 'typescript', 'ts'],
    'r': [r'\br\b', 'r programming', 'r language'],
    'scala': ['scala'],
    'golang': ['go', 'golang'],
    'rust': ['rust'],
    'cpp': ['c\\+\\+', 'c plus plus'],
    'csharp': ['c#', 'csharp', 'dotnet'],
    'php': ['php'],
    
    # Data & Analytics
    'pandas': ['pandas', 'dataframe'],
    'numpy': ['numpy', 'numerical python'],
    'scikit-learn': ['scikit-learn', 'sklearn'],
    'spark': ['spark', 'pyspark', 'apache spark'],
    'hadoop': ['hadoop'],
    'hive': ['hive', 'apache hive'],
    'pig': ['apache pig', 'pig'],
    'kafka': ['kafka', 'apache kafka'],
    'airflow': ['airflow', 'apache airflow', 'dag'],
    'luigi': ['luigi'],
    'dbt': ['dbt', 'data build tool'],
    'talend': ['talend'],
    'informatica': ['informatica'],
    'ssis': ['ssis', 'sql server integration'],
    'etl': ['etl', 'extract transform load'],
    'elt': ['elt', 'extract load transform'],
    
    # Databases
    'postgresql': ['postgresql', 'postgres', 'psql'],
    'mysql': ['mysql'],
    'mongodb': ['mongodb', 'mongo', 'nosql'],
    'cassandra': ['cassandra', 'apache cassandra'],
    'dynamodb': ['dynamodb'],
    'redis': ['redis'],
    'elasticsearch': ['elasticsearch', 'elastic search'],
    'snowflake': ['snowflake'],
    'redshift': ['redshift', 'amazon redshift'],
    'bigquery': ['bigquery', 'big query'],
    'teradata': ['teradata'],
    'oracle': ['oracle database', 'oracle'],
    'sqlserver': ['sql server', 'mssql'],
    
    # ML & AI
    'tensorflow': ['tensorflow', 'tf'],
    'pytorch': ['pytorch', 'torch'],
    'keras': ['keras'],
    'xgboost': ['xgboost'],
    'lightgbm': ['lightgbm', 'light gbm'],
    'catboost': ['catboost'],
    'mlflow': ['mlflow'],
    'machine_learning': ['machine learning', 'ml\\b', 'machine\\s+learning'],
    'deep_learning': ['deep learning', 'neural network'],
    'nlp': ['nlp', 'natural language processing', 'text mining'],
    'computer_vision': ['computer vision', 'cv\\b', 'image processing'],
    
    # Cloud Platforms
    'aws': ['aws', 'amazon web services', 'ec2', 's3', 'lambda', 'rds'],
    'gcp': ['gcp', 'google cloud', 'bigquery', 'dataflow'],
    'azure': ['azure', 'microsoft azure', 'synapse', 'cosmosdb'],
    'kubernetes': ['kubernetes', 'k8s', 'container'],
    'docker': ['docker', 'containerization'],
    
    # BI & Visualization
    'tableau': ['tableau'],
    'powerbi': ['power bi', 'powerbi', 'power-bi'],
    'qlik': ['qlik', 'qlikview', 'qliktools'],
    'looker': ['looker', 'google looker'],
    'metabase': ['metabase'],
    'grafana': ['grafana'],
    'excel': ['excel', 'vba'],
    'power_pivot': ['power pivot', 'pivot table'],
    
    # Version Control & DevOps
    'git': ['git(?!hub)', r'\bgit\b', 'github', 'gitlab'],
    'jenkins': ['jenkins'],
    'gitlab': ['gitlab'],
    'github': ['github'],
    'terraform': ['terraform'],
    'ansible': ['ansible'],
    'docker': ['docker'],
    'ci_cd': ['ci/cd', 'continuous integration', 'continuous delivery'],
    
    # Other Tools
    'jupyter': ['jupyter', 'jupyter notebook', 'ipython'],
    'sagemaker': ['sagemaker'],
    'dataiku': ['dataiku'],
    'knime': ['knime'],
    'spss': ['spss', 'ibm spss'],
    'sas': ['sas'],
    'apache': ['apache'],
}

# Skills with categories
SKILLS_TAXONOMY = {
    'Programming Languages': ['python', 'sql', 'java', 'javascript', 'r', 'scala', 'golang', 'rust', 'cpp', 'csharp', 'php'],
    'Data Engineering': ['spark', 'hadoop', 'hive', 'kafka', 'airflow', 'luigi', 'dbt', 'etl', 'elt', 'talend', 'informatica', 'ssis'],
    'Databases': ['postgresql', 'mysql', 'mongodb', 'cassandra', 'dynamodb', 'redis', 'elasticsearch', 'snowflake', 'redshift', 'bigquery', 'oracle', 'sqlserver'],
    'Data Analysis': ['pandas', 'numpy', 'scikit-learn', 'excel', 'power_pivot'],
    'Machine Learning': ['tensorflow', 'pytorch', 'keras', 'xgboost', 'lightgbm', 'catboost', 'mlflow', 'machine_learning', 'deep_learning'],
    'NLP & AI': ['nlp', 'computer_vision'],
    'Cloud Platforms': ['aws', 'gcp', 'azure', 'kubernetes', 'docker', 'sagemaker'],
    'BI & Visualization': ['tableau', 'powerbi', 'qlik', 'looker', 'metabase', 'grafana'],
    'DevOps & Tools': ['git', 'jenkins', 'ci_cd', 'terraform', 'ansible', 'jupyter', 'dataiku', 'knime', 'spss', 'sas'],
}

# ============================================================
# SKILL EXTRACTOR CLASS
# ============================================================

class SkillsExtractor:
    def __init__(self, use_bert=True):
        self.skills_dict = TECH_SKILLS
        self.skills_taxonomy = SKILLS_TAXONOMY
        self.use_bert = use_bert and BERT_AVAILABLE
        
        if self.use_bert:
            logger.info("Loading Sentence-BERT model...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self._encode_skills()
        
        logger.info(f"SkillsExtractor initialized | BERT: {self.use_bert} | Skills DB: {len(self.skills_dict)}")
    
    def _encode_skills(self):
        """Pre-encode skill names for similarity search"""
        skill_names = list(self.skills_dict.keys())
        self.skill_embeddings = self.model.encode(skill_names, convert_to_tensor=True)
        self.skill_names = skill_names
    
    def extract_by_regex(self, text: str, min_word_length=2) -> Dict[str, Tuple[float, int]]:
        """Extract skills using regex patterns"""
        text_lower = text.lower()
        found_skills = {}
        
        for skill, patterns in self.skills_dict.items():
            for pattern in patterns:
                matches = list(re.finditer(r'\b' + pattern + r'\b', text_lower, re.IGNORECASE))
                if matches:
                    # Found at least once
                    found_skills[skill] = (1.0, matches[0].start())  # confidence=1.0, position=first match
                    break
        
        return found_skills
    
    def extract_by_bert(self, text: str, threshold=0.5) -> Dict[str, Tuple[float, int]]:
        """Extract skills using semantic similarity (Sentence-BERT)"""
        if not self.use_bert:
            return {}
        
        try:
            # Split text into sentences for context
            sentences = re.split(r'[.!?]+', text)
            found_skills = {}
            
            for sentence in sentences:
                if len(sentence.strip()) < 20:
                    continue
                
                # Encode sentence
                sent_embedding = self.model.encode(sentence, convert_to_tensor=True)
                
                # Compute similarity with all skills
                similarities = util.cos_sim(sent_embedding, self.skill_embeddings)[0]
                
                # Get top matches
                for idx, similarity in enumerate(similarities):
                    score = float(similarity)
                    if score > threshold:
                        skill = self.skill_names[idx]
                        position = text.lower().find(skill)
                        
                        # Keep highest confidence for each skill
                        if skill not in found_skills or score > found_skills[skill][0]:
                            found_skills[skill] = (score, position)
            
            return found_skills
        except Exception as e:
            logger.warning(f"BERT extraction failed: {e}")
            return {}
    
    def extract(self, text: str, method='hybrid') -> Dict[str, Tuple[float, int]]:
        """
        Extract skills from text
        
        Args:
            text: Job description text
            method: 'regex', 'bert', or 'hybrid'
        
        Returns:
            Dict of {skill_name: (confidence_score, position_in_text)}
        """
        if not text:
            return {}
        
        skills = {}
        
        if method in ['regex', 'hybrid']:
            regex_skills = self.extract_by_regex(text)
            skills.update(regex_skills)
        
        if method in ['bert', 'hybrid'] and self.use_bert:
            bert_skills = self.extract_by_bert(text)
            for skill, (score, pos) in bert_skills.items():
                if skill not in skills:
                    skills[skill] = (score, pos)
        
        return skills
    
    def get_skill_category(self, skill: str) -> str:
        """Get category of skill"""
        for category, skills in self.skills_taxonomy.items():
            if skill in skills:
                return category
        return 'Other'
    
    def to_dataframe(self, job_descriptions: pd.DataFrame) -> pd.DataFrame:
        """Convert job descriptions to skills dataset"""
        records = []
        
        for idx, row in job_descriptions.iterrows():
            job_id = row.get('job_id', f'job_{idx}')
            description = row.get('description', '')
            
            if not description:
                continue
            
            # Extract skills
            extracted_skills = self.extract(description, method='hybrid')
            
            for skill, (confidence, position) in extracted_skills.items():
                records.append({
                    'job_id': job_id,
                    'skill_name': skill,
                    'skill_category': self.get_skill_category(skill),
                    'confidence_score': confidence,
                    'position_in_description': position if position >= 0 else -1,
                    'extraction_method': 'bert' if confidence < 1.0 else 'regex'
                })
        
        return pd.DataFrame(records)


# ============================================================
# MAIN EXTRACTION PIPELINE
# ============================================================

def extract_skills_from_cleaned_data(
    input_csv: str = 'data/jobs_cleaned.csv',
    output_csv: str = 'data/jobs_skills.csv',
    method: str = 'hybrid'
) -> pd.DataFrame:
    """
    Main pipeline: Load cleaned jobs and extract skills
    """
    logger.info(f"Starting skills extraction from {input_csv}")
    
    # Load cleaned data
    try:
        df_jobs = pd.read_csv(input_csv)
        logger.info(f"✓ Loaded {len(df_jobs)} jobs from {input_csv}")
    except FileNotFoundError:
        logger.error(f"✗ File not found: {input_csv}")
        return pd.DataFrame()
    
    # Initialize extractor
    extractor = SkillsExtractor(use_bert=BERT_AVAILABLE)
    
    # Extract skills
    logger.info("Extracting skills from descriptions...")
    df_skills = extractor.to_dataframe(df_jobs)
    
    logger.info(f"✓ Extracted {len(df_skills)} skill occurrences")
    logger.info(f"✓ Unique skills found: {df_skills['skill_name'].nunique()}")
    
    # Save output
    df_skills.to_csv(output_csv, index=False)
    logger.info(f"✓ Saved skills to {output_csv}")
    
    # Summary stats
    logger.info("\n" + "="*60)
    logger.info("SKILLS EXTRACTION SUMMARY")
    logger.info("="*60)
    logger.info(f"Total jobs processed: {len(df_jobs)}")
    logger.info(f"Total skills extracted: {len(df_skills)}")
    logger.info(f"Unique skills: {df_skills['skill_name'].nunique()}")
    logger.info(f"Average skills per job: {len(df_skills) / len(df_jobs):.2f}")
    
    # Top skills
    logger.info("\nTOP 20 SKILLS DEMANDED:")
    top_skills = df_skills['skill_name'].value_counts().head(20)
    for skill, count in top_skills.items():
        logger.info(f"  {skill}: {count} occurrences")
    
    # Skills by category
    logger.info("\nSKILLS BY CATEGORY:")
    by_category = df_skills.groupby('skill_category')['skill_name'].nunique().sort_values(ascending=False)
    for category, count in by_category.items():
        logger.info(f"  {category}: {count} unique skills")
    
    logger.info("="*60)
    
    return df_skills


if __name__ == '__main__':
    import os
    os.chdir(Path(__file__).parent.parent.parent)  # Go to project root
    
    df_skills = extract_skills_from_cleaned_data(
        input_csv='data/jobs_cleaned.csv',
        output_csv='data/jobs_skills.csv',
        method='hybrid'
    )
