# 📊 Database Schema Guide - Idea Submissions

## 🎯 Where Submitted Ideas Are Stored

Submitted ideas are stored in **TWO tables**:

### 1. `idea_submissions` Table
Stores the **CSV upload metadata** (the submission itself)

### 2. `ideas` Table
Stores the **individual ideas** from the CSV (one row per idea)

---

## 📋 Table Structure

### `idea_submissions` Table (CSV Upload Info)

**Purpose:** Tracks each CSV file upload and its processing status

```sql
CREATE TABLE idea_submissions (
  id UUID PRIMARY KEY,                    -- Unique submission ID
  submitter_id UUID NOT NULL,             -- Who submitted it
  csv_file_uri TEXT NOT NULL,             -- S3 path to CSV file
  support_file_uri TEXT,                  -- S3 path to support file (optional)
  support_file_type VARCHAR(10),          -- File type (pdf, doc, etc.)
  total_rows INTEGER NOT NULL,            -- Total rows in CSV
  valid_rows INTEGER NOT NULL,            -- Valid ideas
  invalid_rows INTEGER NOT NULL,          -- Invalid/error rows
  error_report_uri TEXT,                  -- S3 path to error report
  status VARCHAR(30) NOT NULL,            -- Processing status
  source_ip INET,                         -- Submitter's IP
  checksum VARCHAR(64),                   -- File integrity check
  created_at TIMESTAMP DEFAULT NOW(),     -- When submitted
  processed_at TIMESTAMP                  -- When processed
);
```

**Status Values:**
- `received` - CSV uploaded, not yet validated
- `validated` - CSV validated, ideas extracted
- `queued_for_scoring` - Ready for AI scoring
- `failed` - Processing failed

**Example Row:**
```
id: 123e4567-e89b-12d3-a456-426614174000
submitter_id: user-uuid-here
csv_file_uri: s3://bucket/submissions/2024/file.csv
total_rows: 50
valid_rows: 48
invalid_rows: 2
status: validated
created_at: 2024-01-15 10:30:00
```

---

### `ideas` Table (Individual Ideas)

**Purpose:** Stores each individual idea from the CSV

```sql
CREATE TABLE ideas (
  id UUID PRIMARY KEY,                    -- Unique idea ID
  submission_id UUID NOT NULL,            -- Links to idea_submissions
  title VARCHAR(120) NOT NULL,            -- Idea title
  logline VARCHAR(300) NOT NULL,          -- Short description
  genre VARCHAR(40) NOT NULL,             -- Genre/category
  target_audience VARCHAR(100) NOT NULL,  -- Target audience
  duration_or_format VARCHAR(50) NOT NULL,-- Duration/format
  submitter_email VARCHAR(255) NOT NULL,  -- Submitter email
  reference_urls TEXT,                    -- Reference links
  notes TEXT,                             -- Additional notes
  status VARCHAR(30) DEFAULT 'pending_scoring', -- Scoring status
  created_at TIMESTAMP DEFAULT NOW(),     -- When created
  CONSTRAINT fk_submission 
    FOREIGN KEY (submission_id) 
    REFERENCES idea_submissions(id) 
    ON DELETE CASCADE
);
```

**Status Values:**
- `pending_scoring` - Waiting to be scored
- `scoring_in_progress` - Currently being scored
- `scored` - Scoring complete
- `failed` - Scoring failed

**Example Row:**
```
id: 789e4567-e89b-12d3-a456-426614174001
submission_id: 123e4567-e89b-12d3-a456-426614174000
title: "The Last Sunset"
logline: "A detective races against time to solve..."
genre: "Mystery Thriller"
target_audience: "Adults 25-45"
duration_or_format: "90 minutes"
submitter_email: john@example.com
status: pending_scoring
created_at: 2024-01-15 10:30:05
```

---

## 🔗 Relationship Between Tables

```
idea_submissions (1) ──────< (many) ideas
     (CSV Upload)              (Individual Ideas)

One CSV submission → Many ideas
```

**Example:**
- User uploads CSV with 50 ideas
- Creates **1 row** in `idea_submissions`
- Creates **50 rows** in `ideas` (one per idea)
- All 50 ideas link back to the same `submission_id`

---

## 📊 Complete Data Flow

### Step 1: CSV Upload
```
User uploads CSV
↓
Creates row in idea_submissions
  - status: 'received'
  - csv_file_uri: S3 path
  - total_rows: 0 (not yet counted)
```

### Step 2: CSV Validation
```
System validates CSV
↓
Updates idea_submissions
  - status: 'validated'
  - total_rows: 50
  - valid_rows: 48
  - invalid_rows: 2
```

### Step 3: Extract Ideas
```
System extracts each valid row
↓
Creates 48 rows in ideas table
  - Each with submission_id linking back
  - Each with status: 'pending_scoring'
```

### Step 4: AI Scoring
```
AI scores each idea
↓
Updates each idea row
  - status: 'scored'
  - (scores stored in separate table)
```

---

## 🔍 Example Queries

### Get All Submissions
```sql
SELECT * FROM idea_submissions
ORDER BY created_at DESC;
```

