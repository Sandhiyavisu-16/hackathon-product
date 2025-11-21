"""
Classification Pipeline - Classifies ideas into themes and industries
"""
from typing import Dict, Any, Optional, Callable
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from services.classification.tcs_classifier import TCSClassifier
from services.database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class ClassificationPipeline:
    """Pipeline for classifying hackathon ideas"""
    
    def __init__(
        self, 
        db_manager: DatabaseManager, 
        provider: Optional[str] = None, 
        model_name: Optional[str] = None,
        model_settings: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize classification pipeline
        
        Args:
            db_manager: Database manager instance
            provider: LLM provider
            model_name: Model name to use
            model_settings: Model configuration settings
        """
        self.db_manager = db_manager
        self.classifier = TCSClassifier(
            provider=provider, 
            model_name=model_name,
            model_settings=model_settings
        )
    
    def run(
        self,
        batch_size: int = 8,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, int]:
        """
        Run classification for all extracted ideas
        
        Args:
            batch_size: Number of ideas to process in parallel
            progress_callback: Optional callback for progress updates
        
        Returns:
            Statistics dictionary
        """
        logger.info("Starting classification pipeline")
        
        # Get ideas needing classification
        ideas = self.db_manager.get_ideas_for_classification()
        total = len(ideas)
        
        if total == 0:
            logger.info("No ideas need classification")
            return {'processed': 0, 'succeeded': 0, 'failed': 0}
        
        logger.info(f"Found {total} ideas for classification")
        
        succeeded = 0
        failed = 0
        
        # Process in batches
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            futures = {
                executor.submit(self._classify_idea, idea): idea
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
                    logger.error(f"Classification failed for idea {idea.get('id')}: {e}")
                    failed += 1
                
                # Update progress
                if progress_callback:
                    progress = int((i / total) * 100)
                    progress_callback(progress, f'Classified {i}/{total} ideas')
        
        logger.info(f"Classification complete: {succeeded} succeeded, {failed} failed")
        
        return {
            'processed': total,
            'succeeded': succeeded,
            'failed': failed
        }
    
    def _classify_idea(self, idea: Dict[str, Any]) -> Dict[str, Any]:
        """Classify a single idea with retry logic for rate limits"""
        idea_id = str(idea['id'])
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Classifying idea {idea_id} (attempt {attempt + 1}/{max_retries})")
                
                # Classify the idea
                classification = self.classifier.classify_idea(idea)
                
                # Update database
                self.db_manager.update_classification(idea_id, classification)
                
                logger.info(f"Classification succeeded for idea {idea_id}: {classification['primary_theme']}")
                return {'success': True}
                
            except Exception as e:
                error_str = str(e)
                
                # Check if it's a rate limit error (429)
                if '429' in error_str or 'quota' in error_str.lower() or 'rate limit' in error_str.lower():
                    if attempt < max_retries - 1:
                        # Wait before retrying (exponential backoff)
                        wait_time = (attempt + 1) * 5  # 5, 10, 15 seconds
                        logger.warning(f"Rate limit hit for idea {idea_id}, waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"Rate limit exceeded for idea {idea_id} after {max_retries} attempts")
                else:
                    logger.error(f"Classification error for idea {idea_id}: {e}")
                
                # Mark as failed
                self.db_manager.update_status(idea_id, 'classification_status', 'failed')
                return {'success': False, 'error': error_str}
