# """
# TCS Classifier - Classifies hackathon ideas into themes and industries
# """
# from typing import Dict, List, Any, Optional
# import logging
# import json
# import asyncio
# from .theme_definitions import THEME_TAXONOMY
# from services.llm_service import llm_service

# logger = logging.getLogger(__name__)


# class TCSClassifier:
#     """Classifies ideas into TCS themes, industries, and technologies"""
    
#     def __init__(
#         self, 
#         provider: Optional[str] = None, 
#         model_name: Optional[str] = None,
#         model_settings: Optional[Dict[str, Any]] = None
#     ):
#         """
#         Initialize classifier with LLM service
        
#         Args:
#             provider: LLM provider (gemini, azure_openai, openai, etc.)
#             model_name: Model name to use
#             model_settings: Model configuration settings (api_key, endpoint, etc.)
#         """
#         self.provider = provider or 'gemini'
#         self.model_name = model_name or 'gemini-2.0-flash-exp'
#         self.model_settings = model_settings or {}
        
#     def _ensure_configured(self):
#         """Validate configuration"""
#         if not self.model_settings.get('api_key'):
#             # Fall back to environment variable
#             import os
#             api_key = os.getenv('GEMINI_API_KEY')
#             if api_key:
#                 self.model_settings['api_key'] = api_key
#                 logger.info("Using API key from environment variable")
#             else:
#                 raise ValueError("No API key available. Configure model settings or set GEMINI_API_KEY in .env file")
    
#     def classify_idea(self, idea_data: Dict[str, Any]) -> Dict[str, Any]:
#         """
#         Classify an idea into themes, industry, and technologies
        
#         Args:
#             idea_data: Dictionary containing:
#                 - idea_title: str
#                 - brief_summary: str
#                 - detailed_description: str
#                 - extracted_files_content: Optional[str]
#                 - content_type: Optional[str]
        
#         Returns:
#             Dictionary containing:
#                 - primary_theme: str
#                 - secondary_themes: List[str]
#                 - industry: str
#                 - technologies: List[str]
#         """
#         self._ensure_configured()
        
#         # Build content for classification
#         content_parts = []
#         content_parts.append(f"Title: {idea_data.get('idea_title', '')}")
#         content_parts.append(f"Summary: {idea_data.get('brief_summary', '')}")
#         content_parts.append(f"Description: {idea_data.get('detailed_description', '')}")
        
#         # Add extracted content if available
#         if idea_data.get('extracted_files_content'):
#             content_parts.append(f"Additional Content: {idea_data['extracted_files_content']}")
        
#         full_content = "\n\n".join(content_parts)
        
#         # Create classification prompt
#         prompt = self._create_classification_prompt(full_content)
        
#         try:
#             logger.info(f"Classifying idea: {idea_data.get('idea_title', 'Unknown')}")
            
#             # Use LLM service for classification
#             loop = asyncio.new_event_loop()
#             asyncio.set_event_loop(loop)
#             try:
#                 response = loop.run_until_complete(
#                     llm_service.chat_completion(
#                         provider=self.provider,
#                         model_name=self.model_name,
#                         messages=[{"role": "user", "content": prompt}],
#                         settings=self.model_settings,
#                         temperature=0.3,
#                         max_tokens=1000
#                     )
#                 )
#             finally:
#                 loop.close()
            
#             if not response.get('success'):
#                 raise Exception(response.get('error', 'Unknown error'))
            
#             # Parse response
#             response_text = response['choices'][0]['message']['content']
#             result = self._parse_classification_response(response_text)
#             logger.info(f"Classification complete: {result.get('primary_theme')}")
            
#             return result
            
#         except Exception as e:
#             logger.error(f"Classification failed: {e}")
#             raise
    
#     def _create_classification_prompt(self, content: str) -> str:
#         """Create prompt for Gemini classification"""
        
#         # Get theme list
#         themes = list(THEME_TAXONOMY.keys())
#         theme_descriptions = "\n".join([
#             f"- {theme}: {THEME_TAXONOMY[theme]['description']}"
#             for theme in themes
#         ])
        
#         # Industries
#         industries = [
#             "BFSI (Banking, Financial Services, Insurance)",
#             "CMT (Communications, Media, Technology)",
#             "Healthcare & Life Sciences",
#             "Manufacturing",
#             "Retail & Consumer Goods",
#             "Energy & Utilities",
#             "Public Services & Government",
#             "Other"
#         ]
        