### Get All Ideas from a Submission
```sql
SELECT * FROM ideas
WHERE submission_id = '123e4567-e89b-12d3-a456-426614174000'
ORDER BY created_at;
```

### Get Submission with Idea Count
```sql
SELECT 
  s.*,
  COUNT(i.id) as idea_count
FROM idea_submissions s
LEFT JOIN ideas i ON i.submission_id = s.id
GROUP BY s.id
ORDER BY s.created_at DESC;
```

### Get Ideas Pending Scoring
```sql
SELECT * FROM ideas
WHERE status = 'pending_scoring'
ORDER BY created_at;
```

### Get User's Submissions
```sql
SELECT 
  s.*,
  COUNT(i.id) as total_ideas,
  COUNT(CASE WHEN i.status = 'scored' THEN 1 END) as scored_ideas
FROM idea_submissions s
LEFT JOIN ideas i ON i.submission_id = s.id
WHERE s.submitter_id = 'user-uuid-here'
GROUP BY s.id
ORDER BY s.created_at DESC;
```

---

## 📁 Related Tables

### For Scoring (Not Yet Implemented)
You'll likely need additional tables for:

**`idea_scores` Table:**
```sql
CREATE TABLE idea_scores (
  id UUID PRIMARY KEY,
  idea_id UUID NOT NULL,
  rubric_id UUID NOT NULL,
  score INTEGER NOT NULL,
  reasoning TEXT,
  model_config_id UUID NOT NULL,
  scored_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (idea_id) REFERENCES ideas(id),
  FOREIGN KEY (rubric_id) REFERENCES rubrics(id),
  FOREIGN KEY (model_config_id) REFERENCES model_provider_configs(id)
);
```

**`idea_final_scores` Table:**
```sql
CREATE TABLE idea_final_scores (
  id UUID PRIMARY KEY,
  idea_id UUID NOT NULL,
  total_score DECIMAL(5,2) NOT NULL,
  weighted_score DECIMAL(5,2) NOT NULL,
  rank INTEGER,
  scored_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (idea_id) REFERENCES ideas(id)
);
```

---

## 🎯 Summary

### Where Ideas Are Stored:

**Submission Level:**
- **Table:** `idea_submissions`
- **What:** CSV upload metadata
- **One row per:** CSV file uploaded

**Individual Idea Level:**
- **Table:** `ideas`
- **What:** Each individual idea from CSV
- **One row per:** Idea in the CSV

### Key Points:

1. ✅ **One CSV upload** = 1 row in `idea_submissions`
2. ✅ **50 ideas in CSV** = 50 rows in `ideas`
3. ✅ All ideas link back via `submission_id`
4. ✅ Can track processing status at both levels
5. ✅ Cascade delete: Delete submission → Deletes all its ideas

---

## 🔧 How to View Data

### Using psql:
```bash
# Connect to database
psql -U postgres -d your_database

# View submissions
SELECT id, submitter_id, status, total_rows, created_at 
FROM idea_submissions 
ORDER BY created_at DESC 
LIMIT 10;

# View ideas
SELECT id, title, genre, status, created_at 
FROM ideas 
ORDER BY created_at DESC 
LIMIT 10;

# View submission with its ideas
SELECT 
  s.id as submission_id,
  s.status as submission_status,
  s.total_rows,
  i.id as idea_id,
  i.title,
  i.status as idea_status
FROM idea_submissions s
LEFT JOIN ideas i ON i.submission_id = s.id
WHERE s.id = 'your-submission-id'
ORDER BY i.created_at;
```

### Using Code:
```typescript
// Get submission with ideas
const submission = await pool.query(`
  SELECT 
    s.*,
    json_agg(i.*) as ideas
  FROM idea_submissions s
  LEFT JOIN ideas i ON i.submission_id = s.id
  WHERE s.id = $1
  GROUP BY s.id
`, [submissionId]);
```

---

## 📊 Database Diagram

```
┌─────────────────────────┐
│  idea_submissions       │
│  (CSV Upload)           │
├─────────────────────────┤
│ id (PK)                 │
│ submitter_id            │
│ csv_file_uri            │
│ total_rows              │
│ valid_rows              │
│ invalid_rows            │
│ status                  │
│ created_at              │
└───────────┬─────────────┘
            │
            │ 1:N
            │
┌───────────▼─────────────┐
│  ideas                  │
│  (Individual Ideas)     │
├─────────────────────────┤
│ id (PK)                 │
│ submission_id (FK)      │
│ title                   │
│ logline                 │
│ genre                   │
│ target_audience         │
│ duration_or_format      │
│ submitter_email         │
│ status                  │
│ created_at              │
└─────────────────────────┘
```

---

## 🎉 Quick Answer

**Q: In which table are submitted ideas stored?**

**A: TWO tables:**
1. **`idea_submissions`** - Stores the CSV upload info (1 row per upload)
2. **`ideas`** - Stores each individual idea (1 row per idea)

**Example:**
- Upload CSV with 50 ideas
- Creates 1 row in `idea_submissions`
- Creates 50 rows in `ideas`
- All linked by `submission_id`

That's it! 🚀
