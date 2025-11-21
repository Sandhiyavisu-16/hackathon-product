"""
Database Manager - Adapted to use connection pool
"""
from config.database import get_db_connection
from psycopg2.extras import execute_batch
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Handle all database operations using connection pool."""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
    
    def insert_idea(self, idea_data: Dict):
        """Insert single idea with extracted content."""
        columns = list(idea_data.keys())
        placeholders = ', '.join(['%s'] * len(columns))
        column_names = ', '.join(columns)
        
        sql = f"""
        INSERT INTO {self.table_name} ({column_names})
        VALUES ({placeholders})
        ON CONFLICT (idea_id) DO UPDATE SET
            extracted_files_content = EXCLUDED.extracted_files_content,
            files_processed = EXCLUDED.files_processed,
            extraction_status = EXCLUDED.extraction_status,
            updated_at = CURRENT_TIMESTAMP
        """
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(sql, list(idea_data.values()))
                conn.commit()
                logger.info(f"✓ Inserted idea {idea_data.get('idea_id')}")
            except Exception as e:
                conn.rollback()
                logger.error(f"✗ Failed to insert idea: {e}")
                raise
            finally:
                cursor.close()
    
    def insert_batch(self, ideas: List[Dict], batch_size: int = 50):
        """Batch insert multiple ideas."""
        if not ideas:
            return
        
        columns = list(ideas[0].keys())
        column_names = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(columns))
        
        sql = f"""
        INSERT INTO {self.table_name} ({column_names})
        VALUES ({placeholders})
        ON CONFLICT (idea_id) DO UPDATE SET
            extracted_files_content = EXCLUDED.extracted_files_content,
            files_processed = EXCLUDED.files_processed,
            extraction_status = EXCLUDED.extraction_status,
            updated_at = CURRENT_TIMESTAMP
        """
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                execute_batch(cursor, sql, [list(idea.values()) for idea in ideas], page_size=batch_size)
                conn.commit()
                logger.info(f"✓ Inserted {len(ideas)} ideas in batch")
            except Exception as e:
                conn.rollback()
                logger.error(f"✗ Batch insert failed: {e}")
                raise
            finally:
                cursor.close()
    
    def get_statistics(self) -> Dict:
        """Get processing statistics."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(f"""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(CASE WHEN extraction_status = 'completed' THEN 1 END) as completed,
                        COUNT(CASE WHEN extraction_status = 'failed' THEN 1 END) as failed,
                        COUNT(CASE WHEN extraction_status = 'no_files' THEN 1 END) as no_files,
                        COUNT(CASE WHEN classification_status = 'completed' THEN 1 END) as classified,
                        COUNT(CASE WHEN classification_status = 'failed' THEN 1 END) as classification_failed
                    FROM {self.table_name}
                """)
                result = cursor.fetchone()
                return {
                    'total': result[0],
                    'completed': result[1],
                    'failed': result[2],
                    'no_files': result[3],
                    'classified': result[4],
                    'classification_failed': result[5]
                }
            finally:
                cursor.close()
    
    def get_ideas_for_extraction(self) -> List[Dict]:
        """Get ideas that need file extraction."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(f"""
                    SELECT * FROM {self.table_name}
                    WHERE extraction_status IS NULL OR extraction_status = 'pending'
                """)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            finally:
                cursor.close()
    
    def get_ideas_for_classification(self) -> List[Dict]:
        """Get ideas that need classification."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(f"""
                    SELECT * FROM {self.table_name}
                    WHERE extraction_status = 'completed'
                    AND (classification_status IS NULL OR classification_status = 'pending' OR classification_status = 'failed')
                """)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            finally:
                cursor.close()
    
    def get_ideas_for_evaluation(self) -> List[Dict]:
        """Get ideas that need evaluation."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(f"""
                    SELECT * FROM {self.table_name}
                    WHERE classification_status = 'completed'
                    AND (evaluation_status IS NULL OR evaluation_status = 'pending' OR evaluation_status = 'failed')
                """)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            finally:
                cursor.close()
    
    def update_extraction_status(self, idea_id: str, status: str, error_message: str = None):
        """Update extraction status for an idea."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                if error_message:
                    cursor.execute(f"""
                        UPDATE {self.table_name}
                        SET extraction_status = %s
                        WHERE id = %s
                    """, (status, idea_id))
                else:
                    cursor.execute(f"""
                        UPDATE {self.table_name}
                        SET extraction_status = %s
                        WHERE id = %s
                    """, (status, idea_id))
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Failed to update extraction status: {e}")
                raise
            finally:
                cursor.close()
    
    def update_classification(self, idea_id: str, classification: Dict):
        """Update classification results for an idea."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(f"""
                    UPDATE {self.table_name}
                    SET 
                        primary_theme = %s,
                        secondary_themes = %s,
                        industry = %s,
                        technologies = %s,
                        classification_status = 'completed'
                    WHERE id = %s
                """, (
                    classification.get('primary_theme'),
                    classification.get('secondary_themes', []),
                    classification.get('industry'),
                    classification.get('technologies', []),
                    idea_id
                ))
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Failed to update classification: {e}")
                raise
            finally:
                cursor.close()
    
    def update_evaluation(self, idea_id: str, evaluation: Dict):
        """Update evaluation results for an idea."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                import json
                cursor.execute(f"""
                    UPDATE {self.table_name}
                    SET 
                        weighted_total_score = %s,
                        investment_recommendation = %s,
                        key_strengths = %s,
                        key_concerns = %s,
                        rubric_scores = %s,
                        evaluation_status = 'completed'
                    WHERE id = %s
                """, (
                    evaluation.get('weighted_total'),
                    evaluation.get('investment_recommendation'),
                    evaluation.get('key_strengths', []),
                    evaluation.get('key_concerns', []),
                    json.dumps(evaluation.get('scores', {})),
                    idea_id
                ))
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Failed to update evaluation: {e}")
                raise
            finally:
                cursor.close()
    
    def get_active_rubrics(self) -> Dict[str, float]:
        """Get active rubrics with their weights."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT name, weight FROM rubrics
                    WHERE is_active = true
                    ORDER BY display_order
                """)
                rows = cursor.fetchall()
                # Convert to {name: weight_as_decimal} format
                return {row[0]: row[1] / 100.0 for row in rows}
            finally:
                cursor.close()

    def update_status(self, idea_id: str, status_type: str, status: str):
        """Update a specific status field (extraction_status, classification_status, or evaluation_status)"""
        valid_types = ['extraction_status', 'classification_status', 'evaluation_status']
        if status_type not in valid_types:
            raise ValueError(f"Invalid status type: {status_type}")
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(f"""
                    UPDATE {self.table_name}
                    SET {status_type} = %s
                    WHERE id = %s
                """, (status, idea_id))
                conn.commit()
                logger.info(f"Updated {status_type} for idea {idea_id}: {status}")
            except Exception as e:
                conn.rollback()
                logger.error(f"Failed to update {status_type}: {e}")
                raise
            finally:
                cursor.close()
    
    def get_idea_by_id(self, idea_id: str):
        """Get a specific idea by ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(f"""
                    SELECT * FROM {self.table_name}
                    WHERE id = %s
                """, (idea_id,))
                row = cursor.fetchone()
                if not row:
                    return None
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            finally:
                cursor.close()
    
    def get_pipeline_stats(self):
        """Get pipeline processing statistics"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(f"""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(CASE WHEN extraction_status = 'completed' THEN 1 END) as extracted,
                        COUNT(CASE WHEN classification_status = 'completed' THEN 1 END) as classified,
                        COUNT(CASE WHEN evaluation_status = 'completed' THEN 1 END) as evaluated,
                        COUNT(CASE WHEN extraction_status = 'failed' THEN 1 END) as extraction_failed,
                        COUNT(CASE WHEN classification_status = 'failed' THEN 1 END) as classification_failed,
                        COUNT(CASE WHEN evaluation_status = 'failed' THEN 1 END) as evaluation_failed
                    FROM {self.table_name}
                """)
                row = cursor.fetchone()
                return {
                    'total': row[0],
                    'extracted': row[1],
                    'classified': row[2],
                    'evaluated': row[3],
                    'extraction_failed': row[4],
                    'classification_failed': row[5],
                    'evaluation_failed': row[6]
                }
            finally:
                cursor.close()
