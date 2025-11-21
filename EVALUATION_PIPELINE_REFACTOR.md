# Evaluation Pipeline Refactor - Multi-Provider Support

## Summary
Refactored the evaluation pipeline to support any LLM provider (not just Gemini) using the existing LLM service with LiteLLM integration.

## Changes Made

### 1. evaluation_service.py
- Updated `get_evaluation_model_config()` to return full config including provider and settings
- Now returns: `{provider, model_name, settings}` instead of just `{api_key, model_name}`
- Passes provider and settings to orchestrator instead of just API key

### 2. orchestrator.py
- Updated `__init__` to accept `provider`, `model_name`, and `model_settings` instead of `api_key`
- Passes these parameters to both classification and evaluation pipelines
- Made `file_extractor` optional (only needed for vision tasks)

### 3. classification_pipeline.py
- Updated to accept `provider`, `model_name`, and `model_settings`
- Passes these to TCSClassifier

### 4. tcs_classifier.py
- **Major refactor**: Removed direct Gemini API calls
- Now uses `llm_service.chat_completion()` for provider-agnostic classification
- Accepts `provider`, `model_name`, and `model_settings` in constructor
- Uses asyncio event loop to call async LLM service from sync context

### 5. evaluation_pipeline.py
- Updated to accept `provider`, `model_name`, and `model_settings`
- Passes these to IdeaEvaluator

### 6. idea_evaluator.py
- **Major refactor**: Removed direct Gemini API calls
- Now uses `llm_service.chat_completion()` for provider-agnostic evaluation
- Accepts `provider`, `model_name`, and `model_settings` in constructor
- Uses asyncio event loop to call async LLM service from sync context

## Benefits

1. **Multi-Provider Support**: Can now use any LLM provider supported by LiteLLM:
   - Google Gemini
   - Azure OpenAI
   - OpenAI
   - Anthropic Claude
   - 100+ other providers

2. **Centralized Configuration**: All LLM calls go through the LLM service, making it easier to:
   - Add retry logic
   - Monitor usage
   - Switch providers
   - Handle rate limits

3. **Model Config Integration**: Fully integrated with the model configuration system:
   - Activate any model config with `purpose='evaluation'`
   - System automatically uses that config for all evaluation tasks
   - Falls back to environment variables if no config is active

## Usage

To use the evaluation pipeline with a specific provider:

1. Go to Model Configuration UI
2. Create a configuration for your desired provider (Gemini, Azure OpenAI, etc.)
3. Enter the required settings (API key, endpoint, etc.)
4. Activate it with `purpose='evaluation'`
5. Run the evaluation pipeline - it will automatically use your configured model

## Backward Compatibility

- Still supports fallback to `GEMINI_API_KEY` environment variable if no model config is active
- Existing Gemini configurations will continue to work

## Technical Notes

- Uses `asyncio.new_event_loop()` to call async LLM service from sync pipeline code
- Properly closes event loops to prevent resource leaks
- Maintains same error handling and retry logic as before
