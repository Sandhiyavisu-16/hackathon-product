-- Add purpose column to model_provider_configs
-- This allows different models to be active for different purposes (evaluation vs verification)

-- Drop the old unique constraint that only allowed one active model
DROP INDEX IF EXISTS idx_model_configs_one_active;

-- Add purpose column
ALTER TABLE model_provider_configs 
ADD COLUMN purpose VARCHAR(20) CHECK (purpose IN ('evaluation', 'verification'));

-- Create a unique constraint: only one active model per purpose
CREATE UNIQUE INDEX idx_model_configs_one_active_per_purpose 
ON model_provider_configs(purpose, is_active) 
WHERE is_active = TRUE;

-- Create index for querying by purpose
CREATE INDEX idx_model_configs_purpose ON model_provider_configs(purpose);

-- Update existing active models to have 'evaluation' as default purpose
UPDATE model_provider_configs 
SET purpose = 'evaluation' 
WHERE is_active = TRUE;
