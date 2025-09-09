#!/usr/bin/env python3
"""
AI Services for BugSeek - OpenAI Integration and NLP Processing

This module provides AI-powered analysis capabilities including:
- OpenAI/Azure OpenAI integration for log analysis
- Error pattern recognition
- Similarity matching using embeddings
- Solution suggestion generation
"""

import os
import re
import json
import hashlib
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import requests
from flask import current_app

# Import models
from backend.models import db, AIAnalysisResult, OpenAIStatus, SimilarLogMatch, ErrorLog

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenAIService:
    """OpenAI/Azure OpenAI integration service."""
    
    def __init__(self):
        """Initialize OpenAI service with configuration."""
        self.api_key = None
        self.endpoint = None
        self.api_version = None
        self.deployment_name = None
        self.model_name = "gpt-4o-mini"
        self.max_retries = 3
        self.request_timeout = 30
        self._initialize_config()
    
    def _initialize_config(self):
        """Initialize configuration from Flask app config or environment variables."""
        try:
            # Try to get config from Flask app context
            if current_app:
                self.api_key = current_app.config.get('OPENAI_API_KEY', os.getenv('OPENAI_API_KEY', ''))
                self.endpoint = current_app.config.get('AZURE_OPENAI_ENDPOINT', os.getenv('AZURE_OPENAI_ENDPOINT', ''))
                self.api_version = current_app.config.get('AZURE_OPENAI_API_VERSION', os.getenv('AZURE_OPENAI_API_VERSION', '2024-10-21'))
                self.deployment_name = current_app.config.get('AZURE_OPENAI_DEPLOYMENT_NAME', os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'aida-gpt-4o-mini'))
                self.max_retries = current_app.config.get('AI_MAX_RETRIES', 3)
                self.request_timeout = current_app.config.get('AI_REQUEST_TIMEOUT', 30)
        except RuntimeError:
            # No Flask app context, use environment variables directly
            self.api_key = os.getenv('OPENAI_API_KEY', '')
            self.endpoint = os.getenv('AZURE_OPENAI_ENDPOINT', '')
            self.api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-10-21')
            self.deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'aida-gpt-4o-mini')
            self.max_retries = int(os.getenv('AI_MAX_RETRIES', '3'))
            self.request_timeout = int(os.getenv('AI_REQUEST_TIMEOUT', '30'))
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for OpenAI API requests."""
        return {
            'Content-Type': 'application/json',
            'api-key': self.api_key,
            'User-Agent': 'BugSeek/1.0'
        }
    
    def _build_api_url(self) -> str:
        """Build the complete API URL for Azure OpenAI."""
        base_url = self.endpoint.rstrip('/')
        return f"{base_url}/openai/deployments/{self.deployment_name}/chat/completions?api-version={self.api_version}"
    
    def check_connection(self) -> Dict[str, Any]:
        """Check OpenAI API connection status."""
        try:
            if not self.api_key:
                return {
                    'success': False,
                    'connected': False,
                    'error': 'OpenAI API key not configured',
                    'message': 'API key is missing or empty'
                }
            
            # Test connection with a simple request
            url = self._build_api_url()
            headers = self._get_headers()
            
            test_payload = {
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello"}
                ],
                "max_tokens": 10,
                "temperature": 0.1
            }
            
            response = requests.post(
                url, 
                headers=headers, 
                json=test_payload, 
                timeout=self.request_timeout
            )
            
            if response.status_code == 200:
                # Update status in database
                self._update_status(True, None)
                return {
                    'success': True,
                    'connected': True,
                    'message': 'OpenAI API connection successful',
                    'model': self.deployment_name,
                    'endpoint': self.endpoint
                }
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                self._update_status(False, error_msg)
                return {
                    'success': False,
                    'connected': False,
                    'error': error_msg,
                    'message': 'Failed to connect to OpenAI API'
                }
                
        except Exception as e:
            error_msg = str(e)
            self._update_status(False, error_msg)
            return {
                'success': False,
                'connected': False,
                'error': error_msg,
                'message': 'OpenAI API connection failed'
            }
    
    def _update_status(self, is_connected: bool, error_message: Optional[str] = None):
        """Update OpenAI status in database."""
        try:
            # Get or create status record
            status = OpenAIStatus.get_current_status()
            if not status:
                status = OpenAIStatus(
                    ApiEndpoint=self.endpoint,
                    ModelVersion=self.deployment_name,
                    ApiKeyHash=hashlib.sha256(self.api_key.encode()).hexdigest() if self.api_key else None
                )
                db.session.add(status)
            
            # Update status
            status.update_connection_status(is_connected, error_message)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to update OpenAI status: {e}")
    
    def _make_chat_request(self, messages: List[Dict[str, str]], max_tokens: int = 1500, temperature: float = 0.7) -> Dict[str, Any]:
        """Make a chat completion request to OpenAI API."""
        try:
            url = self._build_api_url()
            headers = self._get_headers()
            
            payload = {
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": 1.0,
                "frequency_penalty": 0,
                "presence_penalty": 0
            }
            
            for attempt in range(self.max_retries):
                try:
                    response = requests.post(
                        url, 
                        headers=headers, 
                        json=payload, 
                        timeout=self.request_timeout
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Extract usage information
                        usage = result.get('usage', {})
                        tokens_used = usage.get('total_tokens', 0)
                        
                        # Update status with successful call
                        self._update_usage_stats(tokens_used)
                        
                        return {
                            'success': True,
                            'response': result,
                            'tokens_used': tokens_used,
                            'message': 'OpenAI request successful'
                        }
                    else:
                        if attempt == self.max_retries - 1:
                            return {
                                'success': False,
                                'error': f"HTTP {response.status_code}: {response.text}",
                                'message': 'OpenAI API request failed'
                            }
                        time.sleep(2 ** attempt)  # Exponential backoff
                        
                except requests.exceptions.Timeout:
                    if attempt == self.max_retries - 1:
                        return {
                            'success': False,
                            'error': 'Request timeout',
                            'message': 'OpenAI API request timed out'
                        }
                    time.sleep(2 ** attempt)
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'OpenAI API request failed'
            }
    
    def _update_usage_stats(self, tokens_used: int):
        """Update usage statistics in database."""
        try:
            status = OpenAIStatus.get_current_status()
            if status:
                # Simple cost estimation (approximate)
                estimated_cost = tokens_used * 0.00002  # $0.002 per 1K tokens for GPT-4
                status.increment_usage(tokens_used, estimated_cost)
                db.session.commit()
        except Exception as e:
            logger.error(f"Failed to update usage stats: {e}")
    
    def generate_summary(self, log_content: str, error_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI summary for error log."""
        try:
            # Create system prompt for log analysis
            system_prompt = """You are an expert system administrator and software engineer specializing in error log analysis. 
            Your task is to analyze error logs and provide concise, actionable summaries.
            
            Focus on:
            1. Identifying the root cause of the error
            2. Determining severity level
            3. Extracting key technical details
            4. Suggesting immediate investigation areas
            
            Provide your response in JSON format with these fields:
            - summary: Brief description of the error (2-3 sentences)
            - severity: One of [low, medium, high, critical]
            - keywords: Array of important technical terms found
            - root_cause: Likely root cause if identifiable
            - investigation_areas: Array of areas to investigate
            """
            
            # Create user prompt with log content and metadata
            user_prompt = f"""Analyze this error log:

**Metadata:**
- Team: {error_metadata.get('TeamName', 'Unknown')}
- Module: {error_metadata.get('Module', 'Unknown')}
- Error Name: {error_metadata.get('ErrorName', 'Unknown')}
- Description: {error_metadata.get('Description', 'No description')}

**Log Content:**
{log_content[:8000]}  # Limit content to avoid token limits

Please analyze this error log and provide a structured summary."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            result = self._make_chat_request(messages, max_tokens=1000, temperature=0.3)
            
            if result['success']:
                try:
                    # Extract the AI response
                    ai_response = result['response']['choices'][0]['message']['content']
                    
                    # Try to parse JSON response
                    try:
                        parsed_response = json.loads(ai_response)
                    except json.JSONDecodeError:
                        # If not JSON, create structured response
                        parsed_response = {
                            'summary': ai_response[:500],
                            'severity': 'medium',
                            'keywords': [],
                            'root_cause': 'Analysis needed',
                            'investigation_areas': []
                        }
                    
                    return {
                        'success': True,
                        'summary': parsed_response.get('summary', ai_response[:500]),
                        'severity': parsed_response.get('severity', 'medium'),
                        'keywords': parsed_response.get('keywords', []),
                        'root_cause': parsed_response.get('root_cause', ''),
                        'investigation_areas': parsed_response.get('investigation_areas', []),
                        'confidence': 0.85,
                        'tokens_used': result['tokens_used'],
                        'message': 'AI summary generated successfully'
                    }
                    
                except Exception as e:
                    return {
                        'success': False,
                        'error': f"Failed to parse AI response: {e}",
                        'message': 'AI summary generation failed'
                    }
            else:
                return result
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'AI summary generation failed'
            }
    
    def suggest_solutions(self, log_content: str, error_metadata: Dict[str, Any], summary_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate solution suggestions for error log."""
        try:
            # Create system prompt for solution generation
            system_prompt = """You are an expert DevOps engineer and troubleshooter specializing in system errors. 
            Your task is to provide practical, actionable solutions for technical problems.
            
            Based on the error log analysis, suggest specific solutions prioritized by:
            1. Likelihood of success
            2. Implementation difficulty
            3. Risk level
            
            Provide response in JSON format with:
            - solutions: Array of solution objects with fields:
              - description: Clear, actionable solution description
              - category: One of [configuration, code, infrastructure, data, network]
              - priority: One of [high, medium, low]
              - difficulty: One of [easy, medium, hard]
              - risk: One of [low, medium, high]
              - steps: Array of specific implementation steps
            """
            
            # Build context from summary if available
            context = ""
            if summary_data:
                context = f"""
**Previous Analysis:**
- Summary: {summary_data.get('summary', '')}
- Severity: {summary_data.get('severity', '')}
- Root Cause: {summary_data.get('root_cause', '')}
"""
            
            user_prompt = f"""Suggest solutions for this error:

**Error Details:**
- Team: {error_metadata.get('TeamName', 'Unknown')}
- Module: {error_metadata.get('Module', 'Unknown')}
- Error: {error_metadata.get('ErrorName', 'Unknown')}
- Description: {error_metadata.get('Description', 'No description')}
{context}

**Log Sample:**
{log_content[:6000]}

Please provide practical solutions ranked by effectiveness."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            result = self._make_chat_request(messages, max_tokens=1500, temperature=0.5)
            
            if result['success']:
                try:
                    ai_response = result['response']['choices'][0]['message']['content']
                    
                    # Try to parse JSON response
                    try:
                        parsed_response = json.loads(ai_response)
                        solutions = parsed_response.get('solutions', [])
                    except json.JSONDecodeError:
                        # Create fallback solutions from text response
                        solutions = [
                            {
                                'description': ai_response[:500],
                                'category': 'general',
                                'priority': 'medium',
                                'difficulty': 'medium',
                                'risk': 'low',
                                'steps': ['Review the suggested solution', 'Test in development environment']
                            }
                        ]
                    
                    return {
                        'success': True,
                        'solutions': solutions,
                        'total_solutions': len(solutions),
                        'confidence': 0.80,
                        'tokens_used': result['tokens_used'],
                        'message': 'Solutions generated successfully'
                    }
                    
                except Exception as e:
                    return {
                        'success': False,
                        'error': f"Failed to parse solutions: {e}",
                        'message': 'Solution generation failed'
                    }
            else:
                return result
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Solution generation failed'
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current OpenAI service status."""
        try:
            status = OpenAIStatus.get_current_status()
            if status:
                return {
                    'success': True,
                    'status': status.to_dict(),
                    'message': 'Status retrieved successfully'
                }
            else:
                return {
                    'success': True,
                    'status': {
                        'IsConnected': False,
                        'LastConnectionCheck': None,
                        'TotalApiCalls': 0,
                        'TotalTokensUsed': 0,
                        'EstimatedTotalCost': 0.0
                    },
                    'message': 'No status record found'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve status'
            }


