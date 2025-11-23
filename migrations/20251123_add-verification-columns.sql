-- Add verification columns to hackathon_ideas table
-- Migration: 20251123_add-verification-columns
-- Purpose: Add columns to track post-evaluation verification status and results

BEGIN;

-- Verification columns
ALTER TABLE hackathon_ideas ADD COLUMN IF NOT EXISTS verification_status VARCHAR(20) CHECK (verification_status IN ('pending', 'completed', 'failed'));
ALTER TABLE hackathon_ideas ADD COLUMN IF NOT EXISTS verification_results JSONB;
ALTER TABLE hackathon_ideas ADD COLUMN IF NOT EXISTS verification_timestamp TIMESTAMP;

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_verification_status ON hackathon_ideas(verification_status);
CREATE INDEX IF NOT EXISTS idx_verification_timestamp ON hackathon_ideas(verification_timestamp DESC);

-- Comments for documentation
COMMENT ON COLUMN hackathon_ideas.verification_status IS 'Status of post-evaluation verification: pending, completed, failed';
COMMENT ON COLUMN hackathon_ideas.verification_results IS 'Detailed verification results in JSON format including pass/fail status for each check';
COMMENT ON COLUMN hackathon_ideas.verification_timestamp IS 'Timestamp when verification was last performed';

COMMIT;
