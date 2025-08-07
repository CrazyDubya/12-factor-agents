#!/usr/bin/env python3
"""
Comprehensive Input Validation Framework
Secure input validation and sanitization for GPT-OSS interfaces

This module provides enterprise-grade input validation with security
hardening against injection attacks, data leakage, and malicious inputs.
"""

import re
import html
import unicodedata
from typing import Dict, List, Tuple, Optional, Union
from urllib.parse import urlparse
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Raised when input validation fails"""
    pass

class SecurityViolationError(ValidationError):
    """Raised when a security violation is detected"""
    pass

class InputValidator:
    """
    Comprehensive input validation and sanitization framework
    
    Features:
    - Length validation with configurable limits
    - Content sanitization and filtering
    - Security pattern detection and blocking
    - Unicode normalization and character filtering
    - Context-aware validation for different input types
    """
    
    # Security patterns to detect and block
    SECURITY_PATTERNS = [
        # Code execution patterns
        r'__import__\s*\(',
        r'exec\s*\(',
        r'eval\s*\(',
        r'compile\s*\(',
        r'globals\s*\(',
        r'locals\s*\(',
        r'vars\s*\(',
        r'dir\s*\(',
        r'getattr\s*\(',
        r'setattr\s*\(',
        r'delattr\s*\(',
        r'hasattr\s*\(',
        
        # File system access
        r'open\s*\(',
        r'file\s*\(',
        r'input\s*\(',
        r'raw_input\s*\(',
        
        # System/OS access
        r'import\s+os\b',
        r'import\s+sys\b',
        r'import\s+subprocess\b',
        r'import\s+shutil\b',
        r'from\s+os\s+import',
        r'from\s+sys\s+import',
        r'from\s+subprocess\s+import',
        
        # Shell/command injection
        r'subprocess\.',
        r'os\.system\s*\(',
        r'os\.popen\s*\(',
        r'os\.spawn\w*\s*\(',
        r'commands\.',
        
        # File redirection and piping
        r'>\s*[/\\]',        # File redirection
        r'\|\s*sh\b',        # Pipe to shell
        r'\|\s*bash\b',      # Pipe to bash
        r'\|\s*cmd\b',       # Pipe to cmd (Windows)
        r';\s*rm\b',         # Command chaining with rm
        r'&&\s*rm\b',        # Command chaining with rm
        r'\|\|\s*rm\b',      # Or chaining with rm
        
        # Command substitution
        r'\$\(',             # $(command)
        r'`[^`]*`',          # `command`
        
        # Network/URL access (in non-URL contexts)
        r'urllib\.',
        r'requests\.',
        r'http\.client\.',
        r'socket\.',
        
        # Potential data exfiltration
        r'pickle\.',
        r'marshal\.',
        r'base64\.',
        
        # Script injection
        r'<script\b',
        r'</script>',
        r'javascript:',
        r'vbscript:',
        r'data:text/html',
        
        # SQL injection patterns
        r'union\s+select\b',
        r'drop\s+table\b',
        r'delete\s+from\b',
        r'insert\s+into\b',
        r'update\s+\w+\s+set\b',
        r'--\s*$',           # SQL comments
        r'/\*.*\*/',         # SQL block comments
        
        # Path traversal
        r'\.\./',
        r'\.\.\\'
    ]
    
    # Compiled regex patterns for performance
    _compiled_patterns: Optional[List[re.Pattern]] = None
    
    def __init__(self):
        """Initialize input validator with compiled security patterns"""
        if self._compiled_patterns is None:
            InputValidator._compiled_patterns = [
                re.compile(pattern, re.IGNORECASE | re.MULTILINE)
                for pattern in self.SECURITY_PATTERNS
            ]
    
    def validate_text_input(
        self, 
        text: str, 
        max_length: int = 2000,
        min_length: int = 0,
        allow_empty: bool = False,
        context: str = "general"
    ) -> str:
        """
        Validate and sanitize text input
        
        Args:
            text: Input text to validate
            max_length: Maximum allowed length
            min_length: Minimum required length
            allow_empty: Whether empty input is allowed
            context: Validation context (general, math, filename, etc.)
            
        Returns:
            Sanitized text
            
        Raises:
            ValidationError: If validation fails
            SecurityViolationError: If security violation detected
        """
        # Type checking
        if not isinstance(text, str):
            if text is None and allow_empty:
                return ""
            raise ValidationError(f"Input must be string, got {type(text)}")
        
        original_text = text
        
        # Length validation
        if len(text) > max_length:
            raise ValidationError(f"Input too long (max {max_length} characters)")
        
        if len(text) < min_length:
            raise ValidationError(f"Input too short (min {min_length} characters)")
        
        if not text and not allow_empty:
            raise ValidationError("Input cannot be empty")
        
        # Unicode normalization
        text = unicodedata.normalize('NFKC', text)
        
        # Security pattern detection
        self._check_security_patterns(text, context)
        
        # Context-specific validation
        if context == "math":
            text = self._validate_math_input(text)
        elif context == "filename":
            text = self._validate_filename_input(text)
        elif context == "url":
            text = self._validate_url_input(text)
        elif context == "prompt":
            text = self._validate_prompt_input(text)
        
        # Basic sanitization
        text = self._sanitize_basic(text)
        
        # Log validation for security monitoring
        if original_text != text:
            logger.info(f"Input sanitized: {len(original_text)} -> {len(text)} chars")
        
        return text
    
    def _check_security_patterns(self, text: str, context: str) -> None:
        """
        Check for security violation patterns
        
        Args:
            text: Text to check
            context: Validation context
            
        Raises:
            SecurityViolationError: If security violation detected
        """
        for pattern in self._compiled_patterns:
            match = pattern.search(text)
            if match:
                logger.warning(f"Security pattern detected: {match.group()} in context: {context}")
                raise SecurityViolationError(
                    f"Security violation detected: potentially dangerous pattern found"
                )
    
    def _validate_math_input(self, text: str) -> str:
        """
        Validate mathematical expression input
        
        Args:
            text: Mathematical expression
            
        Returns:
            Validated and normalized math expression
        """
        # Allow only mathematical characters
        allowed_chars = set('0123456789+-*/().^×÷ abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_,')
        
        if not all(c in allowed_chars for c in text):
            disallowed = set(text) - allowed_chars
            raise ValidationError(f"Invalid characters in math expression: {sorted(disallowed)}")
        
        # Basic structure validation
        if text.count('(') != text.count(')'):
            raise ValidationError("Unbalanced parentheses in math expression")
        
        # Normalize mathematical symbols
        text = text.replace('×', '*').replace('÷', '/')
        
        return text.strip()
    
    def _validate_filename_input(self, text: str) -> str:
        """
        Validate filename input
        
        Args:
            text: Filename
            
        Returns:
            Sanitized filename
        """
        # Remove/replace dangerous characters
        text = re.sub(r'[<>:"/\\|?*]', '_', text)
        
        # Remove control characters
        text = ''.join(c for c in text if ord(c) >= 32)
        
        # Prevent directory traversal
        text = text.replace('..', '')
        
        # Validate length
        if len(text) > 255:
            raise ValidationError("Filename too long (max 255 characters)")
        
        # Check for reserved names (Windows)
        reserved = {'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 
                   'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 
                   'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'}
        
        if text.upper().split('.')[0] in reserved:
            raise ValidationError(f"Reserved filename: {text}")
        
        return text.strip()
    
    def _validate_url_input(self, text: str) -> str:
        """
        Validate URL input
        
        Args:
            text: URL string
            
        Returns:
            Validated URL
        """
        try:
            parsed = urlparse(text)
            
            # Validate scheme
            allowed_schemes = {'http', 'https'}
            if parsed.scheme.lower() not in allowed_schemes:
                raise ValidationError(f"Invalid URL scheme: {parsed.scheme}")
            
            # Validate hostname
            if not parsed.netloc:
                raise ValidationError("URL missing hostname")
            
            # Check for localhost/private IPs in production
            localhost_patterns = ['localhost', '127.0.0.1', '0.0.0.0', '::1']
            if any(pattern in parsed.netloc.lower() for pattern in localhost_patterns):
                logger.info(f"Localhost URL detected: {text}")
            
            return text
            
        except Exception as e:
            raise ValidationError(f"Invalid URL format: {e}")
    
    def _validate_prompt_input(self, text: str) -> str:
        """
        Validate prompt/question input for AI models
        
        Args:
            text: User prompt/question
            
        Returns:
            Validated prompt
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Check for potential prompt injection patterns
        injection_patterns = [
            r'ignore\s+previous\s+instructions',
            r'system\s*:\s*you\s+are',
            r'jailbreak',
            r'act\s+as\s+if\s+you\s+are',
            r'pretend\s+to\s+be',
            r'roleplay\s+as',
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Potential prompt injection detected: {pattern}")
                # Don't block, but log for monitoring
        
        return text.strip()
    
    def _sanitize_basic(self, text: str) -> str:
        """
        Basic text sanitization
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        # Remove control characters except newline and tab
        text = ''.join(c for c in text if c.isprintable() or c in '\n\t\r')
        
        # HTML entity encoding for safety
        text = html.escape(text, quote=False)
        
        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text
    
    def validate_json_input(self, json_str: str, max_depth: int = 10) -> dict:
        """
        Validate JSON input with depth checking
        
        Args:
            json_str: JSON string to validate
            max_depth: Maximum nesting depth allowed
            
        Returns:
            Parsed JSON object
            
        Raises:
            ValidationError: If JSON is invalid or too deep
        """
        import json
        
        try:
            data = json.loads(json_str)
            
            # Check nesting depth
            def check_depth(obj, current_depth=0):
                if current_depth > max_depth:
                    raise ValidationError(f"JSON too deeply nested (max depth: {max_depth})")
                
                if isinstance(obj, dict):
                    for value in obj.values():
                        check_depth(value, current_depth + 1)
                elif isinstance(obj, list):
                    for item in obj:
                        check_depth(item, current_depth + 1)
            
            check_depth(data)
            return data
            
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON format: {e}")
    
    def is_safe_for_display(self, text: str) -> bool:
        """
        Check if text is safe for display in UI
        
        Args:
            text: Text to check
            
        Returns:
            True if safe for display
        """
        try:
            self.validate_text_input(text, context="general")
            return True
        except (ValidationError, SecurityViolationError):
            return False

# Convenience functions for backward compatibility
def validate_user_input(text: str, max_length: int = 2000) -> str:
    """Validate general user input"""
    validator = InputValidator()
    return validator.validate_text_input(text, max_length=max_length, context="general")

def validate_math_expression(expression: str) -> str:
    """Validate mathematical expression"""
    validator = InputValidator()
    return validator.validate_text_input(expression, max_length=1000, context="math")

def validate_filename(filename: str) -> str:
    """Validate filename input"""
    validator = InputValidator()
    return validator.validate_text_input(filename, max_length=255, context="filename")

def is_input_safe(text: str) -> bool:
    """Check if input is safe"""
    validator = InputValidator()
    return validator.is_safe_for_display(text)

if __name__ == "__main__":
    # Test cases
    validator = InputValidator()
    
    test_cases = [
        # Valid inputs
        ("Hello world", "general"),
        ("2 + 2 * 3", "math"),
        ("What is machine learning?", "prompt"),
        ("document.txt", "filename"),
        
        # Security test cases (should fail)
        ("import os; os.system('rm -rf /')", "general"),
        ("__import__('subprocess').call(['ls'])", "general"),
        ("eval('print(1)')", "general"),
        ("<script>alert('xss')</script>", "general"),
        ("'; DROP TABLE users; --", "general"),
        ("../../../etc/passwd", "filename"),
    ]
    
    print("Input Validation Test Results:")
    print("=" * 60)
    
    for text, context in test_cases:
        try:
            result = validator.validate_text_input(text, context=context)
            print(f"✅ [{context}] {text[:50]}... -> VALID")
        except SecurityViolationError as e:
            print(f"🛡️  [{context}] {text[:50]}... -> BLOCKED (Security)")
        except ValidationError as e:
            print(f"❌ [{context}] {text[:50]}... -> INVALID ({e})")
        except Exception as e:
            print(f"⚠️  [{context}] {text[:50]}... -> ERROR ({e})")
    
    print("\nMath Expression Validation:")
    print("=" * 60)
    
    math_tests = [
        "2 + 2",
        "sqrt(16) + sin(pi/2)",
        "max(1, 2, 3, 4, 5)",
        "import os",  # Should fail
        "exec('print(1)')",  # Should fail
    ]
    
    for expr in math_tests:
        try:
            result = validator.validate_text_input(expr, context="math")
            print(f"✅ {expr} -> VALID MATH")
        except Exception as e:
            print(f"❌ {expr} -> {type(e).__name__}: {e}")