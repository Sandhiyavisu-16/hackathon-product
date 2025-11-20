-- Add evaluation pipeline columns to hackathon_ideas table
-- Migration: 20251120052635_add-evaluation-columns

-- Extraction columns
ALTER TABLE hackathon_ideas ADD COLUMN IF NOT EXISTS extraction_status VARCHAR(50);
ALTER TABLE hackathon_ideas ADD COLUMN IF NOT EXISTS extracted_files_content TEXT;
ALTER TABLE hackathon_ideas ADD COLUMN IF NOT EXISTS files_processed INTEGER;
ALTER TABLE hackathon_ideas ADD COLUMN IF NOT EXISTS content_type VARCHAR(50);

-- Classification columns
ALTER TABLE hackathon_ideas ADD COLUMN IF NOT EXISTS classification_status VARCHAR(50);
ALTER TABLE hackathon_ideas ADD COLUMN IF NOT EXISTS primary_theme VARCHAR(255);
ALTER TABLE hackathon_ideas ADD COLUMN IF NOT EXISTS secondary_themes TEXT[];
ALTER TABLE hackathon_ideas ADD COLUMN IF NOT EXISTS industry VARCHAR(255);
ALTER TABLE hackathon_ideas ADD COLUMN IF NOT EXISTS technologies TEXT[];

-- Evaluation columns
ALTER TABLE hackathon_ideas ADD COLUMN IF NOT EXISTS evaluation_status VARCHAR(50);
ALTER TABLE hackathon_ideas ADD COLUMN IF NOT EXISTS weighted_total_score DECIMAL(5,2);
ALTER TABLE hackathon_ideas ADD COLUMN IF NOT EXISTS investment_recommendation VARCHAR(50);
ALTER TABLE hackathon_ideas ADD COLUMN IF NOT EXISTS key_strengths TEXT[];
ALTER TABLE hackathon_ideas ADD COLUMN IF NOT EXISTS key_concerns TEXT[];
ALTER TABLE hackathon_ideas ADD COLUMN IF NOT EXISTS rubric_scores JSONB;

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_extraction_status ON hackathon_ideas(extraction_status);
CREATE INDEX IF NOT EXISTS idx_classification_status ON hackathon_ideas(classification_status);
CREATE INDEX IF NOT EXISTS idx_evaluation_status ON hackathon_ideas(evaluation_status);
CREATE INDEX IF NOT EXISTS idx_weighted_score ON hackathon_ideas(weighted_total_score DESC);
CREATE INDEX IF NOT EXISTS idx_primary_theme ON hackathon_ideas(primary_theme);
CREATE INDEX IF NOT EXISTS idx_industry ON hackathon_ideas(industry);

-- Comments for documentation
COMMENT ON COLUMN hackathon_ideas.extraction_status IS 'Status of file content extraction: pending, in_progress, completed, failed, no_files';
COMMENT ON COLUMN hackathon_ideas.classification_status IS 'Status of theme/industry classification: pending, in_progress, completed, failed';
COMMENT ON COLUMN hackathon_ideas.evaluation_status IS 'Status of rubric-based evaluation: pending, in_progress, completed, failed';
COMMENT ON COLUMN hackathon_ideas.weighted_total_score IS 'Final weighted score from rubric evaluation (0-10 scale)';
COMMENT ON COLUMN hackathon_ideas.investment_recommendation IS 'AI recommendation: go, consider-with-mitigations, no-go';
COMMENT ON COLUMN hackathon_ideas.rubric_scores IS 'Detailed scores for each rubric in JSON format';
