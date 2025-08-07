#!/usr/bin/env python3
"""
Production Security Test Suite
Comprehensive security testing for GPT-OSS interface implementations

This test suite validates all security controls and ensures production readiness
by testing against known attack vectors and security vulnerabilities.
"""

import unittest
import sys
import os
from pathlib import Path
import time
import threading
from unittest.mock import patch, MagicMock, Mock

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

# Import security modules
from safe_math_parser import SafeMathEvaluator, MathSecurityError
from input_validator import InputValidator, ValidationError, SecurityViolationError

class TestSafeMathParser(unittest.TestCase):
    """Test safe mathematical expression parser security"""
    
    def setUp(self):
        self.evaluator = SafeMathEvaluator()
    
    def test_basic_math_operations(self):
        """Test that basic math operations work correctly"""
        test_cases = [
            ("2 + 2", 4),
            ("15 * 23 + 45", 390),
            ("(10 + 5) * 2", 30),
            ("2^3", 8),
            ("sqrt(16)", 4.0),
            ("sin(pi/2)", 1.0),
            ("abs(-42)", 42),
        ]
        
        for expr, expected in test_cases:
            with self.subTest(expr=expr):
                result = self.evaluator.evaluate(expr)
                if isinstance(expected, float):
                    self.assertAlmostEqual(result, expected, places=5)
                else:
                    self.assertEqual(result, expected)
    
    def test_code_execution_prevention(self):
        """Test that code execution attempts are blocked"""
        dangerous_expressions = [
            "__import__('os').system('whoami')",
            "exec('print(1)')",
            "eval('2+2')",
            "compile('print(1)', '<string>', 'exec')",
            "globals()",
            "locals()",
            "vars()",
            "dir()",
            "getattr(os, 'system')('ls')",
            "setattr(sys, 'exit', lambda: None)",
            "open('/etc/passwd')",
            "[x for x in ().__class__.__bases__[0].__subclasses__() if 'file' in x.__name__][0]",
        ]
        
        for expr in dangerous_expressions:
            with self.subTest(expr=expr):
                with self.assertRaises(MathSecurityError):
                    self.evaluator.evaluate(expr)
    
    def test_input_length_limits(self):
        """Test input length validation"""
        # Test maximum length
        long_expr = "1 + " * 1000 + "1"  # Exceeds default max_length
        with self.assertRaises(MathSecurityError):
            self.evaluator.evaluate(long_expr)
    
    def test_depth_protection(self):
        """Test recursion depth protection"""
        # Create deeply nested expression
        nested_expr = "(" * 100 + "1" + ")" * 100
        with self.assertRaises(MathSecurityError):
            self.evaluator.evaluate(nested_expr)
    
    def test_error_handling(self):
        """Test mathematical error handling"""
        error_cases = [
            ("1/0", ArithmeticError),  # Division by zero
            ("sqrt(-1)", ArithmeticError),  # Invalid math operation
            ("unknown_func(1)", MathSecurityError),  # Unknown function
            ("1 +", ValueError),  # Syntax error
        ]
        
        for expr, expected_error in error_cases:
            with self.subTest(expr=expr):
                with self.assertRaises(expected_error):
                    self.evaluator.evaluate(expr)
    
    def test_function_whitelist(self):
        """Test that only whitelisted functions are allowed"""
        # Allowed functions
        allowed_functions = [
            "abs(-5)",
            "max(1, 2, 3)",
            "min(4, 5, 6)",
            "round(3.14159, 2)",
            "sqrt(25)",
            "sin(0)",
            "log(e)",
        ]
        
        for expr in allowed_functions:
            with self.subTest(expr=expr):
                result = self.evaluator.evaluate(expr)
                self.assertIsInstance(result, (int, float))
        
        # Disallowed functions
        disallowed_functions = [
            "print(1)",
            "input()",
            "len('test')",
            "str(123)",
            "int('42')",
            "list([1, 2, 3])",
            "dict()",
        ]
        
        for expr in disallowed_functions:
            with self.subTest(expr=expr):
                with self.assertRaises(MathSecurityError):
                    self.evaluator.evaluate(expr)

