-- ============================================
-- Create Base Schema (if not exists)
-- ============================================
-- This creates the base tables needed for the platform
-- Run this BEFORE the evaluation columns migration
-- ============================================

BEGIN;

-- Create Model Provider Configuration (if not exists)
CREATE TABLE IF NOT EXISTS model_provider_configs (
  id SERIAL PRIMARY KEY,
  provider VARCHAR(50) NOT NULL CHECK (provider IN ('azure_openai', 'gemini', 'gemma')),
  name VARCHAR(100) NOT NULL,
  is_active BOOLEAN DEFAULT FALSE,
  settings JSONB NOT NULL,
  status VARCHAR(20) NOT NULL CHECK (status IN ('draft', 'tested', 'active', 'inactive')),
  version INTEGER NOT NULL DEFAULT 1,
  notes TEXT,
  purpose VARCHAR(20) CHECK (purpose IN ('evaluation', 'verification')),
  created_by INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_model_configs_active ON model_provider_configs(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_model_configs_provider ON model_provider_configs(provider);
CREATE INDEX IF NOT EXISTS idx_model_configs_purpose ON model_provider_configs(purpose);

-- Create Rubrics (if not exists)
CREATE TABLE IF NOT EXISTS rubrics (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) UNIQUE NOT NULL,
  description TEXT NOT NULL,
  guidance TEXT NOT NULL,
  scale_min INTEGER DEFAULT 1,
  scale_max INTEGER DEFAULT 5,
  weight INTEGER NOT NULL CHECK (weight >= 0 AND weight <= 100),
  is_default BOOLEAN DEFAULT FALSE,
  is_active BOOLEAN DEFAULT TRUE,
  display_order INTEGER NOT NULL,
  created_by INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rubrics_active ON rubrics(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_rubrics_order ON rubrics(display_order);

-- Create Idea Submissions (if not exists)
CREATE TABLE IF NOT EXISTS idea_submissions (
  id SERIAL PRIMARY KEY,
  submitter_id INTEGER NOT NULL,
  csv_file_uri TEXT NOT NULL,
  support_file_uri TEXT,
  support_file_type VARCHAR(10),
  total_rows INTEGER NOT NULL,
  valid_rows INTEGER NOT NULL,
  invalid_rows INTEGER NOT NULL,
  error_report_uri TEXT,
  status VARCHAR(30) NOT NULL CHECK (status IN ('received', 'validated', 'queued_for_scoring', 'failed')),
  source_ip INET,
  checksum VARCHAR(64),
  created_at TIMESTAMP DEFAULT NOW(),
  processed_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_submissions_submitter ON idea_submissions(submitter_id);
CREATE INDEX IF NOT EXISTS idx_submissions_status ON idea_submissions(status);
CREATE INDEX IF NOT EXISTS idx_submissions_created ON idea_submissions(created_at DESC);

-- Create Ideas table (renamed to hackathon_ideas for evaluation pipeline)
CREATE TABLE IF NOT EXISTS hackathon_ideas (
  id SERIAL PRIMARY KEY,
  submission_id INTEGER,
  idea_title VARCHAR(500) NOT NULL,
  brief_summary TEXT NOT NULL,
  detailed_description TEXT,
  challenge_opportunity TEXT,
  novelty_benefits_risks TEXT,
  responsible_ai_adherence TEXT,
  additional_documentation TEXT,
  supporting_artefacts TEXT,
  second_file_upload TEXT,
  preferred_week VARCHAR(200),
  build_phase_preference VARCHAR(200),
  build_preference VARCHAR(200),
  code_development_preference VARCHAR(200),
  submitter_email VARCHAR(255),
  status VARCHAR(30) DEFAULT 'pending_scoring',
  created_at TIMESTAMP DEFAULT NOW(),
  CONSTRAINT fk_submission FOREIGN KEY (submission_id) REFERENCES idea_submissions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_ideas_submission ON hackathon_ideas(submission_id);
CREATE INDEX IF NOT EXISTS idx_ideas_status ON hackathon_ideas(status);
CREATE INDEX IF NOT EXISTS idx_ideas_email ON hackathon_ideas(submitter_email);

-- Seed Default Rubrics (if empty)
INSERT INTO rubrics (name, description, guidance, weight, is_default, display_order, created_by)
SELECT 'Novelty', 'Originality and uniqueness of the concept', 'Score 5 for highly original ideas, 1 for derivative concepts', 20, TRUE, 1, 1
WHERE NOT EXISTS (SELECT 1 FROM rubrics WHERE name = 'Novelty');

INSERT INTO rubrics (name, description, guidance, weight, is_default, display_order, created_by)
SELECT 'Audience Fit', 'Alignment with target audience preferences', 'Consider demographic appeal and market demand', 25, TRUE, 2, 1
WHERE NOT EXISTS (SELECT 1 FROM rubrics WHERE name = 'Audience Fit');

INSERT INTO rubrics (name, description, guidance, weight, is_default, display_order, created_by)
SELECT 'Feasibility', 'Production viability and resource requirements', 'Assess budget, timeline, and technical complexity', 20, TRUE, 3, 1
WHERE NOT EXISTS (SELECT 1 FROM rubrics WHERE name = 'Feasibility');

INSERT INTO rubrics (name, description, guidance, weight, is_default, display_order, created_by)
SELECT 'Public Service/Value', 'Social impact and educational value', 'Evaluate community benefit and cultural significance', 20, TRUE, 4, 1
WHERE NOT EXISTS (SELECT 1 FROM rubrics WHERE name = 'Public Service/Value');

INSERT INTO rubrics (name, description, guidance, weight, is_default, display_order, created_by)
SELECT 'Ethical/Compliance Risk', 'Legal, ethical, and regulatory concerns (inverse)', 'Score 5 for minimal risk, 1 for high risk', 15, TRUE, 5, 1
WHERE NOT EXISTS (SELECT 1 FROM rubrics WHERE name = 'Ethical/Compliance Risk');

COMMIT;

-- Verification
SELECT 'Base schema created successfully!' as status;
