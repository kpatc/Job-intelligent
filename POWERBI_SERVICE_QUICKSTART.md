# Power BI Service (Ubuntu) - Quick Setup Guide

## ✅ Prérequis

- ✓ Snowflake data loaded (JOB_INTELLIGENT database)
- ✓ 9 BI views created
- ✓ Browser (Chrome, Edge, Firefox)
- ✓ Microsoft account (free)

---

## 🚀 Step-by-Step Setup (15 minutes)

### STEP 1: Sign In to Power BI Service
```
1. Open browser → https://app.powerbi.com
2. Click "Sign In"
3. Enter Microsoft account email
4. Enter password
5. You're in! (My Workspace shown)
```

### STEP 2: Create Snowflake Connection
```
1. Click "Get Data" (top right)
2. Search "Snowflake"
3. Click "Snowflake"
4. Fill in connection:
   - Server: ZMQDXFA-DS70598.snowflakecomputing.com
   - Warehouse: COMPUTE_WH
   - Database: JOB_INTELLIGENT
   - Schema: PUBLIC
5. Click "Connect"
6. Username: admin
7. Password: fQPw5eaPUAdaz72
8. Click "Sign In"
```

### STEP 3: Select Tables to Import
**Check these tables:**
- [ ] FACT_JOBS
- [ ] FACT_JOB_SKILLS
- [ ] DIM_COMPANIES
- [ ] DIM_LOCATIONS
- [ ] DIM_SKILLS
- [ ] VW_JOBS_FULL_CONTEXT
- [ ] VW_SKILLS_DEMAND
- [ ] VW_JOBS_BY_TITLE
- [ ] VW_MARKET_OVERVIEW
- [ ] VW_COMPANY_OPPORTUNITIES
- [ ] VW_REGIONAL_ANALYSIS
- [ ] VW_SKILL_SPECIALIZATION
- [ ] VW_TRENDING_SKILLS
- [ ] VW_JOB_COMPLEXITY

```
9. Click "Load" and wait 2-5 minutes
```

### STEP 4: Create First Dashboard (Market Overview)
```
1. Click "New Dashboard"
2. Name it: "Market Overview"
3. Click "Create"
```

### STEP 5: Add KPI Cards (Top Row)
```
For each card:
1. Click "+ Add visual"
2. Select "Card" visualization
3. Set VALUE field:
   - Card 1: FACT_JOBS.JOB_ID (Count Distinct) → "Total Jobs"
   - Card 2: DIM_COMPANIES.COMPANY_ID (Count) → "Companies"
   - Card 3: DIM_SKILLS.SKILL_ID (Count) → "Unique Skills"
   - Card 4: FACT_JOBS.JOB_POSTING_DAYS_OLD (Average) → "Avg Job Age"
```

### STEP 6: Add Charts
```
1. Click "+ Add visual"
2. Select "Horizontal Bar Chart"
3. X-axis: VW_JOBS_BY_TITLE.JOB_TITLE_NORMALIZED
4. Y-axis: VW_JOBS_BY_TITLE.JOB_COUNT
5. Sort: Descending
6. Limit to Top 15
7. Title: "Top Job Titles"
```

### STEP 7: Repeat for Other Dashboards

**Dashboard 2: Skills Demand**
- Slicer: SKILL_CATEGORY
- Bar Chart: Top 20 skills by demand
- Table: Skills metrics

**Dashboard 3: Companies**
- Bar Chart: Top 20 hiring companies
- Treemap: Companies by industry
- Column Chart: Locations per company

**Dashboard 4: Job Explorer**
- Slicers: Title, Company, Location, Source
- Table: Job listings
- Text box: Description (dynamic)

**Dashboard 5: Regional**
- Map: Jobs by country
- Bar charts: Regional breakdowns

**Dashboard 6: Role Skills**
- Slicer: Job title
- Bar chart: Top skills for role
- Pie chart: Skills by category

---

## 📊 Dashboard Templates

### Each Dashboard Should Have:
- **Slicers** (top): Filter by job title, company, location, etc.
- **KPIs** (cards): Summary numbers
- **Charts** (bar, column, pie): Trends and distributions
- **Tables**: Detailed data view

---

## 💡 Tips for Power BI Service

### Formatting
1. Click visual → Format (paint brush icon)
2. Style options:
   - Title: Font, size, color
   - Legend: Position, font
   - Axis: Format, labels
   - Colors: Custom palette

### Interactivity
1. Slicers filter other visuals automatically
2. Click bars/slices to drill down
3. Hover for tooltips (configured by default)

### Saving
- All changes auto-save
- No "Save" button needed (unlike Desktop)
- Dashboards live immediately

### Sharing
1. Click "Share" (top right)
2. Add email addresses
3. Grant "View" or "Edit" permission
4. Send

---

## 🔗 Important Snowflake Connection Details

```
Connection Settings (Save for reference):

Account:   ZMQDXFA-DS70598.snowflakecomputing.com
Warehouse: COMPUTE_WH
Database:  JOB_INTELLIGENT
Schema:    PUBLIC
User:      admin
Pass:      fQPw5eaPUAdaz72

Views Available:
- VW_JOBS_FULL_CONTEXT
- VW_SKILLS_DEMAND
- VW_JOBS_BY_TITLE
- VW_MARKET_OVERVIEW
- VW_COMPANY_OPPORTUNITIES
- VW_REGIONAL_ANALYSIS
- VW_SKILL_SPECIALIZATION
- VW_TRENDING_SKILLS
- VW_JOB_COMPLEXITY
```

---

## ✅ Validation Checklist

- [ ] Connected to Snowflake successfully
- [ ] All tables imported (79 jobs, 55 companies, etc.)
- [ ] Created 6 dashboards
- [ ] All dashboards have visuals
- [ ] Slicers filter correctly
- [ ] Charts display data
- [ ] Dashboards look good
- [ ] Can share with others (if needed)

---

## 🎯 Expected Data in Dashboards

When you create visualizations, you should see:

**Total Jobs**: 79
**Companies**: 55
**Locations**: 3
**Skills**: 61

**Top Job Titles**:
1. Data Scientist
2. Data Engineer
3. ML Engineer

**Top Skills**:
1. Python
2. SQL
3. Machine Learning
4. TensorFlow
5. Pandas

**Job Distribution**:
- ReKrute: ~41 jobs
- Indeed: ~38 jobs

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Connection fails | Check credentials, ensure Snowflake is running |
| No data shows | Click "Refresh" (circular arrow icon) |
| Slicer not filtering | Click slicer → Format → Turn on "Multi-select" |
| Chart looks wrong | Check X/Y axis fields are correct |
| Slow loading | Tables are large, this is normal (5-10s) |

---

## 📚 Next Steps

1. ✅ Create all 6 dashboards
2. ✅ Add recommended visuals
3. ✅ Format with company colors
4. ✅ Test all filters
5. ✅ Share dashboards
6. **Optional**: Schedule data refresh
7. **Optional**: Add more complex DAX measures
8. **Optional**: Publish as Power BI App

---

## 🎓 Project Complete!

You now have:
- ✅ Data scraped from 2 sources (79 jobs)
- ✅ Skills extracted via NLP (61 unique, 370 mentions)
- ✅ Data loaded to Snowflake (star schema)
- ✅ BI views created (9 optimized views)
- ✅ Recommendation engine built (semantic + skills)
- ✅ Power BI dashboards ready (6 interactive dashboards)

**Deployed on**: Power BI Service (web, Ubuntu-compatible)
**Access**: https://app.powerbi.com (anytime, anywhere)
**Status**: Ready for academic presentation! 🚀