class TestInputValidator(unittest.TestCase):
    """Test comprehensive input validation security"""
    
    def setUp(self):
        self.validator = InputValidator()
    
    def test_basic_validation(self):
        """Test basic input validation"""
        valid_inputs = [
            "Hello world",
            "What is machine learning?",
            "Calculate 2 + 2",
            "Normal text with numbers 123",
        ]
        
        for text in valid_inputs:
            with self.subTest(text=text):
                result = self.validator.validate_text_input(text)
                self.assertIsInstance(result, str)
                self.assertGreater(len(result), 0)
    
    def test_security_pattern_detection(self):
        """Test detection of security violation patterns"""
        security_violations = [
            "__import__('os')",
            "exec('malicious code')",
            "eval('dangerous')",
            "subprocess.call(['ls'])",
            "os.system('whoami')",
            "import sys",
            "from os import system",
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "$(rm -rf /)",
            "`malicious command`",
            "union select * from users",
            "delete from users where 1=1",
        ]
        
        for violation in security_violations:
            with self.subTest(violation=violation):
                with self.assertRaises(SecurityViolationError):
                    self.validator.validate_text_input(violation, context="general")
    
    def test_length_validation(self):
        """Test input length limits"""
        # Test within limits
        normal_text = "Normal length text"
        result = self.validator.validate_text_input(normal_text, max_length=100)
        self.assertEqual(result, normal_text)
        
        # Test exceeding limits
        long_text = "x" * 5000
        with self.assertRaises(ValidationError):
            self.validator.validate_text_input(long_text, max_length=1000)
    
    def test_context_specific_validation(self):
        """Test context-aware validation"""
        # Math context
        math_expr = "2 + 2 * sin(pi)"
        result = self.validator.validate_text_input(math_expr, context="math")
        self.assertIn("sin", result)
        
        # Math context with invalid chars
        with self.assertRaises(ValidationError):
            self.validator.validate_text_input("2 + eval('3')", context="math")
        
        # Filename context
        filename = "document.txt"
        result = self.validator.validate_text_input(filename, context="filename")
        self.assertEqual(result, filename)
        
        # Filename with dangerous chars
        result = self.validator.validate_text_input("doc<>:name.txt", context="filename")
        self.assertNotIn("<", result)
        self.assertNotIn(":", result)
    
    def test_unicode_normalization(self):
        """Test Unicode normalization and filtering"""
        # Test Unicode normalization
        unicode_text = "café"  # Contains combining characters
        result = self.validator.validate_text_input(unicode_text)
        self.assertIsInstance(result, str)
        
        # Test control character removal
        control_chars = "text\x00with\x01controls"
        result = self.validator.validate_text_input(control_chars)
        self.assertNotIn("\x00", result)
        self.assertNotIn("\x01", result)
    
    def test_json_validation(self):
        """Test JSON input validation with depth checking"""
        # Valid JSON
        valid_json = '{"name": "test", "value": 123}'
        result = self.validator.validate_json_input(valid_json)
        self.assertIsInstance(result, dict)
        
        # Invalid JSON
        invalid_json = '{"invalid": json}'
        with self.assertRaises(ValidationError):
            self.validator.validate_json_input(invalid_json)
        
        # Deeply nested JSON
        deep_json = '{"a":' * 20 + '"value"' + '}' * 20
        with self.assertRaises(ValidationError):
            self.validator.validate_json_input(deep_json, max_depth=10)

class TestRateLimiting(unittest.TestCase):
    """Test rate limiting functionality"""
    
    def test_rate_limiter_basic(self):
        """Test basic rate limiting functionality"""
        # Import here to avoid circular imports during test discovery
        from harmony_expert_production import RateLimiter
        
        rate_limiter = RateLimiter(max_requests=5, time_window=10)
        
        # Should allow up to max_requests
        for i in range(5):
            self.assertTrue(rate_limiter.is_allowed())
        
        # Should block additional requests
        self.assertFalse(rate_limiter.is_allowed())
    
    def test_rate_limiter_time_window(self):
        """Test rate limiter time window functionality"""
        from harmony_expert_production import RateLimiter
        
        rate_limiter = RateLimiter(max_requests=2, time_window=1)
        
        # Use up quota
        self.assertTrue(rate_limiter.is_allowed())
        self.assertTrue(rate_limiter.is_allowed())
        self.assertFalse(rate_limiter.is_allowed())
        
        # Wait for time window to pass
        time.sleep(1.1)
        
        # Should be allowed again
        self.assertTrue(rate_limiter.is_allowed())
    
    def test_rate_limiter_status(self):
        """Test rate limiter status reporting"""
        from harmony_expert_production import RateLimiter
        
        rate_limiter = RateLimiter(max_requests=3, time_window=60)
        
        # Initial status
        status = rate_limiter.get_status()
        self.assertEqual(status['current_requests'], 0)
        self.assertEqual(status['max_requests'], 3)
        self.assertEqual(status['available'], 3)
        
        # After some requests
        rate_limiter.is_allowed()
        rate_limiter.is_allowed()
        
        status = rate_limiter.get_status()
        self.assertEqual(status['current_requests'], 2)
        self.assertEqual(status['available'], 1)

class TestProductionConfiguration(unittest.TestCase):
    """Test production configuration management"""
    
    @patch.dict(os.environ, {
        'OLLAMA_URL': 'http://test:11434',
        'REQUEST_TIMEOUT': '30',
        'STRICT_VALIDATION': 'true'
    })
    def test_environment_configuration(self):
        """Test configuration loading from environment"""
        from harmony_expert_production import ProductionConfig
        
        config = ProductionConfig()
        self.assertEqual(config.ollama_url, 'http://test:11434')
        self.assertEqual(config.request_timeout, 30)
        self.assertTrue(config.strict_validation)
    
    def test_configuration_validation(self):
        """Test configuration validation"""
        from harmony_expert_production import ProductionConfig, ConfigurationError
        
        # Test invalid URL
        with patch.dict(os.environ, {'OLLAMA_URL': 'invalid-url'}):
            with self.assertRaises(ConfigurationError):
                ProductionConfig()
        
        # Test invalid timeout
        with patch.dict(os.environ, {'REQUEST_TIMEOUT': '500'}):
            with self.assertRaises(ConfigurationError):
                ProductionConfig()