class ErrorPatternRecognizer:
    """Service for recognizing common error patterns."""
    
    # Common Linux/Android error patterns from requirements
    ERROR_PATTERNS = {
        'kernel_panic': {
            'patterns': [r'kernel panic', r'oops:', r'unable to handle kernel'],
            'category': 'kernel',
            'severity': 'critical',
            'description': 'Kernel panic or critical kernel error'
        },
        'segmentation_fault': {
            'patterns': [r'segmentation fault', r'sigsegv', r'signal 11'],
            'category': 'memory',
            'severity': 'high',
            'description': 'Memory access violation'
        },
        'out_of_memory': {
            'patterns': [r'out of memory', r'oom killer', r'memory allocation failed'],
            'category': 'memory',
            'severity': 'high',
            'description': 'System out of memory'
        },
        'buffer_overflow': {
            'patterns': [r'buffer overflow', r'stack smashing', r'heap overflow'],
            'category': 'security',
            'severity': 'critical',
            'description': 'Buffer overflow vulnerability'
        },
        'device_not_found': {
            'patterns': [r'device not found', r'no such device', r'device or resource busy'],
            'category': 'hardware',
            'severity': 'medium',
            'description': 'Hardware device access issue'
        },
        'io_error': {
            'patterns': [r'i/o error', r'input/output error', r'read-only file system'],
            'category': 'filesystem',
            'severity': 'high',
            'description': 'File system I/O error'
        },
        'permission_denied': {
            'patterns': [r'permission denied', r'access denied', r'operation not permitted'],
            'category': 'security',
            'severity': 'medium',
            'description': 'File or resource access permission error'
        },
        'network_error': {
            'patterns': [r'network is unreachable', r'connection refused', r'network down'],
            'category': 'network',
            'severity': 'medium',
            'description': 'Network connectivity issue'
        },
        'watchdog_timeout': {
            'patterns': [r'watchdog timeout', r'watchdog bite', r'hardware watchdog'],
            'category': 'hardware',
            'severity': 'high',
            'description': 'Hardware watchdog timeout'
        },
        'android_anr': {
            'patterns': [r'anr', r'application not responding', r'input dispatching timed out'],
            'category': 'android',
            'severity': 'medium',
            'description': 'Android Application Not Responding'
        },
        'java_exception': {
            'patterns': [r'exception in thread', r'java.lang.', r'caused by:'],
            'category': 'application',
            'severity': 'medium',
            'description': 'Java application exception'
        }
    }
    
    @classmethod
    def recognize_patterns(cls, log_content: str) -> Dict[str, Any]:
        """Recognize error patterns in log content."""
        try:
            log_lower = log_content.lower()
            matched_patterns = []
            highest_severity = 'low'
            primary_category = 'general'
            
            # Check each pattern
            for pattern_name, pattern_info in cls.ERROR_PATTERNS.items():
                for pattern_regex in pattern_info['patterns']:
                    if re.search(pattern_regex, log_lower):
                        matched_patterns.append({
                            'name': pattern_name,
                            'category': pattern_info['category'],
                            'severity': pattern_info['severity'],
                            'description': pattern_info['description']
                        })
                        
                        # Track highest severity
                        if cls._compare_severity(pattern_info['severity'], highest_severity) > 0:
                            highest_severity = pattern_info['severity']
                            primary_category = pattern_info['category']
                        break
            
            return {
                'success': True,
                'matched_patterns': matched_patterns,
                'primary_pattern': matched_patterns[0]['name'] if matched_patterns else None,
                'primary_category': primary_category,
                'estimated_severity': highest_severity,
                'pattern_count': len(matched_patterns),
                'message': f'Found {len(matched_patterns)} matching patterns'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Pattern recognition failed'
            }
    
    @staticmethod
    def _compare_severity(sev1: str, sev2: str) -> int:
        """Compare severity levels. Returns 1 if sev1 > sev2, -1 if sev1 < sev2, 0 if equal."""
        severity_order = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        return severity_order.get(sev1, 2) - severity_order.get(sev2, 2)


