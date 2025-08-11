#!/usr/bin/env python3
"""
Configuration management for disaster preparedness system
"""

import os
import json
import yaml
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

@dataclass
class AppConfig:
    """Application configuration settings"""
    data_dir: str = "data"
    output_dir: str = "output"
    cache_dir: str = "cache"
    log_level: str = "INFO"
    cache_enabled: bool = True
    max_cache_size: int = 1000
    session_timeout_minutes: int = 30
    backup_enabled: bool = True
    
    def __post_init__(self):
        """Create directories if they don't exist"""
        for directory in [self.data_dir, self.output_dir, self.cache_dir]:
            Path(directory).mkdir(exist_ok=True)
    
    @classmethod
    def from_file(cls, config_path: str) -> 'AppConfig':
        """Load configuration from file"""
        try:
            config_file = Path(config_path)
            if config_file.exists():
                if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                    with open(config_file, 'r') as f:
                        data = yaml.safe_load(f)
                else:
                    with open(config_file, 'r') as f:
                        data = json.load(f)
                return cls(**data)
            else:
                logger.info(f"Config file {config_path} not found, using defaults")
                return cls()
        except Exception as e:
            logger.error(f"Error loading config from {config_path}: {e}")
            return cls()
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Load configuration from environment variables"""
        return cls(
            data_dir=os.getenv('RISK_DATA_DIR', 'data'),
            output_dir=os.getenv('RISK_OUTPUT_DIR', 'output'),
            cache_dir=os.getenv('RISK_CACHE_DIR', 'cache'),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            cache_enabled=os.getenv('CACHE_ENABLED', 'true').lower() == 'true',
            max_cache_size=int(os.getenv('MAX_CACHE_SIZE', '1000')),
            session_timeout_minutes=int(os.getenv('SESSION_TIMEOUT', '30')),
            backup_enabled=os.getenv('BACKUP_ENABLED', 'true').lower() == 'true'
        )
    
    def save_to_file(self, config_path: str):
        """Save configuration to file"""
        try:
            config_file = Path(config_path)
            data = asdict(self)
            
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                with open(config_file, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False)
            else:
                with open(config_file, 'w') as f:
                    json.dump(data, f, indent=2)
            
            logger.info(f"Configuration saved to {config_path}")
        except Exception as e:
            logger.error(f"Error saving config to {config_path}: {e}")

def setup_logging(config: AppConfig):
    """Setup logging configuration"""
    log_dir = Path(config.output_dir) / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.log_level))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # File handler for detailed logs
    file_handler = logging.FileHandler(log_dir / 'risk_assessment.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler for user-friendly output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, config.log_level))
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # Error file handler
    error_handler = logging.FileHandler(log_dir / 'errors.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    logger.info(f"Logging configured with level: {config.log_level}")

# Global configuration instance
app_config = AppConfig.from_env()