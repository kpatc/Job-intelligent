
-- Database
CREATE DATABASE IF NOT EXISTS job_intelligent;
USE DATABASE job_intelligent;
-- DIMENSION TABLES

-- DIM_COMPANIES
CREATE TABLE IF NOT EXISTS dim_companies (
    company_id INT AUTOINCREMENT PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL UNIQUE,
    industry VARCHAR(100),
    country VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DIM_LOCATIONS
CREATE TABLE IF NOT EXISTS dim_locations (
    location_id INT AUTOINCREMENT PRIMARY KEY,
    location_name VARCHAR(255) NOT NULL UNIQUE,
    country VARCHAR(100),
    region VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DIM_SKILLS
CREATE TABLE IF NOT EXISTS dim_skills (
    skill_id INT AUTOINCREMENT PRIMARY KEY,
    skill_name VARCHAR(100) NOT NULL UNIQUE,
    skill_category VARCHAR(50),  -- e.g., 'Programming', 'Data', 'Cloud', 'Tools'
    skill_level VARCHAR(50),      -- e.g., 'Junior', 'Mid', 'Senior'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DIM_TIME (for temporal analysis)
CREATE TABLE IF NOT EXISTS dim_time (
    date_id INT PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    year INT,
    month INT,
    day INT,
    quarter INT,
    week INT,
    day_of_week INT
);

-- FACT TABLES

-- FACT_JOBS (Main fact table)
CREATE TABLE IF NOT EXISTS fact_jobs (
    job_id VARCHAR(50) PRIMARY KEY,
    company_id INT NOT NULL,
    location_id INT NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    job_title_normalized VARCHAR(255),  -- Normalized title
    description TEXT,
    description_length INT,
    publish_date DATE,
    publish_date_id INT,
    scrape_date TIMESTAMP,
    source VARCHAR(50),  -- 'indeed' or 'rekrute'
    url VARCHAR(512),
    job_posting_days_old INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES dim_companies(company_id),
    FOREIGN KEY (location_id) REFERENCES dim_locations(location_id),
    FOREIGN KEY (publish_date_id) REFERENCES dim_time(date_id)
);

-- FACT_JOB_SKILLS (Bridge table: Jobs ↔ Skills)
CREATE TABLE IF NOT EXISTS fact_job_skills (
    job_skill_id INT AUTOINCREMENT PRIMARY KEY,
    job_id VARCHAR(50) NOT NULL,
    skill_id INT NOT NULL,
    mentioned_count INT DEFAULT 1,
    extracted_method VARCHAR(50),  -- 'NLP' or 'regex' or 'manual'
    confidence_score FLOAT,        -- 0-1 for NLP confidence
    position_in_description INT,   -- First mention position
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES fact_jobs(job_id),
    FOREIGN KEY (skill_id) REFERENCES dim_skills(skill_id),
    UNIQUE (job_id, skill_id)
);

-- ============================================================
-- AGGREGATION VIEWS (for BI optimization)
-- ============================================================

-- VW_JOB_SKILLS_AGGREGATED: Skills demand by job
CREATE OR REPLACE VIEW vw_job_skills_aggregated AS
SELECT 
    j.job_id,
    j.job_title_normalized,
    j.company_id,
    j.location_id,
    COUNT(DISTINCT js.skill_id) as total_skills_required,
    LISTAGG(DISTINCT s.skill_name, ', ') WITHIN GROUP (ORDER BY s.skill_name) as required_skills,
    AVG(js.confidence_score) as avg_confidence
FROM fact_jobs j
LEFT JOIN fact_job_skills js ON j.job_id = js.job_id
LEFT JOIN dim_skills s ON js.skill_id = s.skill_id
GROUP BY j.job_id, j.job_title_normalized, j.company_id, j.location_id;

-- VW_SKILLS_DEMAND: Most demanded skills
CREATE OR REPLACE VIEW vw_skills_demand AS
SELECT 
    s.skill_id,
    s.skill_name,
    s.skill_category,
    COUNT(DISTINCT js.job_id) as job_count,
    AVG(js.confidence_score) as avg_confidence,
    ROUND(100.0 * COUNT(DISTINCT js.job_id) / 
        (SELECT COUNT(DISTINCT job_id) FROM fact_jobs), 2) as demand_percentage
FROM dim_skills s
LEFT JOIN fact_job_skills js ON s.skill_id = js.skill_id
GROUP BY s.skill_id, s.skill_name, s.skill_category
ORDER BY job_count DESC;

-- VW_JOBS_BY_TITLE: Job distribution by normalized title
CREATE OR REPLACE VIEW vw_jobs_by_title AS
SELECT 
    job_title_normalized,
    source,
    COUNT(*) as job_count,
    COUNT(DISTINCT company_id) as unique_companies,
    COUNT(DISTINCT location_id) as unique_locations,
    MIN(publish_date) as earliest_posting,
    MAX(publish_date) as latest_posting
FROM fact_jobs
GROUP BY job_title_normalized, source
ORDER BY job_count DESC;

-- VW_MARKET_OVERVIEW: Key metrics
CREATE OR REPLACE VIEW vw_market_overview AS
SELECT 
    COUNT(DISTINCT job_id) as total_jobs,
    COUNT(DISTINCT company_id) as unique_companies,
    COUNT(DISTINCT location_id) as unique_locations,
    COUNT(DISTINCT skill_id) as unique_skills,
    AVG(job_posting_days_old) as avg_posting_age_days,
    MAX(scrape_date) as last_scrape_date
FROM fact_jobs
CROSS JOIN dim_skills;

-- ============================================================
-- INDEXES for Performance
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_jobs_company ON fact_jobs(company_id);
CREATE INDEX IF NOT EXISTS idx_jobs_location ON fact_jobs(location_id);
CREATE INDEX IF NOT EXISTS idx_jobs_source ON fact_jobs(source);
CREATE INDEX IF NOT EXISTS idx_jobs_date ON fact_jobs(publish_date);
CREATE INDEX IF NOT EXISTS idx_job_skills_skill ON fact_job_skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_job_skills_job ON fact_job_skills(job_id);
CREATE INDEX IF NOT EXISTS idx_skills_category ON dim_skills(skill_category);

-- ============================================================
-- COMMENTS
-- ============================================================

COMMENT ON TABLE fact_jobs IS 'Central fact table containing all job postings';
COMMENT ON TABLE fact_job_skills IS 'Bridge table linking jobs to required skills';
COMMENT ON TABLE dim_skills IS 'Dimension: All skills extracted from job descriptions';
COMMENT ON COLUMN fact_job_skills.confidence_score IS 'NLP confidence (0-1): how confident we are about the skill extraction';
