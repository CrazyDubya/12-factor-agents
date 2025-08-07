#!/usr/bin/env python3
"""
GPT Interface Framework
Common base architecture with abstract interfaces and dependency injection

This module provides the foundational architecture for all GPT-OSS interface
implementations, ensuring consistent patterns, extensibility, and maintainability.
"""

from abc import ABC, abstractmethod
from typing import Protocol, Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import threading
import queue
import time
from datetime import datetime
import requests
from pathlib import Path

# Configure framework logging
logger = logging.getLogger(__name__)

class InterfaceType(Enum):
    """Interface type enumeration"""
    MINIMAL = "minimal"
    BEAUTIFUL = "beautiful" 
    EXPERT = "expert"
    PRODUCTION = "production"

class SecurityLevel(Enum):
    """Security level enumeration"""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    PARANOID = "paranoid"

class ResponseFormat(Enum):
    """Response format enumeration"""
    PLAIN_TEXT = "plain_text"
    HARMONY = "harmony"
    JSON = "json"
    STRUCTURED = "structured"

@dataclass
class ModelConfig:
    """Model configuration data class"""
    name: str
    url: str
    timeout: int = 30
    max_tokens: int = 2048
    temperature: float = 0.7
    format: ResponseFormat = ResponseFormat.PLAIN_TEXT
    
    def validate(self) -> bool:
        """Validate configuration"""
        return (
            bool(self.name) and
            bool(self.url) and
            0 < self.timeout <= 300 and
            0 < self.max_tokens <= 50000 and
            0.0 <= self.temperature <= 2.0
        )

@dataclass
class SecurityConfig:
    """Security configuration data class"""
    level: SecurityLevel = SecurityLevel.STRICT
    enable_math_eval: bool = True
    enable_code_execution: bool = False
    max_input_length: int = 2000
    rate_limit: int = 10
    enable_audit_logging: bool = True
    blocked_patterns: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.level == SecurityLevel.PARANOID:
            self.enable_code_execution = False
            self.rate_limit = min(self.rate_limit, 5)

@dataclass
class UIConfig:
    """UI configuration data class"""
    interface_type: InterfaceType = InterfaceType.PRODUCTION
    window_size: tuple = (1000, 700)
    theme: str = "default"
    enable_tabs: bool = True
    enable_streaming: bool = True
    auto_save: bool = False

@dataclass
class PerformanceConfig:
    """Performance configuration data class"""
    connection_pool_size: int = 5
    max_connections: int = 10
    memory_limit_mb: int = 256
    enable_caching: bool = True
    cache_ttl_seconds: int = 300
    background_threads: int = 2

class ConfigurationProtocol(Protocol):
    """Configuration protocol for dependency injection"""
    model: ModelConfig
    security: SecurityConfig
    ui: UIConfig
    performance: PerformanceConfig

class ValidatorProtocol(Protocol):
    """Input validator protocol"""
    def validate_input(self, text: str, context: str = "general") -> str: ...
    def is_safe(self, text: str) -> bool: ...

class MathEvaluatorProtocol(Protocol):
    """Mathematical evaluator protocol"""
    def evaluate(self, expression: str) -> Union[int, float, str]: ...
    def is_math_expression(self, text: str) -> bool: ...

class ModelClientProtocol(Protocol):
    """Model client protocol"""
    def generate_response(self, prompt: str, **kwargs) -> str: ...
    def test_connection(self) -> bool: ...

class SecurityMonitorProtocol(Protocol):
    """Security monitoring protocol"""
    def log_event(self, event: str, severity: str = "INFO") -> None: ...
    def get_events(self) -> List[Dict[str, Any]]: ...

class PerformanceMonitorProtocol(Protocol):
    """Performance monitoring protocol"""
    def record_metric(self, name: str, value: float, tags: Dict[str, str] = None) -> None: ...
    def get_metrics(self) -> Dict[str, Any]: ...

