"""
Power BI Service Setup Guide - Ubuntu/Web
Phase 6: Build Dashboards without Desktop
"""

import json
from pathlib import Path

POWERBI_SERVICE_SETUP = {
    "version": "1.0",
    "platform": "Power BI Service (Web)",
    "os": "Ubuntu (any OS with browser)",
    "status": "✅ Ready for implementation",
    
    # ============================================================
    # STEP 1: PREREQUISITES
    # ============================================================
    "prerequisites": {
        "account": {
            "create_powerbi_account": "https://app.powerbi.com",
            "signup_options": [
                "Microsoft Account (outlook.com, hotmail.com, etc.)",
                "Work/School Account",
                "Free license (recommended for academic projects)"
            ]
        },
        "snowflake_access": {
            "account": "ZMQDXFA-DS70598",
            "warehouse": "COMPUTE_WH",
            "database": "JOB_INTELLIGENT",
            "schema": "PUBLIC",
            "username": "admin",
            "password": "fQPw5eaPUAdaz72"
        },
        "browser": {
            "recommended": "Chrome or Edge",
            "not_required": "No Power BI Desktop installation needed"
        }
    },
    
    # ============================================================
    # STEP 2: CREATE SNOWFLAKE CONNECTION IN POWER BI SERVICE
    # ============================================================
    "snowflake_connection": {
        "step_1": "Go to https://app.powerbi.com",
        "step_2": "Sign in with Microsoft account",
        "step_3": "Click 'Get Data' (top left of workspace)",
        "step_4": "Search for 'Snowflake'",
        "step_5": "Select 'Snowflake' from connectors",
        "step_6": "Connection details to enter": {
            "server": "ZMQDXFA-DS70598.snowflakecomputing.com",
            "warehouse": "COMPUTE_WH",
            "database": "JOB_INTELLIGENT",
            "schema": "PUBLIC"
        },
        "step_7": "Click 'Connect'",
        "step_8": "Authentication": {
            "method": "Username/Password",
            "username": "admin",
            "password": "fQPw5eaPUAdaz72"
        },
        "step_9": "Select tables to import": [
            "FACT_JOBS",
            "FACT_JOB_SKILLS",
            "DIM_COMPANIES",
            "DIM_LOCATIONS",
            "DIM_SKILLS",
            "VW_JOBS_FULL_CONTEXT",
            "VW_SKILLS_DEMAND",
            "VW_JOBS_BY_TITLE",
            "VW_MARKET_OVERVIEW",
            "VW_COMPANY_OPPORTUNITIES",
            "VW_REGIONAL_ANALYSIS",
            "VW_SKILL_SPECIALIZATION",
            "VW_TRENDING_SKILLS",
            "VW_JOB_COMPLEXITY"
        ],
        "step_10": "Click 'Load'",
        "step_11": "Wait for data to load (2-5 minutes)",
        "step_12": "You now have a dataset in Power BI Service!"
    },
    
    # ============================================================
    # STEP 3: CREATE RELATIONSHIPS (Data Model)
    # ============================================================
    "relationships": {
        "instructions": "Only needed if not using views",
        "setup_automatic": "Power BI may auto-detect relationships",
        "manual_setup_if_needed": [
            {
                "relationship": "FACT_JOBS → DIM_COMPANIES",
                "from_table": "FACT_JOBS",
                "from_column": "COMPANY_ID",
                "to_table": "DIM_COMPANIES",
                "to_column": "COMPANY_ID",
                "cardinality": "Many-to-One"
            },
            {
                "relationship": "FACT_JOBS → DIM_LOCATIONS",
                "from_table": "FACT_JOBS",
                "from_column": "LOCATION_ID",
                "to_table": "DIM_LOCATIONS",
                "to_column": "LOCATION_ID",
                "cardinality": "Many-to-One"
            },
            {
                "relationship": "FACT_JOB_SKILLS → FACT_JOBS",
                "from_table": "FACT_JOB_SKILLS",
                "from_column": "JOB_ID",
                "to_table": "FACT_JOBS",
                "to_column": "JOB_ID",
                "cardinality": "Many-to-One"
            },
            {
                "relationship": "FACT_JOB_SKILLS → DIM_SKILLS",
                "from_table": "FACT_JOB_SKILLS",
                "from_column": "SKILL_ID",
                "to_table": "DIM_SKILLS",
                "to_column": "SKILL_ID",
                "cardinality": "Many-to-One"
            }
        ]
    },
    
    # ============================================================
    # STEP 4: DASHBOARD 1 - MARKET OVERVIEW
    # ============================================================
    "dashboard_1_market_overview": {
        "name": "Market Overview",
        "description": "High-level market metrics and job trends",
        "access_url": "https://app.powerbi.com → New Dashboard",
        "visuals": [
            {
                "position": "Top Left (1,1)",
                "type": "Card",
                "title": "Total Jobs Available",
                "data_source": "FACT_JOBS",
                "value_field": "JOB_ID",
                "aggregation": "Count Distinct",
                "format": "Whole Number"
            },
            {
                "position": "Top Left (2,1)",
                "type": "Card",
                "title": "Active Companies",
                "data_source": "DIM_COMPANIES",
                "value_field": "COMPANY_ID",
                "aggregation": "Count",
                "format": "Whole Number"
            },
            {
                "position": "Top Right (1,2)",
                "type": "Card",
                "title": "Unique Skills",
                "data_source": "DIM_SKILLS",
                "value_field": "SKILL_ID",
                "aggregation": "Count",
                "format": "Whole Number"
            },
            {
                "position": "Top Right (2,2)",
                "type": "Card",
                "title": "Avg Job Age (Days)",
                "data_source": "FACT_JOBS",
                "value_field": "JOB_POSTING_DAYS_OLD",
                "aggregation": "Average",
                "format": "Decimal (0)"
            },
            {
                "position": "Middle (Full Width)",
                "type": "Horizontal Bar Chart",
                "title": "Top 15 Job Titles",
                "data_source": "VW_JOBS_BY_TITLE",
                "x_axis": "JOB_TITLE_NORMALIZED",
                "y_axis": "JOB_COUNT",
                "sort": "Descending",
                "limit": 15,
                "height": "Medium"
            },
            {
                "position": "Bottom Left",
                "type": "Pie Chart",
                "title": "Jobs by Source",
                "data_source": "FACT_JOBS",
                "category": "SOURCE",
                "values": "JOB_ID",
                "aggregation": "Count Distinct"
            },
            {
                "position": "Bottom Right",
                "type": "Clustered Column Chart",
                "title": "Jobs by Location",
                "data_source": "VW_REGIONAL_ANALYSIS",
                "x_axis": "LOCATION_NAME",
                "y_axis": "JOB_COUNT",
                "sort": "Descending"
            }
        ]
    },
    
    # ============================================================
    # STEP 5: DASHBOARD 2 - SKILLS DEMAND
    # ============================================================
    "dashboard_2_skills": {
        "name": "Skills Demand & Market",
        "description": "Most demanded skills and trends",
        "visuals": [
            {
                "type": "Slicer",
                "position": "Top",
                "field": "SKILL_CATEGORY",
                "data_source": "DIM_SKILLS",
                "style": "Dropdown",
                "applies_to": "All other visuals"
            },
            {
                "type": "Horizontal Bar Chart",
                "position": "Left (Large)",
                "title": "Top 20 Demanded Skills",
                "data_source": "VW_SKILLS_DEMAND",
                "x_axis": "SKILL_NAME",
                "y_axis": "JOBS_REQUIRING_SKILL",
                "sort": "Descending",
                "limit": 20,
                "tooltip": ["DEMAND_PERCENTAGE", "AVG_CONFIDENCE"]
            },
            {
                "type": "Clustered Column Chart",
                "position": "Top Right",
                "title": "Skills by Category",
                "data_source": "VW_SKILLS_DEMAND",
                "x_axis": "SKILL_CATEGORY",
                "y_axis": "JOBS_REQUIRING_SKILL",
                "aggregation": "Sum"
            },
            {
                "type": "Table",
                "position": "Bottom Right",
                "title": "Skill Metrics",
                "data_source": "VW_SKILLS_DEMAND",
                "columns": [
                    "SKILL_NAME",
                    "SKILL_CATEGORY",
                    "JOBS_REQUIRING_SKILL",
                    "DEMAND_PERCENTAGE",
                    "AVG_CONFIDENCE"
                ],
                "sort": "JOBS_REQUIRING_SKILL (Descending)"
            }
        ]
    },
    
    # ============================================================
    # STEP 6: DASHBOARD 3 - COMPANIES & OPPORTUNITIES
    # ============================================================
    "dashboard_3_companies": {
        "name": "Company Opportunities",
        "description": "Which companies are hiring and their needs",
        "visuals": [
            {
                "type": "Horizontal Bar Chart",
                "position": "Top (Full Width)",
                "title": "Top 20 Hiring Companies",
                "data_source": "VW_COMPANY_OPPORTUNITIES",
                "x_axis": "COMPANY_NAME",
                "y_axis": "OPEN_POSITIONS",
                "sort": "Descending",
                "limit": 20,
                "height": "Large"
            },
            {
                "type": "Treemap",
                "position": "Bottom Left",
                "title": "Companies by Industry",
                "data_source": "VW_COMPANY_OPPORTUNITIES",
                "group": "INDUSTRY",
                "value": "OPEN_POSITIONS",
                "tooltip": "COMPANY_NAME"
            },
            {
                "type": "Clustered Column Chart",
                "position": "Bottom Right",
                "title": "Locations Hiring per Company",
                "data_source": "VW_COMPANY_OPPORTUNITIES",
                "x_axis": "COMPANY_NAME",
                "y_axis": "LOCATIONS_HIRING",
                "limit": 15,
                "sort": "Descending"
            }
        ]
    },
    
    # ============================================================
    # STEP 7: DASHBOARD 4 - JOB EXPLORER
    # ============================================================
    "dashboard_4_explorer": {
        "name": "Job Details Explorer",
        "description": "Interactive job search and details",
        "visuals": [
            {
                "type": "Slicer Panel (Top)",
                "position": "Full Width",
                "slicers": [
                    {
                        "field": "JOB_TITLE_NORMALIZED",
                        "data_source": "FACT_JOBS",
                        "type": "Dropdown",
                        "width": "25%"
                    },
                    {
                        "field": "COMPANY_NAME",
                        "data_source": "DIM_COMPANIES",
                        "type": "Dropdown",
                        "width": "25%"
                    },
                    {
                        "field": "LOCATION_NAME",
                        "data_source": "DIM_LOCATIONS",
                        "type": "List",
                        "width": "25%"
                    },
                    {
                        "field": "SOURCE",
                        "data_source": "FACT_JOBS",
                        "type": "Buttons",
                        "width": "25%"
                    }
                ]
            },
            {
                "type": "Table",
                "position": "Middle (Full Width)",
                "title": "Job Listings",
                "data_source": "VW_JOBS_FULL_CONTEXT",
                "columns": [
                    "JOB_TITLE",
                    "COMPANY_NAME",
                    "LOCATION_NAME",
                    "REQUIRED_SKILLS_COUNT",
                    "SOURCE",
                    "PUBLISH_DATE"
                ],
                "sort": "PUBLISH_DATE (Descending)",
                "height": "Large",
                "allow_selection": true
            },
            {
                "type": "Text Box",
                "position": "Bottom Left",
                "title": "Job Description",
                "data_source": "VW_JOBS_FULL_CONTEXT",
                "field": "DESCRIPTION",
                "tooltip": "Click job row above to see description"
            },
            {
                "type": "Card List",
                "position": "Bottom Right",
                "title": "Required Skills",
                "data_source": "VW_JOBS_FULL_CONTEXT",
                "field": "REQUIRED_SKILLS"
            }
        ]
    },
    
    # ============================================================
    # STEP 8: DASHBOARD 5 - REGIONAL ANALYSIS
    # ============================================================
    "dashboard_5_regional": {
        "name": "Regional Job Market",
        "description": "Geographic job distribution",
        "visuals": [
            {
                "type": "Map",
                "position": "Top (Full Width)",
                "title": "Jobs by Country",
                "data_source": "VW_REGIONAL_ANALYSIS",
                "location": "COUNTRY",
                "bubble_size": "JOB_COUNT",
                "bubble_color": "COMPANY_COUNT",
                "height": "Large"
            },
            {
                "type": "Horizontal Bar Chart",
                "position": "Bottom Left",
                "title": "Jobs by Region",
                "data_source": "VW_REGIONAL_ANALYSIS",
                "x_axis": "REGION",
                "y_axis": "JOB_COUNT",
                "sort": "Descending"
            },
            {
                "type": "Clustered Column Chart",
                "position": "Bottom Middle",
                "title": "Companies Hiring by Region",
                "data_source": "VW_REGIONAL_ANALYSIS",
                "x_axis": "REGION",
                "y_axis": "COMPANY_COUNT"
            },
            {
                "type": "Line Chart",
                "position": "Bottom Right",
                "title": "Avg Job Age by Region",
                "data_source": "VW_REGIONAL_ANALYSIS",
                "x_axis": "REGION",
                "y_axis": "AVG_JOB_AGE",
                "format": "Days"
            }
        ]
    },
    
    # ============================================================
    # STEP 9: DASHBOARD 6 - ROLE-SPECIFIC SKILLS
    # ============================================================
    "dashboard_6_role_skills": {
        "name": "Role-Specific Skills Analysis",
        "description": "Skills required per job title",
        "visuals": [
            {
                "type": "Slicer",
                "position": "Top",
                "field": "JOB_TITLE_NORMALIZED",
                "data_source": "VW_SKILL_SPECIALIZATION",
                "style": "Dropdown",
                "width": "50%"
            },
            {
                "type": "Horizontal Bar Chart",
                "position": "Left (Large)",
                "title": "Top Skills for Selected Role",
                "data_source": "VW_SKILL_SPECIALIZATION",
                "x_axis": "SKILL_NAME",
                "y_axis": "SKILL_RELEVANCE_PCT",
                "sort": "Descending",
                "format": "Percentage"
            },
            {
                "type": "Pie Chart",
                "position": "Top Right",
                "title": "Skills by Category",
                "data_source": "VW_SKILL_SPECIALIZATION",
                "category": "SKILL_CATEGORY",
                "values": "JOBS_MENTIONING_SKILL"
            },
            {
                "type": "Scatter Plot",
                "position": "Bottom Right",
                "title": "Skill Demand vs Confidence",
                "data_source": "VW_SKILL_SPECIALIZATION",
                "x_axis": "JOBS_MENTIONING_SKILL",
                "y_axis": "AVG_CONFIDENCE",
                "bubble_size": "SKILL_RELEVANCE_PCT",
                "legend": "SKILL_CATEGORY"
            }
        ]
    },
    
    # ============================================================
    # STEP 10: STYLING & BRANDING
    # ============================================================
    "styling": {
        "theme_colors": {
            "primary": "#1f77b4",       # Blue
            "secondary": "#ff7f0e",     # Orange
            "accent": "#2ca02c",        # Green
            "background": "#f8f9fa",
            "text": "#2c3e50"
        },
        "fonts": {
            "title": "Segoe UI, 16pt, Bold",
            "subtitle": "Segoe UI, 12pt, Regular",
            "labels": "Segoe UI, 11pt, Regular"
        },
        "layout": {
            "page_size": "16:9 (recommended)",
            "margins": "Medium",
            "grid_snap": "enabled"
        }
    },
    
    # ============================================================
    # STEP 11: PUBLISH & SHARE
    # ============================================================
    "publishing": {
        "step_1": "Click 'File' → 'Save'",
        "step_2": "Give dashboard a name",
        "step_3": "Select workspace (My Workspace if personal)",
        "step_4": "Click 'Save'",
        "step_5": "Dashboards are now live at app.powerbi.com",
        "step_6": "Share with others": {
            "method_1": "Share button → Add email addresses",
            "method_2": "Publish as App (requires Pro license)",
            "method_3": "Generate shareable link"
        }
    },
    
    # ============================================================
    # STEP 12: COMMON DAX MEASURES (Optional)
    # ============================================================
    "dax_measures": {
        "TotalJobs": {
            "formula": "DISTINCTCOUNT(FACT_JOBS[JOB_ID])",
            "category": "Overview",
            "use_case": "KPI card showing total jobs"
        },
        "TotalCompanies": {
            "formula": "DISTINCTCOUNT(DIM_COMPANIES[COMPANY_ID])",
            "category": "Overview",
            "use_case": "KPI card for company count"
        },
        "AvgJobAge": {
            "formula": "AVERAGE(FACT_JOBS[JOB_POSTING_DAYS_OLD])",
            "category": "Overview",
            "use_case": "Average days since posting"
        },
        "JobsThisMonth": {
            "formula": "CALCULATE([TotalJobs], DATESMTD(TODAY()))",
            "category": "Time-based",
            "use_case": "Monthly job count"
        },
        "TopSkill": {
            "formula": "TOPN(1, VALUES(DIM_SKILLS[SKILL_NAME]), [JobsRequiringSkill])",
            "category": "Skills",
            "use_case": "Display most demanded skill"
        }
    }
}

def create_powerbi_service_guide():
    """Create comprehensive Power BI Service setup guide"""
    
    guide_path = Path('/home/josh/PowerBi/job-intelligent/docs/POWERBI_SERVICE_UBUNTU.json')
    guide_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(guide_path, 'w') as f:
        json.dump(POWERBI_SERVICE_SETUP, f, indent=2)
    
    print(f"✓ Power BI Service guide created: {guide_path}")
    return POWERBI_SERVICE_SETUP

if __name__ == '__main__':
    create_powerbi_service_guide()
