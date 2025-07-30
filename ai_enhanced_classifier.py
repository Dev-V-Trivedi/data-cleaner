import re
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import requests
import json
import time
import os
from dataclasses import dataclass
import logging

@dataclass
class AIClassificationResult:
    """Result from AI-based classification."""
    category: str
    confidence: float
    reasoning: str

class AIEnhancedColumnClassifier:
    """
    Column classifier enhanced with free AI APIs for better accuracy.
    Uses multiple free AI services as fallbacks.
    """
    
    def __init__(self):
        # Initialize enhanced classifier as fallback
        from enhanced_column_classifier import EnhancedColumnClassifier
        self.enhanced_classifier = EnhancedColumnClassifier()
        
        # Load API keys from environment variables for security
        openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        huggingface_api_key = os.getenv('HUGGINGFACE_API_KEY')
        groq_api_key = os.getenv('GROQ_API_KEY')
        
        # AI API configurations
        self.ai_apis = {
            'openrouter': {
                'url': 'https://openrouter.ai/api/v1/chat/completions',
                'headers': {
                    'Authorization': f'Bearer {openrouter_api_key}' if openrouter_api_key else None,
                    'Content-Type': 'application/json'
                },
                'enabled': bool(openrouter_api_key)
            },
            'huggingface': {
                'url': 'https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium',
                'headers': {'Authorization': f'Bearer {huggingface_api_key}'} if huggingface_api_key else {},
                'enabled': bool(huggingface_api_key)
            },
            'groq': {
                'url': 'https://api.groq.com/openai/v1/chat/completions',
                'headers': {'Authorization': f'Bearer {groq_api_key}'} if groq_api_key else {},
                'enabled': bool(groq_api_key)
            }
        }
        
        # Log API availability (without exposing keys)
        enabled_apis = [api for api, config in self.ai_apis.items() if config['enabled']]
        if enabled_apis:
            print(f"AI APIs available: {', '.join(enabled_apis)}")
        else:
            print("No AI API keys found, using enhanced classifier only")
        
        # Categories for AI classification
        self.categories = [
            'Business Name', 'Phone Number', 'Email', 'Category', 
            'Location', 'Social Links', 'Review', 'Hours', 'Price', 
            'Unknown / Junk'
        ]
        
        self.logger = logging.getLogger(__name__)

    def classify_columns_with_ai(self, df: pd.DataFrame, use_ai: bool = True) -> Dict[str, Dict[str, Any]]:
        """
        Classify columns using AI enhancement when available.
        
        Args:
            df: DataFrame to analyze
            use_ai: Whether to use AI APIs (requires API keys)
            
        Returns:
            Enhanced classification results
        """
        # Get base classification from enhanced classifier
        base_results = self.enhanced_classifier.classify_columns(df)
        
        if not use_ai or not any(api['enabled'] for api in self.ai_apis.values()):
            self.logger.info("AI enhancement disabled or no API keys available. Using enhanced classifier only.")
            return base_results
        
        # Enhance with AI for uncertain classifications
        enhanced_results = {}
        
        for column, result in base_results.items():
            enhanced_results[column] = result.copy()
            
            # Use AI for low-confidence predictions
            if result['confidence'] < 0.7:
                ai_result = self._classify_with_ai(
                    column_name=column,
                    sample_values=result['sample_values'],
                    base_category=result['suggested_category'],
                    base_confidence=result['confidence']
                )
                
                if ai_result and ai_result.confidence > result['confidence']:
                    enhanced_results[column].update({
                        'suggested_category': ai_result.category,
                        'confidence': min(0.95, ai_result.confidence),  # Cap AI confidence
                        'ai_enhanced': True,
                        'ai_reasoning': ai_result.reasoning,
                        'base_suggestion': {
                            'category': result['suggested_category'],
                            'confidence': result['confidence']
                        }
                    })
                else:
                    enhanced_results[column]['ai_enhanced'] = False
            else:
                enhanced_results[column]['ai_enhanced'] = False
        
        return enhanced_results

    def _classify_with_ai(self, column_name: str, sample_values: List[str], 
                         base_category: str, base_confidence: float) -> Optional[AIClassificationResult]:
        """Classify a column using AI APIs."""
        
        # Create prompt for AI
        prompt = self._create_classification_prompt(column_name, sample_values, base_category)
        
        # Try each AI API
        for api_name, api_config in self.ai_apis.items():
            if not api_config['enabled']:
                continue
                
            try:
                result = self._query_ai_api(api_name, api_config, prompt)
                if result:
                    return result
            except Exception as e:
                self.logger.warning(f"AI API {api_name} failed: {e}")
                continue
        
        return None

    def _create_classification_prompt(self, column_name: str, sample_values: List[str], 
                                    base_category: str) -> str:
        """Create a detailed prompt for AI classification."""
        
        sample_text = ", ".join(sample_values[:3]) if sample_values else "No samples"
        
        prompt = f"""
You are an expert data analyst. Classify this CSV column into one of these categories:

Categories:
- Business Name: Names of businesses, companies, shops, restaurants
- Phone Number: Phone numbers in any format
- Email: Email addresses
- Category: Business types, categories, amenities, services offered
- Location: Addresses, cities, states, coordinates, geographic locations
- Social Links: Websites, social media URLs, online links
- Review: Customer reviews, ratings, feedback, comments
- Hours: Operating hours, schedules, time information
- Price: Pricing information, costs, fees, price ranges
- Unknown / Junk: Unclear or irrelevant data

Column Analysis:
- Column Name: "{column_name}"
- Sample Values: {sample_text}
- Current Classification: {base_category}

Instructions:
1. Analyze the column name and sample values
2. Choose the MOST APPROPRIATE category
3. Provide confidence score (0.0 to 1.0)
4. Give brief reasoning

Respond in this exact JSON format:
{{"category": "Category Name", "confidence": 0.85, "reasoning": "Brief explanation"}}
"""
        return prompt

    def _query_ai_api(self, api_name: str, api_config: Dict, prompt: str) -> Optional[AIClassificationResult]:
        """Query a specific AI API."""
        
        if api_name == 'openrouter':
            return self._query_openrouter(api_config, prompt)
        elif api_name == 'huggingface':
            return self._query_huggingface(api_config, prompt)
        elif api_name in ['openai_compatible', 'groq']:
            return self._query_openai_compatible(api_config, prompt)
        
        return None

    def _query_openrouter(self, api_config: Dict, prompt: str) -> Optional[AIClassificationResult]:
        """Query OpenRouter API."""
        try:
            payload = {
                "model": "meta-llama/llama-3.1-8b-instruct:free",  # Use free model
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert data analyst specializing in CSV column classification. Always respond with valid JSON."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 200
            }
            
            response = requests.post(
                api_config['url'],
                headers=api_config['headers'],
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    return self._parse_ai_response(content)
            else:
                self.logger.warning(f"OpenRouter API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.logger.error(f"OpenRouter API request failed: {e}")
            
        return None

    def _query_huggingface(self, api_config: Dict, prompt: str) -> Optional[AIClassificationResult]:
        """Query Hugging Face Inference API."""
        try:
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 200,
                    "temperature": 0.1,
                    "return_full_text": False
                }
            }
            
            response = requests.post(
                api_config['url'],
                headers=api_config['headers'],
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    return self._parse_ai_response(generated_text)
            
        except Exception as e:
            self.logger.error(f"Hugging Face API error: {e}")
        
        return None

    def _query_openai_compatible(self, api_config: Dict, prompt: str) -> Optional[AIClassificationResult]:
        """Query OpenAI-compatible APIs (OpenAI, Groq, etc.)."""
        try:
            payload = {
                "model": "llama3-8b-8192",  # For Groq, adjust for other APIs
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert data analyst specializing in CSV column classification. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 200
            }
            
            response = requests.post(
                api_config['url'],
                headers=api_config['headers'],
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    return self._parse_ai_response(content)
            
        except Exception as e:
            self.logger.error(f"OpenAI-compatible API error: {e}")
        
        return None

    def _parse_ai_response(self, response_text: str) -> Optional[AIClassificationResult]:
        """Parse AI response and extract classification result."""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                result = json.loads(json_str)
                
                category = result.get('category', '').strip()
                confidence = float(result.get('confidence', 0))
                reasoning = result.get('reasoning', '').strip()
                
                # Validate category
                if category in self.categories and 0 <= confidence <= 1:
                    return AIClassificationResult(
                        category=category,
                        confidence=confidence,
                        reasoning=reasoning
                    )
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            self.logger.warning(f"Failed to parse AI response: {e}")
        
        return None

    def setup_api_key(self, api_name: str, api_key: str) -> bool:
        """
        Setup API key for a specific AI service.
        
        Args:
            api_name: Name of the API ('huggingface', 'groq', 'openai_compatible')
            api_key: API key
            
        Returns:
            True if setup successful
        """
        if api_name not in self.ai_apis:
            return False
        
        if api_name == 'huggingface':
            self.ai_apis[api_name]['headers']['Authorization'] = f'Bearer {api_key}'
        else:
            self.ai_apis[api_name]['headers']['Authorization'] = f'Bearer {api_key}'
        
        self.ai_apis[api_name]['enabled'] = True
        return True

    def test_ai_connection(self) -> Dict[str, bool]:
        """Test connection to all enabled AI APIs."""
        results = {}
        
        for api_name, api_config in self.ai_apis.items():
            if not api_config['enabled']:
                results[api_name] = False
                continue
            
            try:
                # Simple test prompt
                test_prompt = "Classify this column: 'email' with sample 'john@example.com'"
                result = self._query_ai_api(api_name, api_config, test_prompt)
                results[api_name] = result is not None
            except:
                results[api_name] = False
        
        return results

    # Additional utility methods
    def get_free_api_setup_instructions(self) -> Dict[str, str]:
        """Get instructions for setting up free AI APIs."""
        return {
            'huggingface': """
            Hugging Face Inference API (Free):
            1. Sign up at https://huggingface.co/
            2. Go to Settings > Access Tokens
            3. Create a new token with 'Read' permissions
            4. Use: classifier.setup_api_key('huggingface', 'your_token')
            
            Free tier: 1000 requests/month
            """,
            
            'groq': """
            Groq API (Free):
            1. Sign up at https://console.groq.com/
            2. Get your API key from the dashboard
            3. Use: classifier.setup_api_key('groq', 'your_api_key')
            
            Free tier: 6000 tokens/minute, very fast inference
            """,
            
            'together': """
            Together AI (Free tier available):
            1. Sign up at https://www.together.ai/
            2. Get API key from dashboard
            3. Modify the openai_compatible config to use Together's endpoint
            
            Free tier: $25 credit for new users
            """
        }

    def classify_with_ensemble(self, df: pd.DataFrame, confidence_threshold: float = 0.8) -> Dict[str, Dict[str, Any]]:
        """
        Use ensemble method combining enhanced classifier + AI for best results.
        
        Args:
            df: DataFrame to analyze
            confidence_threshold: Threshold for using AI enhancement
            
        Returns:
            Best possible classification results
        """
        # Get enhanced classification
        enhanced_results = self.enhanced_classifier.classify_columns(df)
        
        # Use AI for uncertain cases
        final_results = {}
        
        for column, result in enhanced_results.items():
            final_results[column] = result.copy()
            
            # Use AI enhancement for low confidence predictions
            if result['confidence'] < confidence_threshold:
                ai_result = self._classify_with_ai(
                    column_name=column,
                    sample_values=result['sample_values'][:3],  # Limit samples for API
                    base_category=result['suggested_category'],
                    base_confidence=result['confidence']
                )
                
                if ai_result:
                    # Ensemble: Average the confidences with weights
                    enhanced_confidence = (
                        result['confidence'] * 0.4 +  # Enhanced classifier weight
                        ai_result.confidence * 0.6     # AI weight (higher for uncertain cases)
                    )
                    
                    final_results[column].update({
                        'suggested_category': ai_result.category,
                        'confidence': min(0.95, enhanced_confidence),
                        'ensemble_method': True,
                        'ai_reasoning': ai_result.reasoning,
                        'base_method': {
                            'category': result['suggested_category'],
                            'confidence': result['confidence']
                        },
                        'ai_method': {
                            'category': ai_result.category,
                            'confidence': ai_result.confidence
                        }
                    })
        
        return final_results