class BaseGPTInterface(ABC):
    """
    Abstract base class for all GPT interface implementations
    
    Provides common functionality and enforces consistent interface patterns
    across all implementations while allowing for specific customizations.
    """
    
    def __init__(
        self,
        config: ConfigurationProtocol,
        validator: ValidatorProtocol,
        math_evaluator: MathEvaluatorProtocol,
        model_client: ModelClientProtocol,
        security_monitor: SecurityMonitorProtocol,
        performance_monitor: PerformanceMonitorProtocol
    ):
        """
        Initialize base interface with dependency injection
        
        Args:
            config: Configuration object
            validator: Input validator
            math_evaluator: Math expression evaluator
            model_client: Model communication client
            security_monitor: Security event monitor
            performance_monitor: Performance metrics monitor
        """
        self.config = config
        self.validator = validator
        self.math_evaluator = math_evaluator
        self.model_client = model_client
        self.security_monitor = security_monitor
        self.performance_monitor = performance_monitor
        
        # Common state
        self.is_processing = False
        self.processing_lock = threading.Lock()
        self.message_history: List[Dict[str, Any]] = []
        self.session_start = datetime.now()
        
        # Validate configuration
        self._validate_configuration()
        
        logger.info(f"Initialized {self.__class__.__name__} interface")
    
    def _validate_configuration(self) -> None:
        """Validate configuration at startup"""
        if not self.config.model.validate():
            raise ValueError("Invalid model configuration")
        
        logger.info("Configuration validation passed")
    
    @abstractmethod
    def setup_gui(self) -> None:
        """Setup graphical user interface - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def display_response(self, response: str, **kwargs) -> None:
        """Display response - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def update_status(self, message: str, status_type: str = "info") -> None:
        """Update status display - must be implemented by subclasses"""
        pass
    
    def send_message(self, user_input: str) -> bool:
        """
        Send message with common validation and processing
        
        Args:
            user_input: User input text
            
        Returns:
            True if message sent successfully, False otherwise
        """
        start_time = time.time()
        
        try:
            # Check if already processing
            with self.processing_lock:
                if self.is_processing:
                    self.update_status("Already processing a request", "warning")
                    return False
                self.is_processing = True
            
            # Validate input
            validated_input = self.validator.validate_input(
                user_input, 
                context="prompt"
            )
            
            # Security logging
            self.security_monitor.log_event(f"Message sent: {len(validated_input)} chars")
            
            # Handle math expressions locally
            if self.math_evaluator.is_math_expression(validated_input):
                result = self.math_evaluator.evaluate(validated_input)
                self.display_response(f"Math: {result}", response_type="math")
                self._add_to_history("USER", validated_input)
                self._add_to_history("MATH", str(result))
                return True
            
            # Send to model
            response = self.model_client.generate_response(validated_input)
            
            if response:
                self.display_response(response, response_type="assistant")
                self._add_to_history("USER", validated_input)
                self._add_to_history("ASSISTANT", response)
                
                # Performance metrics
                duration = time.time() - start_time
                self.performance_monitor.record_metric(
                    "response_time", 
                    duration, 
                    {"input_length": str(len(validated_input))}
                )
                
                return True
            else:
                self.update_status("No response received", "error")
                return False
                
        except Exception as e:
            self.security_monitor.log_event(f"Message processing error: {e}", "ERROR")
            self.update_status(f"Error: {e}", "error")
            return False
        finally:
            with self.processing_lock:
                self.is_processing = False
    
    def _add_to_history(self, role: str, content: str) -> None:
        """Add message to conversation history"""
        self.message_history.append({
            'timestamp': datetime.now().isoformat(),
            'role': role,
            'content': content[:1000]  # Truncate for storage
        })
        
        # Limit history size
        if len(self.message_history) > 1000:
            self.message_history = self.message_history[-500:]
    
    def clear_history(self) -> None:
        """Clear conversation history"""
        self.message_history.clear()
        self.security_monitor.log_event("History cleared")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        return {
            'session_duration': (datetime.now() - self.session_start).total_seconds(),
            'messages_sent': len([m for m in self.message_history if m['role'] == 'USER']),
            'responses_received': len([m for m in self.message_history if m['role'] == 'ASSISTANT']),
            'math_evaluations': len([m for m in self.message_history if m['role'] == 'MATH']),
            'security_events': len(self.security_monitor.get_events()),
            'interface_type': self.config.ui.interface_type.value
        }
    
    def test_system_health(self) -> Dict[str, bool]:
        """Test system health and component status"""
        health_status = {
            'model_connection': False,
            'validator_ready': False,
            'math_evaluator_ready': False,
            'security_monitor_ready': False,
            'performance_monitor_ready': False
        }
        
        try:
            health_status['model_connection'] = self.model_client.test_connection()
        except:
            pass
        
        try:
            health_status['validator_ready'] = self.validator.is_safe("test")
        except:
            pass
        
        try:
            health_status['math_evaluator_ready'] = isinstance(
                self.math_evaluator.evaluate("2+2"), (int, float)
            )
        except:
            pass
        
        try:
            health_status['security_monitor_ready'] = isinstance(
                self.security_monitor.get_events(), list
            )
        except:
            pass
        
        try:
            health_status['performance_monitor_ready'] = isinstance(
                self.performance_monitor.get_metrics(), dict
            )
        except:
            pass
        
        return health_status

