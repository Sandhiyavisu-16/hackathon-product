"""
Evaluation Service - FastAPI wrapper for the evaluation pipeline
"""
from pathlib import Path
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class EvaluationService:
    """Service wrapper for evaluation pipeline operations"""
    
    def __init__(self):
        self.status = {
            'running': False,
            'stage': None,
            'progress': 0,
            'total': 0,
            'completed': 0,
            'failed': 0
        }
    
    async def get_evaluation_model_config(self):
        """Get model configuration for evaluation purpose"""
        from services.model_config_service import model_config_service
        from config.settings import get_settings
        from config.database import get_db_connection
        
        settings = get_settings()
        
        # Try to get active config for evaluation purpose
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM model_provider_configs
                    WHERE is_active = true AND purpose = 'evaluation'
                    LIMIT 1
                """)
                row = cursor.fetchone()
                
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    config = dict(zip(columns, row))
                    cursor.close()
                    
                    # Parse JSON settings
                    import json
                    if isinstance(config.get('settings'), str):
                        config['settings'] = json.loads(config['settings'])
                    
                    logger.info(f"Found evaluation config: {config.get('name')}")
                    logger.info(f"Provider: {config.get('provider')}")
                    logger.info(f"Config settings keys: {list(config['settings'].keys())}")
                    
                    # Return full config for LLM service
                    return {
                        'provider': config.get('provider'),
                        'model_name': config['settings'].get('model_name') or config['settings'].get('model', 'gemini-2.0-flash-exp'),
                        'settings': config['settings']
                    }
                
                cursor.close()
        except Exception as e:
            logger.warning(f"Could not get evaluation model config: {e}")
        
        # Fallback to environment variable (Gemini)
        if settings.gemini_api_key:
            logger.info("Using Gemini API key from environment variable")
            return {
                'provider': 'gemini',
                'model_name': 'gemini-2.0-flash-exp',
                'settings': {'api_key': settings.gemini_api_key}
            }
        
        raise ValueError("No model configuration found for evaluation. Please activate a model config with purpose='evaluation' or set GEMINI_API_KEY environment variable.")
    
    def _update_progress(self, progress_data: Dict):
        """Update progress from pipeline callback"""
        self.status['stage'] = progress_data.get('stage')
        self.status['progress'] = progress_data.get('progress', 0)
        logger.info(f"Pipeline progress: {progress_data.get('message')}")
    
    async def start_pipeline(self) -> Dict:
        """Start the evaluation pipeline"""
        if self.status['running']:
            return {'success': False, 'error': 'Pipeline already running'}
        
        self.status['running'] = True
        self.status['stage'] = 'initializing'
        
        try:
            from services.extraction.file_extractor import FileExtractor
            from services.pipeline.orchestrator import PipelineOrchestrator
            from services.database.db_manager import DatabaseManager
            from config.settings import get_settings
            
            settings = get_settings()
            
            # Get model config for evaluation
            model_config = await self.get_evaluation_model_config()
            provider = model_config['provider']
            model_name = model_config['model_name']
            model_settings = model_config['settings']
            
            logger.info(f"Starting pipeline with provider: {provider}, model: {model_name}")
            
            # Initialize components
            # Note: FileExtractor still uses Gemini directly for vision tasks
            api_key = model_settings.get('api_key', '')
            file_extractor = FileExtractor(api_key, model=model_name) if api_key else None
            db_manager = DatabaseManager('hackathon_ideas')
            
            # Initialize orchestrator
            orchestrator = PipelineOrchestrator(
                db_manager=db_manager,
                file_extractor=file_extractor,
                batch_size=settings.evaluation_batch_size,
                max_workers=settings.evaluation_batch_size,
                progress_callback=self._update_progress,
                provider=provider,
                model_name=model_name,
                model_settings=model_settings
            )
            
            # Run full pipeline
            logger.info("Starting full evaluation pipeline...")
            stats = orchestrator.run_full_pipeline()
            
            self.status['running'] = False
            self.status['stage'] = 'completed'
            # Show number of ideas processed (not total tasks)
            # Use the max of succeeded counts since each idea goes through all stages
            self.status['completed'] = max(
                stats['extraction']['succeeded'],
                stats['classification']['succeeded'],
                stats['evaluation']['succeeded']
            )
            # Show number of ideas that failed at any stage
            self.status['failed'] = max(
                stats['extraction']['failed'],
                stats['classification']['failed'],
                stats['evaluation']['failed']
            )
            
            logger.info("Pipeline completed successfully!")
            
            return {
                'success': True,
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            self.status['running'] = False
            self.status['stage'] = 'failed'
            return {'success': False, 'error': str(e)}
    
    async def get_status(self) -> Dict:
        """Get current pipeline status"""
        return self.status
    
    async def get_idea_scores(self, idea_id: int) -> Dict:
        """Get evaluation results for a specific idea"""
        from config.database import get_db_connection
        
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        weighted_total_score,
                        investment_recommendation,
                        rubric_scores,
                        key_strengths,
                        key_concerns,
                        primary_theme,
                        secondary_themes,
                        industry,
                        technologies,
                        extraction_status,
                        classification_status,
                        evaluation_status
                    FROM hackathon_ideas
                    WHERE id = %s
                """, (idea_id,))
                
                row = cursor.fetchone()
                cursor.close()
                
                if not row:
                    return {'error': 'Idea not found'}
                
                return {
                    'weighted_total_score': float(row[0]) if row[0] else None,
                    'investment_recommendation': row[1],
                    'rubric_scores': row[2],
                    'key_strengths': row[3],
                    'key_concerns': row[4],
                    'primary_theme': row[5],
                    'secondary_themes': row[6],
                    'industry': row[7],
                    'technologies': row[8],
                    'extraction_status': row[9],
                    'classification_status': row[10],
                    'evaluation_status': row[11]
                }
        except Exception as e:
            logger.error(f"Error getting idea scores: {e}")
            return {'error': str(e)}


# Global instance
evaluation_service = EvaluationService()
