"""
Power BI Dashboard Setup Guide - Phase 6
Configure connections and create dashboards for job intelligence
"""

import json
from pathlib import Path

POWERBI_SETUP = {
    "version": "1.0",
    "description": "Job Intelligence Data Dashboards for Power BI",
    "created_for": "job-intelligent project",
    
    # ============================================================
    # STEP 1: CONNECTION SETUP
    # ============================================================
    "connection_setup": {
        "data_source": "Snowflake",
        "credentials": {
            "account_identifier": "ZMQDXFA-DS70598",
            "warehouse": "COMPUTE_WH",
            "database": "JOB_INTELLIGENT",
            "schema": "PUBLIC"
        },
        "connection_string_template": (
            "Driver=ODBC Driver 17 for SQL Server;"
            "Server=ZMQDXFA-DS70598.snowflakecomputing.com;"
            "Warehouse=COMPUTE_WH;"
            "Database=JOB_INTELLIGENT;"
            "UID=admin;"
            "PWD=<password>;"
        ),
        "instructions": [
            "1. In Power BI Desktop, select 'Get Data'",
            "2. Search for 'Snowflake'",
            "3. Enter Server: ZMQDXFA-DS70598.snowflakecomputing.com",
            "4. Enter Warehouse: COMPUTE_WH",
            "5. Enter Database: JOB_INTELLIGENT",
            "6. Select 'Import' mode for best performance"
        ]
    },
    
    # ============================================================
    # STEP 2: DATA TABLES TO IMPORT
    # ============================================================
    "data_tables": {
        "dimension_tables": [
            "DIM_COMPANIES",
            "DIM_LOCATIONS",
            "DIM_SKILLS"
        ],
        "fact_tables": [
            "FACT_JOBS",
            "FACT_JOB_SKILLS"
        ],
        "views_for_dashboards": [
            "VW_JOBS_FULL_CONTEXT",
            "VW_SKILLS_DEMAND",
            "VW_JOBS_BY_TITLE",
            "VW_MARKET_OVERVIEW",
            "VW_COMPANY_OPPORTUNITIES",
            "VW_REGIONAL_ANALYSIS",
            "VW_SKILL_SPECIALIZATION",
            "VW_TRENDING_SKILLS",
            "VW_JOB_COMPLEXITY"
        ]
    },
    
    # ============================================================
    # STEP 3: RECOMMENDED DASHBOARDS
    # ============================================================
    "dashboards": [
        {
            "name": "Market Overview",
            "description": "High-level market metrics and trends",
            "key_visuals": [
                {
                    "title": "Total Jobs",
                    "type": "KPI Card",
                    "source": "VW_MARKET_OVERVIEW",
                    "field": "TOTAL_JOBS",
                    "format": "Number"
                },
                {
                    "title": "Total Companies",
                    "type": "KPI Card",
                    "source": "VW_MARKET_OVERVIEW",
                    "field": "TOTAL_COMPANIES"
                },
                {
                    "title": "Average Job Age",
                    "type": "KPI Card",
                    "source": "VW_MARKET_OVERVIEW",
                    "field": "AVG_JOB_AGE_DAYS",
                    "format": "Decimal"
                },
                {
                    "title": "Top 20 Job Titles",
                    "type": "Horizontal Bar Chart",
                    "source": "VW_JOBS_BY_TITLE",
                    "x_axis": "JOB_TITLE_NORMALIZED",
                    "y_axis": "JOB_COUNT",
                    "top_n": 20,
                    "sort": "Descending"
                },
                {
                    "title": "Job Postings by Region",
                    "type": "Map",
                    "source": "VW_REGIONAL_ANALYSIS",
                    "location": "COUNTRY",
                    "value": "JOB_COUNT",
                    "color_gradient": "Orange-Red"
                },
                {
                    "title": "Jobs by Source",
                    "type": "Pie Chart",
                    "source": "FACT_JOBS",
                    "value": "SOURCE",
                    "count": "JOB_ID"
                }
            ]
        },
        
        {
            "name": "Skills Market Analysis",
            "description": "Most demanded skills and market trends",
            "key_visuals": [
                {
                    "title": "Top 30 Demanded Skills",
                    "type": "Horizontal Bar Chart",
                    "source": "VW_SKILLS_DEMAND",
                    "x_axis": "SKILL_NAME",
                    "y_axis": "JOBS_REQUIRING_SKILL",
                    "top_n": 30,
                    "color_by": "SKILL_CATEGORY"
                },
                {
                    "title": "Skills Demand %",
                    "type": "Horizontal Bar Chart",
                    "source": "VW_SKILLS_DEMAND",
                    "x_axis": "SKILL_NAME",
                    "y_axis": "DEMAND_PERCENTAGE",
                    "top_n": 20,
                    "format": "Percentage"
                },
                {
                    "title": "Skills by Category",
                    "type": "Clustered Bar Chart",
                    "source": "VW_SKILLS_DEMAND",
                    "x_axis": "SKILL_CATEGORY",
                    "y_axis": "JOBS_REQUIRING_SKILL",
                    "legend": "SKILL_NAME"
                },
                {
                    "title": "Trending Skills (Last 30 Days)",
                    "type": "Line Chart",
                    "source": "VW_TRENDING_SKILLS",
                    "x_axis": "SKILL_NAME",
                    "y_axis": "RECENT_JOBS_30D",
                    "top_n": 15
                },
                {
                    "title": "Skill Confidence Scores",
                    "type": "Scatter Plot",
                    "source": "VW_SKILLS_DEMAND",
                    "x_axis": "JOBS_REQUIRING_SKILL",
                    "y_axis": "AVG_CONFIDENCE",
                    "size": "DEMAND_PERCENTAGE"
                }
            ]
        },
        
        {
            "name": "Company Opportunities",
            "description": "Which companies are hiring and what they need",
            "key_visuals": [
                {
                    "title": "Top 20 Hiring Companies",
                    "type": "Horizontal Bar Chart",
                    "source": "VW_COMPANY_OPPORTUNITIES",
                    "x_axis": "COMPANY_NAME",
                    "y_axis": "OPEN_POSITIONS",
                    "top_n": 20,
                    "sort": "Descending"
                },
                {
                    "title": "Companies by Industry",
                    "type": "Treemap",
                    "source": "VW_COMPANY_OPPORTUNITIES",
                    "group": "INDUSTRY",
                    "value": "OPEN_POSITIONS"
                },
                {
                    "title": "Company Hiring Locations",
                    "type": "Clustered Column Chart",
                    "source": "VW_COMPANY_OPPORTUNITIES",
                    "x_axis": "COMPANY_NAME",
                    "y_axis": "LOCATIONS_HIRING",
                    "top_n": 15
                },
                {
                    "title": "Top Skills by Company",
                    "type": "Slicer + Table",
                    "source": "VW_COMPANY_OPPORTUNITIES",
                    "slicer": "COMPANY_NAME",
                    "display": "TOP_SKILLS"
                }
            ]
        },
        
        {
            "name": "Job Details Explorer",
            "description": "Detailed view of individual job postings",
            "key_visuals": [
                {
                    "title": "Job Search",
                    "type": "Multi-Select Slicers",
                    "fields": [
                        "JOB_TITLE_NORMALIZED",
                        "COMPANY_NAME",
                        "LOCATION_NAME",
                        "SKILL_NAME",
                        "SOURCE"
                    ]
                },
                {
                    "title": "Job Listings",
                    "type": "Table",
                    "source": "VW_JOBS_FULL_CONTEXT",
                    "columns": [
                        "JOB_TITLE",
                        "COMPANY_NAME",
                        "LOCATION_NAME",
                        "REQUIRED_SKILLS_COUNT",
                        "SOURCE",
                        "PUBLISH_DATE"
                    ]
                },
                {
                    "title": "Job Description",
                    "type": "Text Box (Dynamic)",
                    "source": "VW_JOBS_FULL_CONTEXT",
                    "field": "DESCRIPTION"
                },
                {
                    "title": "Required Skills",
                    "type": "Multi-Row Card",
                    "source": "VW_JOBS_FULL_CONTEXT",
                    "field": "REQUIRED_SKILLS"
                }
            ]
        },
        
        {
            "name": "Regional Analysis",
            "description": "Job market by geography",
            "key_visuals": [
                {
                    "title": "Job Availability by Country",
                    "type": "Choropleth Map",
                    "source": "VW_REGIONAL_ANALYSIS",
                    "location": "COUNTRY",
                    "value": "JOB_COUNT"
                },
                {
                    "title": "Jobs by Region",
                    "type": "Horizontal Bar Chart",
                    "source": "VW_REGIONAL_ANALYSIS",
                    "x_axis": "REGION",
                    "y_axis": "JOB_COUNT",
                    "sort": "Descending"
                },
                {
                    "title": "Hiring Companies by Region",
                    "type": "Clustered Column Chart",
                    "source": "VW_REGIONAL_ANALYSIS",
                    "x_axis": "REGION",
                    "y_axis": "COMPANY_COUNT"
                },
                {
                    "title": "Average Job Age by Region",
                    "type": "Horizontal Bar Chart",
                    "source": "VW_REGIONAL_ANALYSIS",
                    "x_axis": "REGION",
                    "y_axis": "AVG_JOB_AGE",
                    "format": "Number (Days)"
                }
            ]
        },
        
        {
            "name": "Role-Specific Skills",
            "description": "Which skills are most relevant for each job title",
            "key_visuals": [
                {
                    "title": "Select Job Title",
                    "type": "Dropdown Slicer",
                    "source": "VW_SKILL_SPECIALIZATION",
                    "field": "JOB_TITLE_NORMALIZED"
                },
                {
                    "title": "Top Skills for Role",
                    "type": "Horizontal Bar Chart",
                    "source": "VW_SKILL_SPECIALIZATION",
                    "x_axis": "SKILL_NAME",
                    "y_axis": "SKILL_RELEVANCE_PCT",
                    "format": "Percentage"
                },
                {
                    "title": "Skills Breakdown by Category",
                    "type": "Pie Chart",
                    "source": "VW_SKILL_SPECIALIZATION",
                    "value": "SKILL_CATEGORY",
                    "count": "JOBS_MENTIONING_SKILL"
                },
                {
                    "title": "Skill Confidence by Role",
                    "type": "Scatter Plot",
                    "source": "VW_SKILL_SPECIALIZATION",
                    "x_axis": "JOBS_MENTIONING_SKILL",
                    "y_axis": "AVG_CONFIDENCE",
                    "legend": "SKILL_CATEGORY"
                }
            ]
        }
    ],
    
    # ============================================================
    # STEP 4: POWER BI SETUP CHECKLIST
    # ============================================================
    "setup_checklist": [
        "☐ Download Power BI Desktop (if not already installed)",
        "☐ Create Snowflake ODBC connection",
        "☐ Get Data from Snowflake",
        "☐ Import all dimension tables (DIM_COMPANIES, DIM_LOCATIONS, DIM_SKILLS)",
        "☐ Import fact tables (FACT_JOBS, FACT_JOB_SKILLS)",
        "☐ Import all BI views (VW_*)",
        "☐ Configure relationships (FACT_JOBS -> DIM_COMPANIES/LOCATIONS via IDs)",
        "☐ Create Calendar table (if needed for date analytics)",
        "☐ Create measures for KPIs",
        "☐ Create calculated columns (if needed)",
        "☐ Build Market Overview dashboard",
        "☐ Build Skills Market Analysis dashboard",
        "☐ Build Company Opportunities dashboard",
        "☐ Build Job Details Explorer dashboard",
        "☐ Build Regional Analysis dashboard",
        "☐ Build Role-Specific Skills dashboard",
        "☐ Test all filters and slicers",
        "☐ Publish to Power BI Service (optional)",
        "☐ Configure scheduled refresh (optional)"
    ],
    
    # ============================================================
    # STEP 5: RECOMMENDED MEASURES (DAX)
    # ============================================================
    "dax_measures": {
        "TotalJobs": "DISTINCTCOUNT(FACT_JOBS[JOB_ID])",
        "TotalCompanies": "DISTINCTCOUNT(DIM_COMPANIES[COMPANY_ID])",
        "TotalSkills": "DISTINCTCOUNT(DIM_SKILLS[SKILL_ID])",
        "AvgJobAge": "AVERAGE(FACT_JOBS[JOB_POSTING_DAYS_OLD])",
        "JobsWithSkills": "CALCULATE(DISTINCTCOUNT(FACT_JOBS[JOB_ID]), NOT(ISBLANK(FACT_JOB_SKILLS[SKILL_ID])))",
        "AvgSkillsPerJob": "DIVIDE(COUNT(FACT_JOB_SKILLS[SKILL_ID]), DISTINCTCOUNT(FACT_JOBS[JOB_ID]))",
        "MostCommonTitle": "TOPN(1, VALUES(FACT_JOBS[JOB_TITLE_NORMALIZED]), DISTINCTCOUNT(FACT_JOBS[JOB_ID]))",
        "JobsThisMonth": "CALCULATE(DISTINCTCOUNT(FACT_JOBS[JOB_ID]), DATESMTD(FACT_JOBS[PUBLISH_DATE]))"
    }
}

def create_powerbi_guide():
    """Create Power BI setup guide file"""
    
    guide_path = Path('/home/josh/PowerBi/job-intelligent/docs/POWERBI_SETUP.json')
    guide_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(guide_path, 'w') as f:
        json.dump(POWERBI_SETUP, f, indent=2)
    
    print(f"✓ Power BI setup guide created: {guide_path}")
    return POWERBI_SETUP

if __name__ == '__main__':
    create_powerbi_guide()
