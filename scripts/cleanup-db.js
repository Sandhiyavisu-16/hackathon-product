const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

async function cleanup() {
  try {
    console.log('Cleaning up database...');
    
    await pool.query(`
      DROP TABLE IF EXISTS 
        ideas,
        idea_submissions,
        audit_logs,
        rate_limits,
        weight_presets,
        rubrics,
        model_provider_configs,
        pgmigrations
      CASCADE;
    `);
    
    console.log('✅ Database cleaned successfully!');
    console.log('Now run: npm run migrate:up');
  } catch (error) {
    console.error('Error cleaning database:', error.message);
  } finally {
    await pool.end();
  }
}

cleanup();
