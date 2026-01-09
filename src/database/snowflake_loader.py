"""
Snowflake Loader - Load cleaned jobs and extracted skills into Snowflake
Handles table creation and data loading
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime, date
import os
import sys

# Load .env file first
try:
    from dotenv import load_dotenv
    PROJECT_ROOT = Path(__file__).parent.parent.parent  # job-intelligent/
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        load_dotenv(env_file, override=True)
except ImportError:
    pass

# Snowflake connector
try:
    from snowflake.connector import connect
    from snowflake.connector.pandas_tools import write_pandas
    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False
    print("⚠️  snowflake-connector-python not installed. Install with: pip install snowflake-connector-python")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('snowflake_loader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================
# SNOWFLAKE CONFIG - Load from environment
# ============================================================

SNOWFLAKE_CONFIG = {
    'user': os.getenv('SNOWFLAKE_USER'),
    'password': os.getenv('SNOWFLAKE_PASSWORD'),
    'account': os.getenv('SNOWFLAKE_ACCOUNT'),
    'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
    'database': os.getenv('SNOWFLAKE_DATABASE', 'JOB_INTELLIGENT'),
    'schema': os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC'),
    'role': os.getenv('SNOWFLAKE_ROLE', 'ACCOUNTADMIN'),
}

# ============================================================
# SNOWFLAKE LOADER CLASS
# ============================================================

class SnowflakeLoader:
    def __init__(self, config: Dict = None):
        if not SNOWFLAKE_AVAILABLE:
            logger.error("Snowflake connector not available")
            raise ImportError("snowflake-connector-python required")
        
        self.config = config or SNOWFLAKE_CONFIG
        self.conn = None
        self.cursor = None
        
        # Validate config
        if not all([self.config.get('user'), self.config.get('password'), self.config.get('account')]):
            raise ValueError("Missing Snowflake credentials. Set SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_ACCOUNT env vars")
    
    def connect(self):
        """Connect to Snowflake"""
        try:
            self.conn = connect(
                user=self.config['user'],
                password=self.config['password'],
                account=self.config['account'],
                warehouse=self.config['warehouse'],
                database=self.config['database'],
                schema=self.config['schema'],
                role=self.config['role'],
            )
            self.cursor = self.conn.cursor()
            logger.info(f"✓ Connected to Snowflake ({self.config['account']})")
            return True
        except Exception as e:
            logger.error(f"✗ Snowflake connection failed: {e}")
            return False
    
    def execute_sql(self, sql: str, params=None):
        """Execute SQL statement and return results as DataFrame"""
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            
            # Try to fetch results if SELECT query
            if sql.strip().upper().startswith('SELECT'):
                results = self.cursor.fetchall()
                columns = [desc[0] for desc in self.cursor.description]
                df = pd.DataFrame(results, columns=columns)
                logger.debug(f"✓ Query returned {len(df)} rows")
                return df
            else:
                logger.debug(f"✓ Executed: {sql[:100]}...")
                return True
        except Exception as e:
            logger.error(f"✗ SQL execution failed: {e}")
            return None
    
    def load_data(self, df: pd.DataFrame, table_name: str, if_exists='append') -> bool:
        """Load DataFrame to Snowflake table"""
        try:
            result = write_pandas(
                self.conn,
                df,
                table_name.upper()
            )
            
            # write_pandas returns: (success, nrows, nchunks)
            if isinstance(result, tuple) and len(result) == 3:
                success, nrows, nchunks = result
                if success:
                    logger.info(f"✓ Loaded {nrows} rows to {table_name}")
                    return True
                else:
                    logger.warning(f"⚠️  Partial load to {table_name} ({nrows} rows)")
                    return True
            else:
                logger.warning(f"⚠️  Unexpected return from write_pandas: {result}")
                return True
        except Exception as e:
            logger.error(f"✗ Failed to load {table_name}: {e}")
            return False
    
    def close(self):
        """Close connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Connection closed")

# ============================================================
# DATA PREPARATION FUNCTIONS
# ============================================================