class ModelClientFactory:
    """Factory for creating model clients"""
    
    @staticmethod
    def create_ollama_client(config: ModelConfig) -> 'OllamaModelClient':
        """Create Ollama model client"""
        return OllamaModelClient(config)
    
    @staticmethod
    def create_openai_client(config: ModelConfig) -> 'OpenAIModelClient':
        """Create OpenAI model client"""
        return OpenAIModelClient(config)

class OllamaModelClient:
    """Ollama model client implementation"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.session = requests.Session()
        # Configure connection pooling
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=5,
            pool_maxsize=10,
            max_retries=3
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response from Ollama"""
        try:
            response = self.session.post(
                f"{self.config.url}/api/generate",
                json={
                    "model": self.config.name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": self.config.max_tokens,
                        "temperature": self.config.temperature
                    }
                },
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return ""
                
        except Exception as e:
            logger.error(f"Ollama client error: {e}")
            return ""
    
    def test_connection(self) -> bool:
        """Test connection to Ollama"""
        try:
            response = self.session.get(
                f"{self.config.url}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False

class OpenAIModelClient:
    """OpenAI model client implementation"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        # Implementation for OpenAI API would go here
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response from OpenAI"""
        # Placeholder implementation
        return f"OpenAI response to: {prompt[:50]}..."
    
    def test_connection(self) -> bool:
        """Test connection to OpenAI"""
        # Placeholder implementation
        return False

class DefaultSecurityMonitor:
    """Default security monitoring implementation"""
    
    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
    
    def log_event(self, event: str, severity: str = "INFO") -> None:
        """Log security event"""
        with self.lock:
            self.events.append({
                'timestamp': datetime.now().isoformat(),
                'event': event,
                'severity': severity
            })
            
            # Limit event history
            if len(self.events) > 10000:
                self.events = self.events[-5000:]
        
        logger.log(
            getattr(logging, severity, logging.INFO),
            f"SECURITY: {event}"
        )
    
    def get_events(self) -> List[Dict[str, Any]]:
        """Get security events"""
        with self.lock:
            return self.events.copy()

class DefaultPerformanceMonitor:
    """Default performance monitoring implementation"""
    
    def __init__(self):
        self.metrics: Dict[str, List[Dict[str, Any]]] = {}
        self.lock = threading.Lock()
    
    def record_metric(self, name: str, value: float, tags: Dict[str, str] = None) -> None:
        """Record performance metric"""
        with self.lock:
            if name not in self.metrics:
                self.metrics[name] = []
            
            self.metrics[name].append({
                'timestamp': datetime.now().isoformat(),
                'value': value,
                'tags': tags or {}
            })
            
            # Limit metric history
            if len(self.metrics[name]) > 1000:
                self.metrics[name] = self.metrics[name][-500:]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics summary"""
        with self.lock:
            summary = {}
            for name, values in self.metrics.items():
                if values:
                    recent_values = [v['value'] for v in values[-100:]]
                    summary[name] = {
                        'count': len(values),
                        'latest': values[-1]['value'],
                        'average': sum(recent_values) / len(recent_values),
                        'min': min(recent_values),
                        'max': max(recent_values)
                    }
            return summary

class InterfaceFactory:
    """Factory for creating interface implementations"""
    
    @staticmethod
    def create_interface(
        interface_type: InterfaceType,
        config: ConfigurationProtocol,
        **dependencies
    ) -> BaseGPTInterface:
        """
        Create interface instance based on type
        
        Args:
            interface_type: Type of interface to create
            config: Configuration object
            **dependencies: Injected dependencies
            
        Returns:
            Interface instance
        """
        # Import specific implementations here to avoid circular imports
        if interface_type == InterfaceType.MINIMAL:
            from harmony_minimal_framework import MinimalInterface
            return MinimalInterface(config, **dependencies)
        elif interface_type == InterfaceType.BEAUTIFUL:
            from harmony_beautiful_framework import BeautifulInterface
            return BeautifulInterface(config, **dependencies)
        elif interface_type == InterfaceType.EXPERT:
            from harmony_expert_framework import ExpertInterface
            return ExpertInterface(config, **dependencies)
        elif interface_type == InterfaceType.PRODUCTION:
            from harmony_production_framework import ProductionInterface
            return ProductionInterface(config, **dependencies)
        else:
            raise ValueError(f"Unknown interface type: {interface_type}")

class DependencyContainer:
    """Dependency injection container"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
    
    def register(self, name: str, service: Any) -> None:
        """Register a service instance"""
        self._services[name] = service
    
    def register_factory(self, name: str, factory: Callable) -> None:
        """Register a service factory"""
        self._factories[name] = factory
    
    def get(self, name: str) -> Any:
        """Get service by name"""
        if name in self._services:
            return self._services[name]
        elif name in self._factories:
            service = self._factories[name]()
            self._services[name] = service
            return service
        else:
            raise KeyError(f"Service not found: {name}")
    
    def create_default_container(config: ConfigurationProtocol) -> 'DependencyContainer':
        """Create container with default services"""
        container = DependencyContainer()
        
        # Register default implementations
        from safe_math_parser import SafeMathEvaluator
        from input_validator import InputValidator
        
        container.register('validator', InputValidator())
        container.register('math_evaluator', SafeMathEvaluator())
        container.register('security_monitor', DefaultSecurityMonitor())
        container.register('performance_monitor', DefaultPerformanceMonitor())
        container.register('model_client', 
                          ModelClientFactory.create_ollama_client(config.model))
        
        return container

def create_production_interface(config_overrides: Dict[str, Any] = None) -> BaseGPTInterface:
    """
    Convenience function to create a production-ready interface
    
    Args:
        config_overrides: Optional configuration overrides
        
    Returns:
        Production interface instance
    """
    # Default configuration
    model_config = ModelConfig(
        name="gpt-oss:latest",
        url="http://localhost:11434"
    )
    
    security_config = SecurityConfig(
        level=SecurityLevel.STRICT,
        enable_audit_logging=True
    )
    
    ui_config = UIConfig(
        interface_type=InterfaceType.PRODUCTION
    )
    
    performance_config = PerformanceConfig(
        connection_pool_size=5
    )
    
    # Apply overrides
    if config_overrides:
        for key, value in config_overrides.items():
            if hasattr(model_config, key):
                setattr(model_config, key, value)
            elif hasattr(security_config, key):
                setattr(security_config, key, value)
            elif hasattr(ui_config, key):
                setattr(ui_config, key, value)
            elif hasattr(performance_config, key):
                setattr(performance_config, key, value)
    
    # Create configuration object
    class DefaultConfig:
        def __init__(self):
            self.model = model_config
            self.security = security_config
            self.ui = ui_config
            self.performance = performance_config
    
    config = DefaultConfig()
    
    # Create dependency container
    container = DependencyContainer.create_default_container(config)
    
    # Create interface
    return InterfaceFactory.create_interface(
        InterfaceType.PRODUCTION,
        config,
        validator=container.get('validator'),
        math_evaluator=container.get('math_evaluator'),
        model_client=container.get('model_client'),
        security_monitor=container.get('security_monitor'),
        performance_monitor=container.get('performance_monitor')
    )

if __name__ == "__main__":
    # Example usage and testing
    logging.basicConfig(level=logging.INFO)
    
    # Test configuration
    model_config = ModelConfig("gpt-oss:latest", "http://localhost:11434")
    print(f"Model config valid: {model_config.validate()}")
    
    # Test dependency injection
    container = DependencyContainer()
    container.register('test_service', "Hello World")
    print(f"Service retrieved: {container.get('test_service')}")
    
    # Test monitoring
    security_monitor = DefaultSecurityMonitor()
    security_monitor.log_event("Test security event")
    events = security_monitor.get_events()
    print(f"Security events: {len(events)}")
    
    performance_monitor = DefaultPerformanceMonitor()
    performance_monitor.record_metric("test_metric", 123.45)
    metrics = performance_monitor.get_metrics()
    print(f"Performance metrics: {metrics}")
    
    print("Framework validation completed successfully!")