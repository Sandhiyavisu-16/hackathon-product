"""
Evaluation Pipeline - Evaluates ideas using custom rubrics
"""
from typing import Dict, Any, Optional, Callable
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from services.evaluation.idea_evaluator import IdeaEvaluator
from services.database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class EvaluationPipeline:
    """Pipeline for evaluating hackathon ideas"""
    
    def __init__(
        self, 
        db_manager: DatabaseManager, 
        provider: Optional[str] = None, 
        model_name: Optional[str] = None,
        model_settings: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize evaluation pipeline
        
        Args:
            db_manager: Database manager instance
            provider: LLM provider
            model_name: Model name to use
            model_settings: Model configuration settings
        """
        self.db_manager = db_manager
        self.provider = provider
        self.model_name = model_name
        self.model_settings = model_settings or {}
    
    def run(
        self,
        batch_size: int = 8,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, int]:
        """
        Run evaluation for all classified ideas
        
        Args:
            batch_size: Number of ideas to process in parallel
            progress_callback: Optional callback for progress updates
        
        Returns:
            Statistics dictionary
        """
        logger.info("Starting evaluation pipeline")
        
        # Get active rubrics
        rubrics = self.db_manager.get_active_rubrics()
        
        if not rubrics:
            logger.warning("No active rubrics found, cannot evaluate")
            return {'processed': 0, 'succeeded': 0, 'failed': 0}
        
        logger.info(f"Using {len(rubrics)} active rubrics")
        
        # Initialize evaluator with rubrics
        evaluator = IdeaEvaluator(
            rubrics=rubrics, 
            provider=self.provider, 
            model_name=self.model_name,
            model_settings=self.model_settings
        )
        
        # Get ideas needing evaluation
        ideas = self.db_manager.get_ideas_for_evaluation()
        total = len(ideas)
        
        if total == 0:
            logger.info("No ideas need evaluation")
            return {'processed': 0, 'succeeded': 0, 'failed': 0}
        
        logger.info(f"Found {total} ideas for evaluation")
        
        succeeded = 0
        failed = 0
        
        # Process in batches
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            futures = {
                executor.submit(self._evaluate_idea, idea, evaluator): idea
                for idea in ideas
            }
            
            for i, future in enumerate(as_completed(futures), 1):
                idea = futures[future]
                try:
                    result = future.result()
                    if result['success']:
                        succeeded += 1
                    else:
                        failed += 1
                except Exception as e:
                    logger.error(f"Evaluation failed for idea {idea.get('id')}: {e}")
                    failed += 1
                
                # Update progress
                if progress_callback:
                    progress = int((i / total) * 100)
                    progress_callback(progress, f'Evaluated {i}/{total} ideas')
        
        logger.info(f"Evaluation complete: {succeeded} succeeded, {failed} failed")
        
        return {
            'processed': total,
            'succeeded': succeeded,
            'failed': failed
        }
    
    def _evaluate_idea(self, idea: Dict[str, Any], evaluator: IdeaEvaluator) -> Dict[str, Any]:
        """Evaluate a single idea"""
        idea_id = str(idea['id'])
        
        try:
            logger.info(f"Evaluating idea {idea_id}")
            
            # Evaluate the idea
            evaluation = evaluator.evaluate_idea(idea)
            
            # Update database
            self.db_manager.update_evaluation(idea_id, evaluation)
            
            logger.info(f"Evaluation succeeded for idea {idea_id}: {evaluation['weighted_total']:.2f}")
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Evaluation error for idea {idea_id}: {e}")
            # Mark as failed
            self.db_manager.update_status(idea_id, 'evaluation_status', 'failed')
            return {'success': False, 'error': str(e)}
