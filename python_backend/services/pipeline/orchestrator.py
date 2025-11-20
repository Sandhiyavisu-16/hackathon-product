"""
Pipeline Orchestrator - Coordinates the evaluation pipeline stages
"""
from typing import Dict, Any, Optional, Callable
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from services.extraction.file_extractor import FileExtractor
from services.extraction.content_processor import ContentProcessor
from services.database.db_manager import DatabaseManager
from .classification_pipeline import ClassificationPipeline
from .evaluation_pipeline import EvaluationPipeline

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """Orchestrates the complete evaluation pipeline"""
    
    def __init__(
        self,
        db_manager: DatabaseManager,
        file_extractor: FileExtractor,
        batch_size: int = 8,
        max_workers: int = 8,
        progress_callback: Optional[Callable] = None
    ):
        """
        Initialize pipeline orchestrator
        
        Args:
            db_manager: Database manager instance
            file_extractor: File extractor instance
            batch_size: Number of ideas to process in parallel
            max_workers: Maximum number of worker threads
            progress_callback: Optional callback for progress updates
        """
        self.db_manager = db_manager
        self.file_extractor = file_extractor
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.progress_callback = progress_callback
        
        # Initialize pipelines
        self.content_processor = ContentProcessor(file_extractor)
        self.classification_pipeline = ClassificationPipeline(db_manager)
        self.evaluation_pipeline = EvaluationPipeline(db_manager)
    
    def run_full_pipeline(self) -> Dict[str, Any]:
        """
        Run the complete evaluation pipeline
        
        Returns:
            Dictionary with pipeline statistics
        """
        logger.info("Starting full evaluation pipeline")
        
        stats = {
            'extraction': {'processed': 0, 'succeeded': 0, 'failed': 0},
            'classification': {'processed': 0, 'succeeded': 0, 'failed': 0},
            'evaluation': {'processed': 0, 'succeeded': 0, 'failed': 0}
        }
        
        try:
            # Stage 1: Extraction
            self._update_progress('extraction', 0, 'Starting extraction stage')
            extraction_stats = self.run_extraction_stage()
            stats['extraction'] = extraction_stats
            logger.info(f"Extraction complete: {extraction_stats}")
            
            # Stage 2: Classification
            self._update_progress('classification', 0, 'Starting classification stage')
            classification_stats = self.run_classification_stage()
            stats['classification'] = classification_stats
            logger.info(f"Classification complete: {classification_stats}")
            
            # Stage 3: Evaluation
            self._update_progress('evaluation', 0, 'Starting evaluation stage')
            evaluation_stats = self.run_evaluation_stage()
            stats['evaluation'] = evaluation_stats
            logger.info(f"Evaluation complete: {evaluation_stats}")
            
            self._update_progress('complete', 100, 'Pipeline complete')
            logger.info("Full pipeline complete")
            
            return stats
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            self._update_progress('error', 0, f'Pipeline failed: {str(e)}')
            raise
    
    def run_extraction_stage(self) -> Dict[str, int]:
        """
        Run extraction stage for all pending ideas
        
        Returns:
            Statistics dictionary
        """
        logger.info("Starting extraction stage")
        
        # Get ideas needing extraction
        ideas = self.db_manager.get_ideas_for_extraction()
        total = len(ideas)
        
        if total == 0:
            logger.info("No ideas need extraction")
            return {'processed': 0, 'succeeded': 0, 'failed': 0}
        
        logger.info(f"Found {total} ideas for extraction")
        
        succeeded = 0
        failed = 0
        
        # Process in batches
        with ThreadPoolExecutor(max_workers=self.batch_size) as executor:
            futures = {
                executor.submit(self._extract_idea, idea): idea
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
                    logger.error(f"Extraction failed for idea {idea.get('id')}: {e}")
                    failed += 1
                
                # Update progress
                progress = int((i / total) * 100)
                self._update_progress('extraction', progress, f'Processed {i}/{total} ideas')
        
        return {
            'processed': total,
            'succeeded': succeeded,
            'failed': failed
        }
    
    def _extract_idea(self, idea: Dict[str, Any]) -> Dict[str, Any]:
        """Extract content from a single idea"""
        idea_id = str(idea['id'])
        
        try:
            logger.info(f"Extracting content for idea {idea_id}")
            
            # Get files directory for this idea
            from pathlib import Path
            files_dir = Path(f'data/additional_files/{idea_id}')
            
            # Process files for this idea
            result = self.content_processor.process_idea_files(idea_id, files_dir)
            
            if result.get('status') == 'no_files':
                # No files to process, mark as completed with empty content
                self.db_manager.update_extraction_status(
                    idea_id=idea_id,
                    status='completed'
                )
                logger.info(f"No files found for idea {idea_id}, marked as completed")
                return {'success': True}
            
            if result.get('extracted_content'):
                # Update database with extracted content
                # Note: update_extraction_status needs to be updated to accept these params
                self.db_manager.update_extraction_status(
                    idea_id=idea_id,
                    status='completed'
                )
                logger.info(f"Extraction succeeded for idea {idea_id}")
                return {'success': True}
            else:
                # Mark as completed with no content
                self.db_manager.update_extraction_status(
                    idea_id=idea_id,
                    status='completed'
                )
                logger.info(f"Extraction completed for idea {idea_id} (no content)")
                return {'success': True}
                
        except Exception as e:
            logger.error(f"Extraction error for idea {idea_id}: {e}")
            self.db_manager.update_extraction_status(
                idea_id=idea_id,
                status='failed'
            )
            return {'success': False, 'error': str(e)}
    
    def run_classification_stage(self) -> Dict[str, int]:
        """
        Run classification stage for all extracted ideas
        
        Returns:
            Statistics dictionary
        """
        logger.info("Starting classification stage")
        return self.classification_pipeline.run(
            batch_size=self.batch_size,
            progress_callback=lambda p, m: self._update_progress('classification', p, m)
        )
    
    def run_evaluation_stage(self) -> Dict[str, int]:
        """
        Run evaluation stage for all classified ideas
        
        Returns:
            Statistics dictionary
        """
        logger.info("Starting evaluation stage")
        return self.evaluation_pipeline.run(
            batch_size=self.batch_size,
            progress_callback=lambda p, m: self._update_progress('evaluation', p, m)
        )
    
    def _update_progress(self, stage: str, progress: int, message: str):
        """Update progress via callback"""
        if self.progress_callback:
            self.progress_callback({
                'stage': stage,
                'progress': progress,
                'message': message
            })
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get overall pipeline statistics"""
        return self.db_manager.get_pipeline_stats()
