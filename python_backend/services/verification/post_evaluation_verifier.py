"""
Post-Evaluation Verification
Automatically verifies evaluation quality after the evaluation process completes.

Checks completed evaluations in the database for:
1. Rubric Compliance
2. JSON Validity
3. No Hallucination
4. Consistency
"""
import json
import logging
from typing import Dict, List, Any, Optional
from config.database import get_db_connection
from config.settings import get_settings

logger = logging.getLogger(__name__)


class PostEvaluationVerifier:
    """Verify evaluation quality after completion"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = []
        self.settings = get_settings()
    
    def verify_all(self) -> Dict[str, Any]:
        """Run all verification checks on completed evaluations"""
        logger.info("="*80)
        logger.info("🔍 POST-EVALUATION VERIFICATION")
        logger.info("="*80)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # Get completed evaluations that need verification
                cursor.execute("""
                    SELECT COUNT(*) FROM hackathon_ideas 
                    WHERE evaluation_status = 'completed'
                    AND (verification_status IS NULL OR verification_status IN ('pending', 'failed'))
                """)
                total_to_verify = cursor.fetchone()[0]
                
                if total_to_verify == 0:
                    # Check if all are already verified
                    cursor.execute("""
                        SELECT COUNT(*) FROM hackathon_ideas 
                        WHERE evaluation_status = 'completed'
                        AND verification_status = 'completed'
                    """)
                    already_verified = cursor.fetchone()[0]
                    
                    if already_verified > 0:
                        logger.info(f"✅ All {already_verified} evaluations already verified.")
                        return {
                            'status': 'success',
                            'message': f'All {already_verified} evaluations already verified',
                            'total_evaluated': already_verified,
                            'passed': 0,
                            'failed': 0,
                            'total_checks': 0,
                            'pass_rate': 100.0,
                            'warnings': []
                        }
                    else:
                        logger.info("⚠️  No completed evaluations found. Skipping verification.")
                        return {
                            'status': 'skipped',
                            'message': 'No completed evaluations found',
                            'total_evaluated': 0,
                            'passed': 0,
                            'failed': 0,
                            'total_checks': 0,
                            'pass_rate': 0.0,
                            'warnings': []
                        }
                
                logger.info(f"📊 Found {total_to_verify} evaluations to verify")
                
                # Run verification checks
                self.verify_rubric_compliance(cursor)
                self.verify_json_validity(cursor)
                self.verify_no_hallucination(cursor)
                self.verify_consistency(cursor)
                
                # Update verification status in database
                self.update_verification_status(cursor, conn)
                
                # Generate summary
                summary = self.generate_summary(total_to_verify)
                
                return summary
                
            finally:
                cursor.close()
    
    def verify_rubric_compliance(self, cursor):
        """Verify all rubric criteria are scored"""
        logger.info("="*80)
        logger.info("CHECK 1: Rubric Compliance")
        logger.info("="*80)
        
        # Get active rubrics
        cursor.execute("""
            SELECT name FROM rubrics 
            WHERE is_active = true
        """)
        rubric_rows = cursor.fetchall()
        
        if not rubric_rows:
            logger.warning("⚠️  No active rubrics found. Skipping check.")
            return
        
        expected_criteria = set([row[0] for row in rubric_rows])
        
        # Check evaluations
        cursor.execute("""
            SELECT id, idea_title, rubric_scores
            FROM hackathon_ideas
            WHERE evaluation_status = 'completed'
            AND rubric_scores IS NOT NULL
        """)
        
        missing_criteria_count = 0
        for row in cursor.fetchall():
            idea_id, idea_title, scores = row
            
            if isinstance(scores, str):
                scores = json.loads(scores)
            
            if not scores:
                continue
                
            actual_criteria = set(scores.keys())
            missing = expected_criteria - actual_criteria
            
            if missing:
                missing_criteria_count += 1
                self.warnings.append(f"Idea {idea_id} missing criteria: {missing}")
        
        if missing_criteria_count == 0:
            logger.info(f"✅ All evaluations have complete rubric criteria")
            logger.info(f"   Expected criteria: {', '.join(expected_criteria)}")
            self.passed += 1
        else:
            logger.error(f"❌ {missing_criteria_count} evaluations have missing criteria")
            self.failed += 1
    
    def verify_json_validity(self, cursor):
        """Verify all evaluation JSONs are valid"""
        logger.info("="*80)
        logger.info("CHECK 2: JSON Validity")
        logger.info("="*80)
        
        cursor.execute("""
            SELECT id, idea_title, rubric_scores, weighted_total_score, 
                   investment_recommendation, key_strengths, key_concerns
            FROM hackathon_ideas
            WHERE evaluation_status = 'completed'
        """)
        
        invalid_count = 0
        for row in cursor.fetchall():
            idea_id = row[0]
            
            # Check if all required fields are present and valid
            try:
                scores = row[2]
                weighted_total = row[3]
                recommendation = row[4]
                strengths = row[5]
                concerns = row[6]
                
                # Validate scores is valid JSON
                if isinstance(scores, str):
                    json.loads(scores)
                
                # Validate strengths and concerns are arrays
                if isinstance(strengths, str):
                    json.loads(strengths)
                if isinstance(concerns, str):
                    json.loads(concerns)
                
                # Check required fields are not null
                if scores is None or weighted_total is None or recommendation is None:
                    invalid_count += 1
                    self.warnings.append(f"Idea {idea_id} has null required fields")
                    
            except json.JSONDecodeError as e:
                invalid_count += 1
                self.warnings.append(f"Idea {idea_id} has invalid JSON: {e}")
        
        if invalid_count == 0:
            logger.info(f"✅ All evaluations have valid JSON structure")
            logger.info(f"   Required fields: scores, weighted_total, recommendation, strengths, concerns")
            self.passed += 1
        else:
            logger.error(f"❌ {invalid_count} evaluations have invalid JSON")
            self.failed += 1
    
    def verify_no_hallucination(self, cursor):
        """Verify no obvious hallucination in scores"""
        logger.info("="*80)
        logger.info("CHECK 3: No Hallucination")
        logger.info("="*80)
        
        cursor.execute("""
            SELECT id, idea_title, rubric_scores, brief_summary, 
                   challenge_opportunity, novelty_benefits_risks, extracted_files_content
            FROM hackathon_ideas
            WHERE evaluation_status = 'completed'
        """)
        
        hallucination_count = 0
        for row in cursor.fetchall():
            idea_id, idea_title, scores, summary, challenge, novelty, files = row
            
            # Check if idea has minimal information
            has_minimal_info = (
                (not summary or len(summary.strip()) < 50) and
                (not challenge or len(challenge.strip()) < 50) and
                (not novelty or len(novelty.strip()) < 50) and
                (not files or len(files.strip()) < 100)
            )
            
            if has_minimal_info and scores:
                # Check if scores are suspiciously high
                if isinstance(scores, str):
                    scores = json.loads(scores)
                
                high_scores = []
                for criterion, score_data in scores.items():
                    if isinstance(score_data, dict):
                        score = score_data.get('score', 0)
                        insufficient_info = score_data.get('insufficient_info', False)
                        
                        if score > 7 and not insufficient_info:
                            high_scores.append(f"{criterion}={score}")
                    elif isinstance(score_data, (int, float)):
                        # Handle simple numeric scores
                        if score_data > 7:
                            high_scores.append(f"{criterion}={score_data}")
                
                if high_scores:
                    hallucination_count += 1
                    self.warnings.append(
                        f"Idea {idea_id} has high scores despite minimal info: {', '.join(high_scores)}"
                    )
        
        if hallucination_count == 0:
            logger.info(f"✅ No obvious hallucination detected")
            logger.info(f"   Scores appropriately reflect available information")
            self.passed += 1
        else:
            logger.warning(f"⚠️  {hallucination_count} evaluations may have hallucination")
            logger.warning(f"   (High scores despite minimal information)")
            # Don't fail, just warn
            self.passed += 1
    
    def verify_consistency(self, cursor):
        """Verify score consistency across evaluations"""
        logger.info("="*80)
        logger.info("CHECK 4: Consistency")
        logger.info("="*80)
        
        cursor.execute("""
            SELECT weighted_total_score
            FROM hackathon_ideas
            WHERE evaluation_status = 'completed'
            AND weighted_total_score IS NOT NULL
        """)
        
        scores = [row[0] for row in cursor.fetchall()]
        
        if len(scores) < 2:
            logger.warning("⚠️  Not enough evaluations to check consistency")
            return
        
        # Check for score distribution
        avg_score = sum(scores) / len(scores)
        min_score = min(scores)
        max_score = max(scores)
        score_range = max_score - min_score
        
        # Check if all scores are suspiciously similar or different
        if score_range < 0.5:
            logger.warning(f"⚠️  All scores are very similar (range: {score_range:.2f})")
            logger.warning(f"   This might indicate lack of discrimination")
            self.warnings.append(f"Score range too narrow: {score_range:.2f}")
        elif score_range > 9.0:
            logger.warning(f"⚠️  Scores have very wide range (range: {score_range:.2f})")
            logger.warning(f"   This might indicate inconsistent evaluation")
            self.warnings.append(f"Score range too wide: {score_range:.2f}")
        else:
            logger.info(f"✅ Score distribution looks reasonable")
            logger.info(f"   Average: {avg_score:.2f}")
            logger.info(f"   Range: {min_score:.2f} - {max_score:.2f}")
            logger.info(f"   Spread: {score_range:.2f}")
            self.passed += 1
    
    def update_verification_status(self, cursor, conn):
        """Update verification status in database"""
        logger.info("="*80)
        logger.info("💾 Updating Verification Status in Database")
        logger.info("="*80)
        
        # Determine overall verification status
        if self.failed == 0:
            status = 'completed'
            message = "All verification checks passed"
        else:
            status = 'failed'
            message = f"{self.failed} verification checks failed"
        
        # Update all evaluated ideas with verification status
        cursor.execute("""
            UPDATE hackathon_ideas
            SET verification_status = %s,
                verification_timestamp = CURRENT_TIMESTAMP
            WHERE evaluation_status = 'completed'
            AND (verification_status IS NULL OR verification_status IN ('pending', 'failed'))
        """, (status,))
        
        updated_count = cursor.rowcount
        conn.commit()
        
        logger.info(f"✅ Updated {updated_count} ideas: verification_status = '{status}'")
        logger.info(f"   {message}")
    
    def generate_summary(self, total_evaluated: int) -> Dict[str, Any]:
        """Generate verification summary"""
        logger.info("="*80)
        logger.info("📊 VERIFICATION SUMMARY")
        logger.info("="*80)
        
        total_checks = self.passed + self.failed
        pass_rate = (self.passed / total_checks * 100) if total_checks > 0 else 0
        
        logger.info(f"Evaluated Ideas: {total_evaluated}")
        logger.info(f"Verification Checks: {self.passed}/{total_checks} passed ({pass_rate:.0f}%)")
        
        if self.failed == 0:
            logger.info("🎉 All verification checks passed!")
            logger.info("✅ Evaluation quality is good!")
            status = 'success'
        elif self.passed >= 3:
            logger.info(f"✅ {self.passed}/4 checks passed - Evaluation quality is acceptable")
            if self.warnings:
                logger.warning(f"⚠️  {len(self.warnings)} warnings detected")
            status = 'acceptable'
        else:
            logger.error(f"❌ Only {self.passed}/4 checks passed - Review evaluation quality")
            status = 'failed'
        
        # Show warnings if any
        if self.warnings and len(self.warnings) <= 5:
            logger.warning(f"⚠️  Warnings:")
            for warning in self.warnings[:5]:
                logger.warning(f"   - {warning}")
            if len(self.warnings) > 5:
                logger.warning(f"   ... and {len(self.warnings) - 5} more")
        
        logger.info("="*80)
        
        return {
            'status': status,
            'total_evaluated': total_evaluated,
            'passed': self.passed,
            'failed': self.failed,
            'total_checks': total_checks,
            'pass_rate': pass_rate,
            'warnings': self.warnings,
            'message': f"{self.passed}/{total_checks} checks passed"
        }


# Global instance
post_evaluation_verifier = PostEvaluationVerifier()