#         prompt = f"""Analyze the following hackathon idea and classify it according to TCS themes, industry, and technologies.

# IDEA CONTENT:
# {content}

# AVAILABLE THEMES:
# {theme_descriptions}

# AVAILABLE INDUSTRIES:
# {chr(10).join([f"- {ind}" for ind in industries])}

# INSTRUCTIONS:
# 1. Select ONE primary theme that best represents the core focus of the idea
# 2. Select 0-3 secondary themes that are also relevant (can be empty if idea is focused on one theme)
# 3. Select ONE primary industry that would benefit most from this idea
# 4. Extract 3-7 specific technologies, tools, frameworks, or platforms mentioned or implied in the idea

# Return your analysis in the following JSON format:
# {{
#     "primary_theme": "theme name",
#     "secondary_themes": ["theme1", "theme2"],
#     "industry": "industry name",
#     "technologies": ["tech1", "tech2", "tech3"]
# }}

# IMPORTANT:
# - Use exact theme names from the list above
# - Use exact industry names from the list above
# - Be specific with technologies (e.g., "TensorFlow" not just "AI")
# - Secondary themes should be genuinely relevant, not just loosely related
# - If no secondary themes are strongly relevant, return empty array
# """
#         return prompt
    
#     def _parse_classification_response(self, response_text: str) -> Dict[str, Any]:
#         """Parse Gemini response into structured classification"""
#         try:
#             # Try to extract JSON from response
#             # Sometimes Gemini wraps JSON in markdown code blocks
#             response_text = response_text.strip()
            
#             # Remove markdown code blocks if present
#             if response_text.startswith('```json'):
#                 response_text = response_text[7:]
#             elif response_text.startswith('```'):
#                 response_text = response_text[3:]
            
#             if response_text.endswith('```'):
#                 response_text = response_text[:-3]
            
#             response_text = response_text.strip()
            
#             # Parse JSON
#             result = json.loads(response_text)
            
#             # Validate and clean result
#             classification = {
#                 'primary_theme': result.get('primary_theme', 'Other'),
#                 'secondary_themes': result.get('secondary_themes', []),
#                 'industry': result.get('industry', 'Other'),
#                 'technologies': result.get('technologies', [])
#             }
            
#             # Ensure secondary_themes is a list
#             if not isinstance(classification['secondary_themes'], list):
#                 classification['secondary_themes'] = []
            
#             # Ensure technologies is a list
#             if not isinstance(classification['technologies'], list):
#                 classification['technologies'] = []
            
#             # Validate primary theme exists in taxonomy
#             if classification['primary_theme'] not in THEME_TAXONOMY:
#                 logger.warning(f"Invalid primary theme: {classification['primary_theme']}, defaulting to 'Other'")
#                 classification['primary_theme'] = 'Other'
            
#             # Validate secondary themes
#             valid_secondary = [
#                 theme for theme in classification['secondary_themes']
#                 if theme in THEME_TAXONOMY
#             ]
#             classification['secondary_themes'] = valid_secondary
            
#             return classification
            
#         except json.JSONDecodeError as e:
#             logger.error(f"Failed to parse JSON response: {e}")
#             logger.error(f"Response text: {response_text}")
#             # Return default classification
#             return {
#                 'primary_theme': 'Other',
#                 'secondary_themes': [],
#                 'industry': 'Other',
#                 'technologies': []
#             }
#         except Exception as e:
#             logger.error(f"Unexpected error parsing response: {e}")
#             return {
#                 'primary_theme': 'Other',
#                 'secondary_themes': [],
#                 'industry': 'Other',
#                 'technologies': []
#             }
    
#     def batch_classify(self, ideas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#         """
#         Classify multiple ideas
        
#         Args:
#             ideas: List of idea dictionaries
        
#         Returns:
#             List of classification results
#         """
#         results = []
#         for idea in ideas:
#             try:
#                 result = self.classify_idea(idea)
#                 results.append(result)
#             except Exception as e:
#                 logger.error(f"Failed to classify idea {idea.get('id')}: {e}")
#                 results.append({
#                     'primary_theme': 'Other',
#                     'secondary_themes': [],
#                     'industry': 'Other',
#                     'technologies': [],
#                     'error': str(e)
#                 })
#         return results
"""
Innovation Idea Classifier
Classifies ideas into AI Themes, Industries, and extracts Technologies
Uses Azure OpenAI for classification
"""
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from .theme_definitions import THEME_TAXONOMY

