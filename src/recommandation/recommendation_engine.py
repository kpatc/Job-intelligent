"""
Job Recommendation System - Phase 4
Semantic similarity matching + Skills matching
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
import logging
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# RECOMMENDATION SYSTEM
# ============================================================

class JobRecommendationEngine:
    """
    Recommends jobs based on:
    1. Semantic similarity (using Sentence-BERT)
    2. Skill matching
    3. Confidence scoring
    """
    
    def __init__(self):
        """Initialize recommendation engine"""
        logger.info("Initializing JobRecommendationEngine...")
        
        # Load pre-trained sentence embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Will be populated when load_jobs() is called
        self.jobs_df = None
        self.job_embeddings = None
        self.job_ids = None
        
        logger.info("✓ Recommendation engine initialized")
    
    def load_jobs(self, jobs_csv_path: str):
        """Load jobs from CSV and pre-compute embeddings"""
        logger.info(f"Loading jobs from {jobs_csv_path}...")
        
        self.jobs_df = pd.read_csv(jobs_csv_path)
        logger.info(f"✓ Loaded {len(self.jobs_df)} jobs")
        
        # Pre-compute embeddings for job descriptions
        logger.info("Computing embeddings for job descriptions...")
        descriptions = self.jobs_df['description'].fillna('').tolist()
        self.job_embeddings = self.embedding_model.encode(descriptions, show_progress_bar=True)
        self.job_ids = self.jobs_df['job_id'].tolist()
        
        logger.info(f"✓ Computed {len(self.job_embeddings)} embeddings")
    
    def recommend_by_profile(
        self,
        candidate_skills: List[str],
        candidate_experience: str = "",
        candidate_interests: str = "",
        top_k: int = 10,
        min_skill_match: float = 0.3
    ) -> pd.DataFrame:
        """
        Recommend jobs based on candidate profile.
        
        Args:
            candidate_skills: List of skills (e.g., ['Python', 'SQL', 'Machine Learning'])
            candidate_experience: Description of experience (optional)
            candidate_interests: Job interests/preferences (optional)
            top_k: Number of top recommendations to return
            min_skill_match: Minimum % of skills to match (0.3 = 30%)
        
        Returns:
            DataFrame with recommended jobs and scores
        """
        if self.jobs_df is None:
            raise ValueError("Jobs not loaded. Call load_jobs() first.")
        
        logger.info(f"\n{'='*70}")
        logger.info(f"GENERATING RECOMMENDATIONS FOR CANDIDATE")
        logger.info(f"{'='*70}")
        logger.info(f"Skills: {', '.join(candidate_skills)}")
        logger.info(f"Experience: {candidate_experience[:100] if candidate_experience else 'Not provided'}...")
        logger.info(f"Interests: {candidate_interests[:100] if candidate_interests else 'Not provided'}...")
        
        # ========== SKILL MATCHING SCORE ==========
        logger.info("\n1️⃣  Computing skill matching scores...")
        skill_scores = self._compute_skill_scores(candidate_skills, min_skill_match)
        
        # ========== SEMANTIC SIMILARITY SCORE ==========
        logger.info("2️⃣  Computing semantic similarity scores...")
        profile_text = f"{' '.join(candidate_skills)} {candidate_experience} {candidate_interests}"
        profile_embedding = self.embedding_model.encode(profile_text)
        semantic_scores = self._compute_semantic_scores(profile_embedding)
        
        # ========== COMBINED SCORING ==========
        logger.info("3️⃣  Computing combined recommendation scores...")
        combined_scores = self._compute_combined_scores(skill_scores, semantic_scores)
        
        # ========== BUILD RECOMMENDATIONS DATAFRAME ==========
        logger.info("4️⃣  Building recommendations...")
        recommendations = pd.DataFrame({
            'job_id': self.job_ids,
            'title': self.jobs_df['title'].values,
            'company': self.jobs_df['company'].values,
            'location': self.jobs_df['location'].values,
            'source': self.jobs_df['source'].values,
            'skill_match_score': skill_scores,
            'semantic_similarity_score': semantic_scores,
            'combined_score': combined_scores
        })
        
        # Filter out jobs with very low scores
        recommendations = recommendations[recommendations['combined_score'] > 0.1]
        
        # Sort by combined score
        recommendations = recommendations.sort_values('combined_score', ascending=False).head(top_k)
        
        logger.info(f"\n✓ Generated {len(recommendations)} recommendations\n")
        
        return recommendations
    
    def _compute_skill_scores(self, candidate_skills: List[str], min_match: float) -> np.ndarray:
        """Compute skill matching scores for each job"""
        
        candidate_skills_lower = [s.lower() for s in candidate_skills]
        skill_scores = np.zeros(len(self.jobs_df))
        
        for idx, description in enumerate(self.jobs_df['description'].fillna('')):
            description_lower = description.lower()
            
            # Count matching skills
            matched_skills = sum(1 for skill in candidate_skills_lower if skill in description_lower)
            match_ratio = matched_skills / len(candidate_skills) if candidate_skills else 0
            
            # Only score if minimum threshold met
            if match_ratio >= min_match:
                skill_scores[idx] = match_ratio
        
        return skill_scores
    
    def _compute_semantic_scores(self, profile_embedding: np.ndarray) -> np.ndarray:
        """Compute semantic similarity scores using embeddings"""
        
        # Compute cosine similarity between profile and all jobs
        similarities = cosine_similarity([profile_embedding], self.job_embeddings)[0]
        
        # Normalize to 0-1 range
        similarities = (similarities + 1) / 2  # Convert from [-1, 1] to [0, 1]
        
        return similarities
    
    def _compute_combined_scores(
        self,
        skill_scores: np.ndarray,
        semantic_scores: np.ndarray,
        skill_weight: float = 0.6,
        semantic_weight: float = 0.4
    ) -> np.ndarray:
        """
        Combine skill and semantic scores with weights.
        Skills are weighted more heavily (60%) as they're more explicit.
        """
        
        # Normalize skill scores to 0-1 range
        if np.max(skill_scores) > 0:
            skill_scores_norm = skill_scores / np.max(skill_scores)
        else:
            skill_scores_norm = skill_scores
        
        # Combine with weights
        combined = (skill_weight * skill_scores_norm) + (semantic_weight * semantic_scores)
        
        return combined
    
    def get_job_details(self, job_id: str) -> Dict:
        """Get full details for a specific job"""
        job = self.jobs_df[self.jobs_df['job_id'] == job_id]
        
        if job.empty:
            return None
        
        job_dict = job.iloc[0].to_dict()
        
        return {
            'job_id': job_dict['job_id'],
            'title': job_dict['title'],
            'company': job_dict['company'],
            'location': job_dict['location'],
            'description': job_dict['description'],
            'url': job_dict['url'],
            'source': job_dict['source'],
            'publish_date': job_dict['publish_date'],
            'scrape_date': job_dict['scrape_date']
        }


# ============================================================
# PROFILE MATCHER
# ============================================================

class CandidateProfileMatcher:
    """
    Matches candidate profiles to job opportunities.
    """
    
    def __init__(self, recommendation_engine: JobRecommendationEngine):
        self.engine = recommendation_engine
    
    def match_candidates_to_jobs(self, candidates: List[Dict]) -> pd.DataFrame:
        """
        Match multiple candidates to jobs.
        
        Args:
            candidates: List of candidate dicts with 'name', 'skills', 'experience'
        
        Returns:
            DataFrame with top matches per candidate
        """
        
        results = []
        
        for candidate in candidates:
            logger.info(f"\nMatching: {candidate['name']}")
            
            recommendations = self.engine.recommend_by_profile(
                candidate_skills=candidate.get('skills', []),
                candidate_experience=candidate.get('experience', ''),
                candidate_interests=candidate.get('interests', ''),
                top_k=5
            )
            
            recommendations['candidate_name'] = candidate['name']
            results.append(recommendations)
        
        return pd.concat(results, ignore_index=True) if results else pd.DataFrame()


# ============================================================
# EXAMPLE USAGE
# ============================================================

def example_recommendation():
    """Example: Get job recommendations for a candidate"""
    
    # Initialize engine
    engine = JobRecommendationEngine()
    engine.load_jobs('/home/josh/PowerBi/job-intelligent/data/jobs_cleaned.csv')
    
    # Example candidate profile
    candidate_skills = [
        'Python',
        'SQL',
        'Machine Learning',
        'Data Analysis',
        'TensorFlow',
        'Pandas'
    ]
    
    candidate_experience = """
    5 years of data science experience.
    Built ML pipelines for predictive analytics.
    Experience with cloud platforms (AWS, GCP).
    """
    
    candidate_interests = "Data science, ML engineering, AI"
    
    # Get recommendations
    recommendations = engine.recommend_by_profile(
        candidate_skills=candidate_skills,
        candidate_experience=candidate_experience,
        candidate_interests=candidate_interests,
        top_k=10,
        min_skill_match=0.3
    )
    
    # Display results
    print("\n" + "="*70)
    print("TOP JOB RECOMMENDATIONS")
    print("="*70)
    
    for idx, row in recommendations.iterrows():
        print(f"\n{idx + 1}. {row['title']}")
        print(f"   Company: {row['company']}")
        print(f"   Location: {row['location']}")
        print(f"   Source: {row['source']}")
        print(f"   Skill Match: {row['skill_match_score']:.1%}")
        print(f"   Semantic Match: {row['semantic_similarity_score']:.3f}")
        print(f"   FINAL SCORE: {row['combined_score']:.3f}")
    
    return recommendations


if __name__ == '__main__':
    recommendations = example_recommendation()
    recommendations.to_csv(
        '/home/josh/PowerBi/job-intelligent/data/candidate_recommendations.csv',
        index=False
    )
    logger.info("✓ Recommendations saved to candidate_recommendations.csv")
