"""
LLM Service - Unified interface for multiple LLM providers
Uses OpenAI SDK for compatibility across providers
"""
from typing import Dict, List, Any, Optional
import openai
from openai import OpenAI, AzureOpenAI


class LLMService:
    """
    Unified LLM service supporting multiple providers:
    - OpenAI (GPT models)
    - Azure OpenAI
    - Google Gemini
    - Anthropic Claude
    - Custom endpoints
    """
    
    def __init__(self):
        self.clients: Dict[str, Any] = {}
    
    def get_client(
        self,
        provider: str,
        api_key: str,
        api_base: Optional[str] = None,
        api_version: Optional[str] = None,
        azure_endpoint: Optional[str] = None
    ) -> OpenAI:
        """
        Get or create a client for the specified provider
        
        Args:
            provider: Provider name (openai, azure, gemini, claude, etc.)
            api_key: API key for the provider
            api_base: Base URL for API (optional)
            api_version: API version (for Azure)
            azure_endpoint: Azure endpoint URL
        
        Returns:
            OpenAI-compatible client
        """
        provider_lower = provider.lower()
        
        # Azure OpenAI
        if 'azure' in provider_lower:
            return AzureOpenAI(
                api_key=api_key,
                api_version=api_version or "2024-02-15-preview",
                azure_endpoint=azure_endpoint or api_base
            )
        
        # Google Gemini (using OpenAI-compatible endpoint)
        elif 'gemini' in provider_lower or 'google' in provider_lower:
            return OpenAI(
                api_key=api_key,
                base_url=api_base or "https://generativelanguage.googleapis.com/v1beta/openai/"
            )
        
        # Anthropic Claude (using OpenAI-compatible endpoint)
        elif 'claude' in provider_lower or 'anthropic' in provider_lower:
            return OpenAI(
                api_key=api_key,
                base_url=api_base or "https://api.anthropic.com/v1"
            )
        
        # OpenAI (default)
        elif 'openai' in provider_lower or 'gpt' in provider_lower:
            return OpenAI(api_key=api_key)
        
        # Custom endpoint
        else:
            return OpenAI(
                api_key=api_key,
                base_url=api_base
            )
    
    async def test_model(
        self,
        provider: str,
        model_name: str,
        api_key: str,
        api_base: Optional[str] = None,
        api_version: Optional[str] = None,
        azure_endpoint: Optional[str] = None,
        prompt: str = "Hello, this is a test message. Please respond with 'Test successful'."
    ) -> Dict[str, Any]:
        """
        Test a model configuration
        
        Args:
            provider: Provider name
            model_name: Model identifier
            api_key: API key
            api_base: Base URL (optional)
            api_version: API version (optional)
            azure_endpoint: Azure endpoint (optional)
            prompt: Test prompt
        
        Returns:
            Dict with success status and response or error
        """
        try:
            # Get client
            client = self.get_client(
                provider=provider,
                api_key=api_key,
                api_base=api_base,
                api_version=api_version,
                azure_endpoint=azure_endpoint
            )
            
            # Send test message
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )
            
            # Check if response is valid
            if response and response.choices and len(response.choices) > 0:
                return {
                    'success': True,
                    'message': f"Model '{model_name}' responded correctly!",
                    'response': response.choices[0].message.content,
                    'model': response.model,
                    'usage': {
                        'prompt_tokens': response.usage.prompt_tokens if response.usage else 0,
                        'completion_tokens': response.usage.completion_tokens if response.usage else 0,
                        'total_tokens': response.usage.total_tokens if response.usage else 0
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f"Model '{model_name}' did not return a valid response.",
                    'error': 'Invalid response format'
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to test model '{model_name}'",
                'error': str(e)
            }
    
    async def chat_completion(
        self,
        provider: str,
        model_name: str,
        messages: List[Dict[str, str]],
        api_key: str,
        api_base: Optional[str] = None,
        api_version: Optional[str] = None,
        azure_endpoint: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send a chat completion request
        
        Args:
            provider: Provider name
            model_name: Model identifier
            messages: List of message dicts with 'role' and 'content'
            api_key: API key
            api_base: Base URL (optional)
            api_version: API version (optional)
            azure_endpoint: Azure endpoint (optional)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
        
        Returns:
            Dict with response or error
        """
        try:
            # Get client
            client = self.get_client(
                provider=provider,
                api_key=api_key,
                api_base=api_base,
                api_version=api_version,
                azure_endpoint=azure_endpoint
            )
            
            # Send request
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            # Return response
            return {
                'success': True,
                'id': response.id,
                'model': response.model,
                'choices': [
                    {
                        'index': choice.index,
                        'message': {
                            'role': choice.message.role,
                            'content': choice.message.content
                        },
                        'finish_reason': choice.finish_reason
                    }
                    for choice in response.choices
                ],
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens if response.usage else 0,
                    'completion_tokens': response.usage.completion_tokens if response.usage else 0,
                    'total_tokens': response.usage.total_tokens if response.usage else 0
                }
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def score_idea(
        self,
        provider: str,
        model_name: str,
        api_key: str,
        idea_title: str,
        idea_summary: str,
        rubric_criteria: List[Dict[str, Any]],
        api_base: Optional[str] = None,
        api_version: Optional[str] = None,
        azure_endpoint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Score an idea using LLM based on rubric criteria
        
        Args:
            provider: Provider name
            model_name: Model identifier
            api_key: API key
            idea_title: Title of the idea
            idea_summary: Summary/description of the idea
            rubric_criteria: List of rubric criteria with name, description, scale
            api_base: Base URL (optional)
            api_version: API version (optional)
            azure_endpoint: Azure endpoint (optional)
        
        Returns:
            Dict with scores and feedback
        """
        # Build prompt
        criteria_text = "\n".join([
            f"- {c['name']}: {c['description']} (Scale: {c['scale_min']}-{c['scale_max']})"
            for c in rubric_criteria
        ])
        
        prompt = f"""
You are an expert evaluator. Please score the following idea based on the given criteria.

Idea Title: {idea_title}
Idea Summary: {idea_summary}

Evaluation Criteria:
{criteria_text}

Please provide:
1. A score for each criterion (within the specified scale)
2. Brief feedback explaining each score
3. Overall feedback and suggestions for improvement

Format your response as JSON with this structure:
{{
    "scores": {{
        "criterion_name": score,
        ...
    }},
    "feedback": {{
        "criterion_name": "explanation",
        ...
    }},
    "overall_feedback": "overall assessment and suggestions"
}}
"""
        
        # Send request
        result = await self.chat_completion(
            provider=provider,
            model_name=model_name,
            messages=[{"role": "user", "content": prompt}],
            api_key=api_key,
            api_base=api_base,
            api_version=api_version,
            azure_endpoint=azure_endpoint,
            temperature=0.3,  # Lower temperature for more consistent scoring
            max_tokens=2000
        )
        
        if result['success']:
            try:
                import json
                # Extract JSON from response
                content = result['choices'][0]['message']['content']
                
                # Try to parse JSON (handle markdown code blocks)
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0].strip()
                elif '```' in content:
                    content = content.split('```')[1].split('```')[0].strip()
                
                scoring_result = json.loads(content)
                
                return {
                    'success': True,
                    'scores': scoring_result.get('scores', {}),
                    'feedback': scoring_result.get('feedback', {}),
                    'overall_feedback': scoring_result.get('overall_feedback', ''),
                    'usage': result.get('usage', {})
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Failed to parse scoring response: {str(e)}",
                    'raw_response': result['choices'][0]['message']['content']
                }
        else:
            return result


# Global instance
llm_service = LLMService()