def prepare_jobs_data(df: pd.DataFrame, company_map: Dict, location_map: Dict) -> pd.DataFrame:
    """
    Prepare jobs data for Snowflake loading.
    Maps company names and locations to their IDs.
    """
    df_prep = df.copy()
    
    # Handle missing values
    df_prep['description'] = df_prep['description'].fillna('')
    df_prep['company'] = df_prep['company'].fillna('Unknown')
    df_prep['location'] = df_prep['location'].fillna('Unknown')
    
    # Map company names to company_ids
    df_prep['COMPANY_ID'] = df_prep['company'].map(company_map)
    
    # Map locations to location_ids
    df_prep['LOCATION_ID'] = df_prep['location'].map(location_map)
    
    # Add computed fields
    df_prep['DESCRIPTION_LENGTH'] = df_prep['description'].str.len()
    df_prep['JOB_TITLE_NORMALIZED'] = df_prep['title'].str.lower().str.strip()
    
    # Parse dates (keep as datetime for computation)
    df_prep['PUBLISH_DATE'] = pd.to_datetime(df_prep['publish_date'], format='mixed', errors='coerce')
    df_prep['SCRAPE_DATE'] = pd.to_datetime(df_prep['scrape_date'], format='mixed', errors='coerce')
    
    # Compute days old BEFORE converting to string
    df_prep['JOB_POSTING_DAYS_OLD'] = (datetime.now() - df_prep['PUBLISH_DATE']).dt.days
    
    # Convert dates to string format (YYYY-MM-DD) for Snowflake
    df_prep['PUBLISH_DATE_STR'] = df_prep['PUBLISH_DATE'].dt.strftime('%Y-%m-%d')
    df_prep['SCRAPE_DATE_STR'] = df_prep['SCRAPE_DATE'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Select and rename columns for Snowflake (UPPERCASE)
    df_final = pd.DataFrame({
        'JOB_ID': df_prep['job_id'],
        'COMPANY_ID': df_prep['COMPANY_ID'],
        'LOCATION_ID': df_prep['LOCATION_ID'],
        'JOB_TITLE': df_prep['title'],
        'JOB_TITLE_NORMALIZED': df_prep['JOB_TITLE_NORMALIZED'],
        'DESCRIPTION': df_prep['description'],
        'DESCRIPTION_LENGTH': df_prep['DESCRIPTION_LENGTH'],
        'PUBLISH_DATE': df_prep['PUBLISH_DATE_STR'],
        'SCRAPE_DATE': df_prep['SCRAPE_DATE_STR'],
        'SOURCE': df_prep['source'],
        'URL': df_prep['url'],
        'JOB_POSTING_DAYS_OLD': df_prep['JOB_POSTING_DAYS_OLD']
    })
    
    return df_final


def prepare_skills_data(df_skills: pd.DataFrame, skill_map: Dict) -> pd.DataFrame:
    """
    Prepare job-skills data for Snowflake loading.
    Maps skill names to skill_ids.
    """
    df_prep = df_skills.copy()
    
    # Map skill names to skill_ids
    df_prep['SKILL_ID'] = df_prep['skill_name'].map(skill_map)
    
    # Ensure confidence_score is float
    df_prep['CONFIDENCE_SCORE'] = pd.to_numeric(df_prep['confidence_score'], errors='coerce').fillna(0.5)
    
    # Ensure position is int
    df_prep['POSITION_IN_DESCRIPTION'] = pd.to_numeric(df_prep['position_in_description'], errors='coerce').fillna(-1).astype(int)
    
    # Create final dataframe with Snowflake column names
    df_final = pd.DataFrame({
        'JOB_ID': df_prep['job_id'],
        'SKILL_ID': df_prep['SKILL_ID'],
        'MENTIONED_COUNT': 1,
        'EXTRACTED_METHOD': df_prep['extraction_method'],
        'CONFIDENCE_SCORE': df_prep['CONFIDENCE_SCORE'],
        'POSITION_IN_DESCRIPTION': df_prep['POSITION_IN_DESCRIPTION']
    })
    
    return df_final


def extract_unique_companies(df: pd.DataFrame) -> pd.DataFrame:
    """Extract unique companies"""
    companies = df[['company']].drop_duplicates()
    companies = companies.rename(columns={'company': 'COMPANY_NAME'})
    companies['COMPANY_NAME'] = companies['COMPANY_NAME'].str.strip()
    companies = companies[companies['COMPANY_NAME'] != 'Unknown']
    return companies.reset_index(drop=True)


def extract_unique_locations(df: pd.DataFrame) -> pd.DataFrame:
    """Extract unique locations"""
    locations = df[['location']].drop_duplicates()
    locations = locations.rename(columns={'location': 'LOCATION_NAME'})
    locations['LOCATION_NAME'] = locations['LOCATION_NAME'].str.strip()
    return locations.reset_index(drop=True)


def extract_unique_skills(df_skills: pd.DataFrame) -> pd.DataFrame:
    """Extract unique skills with categories"""
    skills = df_skills[['skill_name', 'skill_category']].drop_duplicates()
    skills = skills.sort_values('skill_name').reset_index(drop=True)
    # Rename to Snowflake column names
    skills.columns = ['SKILL_NAME', 'SKILL_CATEGORY']
    return skills

# ============================================================
# MAIN LOADING PIPELINE
# ============================================================

def load_to_snowflake(
    jobs_csv: str = 'data/jobs_cleaned.csv',
    skills_csv: str = 'data/jobs_skills.csv',
    config: Dict = None,
    dry_run: bool = False
):
    """
    Main pipeline: Load jobs and skills to Snowflake in correct order.
    
    LOADING ORDER (with dependencies):
    1. DIM_COMPANIES (extracts company names → Snowflake auto-generates COMPANY_ID)
    2. DIM_LOCATIONS (extracts locations → Snowflake auto-generates LOCATION_ID)
    3. DIM_SKILLS (extracts skills → Snowflake auto-generates SKILL_ID)
    4. FACT_JOBS (uses COMPANY_ID and LOCATION_ID from step 1,2)
    5. FACT_JOB_SKILLS (uses SKILL_ID from step 3)
    """
    logger.info("="*70)
    logger.info("SNOWFLAKE LOADING PIPELINE - STARTING")
    logger.info("="*70)
    
    if not SNOWFLAKE_AVAILABLE:
        logger.error("Snowflake connector not available. Install with:")
        logger.error("  pip install 'snowflake-connector-python[pandas]'")
        return False
    
    if dry_run:
        logger.info("🔍 DRY RUN MODE - No data will be written to Snowflake\n")
    
    # ========== LOAD CSV DATA ==========
    try:
        logger.info(f"1️⃣  Loading CSV files...")
        df_jobs = pd.read_csv(jobs_csv)
        logger.info(f"   ✓ {jobs_csv}: {len(df_jobs)} jobs")
        
        df_skills = pd.read_csv(skills_csv)
        logger.info(f"   ✓ {skills_csv}: {len(df_skills)} skill entries\n")
    except FileNotFoundError as e:
        logger.error(f"✗ File not found: {e}")
        return False
    
    # Connect to Snowflake
    loader = SnowflakeLoader(config)
    if not loader.connect():
        logger.error("Failed to connect to Snowflake")
        return False
    
    try:
        if dry_run:
            logger.info("✓ Dry run validation passed")
            return True
        
        # ========== STEP 1: LOAD DIM_COMPANIES ==========
        logger.info("2️⃣  Loading DIM_COMPANIES...")
        df_companies = extract_unique_companies(df_jobs)
        logger.info(f"   Found {len(df_companies)} unique companies")
        
        if not loader.load_data(df_companies, 'DIM_COMPANIES', if_exists='append'):
            logger.error("Failed to load DIM_COMPANIES")
            return False
        logger.info("   ✓ DIM_COMPANIES loaded\n")
        
        # ========== STEP 2: LOAD DIM_LOCATIONS ==========
        logger.info("3️⃣  Loading DIM_LOCATIONS...")
        df_locations = extract_unique_locations(df_jobs)
        logger.info(f"   Found {len(df_locations)} unique locations")
        
        if not loader.load_data(df_locations, 'DIM_LOCATIONS', if_exists='append'):
            logger.error("Failed to load DIM_LOCATIONS")
            return False
        logger.info("   ✓ DIM_LOCATIONS loaded\n")
        
        # ========== STEP 3: LOAD DIM_SKILLS ==========
        logger.info("4️⃣  Loading DIM_SKILLS...")
        df_unique_skills = extract_unique_skills(df_skills)
        logger.info(f"   Found {len(df_unique_skills)} unique skills")
        
        if not loader.load_data(df_unique_skills, 'DIM_SKILLS', if_exists='append'):
            logger.error("Failed to load DIM_SKILLS")
            return False
        logger.info("   ✓ DIM_SKILLS loaded\n")
        
        # ========== GET ID MAPPINGS FROM SNOWFLAKE ==========
        logger.info("5️⃣  Querying ID mappings from Snowflake...")
        
        # Get company_id mappings
        company_map_df = loader.execute_sql("SELECT COMPANY_NAME, COMPANY_ID FROM DIM_COMPANIES")
        if company_map_df is None or company_map_df.empty:
            logger.error("Failed to retrieve company IDs")
            return False
        company_map = dict(zip(company_map_df['COMPANY_NAME'], company_map_df['COMPANY_ID']))
        logger.info(f"   ✓ Company mapping: {len(company_map)} entries")
        
        # Get location_id mappings
        location_map_df = loader.execute_sql("SELECT LOCATION_NAME, LOCATION_ID FROM DIM_LOCATIONS")
        if location_map_df is None or location_map_df.empty:
            logger.error("Failed to retrieve location IDs")
            return False
        location_map = dict(zip(location_map_df['LOCATION_NAME'], location_map_df['LOCATION_ID']))
        logger.info(f"   ✓ Location mapping: {len(location_map)} entries")
        
        # Get skill_id mappings
        skill_map_df = loader.execute_sql("SELECT SKILL_NAME, SKILL_ID FROM DIM_SKILLS")
        if skill_map_df is None or skill_map_df.empty:
            logger.error("Failed to retrieve skill IDs")
            return False
        skill_map = dict(zip(skill_map_df['SKILL_NAME'], skill_map_df['SKILL_ID']))
        logger.info(f"   ✓ Skill mapping: {len(skill_map)} entries\n")
        
        # ========== STEP 4: LOAD FACT_JOBS ==========
        logger.info("6️⃣  Loading FACT_JOBS...")
        df_jobs_prep = prepare_jobs_data(df_jobs, company_map, location_map)
        logger.info(f"   Prepared {len(df_jobs_prep)} jobs with company/location IDs")
        
        if not loader.load_data(df_jobs_prep, 'FACT_JOBS', if_exists='append'):
            logger.error("Failed to load FACT_JOBS")
            return False
        logger.info("   ✓ FACT_JOBS loaded\n")
        
        # ========== STEP 5: LOAD FACT_JOB_SKILLS ==========
        logger.info("7️⃣  Loading FACT_JOB_SKILLS...")
        df_skills_prep = prepare_skills_data(df_skills, skill_map)
        logger.info(f"   Prepared {len(df_skills_prep)} job-skill relationships with skill IDs")
        
        if not loader.load_data(df_skills_prep, 'FACT_JOB_SKILLS', if_exists='append'):
            logger.error("Failed to load FACT_JOB_SKILLS")
            return False
        logger.info("   ✓ FACT_JOB_SKILLS loaded\n")
        
        # ========== VERIFY LOADING ==========
        logger.info("8️⃣  Verifying data loaded to Snowflake...")
        
        tables_to_verify = ['DIM_COMPANIES', 'DIM_LOCATIONS', 'DIM_SKILLS', 'FACT_JOBS', 'FACT_JOB_SKILLS']
        for table_name in tables_to_verify:
            result = loader.execute_sql(f"SELECT COUNT(*) as CNT FROM {table_name}")
            if result is not None and not result.empty:
                count = result['CNT'].iloc[0]
                logger.info(f"   ✓ {table_name}: {count} rows")
            else:
                logger.warning(f"   ⚠️  Could not verify {table_name}")
        
        # ========== SUCCESS ==========
        logger.info("\n" + "="*70)
        logger.info("✅ DATA LOADING COMPLETED SUCCESSFULLY!")
        logger.info("="*70)
        logger.info(f"Summary:")
        logger.info(f"  • Companies: {len(df_companies)}")
        logger.info(f"  • Locations: {len(df_locations)}")
        logger.info(f"  • Skills: {len(df_unique_skills)}")
        logger.info(f"  • Jobs: {len(df_jobs_prep)}")
        logger.info(f"  • Job-Skill Links: {len(df_skills_prep)}")
        logger.info("="*70 + "\n")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Fatal error during loading: {e}", exc_info=True)
        return False
    
    finally:
        loader.close()


# ============================================================
# SETUP INSTRUCTIONS
# ============================================================

def print_setup_instructions():
    """Print setup instructions for Snowflake"""
    instructions = """
╔════════════════════════════════════════════════════════════════════╗
║         SNOWFLAKE SETUP INSTRUCTIONS                              ║
╚════════════════════════════════════════════════════════════════════╝

1. INSTALL SNOWFLAKE CONNECTOR:
   pip install snowflake-connector-python

2. SET ENVIRONMENT VARIABLES:
   export SNOWFLAKE_USER="your_username"
   export SNOWFLAKE_PASSWORD="your_password"
   export SNOWFLAKE_ACCOUNT="xy12345.us-east-1"  # Account ID
   export SNOWFLAKE_WAREHOUSE="COMPUTE_WH"
   export SNOWFLAKE_ROLE="ACCOUNTADMIN"

3. CREATE SCHEMA (via Snowflake UI or SQL):
   CREATE DATABASE JOB_INTELLIGENT;
   USE DATABASE JOB_INTELLIGENT;
   
4. RUN SQL SCHEMA:
   Execute scripts/snowflake_schema.sql in Snowflake

5. LOAD DATA:
   python src/database/snowflake_loader.py

╔════════════════════════════════════════════════════════════════════╗
║ Or use Snowflake Trial: $390 free credits (includes SQL compute)  ║
╚════════════════════════════════════════════════════════════════════╝
"""
    print(instructions)


if __name__ == '__main__':
    import sys
    
    # Print setup instructions
    print_setup_instructions()
    
    # Check for --setup flag
    if '--setup' in sys.argv:
        logger.info("Run the following setup commands:")
        logger.info("pip install snowflake-connector-python")
        sys.exit(0)
    
    # Check for --dry-run flag
    dry_run = '--dry-run' in sys.argv
    
    # Run loader
    os.chdir(Path(__file__).parent.parent.parent)  # Go to project root
    
    success = load_to_snowflake(
        jobs_csv='data/jobs_cleaned.csv',
        skills_csv='data/jobs_skills.csv',
        dry_run=dry_run
    )
    
    sys.exit(0 if success else 1)
