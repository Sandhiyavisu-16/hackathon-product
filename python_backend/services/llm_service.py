"""
LLM Service - Multi-provider LLM integration using LiteLLM
Supports 100+ LLM providers through a unified interface
"""
from typing import Dict, List, Any, Optional
import litellm
from litellm import completion, acompletion
import json
import os


class LLMService:
    """
    Unified LLM service using LiteLLM
    Supports: OpenAI, Azure OpenAI, Google Gemini, Anthropic Claude, and 100+ more providers
    """
    
    def __init__(self):
        # Configure LiteLLM
        litellm.drop_params = True  # Drop unsupported params instead of erroring
        litellm.set_verbose = False  # Disable verbose logging
    
    def _build_model_string(
        self,
        provider: str,
        model_name: str,
        settings: Dict[str, Any]
    ) -> str:
        """
        Build LiteLLM model string based on provider
        
        LiteLLM uses format: provider/deployment_name
        For Azure, we need the deployment name from settings
        """
        provider_lower = provider.lower()
        
        # Azure OpenAI - use deployment name if available
        if 'azure' in provider_lower:
            # Azure needs deployment name, not model name
            deployment = settings.get('deployment_name') or settings.get('model') or model_name
            return f"azure/{deployment}"
        
        # Google Gemini
        elif 'gemini' in provider_lower or 'google' in provider_lower:
            return f"gemini/{model_name}"
        
        # Anthropic Claude
        elif 'claude' in provider_lower or 'anthropic' in provider_lower:
            return model_name  # Claude models don't need prefix
        
        # OpenAI
        elif 'openai' in provider_lower or 'gpt' in provider_lower:
            return model_name  # OpenAI models don't need prefix
        
        # Default
        else:
            return model_name
    
    def _prepare_env_vars(self, provider: str, settings: Dict[str, Any]):
        """
        Set environment variables required by LiteLLM for the provider
        """
        provider_lower = provider.lower()
        
        # Azure OpenAI
        if 'azure' in provider_lower:
            if settings.get('api_key'):
                os.environ['AZURE_API_KEY'] = settings['api_key']
            # Get endpoint from any of these keys
            endpoint = settings.get('azure_endpoint') or settings.get('endpoint') or settings.get('api_base')
            if endpoint:
                os.environ['AZURE_API_BASE'] = endpoint
            if settings.get('api_version'):
                os.environ['AZURE_API_VERSION'] = settings['api_version']
        
        # Google Gemini
        elif 'gemini' in provider_lower or 'google' in provider_lower:
            if settings.get('api_key'):
                os.environ['GEMINI_API_KEY'] = settings['api_key']
        
        # Anthropic Claude
        elif 'claude' in provider_lower or 'anthropic' in provider_lower:
            if settings.get('api_key'):
                os.environ['ANTHROPIC_API_KEY'] = settings['api_key']
        
        # OpenAI
        elif 'openai' in provider_lower or 'gpt' in provider_lower:
            if settings.get('api_key'):
                os.environ['OPENAI_API_KEY'] = settings['api_key']
    
    async def test_model(
        self,
        provider: str,
        model_name: str,
        settings: Dict[str, Any],
        prompt: str = "Hello, this is a test message. Please respond with 'Test successful'."
    ) -> Dict[str, Any]:
        """
        Test a model configuration using LiteLLM
        
        Args:
            provider: Provider name (azure_openai, gemini, claude, etc.)
            model_name: Model identifier
            settings: Provider settings (api_key, api_base, etc.)
            prompt: Test prompt
        
        Returns:
            Dict with success status and response or error
        """
        try:
            print(f"[LLM Service] Testing model: {model_name}")
            print(f"[LLM Service] Provider: {provider}")
            print(f"[LLM Service] Settings keys: {list(settings.keys())}")
            
            # Validate required settings for Azure
            if 'azure' in provider.lower():
                if not settings.get('api_key'):
                    return {
                        'success': False,
                        'message': 'Azure API key is required',
                        'error': 'Missing api_key in settings'
                    }
                # Check for endpoint in any of these keys
                if not (settings.get('api_base') or settings.get('azure_endpoint') or settings.get('endpoint')):
                    return {
                        'success': False,
                        'message': 'Azure endpoint is required',
                        'error': 'Missing api_base, azure_endpoint, or endpoint in settings'
                    }
            
            # Prepare environment variables
            self._prepare_env_vars(provider, settings)
            
            # Build model string
            model_string = self._build_model_string(provider, model_name, settings)
            print(f"[LLM Service] Model string: {model_string}")
            
            # Prepare kwargs for LiteLLM
            kwargs = {
                'model': model_string,
                'messages': [{"role": "user", "content": prompt}],
                'max_tokens': 100,
                'temperature': 0.7
            }
            
            # Add provider-specific parameters
            if 'azure' in provider.lower():
                # Get endpoint from any of these keys
                endpoint = settings.get('azure_endpoint') or settings.get('endpoint') or settings.get('api_base')
                
                # Azure requires api_base and api_version
                if endpoint:
                    kwargs['api_base'] = endpoint
                
                if settings.get('api_version'):
                    kwargs['api_version'] = settings['api_version']
                
                print(f"[LLM Service] Azure kwargs: {kwargs}")
            
            # Send test message using LiteLLM
            response = await acompletion(**kwargs)
            
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
        settings: Dict[str, Any],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send a chat completion request using LiteLLM
        
        Args:
            provider: Provider name
            model_name: Model identifier
            messages: List of message dicts with 'role' and 'content'
            settings: Provider settings (api_key, api_base, etc.)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
        
        Returns:
            Dict with response or error
        """
        try:
            # Prepare environment variables
            self._prepare_env_vars(provider, settings)
            
            # Build model string
            model_string = self._build_model_string(provider, model_name, settings)
            
            # Prepare kwargs for LiteLLM
            litellm_kwargs = {
                'model': model_string,
                'messages': messages,
                'temperature': temperature,
                'max_tokens': max_tokens,
                **kwargs
            }
            
            # Add provider-specific parameters
            if 'azure' in provider.lower():
                # Get endpoint from any of these keys
                endpoint = settings.get('azure_endpoint') or settings.get('endpoint') or settings.get('api_base')
                
                # Azure requires api_base and api_version
                if endpoint:
                    litellm_kwargs['api_base'] = endpoint
                
                if settings.get('api_version'):
                    litellm_kwargs['api_version'] = settings['api_version']
            
            # Send request using LiteLLM
            response = await acompletion(**litellm_kwargs)
            
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
        settings: Dict[str, Any],
        idea_title: str,
        idea_summary: str,
        rubric_criteria: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Score an idea using LLM based on rubric criteria
        
        Args:
            provider: Provider name
            model_name: Model identifier
            settings: Provider settings (api_key, api_base, etc.)
            idea_title: Title of the idea
            idea_summary: Summary/description of the idea
            rubric_criteria: List of rubric criteria with name, description, scale
        
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
            settings=settings,
            temperature=0.3,  # Lower temperature for more consistent scoring
            max_tokens=2000
        )
        
        if result['success']:
            try:
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