logger = logging.getLogger(__name__)

# Try to import LLM service
try:
    from services.llm_service import llm_service
    LLM_SERVICE_AVAILABLE = True
except Exception as e:
    logger.warning(f"LLM service not available in TCS classifier: {e}")
    llm_service = None
    LLM_SERVICE_AVAILABLE = False


# ---------- Data Models ----------
@dataclass
class ThemeClassification:
    primary_theme: str
    secondary_themes: List[str]
    confidence: float
    rationale: str


@dataclass
class IndustryClassification:
    industry_name: str
    confidence: float
    rationale: str


@dataclass
class TechnologyExtraction:
    technologies_extracted: List[str]
    rationale: str


# ---------- Main Class ----------
class TCSClassifier:
    """Main classifier for innovation ideas using Azure OpenAI"""
    
    # AI Themes from comprehensive definitions
    AI_THEMES = list(THEME_TAXONOMY.keys())
    
    INDUSTRIES = {
        "I1": "Banking, Financial Services & Insurance (BFSI)",
        "I2": "Communication, Media & Technology (CMT)",
        "I3": "Consumer Business (Retail & CPG)",
        "I4": "Life Sciences & Healthcare (LSH)",
        "I5": "Manufacturing (MFG)",
        "I6": "Energy, Resources & Utilities (ERU)",
        "I7": "Travel, Transportation & Hospitality (TTH)",
        "I8": "Technology, Software & Services (TechSS)"
    }
    
    def __init__(
        self,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        model_settings: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Azure OpenAI classifier
        
        Args:
            provider: LLM provider (azure_openai, gemini, openai, etc.)
            model_name: Model/deployment name
            model_settings: Configuration (api_key, endpoint, api_version, etc.)
        """
        self.provider = provider or 'azure_openai'
        self.model_name = model_name or 'gpt-4'
        self.model_settings = model_settings or {}
        
    def _ensure_configured(self):
        """Validate configuration"""
        if not self.model_settings.get('api_key'):
            # Fall back to environment variable
            import os
            if 'azure' in self.provider.lower():
                api_key = os.getenv('AZURE_API_KEY')
            elif 'gemini' in self.provider.lower():
                api_key = os.getenv('GEMINI_API_KEY')
            else:
                api_key = os.getenv('OPENAI_API_KEY')
                
            if api_key:
                self.model_settings['api_key'] = api_key
                logger.info("Using API key from environment variable")
            else:
                raise ValueError(f"No API key available for {self.provider}. Configure model settings or set environment variable")
    
    def _parse_json(self, response: str) -> Dict:
        """Safely parse JSON from LLM output"""
        try:
            # Remove markdown code blocks if present
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            elif response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()
            
            data = json.loads(response)
            if isinstance(data, list):  # Handle list wrapping
                data = data[0]
            if not isinstance(data, dict):
                raise ValueError("Invalid JSON structure returned by LLM.")
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"❌ LLM returned invalid JSON: {e}\nResponse: {response}")
    
    # ---------- Classification Method (Single API Call) ----------
    def classify_all(self, idea_text: str) -> Dict:
        """Run all classifications in a single API call"""
        
        # Build detailed theme context from definitions
        theme_context = "AI THEME DEFINITIONS:\n\n"
        for idx, (theme_name, theme_info) in enumerate(THEME_TAXONOMY.items(), 1):
            theme_context += f"{idx}. {theme_name}\n"
            theme_context += f"   Definition: {theme_info.get('description', '')}\n"
            if 'examples' in theme_info:
                theme_context += f"   Examples: {', '.join(theme_info['examples'])}\n"
            theme_context += "\n"
        
        system_message = f"""You are an expert at TCS specializing in AI innovation classification.

Perform THREE tasks in ONE response:

TASK 1 - THEME CLASSIFICATION:
{theme_context}
Classify into one of the {len(self.AI_THEMES)} AI themes:
- Select PRIMARY theme that best matches core purpose
- Identify up to 3 SECONDARY themes if applicable
- Provide confidence score (0.0 to 1.0)
- Explain reasoning with specific references to theme definitions

TASK 2 - INDUSTRY CLASSIFICATION:
Map to TCS Industry:
- Banking, Financial Services & Insurance (BFSI)
- Communication, Media & Technology (CMT)
- Consumer Business (Retail & CPG)
- Life Sciences & Healthcare (LSH)
- Manufacturing (MFG)
- Energy, Resources & Utilities (ERU)
- Travel, Transportation & Hospitality (TTH)
- Technology, Software & Services (TechSS)

TASK 3 - COMPREHENSIVE TECHNOLOGY EXTRACTION:
Extract ALL technologies, tools, frameworks, platforms, and technical components mentioned or implied in the idea.

TECHNOLOGY CATEGORIES TO IDENTIFY:

1. AI/ML Technologies:
   - AI Models: GPT-4, Claude, Gemini, LLaMA, BERT, etc.
   - ML Frameworks: TensorFlow, PyTorch, Scikit-learn, Keras, JAX
   - ML Techniques: Deep Learning, NLP, Computer Vision, Reinforcement Learning
   - AI Services: OpenAI API, Azure AI, Google AI, AWS SageMaker

2. Programming Languages & Runtimes:
   - Languages: Python, JavaScript, Java, C++, Go, Rust, TypeScript
   - Runtimes: Node.js, Deno, .NET, JVM

3. Cloud Platforms & Infrastructure:
   - Cloud Providers: AWS, Azure, Google Cloud, IBM Cloud
   - Services: Lambda, EC2, S3, Cloud Functions, Cloud Run
   - Container Tech: Docker, Kubernetes, OpenShift

4. Databases & Data Storage:
   - SQL: PostgreSQL, MySQL, Oracle, SQL Server
   - NoSQL: MongoDB, Cassandra, Redis, DynamoDB
   - Vector DBs: Pinecone, Weaviate, Milvus, Chroma
   - Data Warehouses: Snowflake, BigQuery, Redshift

5. Web & Mobile Technologies:
   - Frontend: React, Angular, Vue.js, Next.js, Flutter
   - Backend: Express, FastAPI, Django, Spring Boot
   - Mobile: React Native, Swift, Kotlin, Flutter

6. DevOps & Tools:
   - CI/CD: Jenkins, GitHub Actions, GitLab CI, CircleCI
   - Monitoring: Prometheus, Grafana, DataDog, New Relic
   - Version Control: Git, GitHub, GitLab, Bitbucket

7. Data Processing & Analytics:
   - Big Data: Hadoop, Spark, Kafka, Flink
   - ETL: Airflow, dbt, Talend, Informatica
   - Analytics: Tableau, Power BI, Looker, Metabase

8. Enterprise & Business Systems:
   - ERP: SAP, Oracle ERP, Microsoft Dynamics
   - CRM: Salesforce, HubSpot, Microsoft Dynamics CRM
   - Collaboration: Microsoft Teams, Slack, Zoom

9. IoT & Edge Computing:
   - IoT Platforms: AWS IoT, Azure IoT, Google IoT Core
   - Edge: Edge TPU, NVIDIA Jetson, Raspberry Pi
   - Protocols: MQTT, CoAP, LoRaWAN

10. Security & Authentication:
    - Auth: OAuth, JWT, SAML, Active Directory
    - Security: SSL/TLS, VPN, Firewall, WAF
    - Tools: Vault, KeyCloak, Auth0

11. APIs & Integration:
    - API Types: REST, GraphQL, gRPC, WebSocket
    - API Management: Apigee, Kong, AWS API Gateway
    - Integration: MuleSoft, Dell Boomi, Apache Camel

12. Specialized Technologies:
    - Blockchain: Ethereum, Hyperledger, Solidity
    - AR/VR: Unity, Unreal Engine, ARKit, ARCore
    - Quantum: Qiskit, Cirq, Q#

EXTRACTION RULES:
1. Extract EXPLICIT mentions (directly stated technologies)
2. Extract IMPLICIT technologies (inferred from context)
3. Include version numbers if mentioned (e.g., "Python 3.11")
4. Normalize names (e.g., "k8s" → "Kubernetes")
5. Group related technologies logically
6. Prioritize specific over generic (e.g., "GPT-4" over "AI")
7. Include both commercial and open-source technologies
8. Extract technical methodologies (e.g., "microservices", "serverless")
9. Include hardware if mentioned (e.g., "GPU", "TPU", "NVIDIA A100")
10. Extract data formats and protocols (e.g., "JSON", "REST API", "MQTT")

QUALITY CRITERIA:
- Minimum 5 technologies (unless idea is very simple)
- Maximum 20 technologies (focus on most relevant)
- Order by relevance and specificity
- Avoid duplicates and redundancy
- Include both core and supporting technologies

Return JSON with ALL THREE classifications:
{{
    "theme": {{
        "primary_theme": "exact theme name",
        "secondary_themes": ["theme1", "theme2"],
        "confidence": 0.95,
        "rationale": "detailed explanation"
    }},
    "industry": {{
        "industry_name": "industry name",
        "confidence": 0.90,
        "rationale": "explanation"
    }},
    "technologies": {{
        "technologies_extracted": ["tech1", "tech2", "tech3"],
        "rationale": "explanation"
    }}
}}"""
        
        user_message = f"Classify this AI innovation idea:\n\n{idea_text}"
        
        try:
            # Check if LLM service is available
            if not LLM_SERVICE_AVAILABLE or llm_service is None:
                logger.warning("LLM service not available, returning default classification")
                return {
                    'theme': {
                        'primary_theme': 'General Innovation',
                        'secondary_themes': [],
                        'confidence': 0.0,
                        'rationale': 'LLM service unavailable'
                    },
                    'industry': {
                        'industry_name': 'Technology, Software & Services (TechSS)',
                        'confidence': 0.0,
                        'rationale': 'LLM service unavailable'
                    },
                    'technologies': {
                        'technologies_extracted': [],
                        'rationale': 'LLM service unavailable'
                    }
                }
            
            # Use LLM service for classification
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(
                    llm_service.chat_completion(
                        provider=self.provider,
                        model_name=self.model_name,
                        messages=[
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": user_message}
                        ],
                        settings=self.model_settings,
                        temperature=0.3,
                        max_tokens=2000
                    )
                )
            finally:
                loop.close()
            
            if not response.get('success'):
                raise Exception(response.get('error', 'Unknown error'))
            
            response_text = response['choices'][0]['message']['content']
            data = self._parse_json(response_text)
            
            return data
            
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            # Return default classification on error
            return {
                'theme': {
                    'primary_theme': 'Other',
                    'secondary_themes': [],
                    'confidence': 0.0,
                    'rationale': f'Error: {str(e)}'
                },
                'industry': {
                    'industry_name': 'Technology, Software & Services (TechSS)',
                    'confidence': 0.0,
                    'rationale': f'Error: {str(e)}'
                },
                'technologies': {
                    'technologies_extracted': [],
                    'rationale': f'Error: {str(e)}'
                }
            }
    
    def classify_idea(self, idea_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify an idea into themes, industry, and technologies
        
        Args:
            idea_data: Dictionary containing:
                - idea_title: str
                - brief_summary: str
                - detailed_description: str (optional)
                - extracted_files_content: str (optional)
        
        Returns:
            Dictionary with classification results
        """
        self._ensure_configured()
        
        # Build content for classification
        content_parts = []
        content_parts.append(f"Title: {idea_data.get('idea_title', '')}")
        content_parts.append(f"Summary: {idea_data.get('brief_summary', '')}")
        
        if idea_data.get('detailed_description'):
            content_parts.append(f"Description: {idea_data['detailed_description']}")
        
        if idea_data.get('extracted_files_content'):
            content_parts.append(f"Additional Content: {idea_data['extracted_files_content']}")
        
        full_content = "\n\n".join(content_parts)
        
        # Run classification
        result = self.classify_all(full_content)
        
        # Flatten result for database storage
        flattened = {
            'primary_theme': result['theme']['primary_theme'],
            'secondary_themes': result['theme']['secondary_themes'],
            'theme_confidence': result['theme']['confidence'],
            'theme_rationale': result['theme']['rationale'],
            'industry': result['industry']['industry_name'],
            'industry_confidence': result['industry']['confidence'],
            'industry_rationale': result['industry']['rationale'],
            'technologies': result['technologies']['technologies_extracted'],
            'technology_rationale': result['technologies']['rationale']
        }
        
        logger.info(f"Classification complete: {flattened['primary_theme']} | {flattened['industry']}")
        
        return flattened
    
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
                    'theme_confidence': 0.0,
                    'theme_rationale': f'Error: {str(e)}',
                    'industry': 'Technology, Software & Services (TechSS)',
                    'industry_confidence': 0.0,
                    'industry_rationale': f'Error: {str(e)}',
                    'technologies': [],
                    'technology_rationale': f'Error: {str(e)}',
                    'error': str(e)
                })
        return results