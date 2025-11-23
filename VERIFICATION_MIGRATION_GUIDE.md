# Post-Evaluation Verification - Migration Guide

## 🎯 What's New

The evaluation pipeline now includes a **4th stage: Verification** that automatically validates evaluation quality after scoring completes.

## 📋 Prerequisites

- Existing evaluation pipeline setup
- Database access (PostgreSQL)
- Admin privileges to run migrations

## 🚀 Migration Steps

### Step 1: Pull Latest Code

```bash
git pull origin main
```

### Step 2: Run Database Migration

Choose one of the following methods:

#### Option A: Using Python Script (Recommended)

```bash
cd python_backend
python add_verification_columns.py
```

**Expected Output:**
```
============================================================
🗄️  ADDING VERIFICATION COLUMNS
============================================================

This will add:
  - verification_status (VARCHAR)
  - verification_results (JSONB)
  - verification_timestamp (TIMESTAMP)

============================================================

Executing migration...
✅ SUCCESS: Verification columns added

Verifying columns...
✅ All 3 columns verified:
   - verification_results (jsonb)
   - verification_status (character varying)
   - verification_timestamp (timestamp without time zone)

============================================================
🎉 MIGRATION COMPLETE!
============================================================
```

#### Option B: Using psql Command Line

```bash
psql -U your_username -d your_database -f migrations/20251123_add-verification-columns.sql
```

#### Option C: Using pgAdmin

1. Open pgAdmin
2. Connect to your database
3. Open Query Tool
4. Copy and paste the contents of `migrations/20251123_add-verification-columns.sql`
5. Execute the query

### Step 3: Verify Migration

Run this SQL query to confirm columns were added:

```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'hackathon_ideas' 
AND column_name IN ('verification_status', 'verification_results', 'verification_timestamp')
ORDER BY column_name;
```

**Expected Result:**
```
      column_name       |          data_type          
------------------------+-----------------------------
 verification_results   | jsonb
 verification_status    | character varying
 verification_timestamp | timestamp without time zone
```

### Step 4: Restart Application

```bash
# Stop the application
# Then restart
cd python_backend
python main.py
```

### Step 5: Test Verification

1. Run the evaluation pipeline on a few ideas
2. Check the logs for verification output:

```
🔍 Starting post-evaluation verification...
================================================================================
🔍 POST-EVALUATION VERIFICATION
================================================================================
📊 Found 10 evaluations to verify
================================================================================
CHECK 1: Rubric Compliance
================================================================================
✅ All evaluations have complete rubric criteria
================================================================================
CHECK 2: JSON Validity
================================================================================
✅ All evaluations have valid JSON structure
================================================================================
CHECK 3: No Hallucination
================================================================================
✅ No obvious hallucination detected
================================================================================
CHECK 4: Consistency
================================================================================
✅ Score distribution looks reasonable
   Average: 6.45
   Range: 3.20 - 8.70
   Spread: 5.50
================================================================================
💾 Updating Verification Status in Database
================================================================================
✅ Updated 10 ideas: verification_status = 'completed'
   All verification checks passed
================================================================================
📊 VERIFICATION SUMMARY
================================================================================
Evaluated Ideas: 10
Verification Checks: 4/4 passed (100%)
🎉 All verification checks passed!
✅ Evaluation quality is good!
================================================================================
✅ Verification completed: 4/4 checks passed
   Pass rate: 100.0%
   Passed: 4/4 checks
```

## 🔍 What Verification Checks

### 1. Rubric Compliance
- Ensures all active rubric criteria are scored
- Detects missing criteria in evaluation results

### 2. JSON Validity
- Validates evaluation output structure
- Checks for required fields (scores, weighted_total, recommendation, etc.)
- Ensures proper data types

### 3. Hallucination Detection
- Identifies suspicious high scores (>7) with minimal information
- Flags evaluations that may be overconfident
- Checks for proper use of `insufficient_info` flag

### 4. Consistency
- Analyzes score distribution across all evaluations
- Detects if scores are too similar (lack of discrimination)
- Detects if scores are too different (inconsistent evaluation)

## 📊 Verification Results

Results are stored in the `verification_results` column as JSONB:

```json
{
  "status": "success",
  "total_evaluated": 10,
  "passed": 4,
  "failed": 0,
  "total_checks": 4,
  "pass_rate": 100.0,
  "warnings": [],
  "message": "4/4 checks passed"
}
```

## 🔧 Troubleshooting

### Migration Fails: "Column already exists"

This is safe to ignore. The migration uses `IF NOT EXISTS` so it won't fail if columns already exist.

### Verification Fails: "Column does not exist"

Make sure you ran the migration successfully. Check with:

```sql
\d hackathon_ideas
```

### Verification Shows Warnings

Warnings are informational and don't fail the pipeline. Review them to improve evaluation quality:

- **Missing criteria**: Check rubric configuration
- **High scores with minimal info**: Review LLM prompts to emphasize `insufficient_info` flag
- **Narrow score range**: May indicate lack of discrimination in evaluation
- **Wide score range**: May indicate inconsistent evaluation

## 📈 Monitoring Verification

### Check Verification Status

```sql
SELECT 
    verification_status,
    COUNT(*) as count
FROM hackathon_ideas
WHERE evaluation_status = 'completed'
GROUP BY verification_status;
```

### View Recent Verification Results

```sql
SELECT 
    id,
    idea_title,
    verification_status,
    verification_timestamp,
    verification_results->>'pass_rate' as pass_rate
FROM hackathon_ideas
WHERE verification_status IS NOT NULL
ORDER BY verification_timestamp DESC
LIMIT 10;
```

### Check Verification Pass Rate

```sql
SELECT 
    AVG((verification_results->>'pass_rate')::float) as avg_pass_rate,
    MIN((verification_results->>'pass_rate')::float) as min_pass_rate,
    MAX((verification_results->>'pass_rate')::float) as max_pass_rate
FROM hackathon_ideas
WHERE verification_status = 'completed';
```

## 🎓 Best Practices

1. **Monitor Pass Rates**: Keep an eye on verification pass rates over time
2. **Review Warnings**: Investigate warnings to improve evaluation quality
3. **Regular Checks**: Run verification periodically on existing evaluations
4. **Audit Trail**: Use verification results for compliance and quality audits

## 🆘 Support

If you encounter issues:

1. Check the logs in `python_backend/logs/`
2. Verify database connection
3. Ensure all dependencies are installed
4. Review the spec documentation in `.kiro/specs/post-evaluation-verification/`

## ✅ Success Criteria

You'll know the migration was successful when:

- ✅ All 3 columns exist in `hackathon_ideas` table
- ✅ Pipeline runs without errors
- ✅ Verification logs appear after evaluation
- ✅ `verification_status` is updated in database
- ✅ Frontend shows "four stages" in documentation

---

**Migration Date**: November 23, 2024  
**Version**: 1.1.0  
**Status**: ✅ Production Ready
