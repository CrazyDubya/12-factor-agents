#!/usr/bin/env python3
"""
Safe Mathematical Expression Parser
Replaces dangerous eval() calls with AST-based safe evaluation

This module provides secure mathematical expression evaluation without
code execution vulnerabilities. Uses Python's AST module to parse and
evaluate only mathematical operations.
"""

import ast
import operator
from typing import Union, Dict, Any
import re
import math

class MathSecurityError(Exception):
    """Raised when a security violation is detected in mathematical expressions"""
    pass

class SafeMathEvaluator:
    """
    Safe mathematical expression evaluator using AST parsing
    
    Supports:
    - Basic arithmetic: +, -, *, /, **, %
    - Parentheses for grouping
    - Mathematical functions: sin, cos, tan, sqrt, log, etc.
    - Mathematical constants: pi, e
    
    Security features:
    - No code execution capabilities
    - Whitelist-based operation validation
    - Input sanitization and length limits
    - Stack depth protection against infinite recursion
    """
    
    # Whitelisted operations
    SAFE_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }
    
    # Whitelisted mathematical functions
    SAFE_FUNCTIONS = {
        'abs': abs,
        'round': round,
        'min': min,
        'max': max,
        'sum': sum,
        'sqrt': math.sqrt,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'asin': math.asin,
        'acos': math.acos,
        'atan': math.atan,
        'log': math.log,
        'log10': math.log10,
        'exp': math.exp,
        'ceil': math.ceil,
        'floor': math.floor,
        'degrees': math.degrees,
        'radians': math.radians,
    }
    
    # Mathematical constants
    SAFE_CONSTANTS = {
        'pi': math.pi,
        'e': math.e,
        'tau': math.tau,
        'inf': math.inf,
    }
    
    def __init__(self, max_length: int = 1000, max_depth: int = 50):
        """
        Initialize safe math evaluator
        
        Args:
            max_length: Maximum expression length (default 1000)
            max_depth: Maximum AST recursion depth (default 50)
        """
        self.max_length = max_length
        self.max_depth = max_depth
        self._depth = 0
    
    def evaluate(self, expression: str) -> Union[float, int]:
        """
        Safely evaluate a mathematical expression
        
        Args:
            expression: Mathematical expression string
            
        Returns:
            Numeric result of the expression
            
        Raises:
            MathSecurityError: If expression contains unsafe operations
            ValueError: If expression is malformed
            ArithmeticError: If mathematical error occurs (div by zero, etc.)
        """
        # Input validation
        if not expression or not isinstance(expression, str):
            raise ValueError("Expression must be a non-empty string")
        
        if len(expression) > self.max_length:
            raise MathSecurityError(f"Expression too long (max {self.max_length} characters)")
        
        # Sanitize input
        expression = self._sanitize_expression(expression)
        
        # Parse and evaluate
        try:
            tree = ast.parse(expression, mode='eval')
            self._depth = 0
            return self._eval_node(tree.body)
        except SyntaxError as e:
            raise ValueError(f"Invalid mathematical expression: {e}")
        except RecursionError:
            raise MathSecurityError("Expression too complex (recursion limit exceeded)")
    
    def _sanitize_expression(self, expression: str) -> str:
        """
        Sanitize mathematical expression
        
        Args:
            expression: Raw expression string
            
        Returns:
            Sanitized expression
        """
        # Remove whitespace
        expression = expression.strip()
        
        # Replace common mathematical symbols
        replacements = {
            '^': '**',  # Power operator
            '×': '*',   # Multiplication symbol
            '÷': '/',   # Division symbol
        }
        
        for old, new in replacements.items():
            expression = expression.replace(old, new)
        
        # Basic security check - only allow mathematical characters
        allowed_chars = set('0123456789+-*/().,^×÷ abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_')
        if not all(c in allowed_chars for c in expression):
            raise MathSecurityError("Expression contains non-mathematical characters")
        
        return expression
    
    def _eval_node(self, node: ast.AST) -> Union[float, int]:
        """
        Recursively evaluate AST node
        
        Args:
            node: AST node to evaluate
            
        Returns:
            Numeric result
        """
        # Depth protection
        self._depth += 1
        if self._depth > self.max_depth:
            raise MathSecurityError("Expression too complex (depth limit exceeded)")
        
        try:
            if isinstance(node, ast.Constant):
                # Numeric constant
                if isinstance(node.value, (int, float)):
                    return node.value
                else:
                    raise MathSecurityError(f"Non-numeric constant: {type(node.value)}")
            
            elif isinstance(node, ast.Num):  # Python < 3.8 compatibility
                return node.n
            
            elif isinstance(node, ast.Name):
                # Variable/constant reference
                if node.id in self.SAFE_CONSTANTS:
                    return self.SAFE_CONSTANTS[node.id]
                else:
                    raise MathSecurityError(f"Unknown variable: {node.id}")
            
            elif isinstance(node, ast.BinOp):
                # Binary operation
                if type(node.op) not in self.SAFE_OPERATORS:
                    raise MathSecurityError(f"Unsafe binary operator: {type(node.op)}")
                
                left = self._eval_node(node.left)
                right = self._eval_node(node.right)
                op = self.SAFE_OPERATORS[type(node.op)]
                
                try:
                    result = op(left, right)
                    if isinstance(result, complex):
                        raise ArithmeticError("Complex numbers not supported")
                    return result
                except ZeroDivisionError:
                    raise ArithmeticError("Division by zero")
                except OverflowError:
                    raise ArithmeticError("Mathematical overflow")
            
            elif isinstance(node, ast.UnaryOp):
                # Unary operation
                if type(node.op) not in self.SAFE_OPERATORS:
                    raise MathSecurityError(f"Unsafe unary operator: {type(node.op)}")
                
                operand = self._eval_node(node.operand)
                op = self.SAFE_OPERATORS[type(node.op)]
                return op(operand)
            
            elif isinstance(node, ast.Call):
                # Function call
                if not isinstance(node.func, ast.Name):
                    raise MathSecurityError("Only simple function calls allowed")
                
                func_name = node.func.id
                if func_name not in self.SAFE_FUNCTIONS:
                    raise MathSecurityError(f"Unsafe function: {func_name}")
                
                # Evaluate arguments
                args = [self._eval_node(arg) for arg in node.args]
                
                # Check for keyword arguments (not allowed for security)
                if node.keywords:
                    raise MathSecurityError("Keyword arguments not allowed")
                
                # Call function
                func = self.SAFE_FUNCTIONS[func_name]
                try:
                    return func(*args)
                except (ValueError, TypeError, ArithmeticError) as e:
                    raise ArithmeticError(f"Function error: {e}")
            
            elif isinstance(node, ast.List) or isinstance(node, ast.Tuple):
                # List/tuple for functions like sum, min, max
                return [self._eval_node(item) for item in node.elts]
            
            else:
                raise MathSecurityError(f"Unsafe AST node type: {type(node)}")
        
        finally:
            self._depth -= 1
    
    def validate_expression(self, expression: str) -> tuple[bool, str]:
        """
        Validate mathematical expression without evaluation
        
        Args:
            expression: Expression to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            self.evaluate(expression)
            return True, "Valid"
        except (MathSecurityError, ValueError, ArithmeticError) as e:
            return False, str(e)

def safe_eval(expression: str, max_length: int = 1000) -> str:
    """
    Convenience function for safe mathematical evaluation
    
    Args:
        expression: Mathematical expression to evaluate
        max_length: Maximum expression length
        
    Returns:
        String representation of result or error message
    """
    evaluator = SafeMathEvaluator(max_length=max_length)
    
    try:
        result = evaluator.evaluate(expression)
        return str(result)
    except MathSecurityError as e:
        return f"Security Error: {e}"
    except ValueError as e:
        return f"Invalid Expression: {e}"
    except ArithmeticError as e:
        return f"Math Error: {e}"
    except Exception as e:
        return f"Unexpected Error: {e}"

# Compatibility functions for existing code
def is_math_expression(expression: str) -> bool:
    """
    Check if string is a mathematical expression
    
    Args:
        expression: String to check
        
    Returns:
        True if appears to be mathematical expression
    """
    if not expression or len(expression) > 1000:
        return False
    
    # Quick heuristic check
    math_chars = set('0123456789+-*/().^×÷ abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_')
    has_numbers = any(c.isdigit() for c in expression)
    has_operators = any(c in '+-*/' for c in expression)
    all_safe_chars = all(c in math_chars for c in expression)
    
    return has_numbers and has_operators and all_safe_chars

def quick_math_eval(expression: str) -> str:
    """
    Quick mathematical evaluation with basic error handling
    
    Args:
        expression: Mathematical expression
        
    Returns:
        Result string or error message
    """
    if not is_math_expression(expression):
        return "Not a mathematical expression"
    
    return safe_eval(expression)

if __name__ == "__main__":
    # Test cases
    evaluator = SafeMathEvaluator()
    
    test_cases = [
        "2 + 2",
        "15 * 23 + 45",
        "(10 + 5) * 2",
        "2^3",
        "sqrt(16)",
        "sin(pi/2)",
        "log(e)",
        "max(1, 2, 3, 4, 5)",
        "abs(-42)",
        # Security test cases
        "__import__('os')",  # Should fail
        "exec('print(1)')",  # Should fail
        "eval('2+2')",       # Should fail
    ]
    
    print("Safe Math Evaluator Test Results:")
    print("=" * 50)
    
    for expr in test_cases:
        try:
            result = evaluator.evaluate(expr)
            print(f"✅ {expr} = {result}")
        except Exception as e:
            print(f"❌ {expr} -> {type(e).__name__}: {e}")
    
    print("\nValidation Tests:")
    print("=" * 50)
    
    for expr in test_cases[:9]:  # Only valid expressions
        is_valid, message = evaluator.validate_expression(expr)
        status = "✅" if is_valid else "❌"
        print(f"{status} {expr} -> {message}")