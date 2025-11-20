"""
Idea Evaluator - Scores hackathon ideas using custom rubrics
"""
import google.generativeai as genai
from typing import Dict, List, Any, Optional
import logging
import json

logger = logging.getLogger(__name__)


class IdeaEvaluator:
    """Evaluates ideas using rubric-based scoring with Gemini AI"""
    
    def __init__(self, rubrics: Dict[str, float], api_key: Optional[str] = None):
        """
        Initialize evaluator with rubrics and Gemini API
        
        Args:
            rubrics: Dictionary of {rubric_name: weight}
            api_key: Optional Gemini API key
        """
        self.rubrics = rubrics
        self.api_key = api_key
        if self.api_key:
            genai.configure(api_key=self.api_key)
        self.model = None
        
    def _ensure_configured(self):
        """Ensure Gemini is configured with API key"""
        if not self.api_key:
            # Fall back to environment variable
            import os
            self.api_key = os.getenv('GEMINI_API_KEY')
            if self.api_key:
                genai.configure(api_key=self.api_key)
                logger.info("Using API key from environment variable")
            else:
                raise ValueError("No Gemini API key available. Set GEMINI_API_KEY in .env file")
        
        if not self.model:
            self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def evaluate_idea(self, idea_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate an idea using configured rubrics
        
        Args:
            idea_data: Dictionary containing:
                - idea_title: str
                - brief_summary: str
                - detailed_description: str
                - extracted_files_content: Optional[str]
                - primary_theme: Optional[str]
                - secondary_themes: Optional[List[str]]
                - industry: Optional[str]
                - technologies: Optional[List[str]]
        
        Returns:
            Dictionary containing:
                - scores: Dict[str, float] - Individual rubric scores (1-10)
                - weighted_total: float - Weighted total score
                - investment_recommendation: str - go/consider-with-mitigations/no-go
                - key_strengths: List[str] - Top 3-5 strengths
                - key_concerns: List[str] - Top 3-5 concerns
        """
        self._ensure_configured()
        
        # Build content for evaluation
        content_parts = []
        content_parts.append(f"Title: {idea_data.get('idea_title', '')}")
        content_parts.append(f"Summary: {idea_data.get('brief_summary', '')}")
        content_parts.append(f"Description: {idea_data.get('detailed_description', '')}")
        
        # Add classification info if available
        if idea_data.get('primary_theme'):
            content_parts.append(f"Primary Theme: {idea_data['primary_theme']}")
        if idea_data.get('secondary_themes'):
            content_parts.append(f"Secondary Themes: {', '.join(idea_data['secondary_themes'])}")
        if idea_data.get('industry'):
            content_parts.append(f"Industry: {idea_data['industry']}")
        if idea_data.get('technologies'):
            content_parts.append(f"Technologies: {', '.join(idea_data['technologies'])}")
        
        # Add extracted content if available
        if idea_data.get('extracted_files_content'):
            content_parts.append(f"Additional Content: {idea_data['extracted_files_content']}")
        
        full_content = "\n\n".join(content_parts)
        
        # Create evaluation prompt
        prompt = self._create_evaluation_prompt(full_content)
        
        try:
            logger.info(f"Evaluating idea: {idea_data.get('idea_title', 'Unknown')}")
            response = self.model.generate_content(prompt)
            
            # Parse response
            result = self._parse_evaluation_response(response.text)
            
            # Calculate weighted total
            weighted_total = self._calculate_weighted_total(result['scores'])
            result['weighted_total'] = weighted_total
            
            # Generate investment recommendation
            result['investment_recommendation'] = self._generate_recommendation(weighted_total, result)
            
            logger.info(f"Evaluation complete: {weighted_total:.2f}/10 - {result['investment_recommendation']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            raise
    
    def _create_evaluation_prompt(self, content: str) -> str:
        """Create prompt for Gemini evaluation"""
        
        rubric_list = "\n".join([
            f"- {name} (weight: {weight})"
            for name, weight in self.rubrics.items()
        ])
        
        prompt = f"""Evaluate the following hackathon idea using the provided rubrics. Score each rubric on a scale of 1-10.

IDEA CONTENT:
{content}

EVALUATION RUBRICS:
{rubric_list}

SCORING GUIDELINES:
- 1-3: Poor - Significant issues, not viable
- 4-5: Below Average - Has potential but major concerns
- 6-7: Good - Solid idea with some areas for improvement
- 8-9: Excellent - Strong idea with minor concerns
- 10: Outstanding - Exceptional idea, ready for investment

INSTRUCTIONS:
1. Score the idea on EACH rubric (1-10 scale)
2. Identify 3-5 key strengths of the idea
3. Identify 3-5 key concerns or areas for improvement
4. Be objective and specific in your assessment
5. Consider feasibility, innovation, impact, and execution

Return your evaluation in the following JSON format:
{{
    "scores": {{
        "rubric_name_1": 8.5,
        "rubric_name_2": 7.0,
        ...
    }},
    "key_strengths": [
        "Strength 1",
        "Strength 2",
        "Strength 3"
    ],
    "key_concerns": [
        "Concern 1",
        "Concern 2",
        "Concern 3"
    ]
}}

IMPORTANT:
- Use exact rubric names from the list above
- Scores must be numbers between 1 and 10 (decimals allowed)
- Provide 3-5 strengths and 3-5 concerns
- Be specific and actionable in your feedback
"""
        return prompt
    
    def _parse_evaluation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini response into structured evaluation"""
        try:
            # Try to extract JSON from response
            response_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            elif response_text.startswith('```'):
                response_text = response_text[3:]
            
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Parse JSON
            result = json.loads(response_text)
            
            # Validate and clean result
            evaluation = {
                'scores': result.get('scores', {}),
                'key_strengths': result.get('key_strengths', []),
                'key_concerns': result.get('key_concerns', [])
            }
            
            # Ensure scores is a dict
            if not isinstance(evaluation['scores'], dict):
                evaluation['scores'] = {}
            
            # Ensure all rubrics have scores
            for rubric_name in self.rubrics.keys():
                if rubric_name not in evaluation['scores']:
                    logger.warning(f"Missing score for rubric: {rubric_name}, defaulting to 5.0")
                    evaluation['scores'][rubric_name] = 5.0
                else:
                    # Ensure score is a number and within range
                    try:
                        score = float(evaluation['scores'][rubric_name])
                        score = max(1.0, min(10.0, score))  # Clamp to 1-10
                        evaluation['scores'][rubric_name] = score
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid score for {rubric_name}, defaulting to 5.0")
                        evaluation['scores'][rubric_name] = 5.0
            
            # Ensure strengths and concerns are lists
            if not isinstance(evaluation['key_strengths'], list):
                evaluation['key_strengths'] = []
            if not isinstance(evaluation['key_concerns'], list):
                evaluation['key_concerns'] = []
            
            return evaluation
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response_text}")
            # Return default evaluation
            return {
                'scores': {rubric: 5.0 for rubric in self.rubrics.keys()},
                'key_strengths': [],
                'key_concerns': ['Failed to parse evaluation response']
            }
        except Exception as e:
            logger.error(f"Unexpected error parsing response: {e}")
            return {
                'scores': {rubric: 5.0 for rubric in self.rubrics.keys()},
                'key_strengths': [],
                'key_concerns': ['Evaluation error occurred']
            }
    
    def _calculate_weighted_total(self, scores: Dict[str, float]) -> float:
        """Calculate weighted total score"""
        total_weight = sum(self.rubrics.values())
        if total_weight == 0:
            return 0.0
        
        weighted_sum = sum(
            scores.get(rubric, 5.0) * weight
            for rubric, weight in self.rubrics.items()
        )
        
        return weighted_sum / total_weight
    
    def _generate_recommendation(self, weighted_total: float, evaluation: Dict[str, Any]) -> str:
        """
        Generate investment recommendation based on score and evaluation
        
        Returns: 'go', 'consider-with-mitigations', or 'no-go'
        """
        # Base recommendation on weighted total
        if weighted_total >= 7.5:
            return 'go'
        elif weighted_total >= 5.5:
            return 'consider-with-mitigations'
        else:
            return 'no-go'
    
    def batch_evaluate(self, ideas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Evaluate multiple ideas
        
        Args:
            ideas: List of idea dictionaries
        
        Returns:
            List of evaluation results
        """
        results = []
        for idea in ideas:
            try:
                result = self.evaluate_idea(idea)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to evaluate idea {idea.get('id')}: {e}")
                results.append({
                    'scores': {rubric: 5.0 for rubric in self.rubrics.keys()},
                    'weighted_total': 5.0,
                    'investment_recommendation': 'no-go',
                    'key_strengths': [],
                    'key_concerns': [f'Evaluation failed: {str(e)}'],
                    'error': str(e)
                })
        return results
