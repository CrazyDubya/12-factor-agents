#!/usr/bin/env python3
"""
Comprehensive input validation and error handling
"""

import re
from typing import Any, Callable, List, Optional, Union
from models import LocationType
import logging

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class InputValidator:
    """Handles all input validation with clear error messages"""
    
    @staticmethod
    def validate_age(value: str, field_name: str = "Age") -> int:
        """Validate age input with context-specific ranges"""
        try:
            age = int(value.strip())
            if age < 0:
                raise ValidationError(f"{field_name} cannot be negative")
            if age > 120:
                raise ValidationError(f"{field_name} cannot be greater than 120")
            return age
        except ValueError:
            raise ValidationError(f"{field_name} must be a whole number")
    
    @staticmethod
    def validate_adult_age(value: str) -> int:
        """Validate adult age (18-120)"""
        age = InputValidator.validate_age(value, "Adult age")
        if age < 18:
            raise ValidationError("Adult age must be at least 18")
        return age
    
    @staticmethod
    def validate_child_age(value: str) -> int:
        """Validate child age (0-17)"""
        age = InputValidator.validate_age(value, "Child age")
        if age >= 18:
            raise ValidationError("Child age must be less than 18")
        return age
    
    @staticmethod
    def validate_positive_int(value: str, field_name: str) -> int:
        """Validate positive integer"""
        try:
            num = int(value.strip())
            if num < 0:
                raise ValidationError(f"{field_name} cannot be negative")
            return num
        except ValueError:
            raise ValidationError(f"{field_name} must be a whole number")
    
    @staticmethod
    def validate_positive_float(value: str, field_name: str) -> float:
        """Validate positive float"""
        try:
            num = float(value.strip())
            if num < 0:
                raise ValidationError(f"{field_name} cannot be negative")
            return num
        except ValueError:
            raise ValidationError(f"{field_name} must be a number")
    
    @staticmethod
    def validate_choice(value: str, choices: List[str], field_name: str) -> str:
        """Validate choice from list of options"""
        value = value.strip().lower()
        choices_lower = [choice.lower() for choice in choices]
        
        if value not in choices_lower:
            choices_str = ", ".join(choices)
            raise ValidationError(f"{field_name} must be one of: {choices_str}")
        
        # Return original case version
        return choices[choices_lower.index(value)]
    
    @staticmethod
    def validate_location_type(value: str) -> LocationType:
        """Validate location type"""
        location_choices = [loc.value for loc in LocationType]
        validated = InputValidator.validate_choice(value, location_choices, "Location type")
        return LocationType(validated)
    
    @staticmethod
    def validate_income_range(value: str) -> str:
        """Validate income range"""
        valid_ranges = [
            "<30k", "30-50k", "50-75k", "75-100k", "100-150k", ">150k"
        ]
        return InputValidator.validate_choice(value, valid_ranges, "Income range")
    
    @staticmethod
    def validate_yes_no(value: str, field_name: str) -> bool:
        """Validate yes/no input"""
        value = value.strip().lower()
        if value in ['y', 'yes', 'true', '1']:
            return True
        elif value in ['n', 'no', 'false', '0']:
            return False
        else:
            raise ValidationError(f"{field_name} must be yes/no (y/n)")
    
    @staticmethod
    def validate_phone(value: str) -> str:
        """Validate phone number format"""
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', value)
        
        if len(digits) == 10:
            # Format as (XXX) XXX-XXXX
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            # Format as 1-(XXX) XXX-XXXX
            return f"1-({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        else:
            raise ValidationError("Phone number must be 10 digits (or 11 with country code)")
    
    @staticmethod
    def validate_email(value: str) -> str:
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value.strip()):
            raise ValidationError("Please enter a valid email address")
        return value.strip().lower()

def safe_input(prompt: str, 
               validator: Callable[[str], Any], 
               max_attempts: int = 3,
               help_text: Optional[str] = None) -> Optional[Any]:
    """
    Safely collect user input with validation and retry logic
    
    Args:
        prompt: Input prompt to display
        validator: Function to validate input
        max_attempts: Maximum number of retry attempts
        help_text: Optional help text to display on error
    
    Returns:
        Validated input value or None if cancelled
    """
    for attempt in range(max_attempts):
        try:
            value = input(prompt).strip()
            
            # Allow empty input to be handled by validator
            if not value and help_text:
                print(f"Help: {help_text}")
                continue
                
            return validator(value)
            
        except ValidationError as e:
            print(f"❌ {e}")
            if help_text and attempt == 0:
                print(f"💡 {help_text}")
            if attempt < max_attempts - 1:
                print("Please try again.\n")
            else:
                print("❌ Maximum attempts reached.")
                
        except KeyboardInterrupt:
            print("\n🚫 Operation cancelled by user.")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in safe_input: {e}")
            print(f"❌ Unexpected error: {e}")
            if attempt < max_attempts - 1:
                print("Please try again.\n")
    
    return None

def confirm_action(message: str, default: bool = False) -> bool:
    """
    Ask user to confirm an action
    
    Args:
        message: Confirmation message
        default: Default value if user just presses enter
    
    Returns:
        True if confirmed, False otherwise
    """
    default_text = " [Y/n]" if default else " [y/N]"
    prompt = f"{message}{default_text}: "
    
    try:
        response = input(prompt).strip().lower()
        if not response:
            return default
        return response in ['y', 'yes']
    except KeyboardInterrupt:
        print("\n🚫 Operation cancelled.")
        return False

class ProgressIndicator:
    """Simple progress indicator for long operations"""
    
    def __init__(self, total_steps: int, description: str = "Processing"):
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
    
    def update(self, step: Optional[int] = None, description: Optional[str] = None):
        """Update progress"""
        if step is not None:
            self.current_step = step
        else:
            self.current_step += 1
            
        if description:
            self.description = description
        
        percentage = (self.current_step / self.total_steps) * 100
        bar_length = 30
        filled_length = int(bar_length * self.current_step // self.total_steps)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        print(f'\r{self.description}: |{bar}| {percentage:.1f}% ({self.current_step}/{self.total_steps})', end='', flush=True)
        
        if self.current_step >= self.total_steps:
            print()  # New line when complete
    
    def finish(self, message: str = "Complete"):
        """Mark as finished"""
        self.current_step = self.total_steps
        self.update(description=message)