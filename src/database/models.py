"""
Models ORM SQLAlchemy pour Job Intelligent
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Date, Boolean, DateTime, ForeignKey, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# ============================================================
# DIMENSION TABLES
# ============================================================

class Location(Base):
    __tablename__ = 'dim_locations'
    
    id = Column(Integer, primary_key=True)
    city = Column(String(255), nullable=False)
    country = Column(String(255), nullable=False)
    region = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    jobs = relationship("Job", back_populates="location")
    candidates = relationship("CandidateProfile", back_populates="location")

class Skill(Base):
    __tablename__ = 'dim_skills'
    
    id = Column(Integer, primary_key=True)
    skill_name = Column(String(255), nullable=False, unique=True)
    category = Column(String(100))
    skill_level = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    job_skills = relationship("JobSkill", back_populates="skill")
    candidate_skills = relationship("CandidateSkill", back_populates="skill")

class Company(Base):
    __tablename__ = 'dim_companies'
    
    id = Column(Integer, primary_key=True)
    company_name = Column(String(255), nullable=False, unique=True)
    company_url = Column(String(500))
    company_size = Column(String(50))
    industry = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    jobs = relationship("Job", back_populates="company")

class Source(Base):
    __tablename__ = 'dim_sources'
    
    id = Column(Integer, primary_key=True)
    source_name = Column(String(100), nullable=False, unique=True)
    source_type = Column(String(50))
    base_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    jobs = relationship("Job", back_populates="source")

# ============================================================
# FACT TABLE
# ============================================================

class Job(Base):
    __tablename__ = 'fact_jobs'
    
    id = Column(Integer, primary_key=True)
    job_title = Column(String(255), nullable=False)
    job_description = Column(Text, nullable=False)
    location_id = Column(Integer, ForeignKey('dim_locations.id'))
    company_id = Column(Integer, ForeignKey('dim_companies.id'))
    source_id = Column(Integer, ForeignKey('dim_sources.id'))
    experience_level = Column(String(100))
    contract_type = Column(String(100))
    salary_min = Column(Float)
    salary_max = Column(Float)
    salary_currency = Column(String(10))
    job_url = Column(String(500))
    external_job_id = Column(String(255))
    published_at = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    location = relationship("Location", back_populates="jobs")
    company = relationship("Company", back_populates="jobs")
    source = relationship("Source", back_populates="jobs")
    job_skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")
    embedding = relationship("JobEmbedding", back_populates="job", uselist=False, cascade="all, delete-orphan")
    recommendations = relationship("JobRecommendation", back_populates="job")

# ============================================================
# ASSOCIATION TABLES
# ============================================================

class JobSkill(Base):
    __tablename__ = 'job_skills'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('fact_jobs.id'), nullable=False)
    skill_id = Column(Integer, ForeignKey('dim_skills.id'), nullable=False)
    required = Column(Boolean, default=True)
    proficiency_level = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    job = relationship("Job", back_populates="job_skills")
    skill = relationship("Skill", back_populates="job_skills")

class JobEmbedding(Base):
    __tablename__ = 'job_embeddings'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('fact_jobs.id'), nullable=False, unique=True)
    description_embedding = Column(ARRAY(Float))
    title_embedding = Column(ARRAY(Float))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    job = relationship("Job", back_populates="embedding")

# ============================================================
# CANDIDATE PROFILE
# ============================================================

class CandidateProfile(Base):
    __tablename__ = 'candidate_profiles'
    
    id = Column(Integer, primary_key=True)
    candidate_name = Column(String(255))
    target_job_title = Column(String(255))
    location_id = Column(Integer, ForeignKey('dim_locations.id'))
    years_experience = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    location = relationship("Location", back_populates="candidates")
    skills = relationship("CandidateSkill", back_populates="candidate", cascade="all, delete-orphan")
    recommendations = relationship("JobRecommendation", back_populates="candidate")

class CandidateSkill(Base):
    __tablename__ = 'candidate_skills'
    
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidate_profiles.id'), nullable=False)
    skill_id = Column(Integer, ForeignKey('dim_skills.id'), nullable=False)
    proficiency_level = Column(String(50))
    years_of_experience = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    candidate = relationship("CandidateProfile", back_populates="skills")
    skill = relationship("Skill", back_populates="candidate_skills")

# ============================================================
# RECOMMENDATIONS
# ============================================================

class JobRecommendation(Base):
    __tablename__ = 'job_recommendations'
    
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidate_profiles.id'), nullable=False)
    job_id = Column(Integer, ForeignKey('fact_jobs.id'), nullable=False)
    match_score = Column(Float, nullable=False)
    semantic_similarity = Column(Float)
    skills_match_percentage = Column(Float)
    location_match = Column(Boolean)
    matched_skills = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    candidate = relationship("CandidateProfile", back_populates="recommendations")
    job = relationship("Job", back_populates="recommendations")

# ============================================================
# LOGS
# ============================================================

class IngestionLog(Base):
    __tablename__ = 'ingestion_logs'
    
    id = Column(Integer, primary_key=True)
    source_name = Column(String(100))
    status = Column(String(50))
    jobs_count = Column(Integer)
    errors_count = Column(Integer)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
