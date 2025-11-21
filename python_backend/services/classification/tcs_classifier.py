"""
TCS Classifier - Classifies hackathon ideas into themes and industries
"""
from typing import Dict, List, Any, Optional
import logging
import json
import asyncio
from .theme_definitions import THEME_TAXONOMY
from services.llm_service import llm_service

logger = logging.getLogger(__name__)


class TCSClassifier:
    """Classifies ideas into TCS themes, industries, and technologies"""
    
    def __init__(
        self, 
        provider: Optional[str] = None, 
        model_name: Optional[str] = None,
        model_settings: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize classifier with LLM service
        
        Args:
            provider: LLM provider (gemini, azure_openai, openai, etc.)
            model_name: Model name to use
            model_settings: Model configuration settings (api_key, endpoint, etc.)
        """
        self.provider = provider or 'gemini'
        self.model_name = model_name or 'gemini-2.0-flash-exp'
        self.model_settings = model_settings or {}
        
    def _ensure_configured(self):
        """Validate configuration"""
        if not self.model_settings.get('api_key'):
            # Fall back to environment variable
            import os
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                self.model_settings['api_key'] = api_key
                logger.info("Using API key from environment variable")
            else:
                raise ValueError("No API key available. Configure model settings or set GEMINI_API_KEY in .env file")
    
    def classify_idea(self, idea_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify an idea into themes, industry, and technologies
        
        Args:
            idea_data: Dictionary containing:
                - idea_title: str
                - brief_summary: str
                - detailed_description: str
                - extracted_files_content: Optional[str]
                - content_type: Optional[str]
        
        Returns:
            Dictionary containing:
                - primary_theme: str
                - secondary_themes: List[str]
                - industry: str
                - technologies: List[str]
        """
        self._ensure_configured()
        
        # Build content for classification
        content_parts = []
        content_parts.append(f"Title: {idea_data.get('idea_title', '')}")
        content_parts.append(f"Summary: {idea_data.get('brief_summary', '')}")
        content_parts.append(f"Description: {idea_data.get('detailed_description', '')}")
        
        # Add extracted content if available
        if idea_data.get('extracted_files_content'):
            content_parts.append(f"Additional Content: {idea_data['extracted_files_content']}")
        
        full_content = "\n\n".join(content_parts)
        
        # Create classification prompt
        prompt = self._create_classification_prompt(full_content)
        
        try:
            logger.info(f"Classifying idea: {idea_data.get('idea_title', 'Unknown')}")
            
            # Use LLM service for classification
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(
                    llm_service.chat_completion(
                        provider=self.provider,
                        model_name=self.model_name,
                        messages=[{"role": "user", "content": prompt}],
                        settings=self.model_settings,
                        temperature=0.3,
                        max_tokens=1000
                    )
                )
            finally:
                loop.close()
            
            if not response.get('success'):
                raise Exception(response.get('error', 'Unknown error'))
            
            # Parse response
            response_text = response['choices'][0]['message']['content']
            result = self._parse_classification_response(response_text)
            logger.info(f"Classification complete: {result.get('primary_theme')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            raise
    
    def _create_classification_prompt(self, content: str) -> str:
        """Create prompt for Gemini classification"""
        
        # Get theme list
        themes = list(THEME_TAXONOMY.keys())
        theme_descriptions = "\n".join([
            f"- {theme}: {THEME_TAXONOMY[theme]['description']}"
            for theme in themes
        ])
        
        # Industries
        industries = [
            "BFSI (Banking, Financial Services, Insurance)",
            "CMT (Communications, Media, Technology)",
            "Healthcare & Life Sciences",
            "Manufacturing",
            "Retail & Consumer Goods",
            "Energy & Utilities",
            "Public Services & Government",
            "Other"
        ]
        
        prompt = f"""Analyze the following hackathon idea and classify it according to TCS themes, industry, and technologies.

IDEA CONTENT:
{content}

AVAILABLE THEMES:
{theme_descriptions}

AVAILABLE INDUSTRIES:
{chr(10).join([f"- {ind}" for ind in industries])}

INSTRUCTIONS:
1. Select ONE primary theme that best represents the core focus of the idea
2. Select 0-3 secondary themes that are also relevant (can be empty if idea is focused on one theme)
3. Select ONE primary industry that would benefit most from this idea
4. Extract 3-7 specific technologies, tools, frameworks, or platforms mentioned or implied in the idea

Return your analysis in the following JSON format:
{{
    "primary_theme": "theme name",
    "secondary_themes": ["theme1", "theme2"],
    "industry": "industry name",
    "technologies": ["tech1", "tech2", "tech3"]
}}

IMPORTANT:
- Use exact theme names from the list above
- Use exact industry names from the list above
- Be specific with technologies (e.g., "TensorFlow" not just "AI")
- Secondary themes should be genuinely relevant, not just loosely related
- If no secondary themes are strongly relevant, return empty array
"""
        return prompt
    
    def _parse_classification_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini response into structured classification"""
        try:
            # Try to extract JSON from response
            # Sometimes Gemini wraps JSON in markdown code blocks
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
            classification = {
                'primary_theme': result.get('primary_theme', 'Other'),
                'secondary_themes': result.get('secondary_themes', []),
                'industry': result.get('industry', 'Other'),
                'technologies': result.get('technologies', [])
            }
            
            # Ensure secondary_themes is a list
            if not isinstance(classification['secondary_themes'], list):
                classification['secondary_themes'] = []
            
            # Ensure technologies is a list
            if not isinstance(classification['technologies'], list):
                classification['technologies'] = []
            
            # Validate primary theme exists in taxonomy
            if classification['primary_theme'] not in THEME_TAXONOMY:
                logger.warning(f"Invalid primary theme: {classification['primary_theme']}, defaulting to 'Other'")
                classification['primary_theme'] = 'Other'
            
            # Validate secondary themes
            valid_secondary = [
                theme for theme in classification['secondary_themes']
                if theme in THEME_TAXONOMY
            ]
            classification['secondary_themes'] = valid_secondary
            
            return classification
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response_text}")
            # Return default classification
            return {
                'primary_theme': 'Other',
                'secondary_themes': [],
                'industry': 'Other',
                'technologies': []
            }
        except Exception as e:
            logger.error(f"Unexpected error parsing response: {e}")
            return {
                'primary_theme': 'Other',
                'secondary_themes': [],
                'industry': 'Other',
                'technologies': []
            }
    
    def batch_classify(self, ideas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Classify multiple ideas
        
        Args:
            ideas: List of idea dictionaries
        
        Returns:
            List of classification results
        """
        results = []
        for idea in ideas:
            try:
                result = self.classify_idea(idea)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to classify idea {idea.get('id')}: {e}")
                results.append({
                    'primary_theme': 'Other',
                    'secondary_themes': [],
                    'industry': 'Other',
                    'technologies': [],
                    'error': str(e)
                })
        return results