class AIAnalysisService:
    """Main service for coordinating AI analysis tasks."""
    
    def __init__(self):
        """Initialize AI analysis service."""
        self.openai_service = OpenAIService()
        self.pattern_recognizer = ErrorPatternRecognizer()
    
    def analyze_error_log(self, cr_id: str, log_content: str, error_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Perform complete AI analysis of an error log."""
        try:
            # Create analysis record
            analysis = AIAnalysisResult(
                Cr_ID=cr_id,
                AnalysisType='complete',
                Status='processing',
                ProcessingStartTime=datetime.utcnow(),
                ModelUsed=self.openai_service.deployment_name
            )
            db.session.add(analysis)
            db.session.commit()
            
            results = {
                'analysis_id': analysis.Analysis_ID,
                'cr_id': cr_id,
                'status': 'processing'
            }
            
            # Step 1: Pattern recognition
            pattern_result = self.pattern_recognizer.recognize_patterns(log_content)
            if pattern_result['success']:
                analysis.ErrorPattern = pattern_result.get('primary_pattern')
                analysis.ErrorCategory = pattern_result.get('primary_category')
                analysis.EstimatedSeverity = pattern_result.get('estimated_severity', 'medium')
                results['pattern_recognition'] = pattern_result
            
            # Step 2: AI Summary generation
            summary_result = self.openai_service.generate_summary(log_content, error_metadata)
            if summary_result['success']:
                analysis.Summary = summary_result.get('summary')
                analysis.Confidence = summary_result.get('confidence', 0.0)
                analysis.set_keywords(summary_result.get('keywords', []))
                analysis.TokensUsed += summary_result.get('tokens_used', 0)
                results['ai_summary'] = summary_result
            
            # Step 3: Solution suggestions
            solution_result = self.openai_service.suggest_solutions(
                log_content, 
                error_metadata, 
                summary_result if summary_result['success'] else None
            )
            if solution_result['success']:
                analysis.set_solutions(solution_result.get('solutions', []))
                analysis.TokensUsed += solution_result.get('tokens_used', 0)
                results['solutions'] = solution_result
            
            # Update analysis status
            analysis.Status = 'completed'
            analysis.ProcessingEndTime = datetime.utcnow()
            db.session.commit()
            
            results.update({
                'success': True,
                'status': 'completed',
                'total_tokens_used': analysis.TokensUsed,
                'message': 'AI analysis completed successfully'
            })
            
            return results
            
        except Exception as e:
            # Update analysis with error status
            if 'analysis' in locals():
                analysis.Status = 'failed'
                analysis.ErrorMessage = str(e)
                analysis.ProcessingEndTime = datetime.utcnow()
                db.session.commit()
            
            return {
                'success': False,
                'error': str(e),
                'message': 'AI analysis failed'
            }
    
    def get_analysis_status(self, cr_id: str) -> Dict[str, Any]:
        """Get AI analysis status for a specific error log."""
        try:
            analysis = AIAnalysisResult.query.filter_by(Cr_ID=cr_id).first()
            if analysis:
                return {
                    'success': True,
                    'analysis': analysis.to_dict(),
                    'message': 'Analysis status retrieved'
                }
            else:
                return {
                    'success': False,
                    'message': 'No analysis found for this log'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve analysis status'
            }