class TestSecurityLogging(unittest.TestCase):
    """Test security event logging functionality"""
    
    def test_security_event_logging(self):
        """Test security event logging"""
        # Mock the GUI class to test logging
        with patch('tkinter.Tk'), \
             patch('harmony_expert_production.ProductionConfig'), \
             patch('harmony_expert_production.InputValidator'), \
             patch('harmony_expert_production.SafeMathEvaluator'), \
             patch('harmony_expert_production.RateLimiter'):
            
            from harmony_expert_production import HarmonyExpertProductionGUI
            
            gui = HarmonyExpertProductionGUI(MagicMock())
            gui.security_events = []
            gui.security_counter_label = MagicMock()
            gui.display_security_event = MagicMock()
            
            # Test logging
            gui.log_security_event("Test security event", "HIGH")
            
            # Verify event was logged
            self.assertEqual(len(gui.security_events), 1)
            self.assertEqual(gui.security_events[0]['event'], "Test security event")
            self.assertEqual(gui.security_events[0]['severity'], "HIGH")

class TestIntegrationSecurity(unittest.TestCase):
    """Integration tests for complete security functionality"""
    
    def test_end_to_end_security_validation(self):
        """Test complete security validation pipeline"""
        validator = InputValidator()
        evaluator = SafeMathEvaluator()
        
        # Test safe mathematical expression
        math_expr = "sqrt(16) + sin(pi/2)"
        
        # Should pass validation
        validated = validator.validate_text_input(math_expr, context="math")
        self.assertIsInstance(validated, str)
        
        # Should evaluate safely
        result = evaluator.evaluate(validated)
        self.assertIsInstance(result, (int, float))
        
        # Test dangerous expression
        dangerous_expr = "__import__('os').system('whoami')"
        
        # Should be blocked by validator
        with self.assertRaises(SecurityViolationError):
            validator.validate_text_input(dangerous_expr, context="math")
        
        # Should also be blocked by evaluator if it somehow gets through
        with self.assertRaises(MathSecurityError):
            evaluator.evaluate(dangerous_expr)
    
    def test_concurrent_security_operations(self):
        """Test security under concurrent access"""
        validator = InputValidator()
        
        def validate_input(input_text):
            try:
                return validator.validate_text_input(input_text)
            except (ValidationError, SecurityViolationError):
                return None
        
        # Test concurrent validation
        inputs = ["valid text"] * 10 + ["__import__('os')"] * 5
        threads = []
        results = []
        
        def worker(text):
            result = validate_input(text)
            results.append(result)
        
        for text in inputs:
            thread = threading.Thread(target=worker, args=(text,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Check results
        valid_results = [r for r in results if r is not None]
        blocked_results = [r for r in results if r is None]
        
        self.assertEqual(len(valid_results), 10)  # Valid inputs processed
        self.assertEqual(len(blocked_results), 5)  # Dangerous inputs blocked

class SecurityTestSuite:
    """Security test suite runner with reporting"""
    
    def __init__(self):
        self.test_results = {}
    
    def run_all_tests(self):
        """Run all security tests and generate report"""
        test_classes = [
            TestSafeMathParser,
            TestInputValidator,
            TestRateLimiting,
            TestProductionConfiguration,
            TestSecurityLogging,
            TestIntegrationSecurity,
        ]
        
        total_tests = 0
        total_failures = 0
        total_errors = 0
        
        print("=" * 80)
        print("GPT-OSS PRODUCTION SECURITY TEST SUITE")
        print("=" * 80)
        
        for test_class in test_classes:
            suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)
            
            total_tests += result.testsRun
            total_failures += len(result.failures)
            total_errors += len(result.errors)
            
            self.test_results[test_class.__name__] = {
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'success': result.wasSuccessful()
            }
        
        self.generate_security_report(total_tests, total_failures, total_errors)
    
    def generate_security_report(self, total_tests, total_failures, total_errors):
        """Generate security test report"""
        success_rate = ((total_tests - total_failures - total_errors) / total_tests) * 100 if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("SECURITY TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Failures: {total_failures}")
        print(f"Errors: {total_errors}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100.0:
            print("\n🔒 SECURITY STATUS: ✅ ALL TESTS PASSED - PRODUCTION READY")
        elif success_rate >= 95.0:
            print("\n🔒 SECURITY STATUS: ⚠️ MOSTLY SECURE - REVIEW REQUIRED")
        else:
            print("\n🔒 SECURITY STATUS: ❌ SECURITY ISSUES FOUND - NOT PRODUCTION READY")
        
        print("\nDetailed Results:")
        for test_class, results in self.test_results.items():
            status = "✅ PASS" if results['success'] else "❌ FAIL"
            print(f"  {test_class}: {status} ({results['tests_run']} tests)")
        
        print("=" * 80)

if __name__ == "__main__":
    # Run security test suite
    security_suite = SecurityTestSuite()
    security_suite.run_all_tests()