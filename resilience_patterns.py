#!/usr/bin/env python3
"""
Resilience Patterns Module
Circuit breaker, retry logic, bulkhead isolation, and timeout handling
for robust GPT-OSS interface operations
"""

import time
import threading
import logging
import random
from typing import Optional, Callable, Any, Dict, List, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import deque, defaultdict
import asyncio
import inspect
from contextlib import contextmanager
import queue

logger = logging.getLogger(__name__)

class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking requests
    HALF_OPEN = "half_open"  # Testing recovery

class RetryStrategy(Enum):
    """Retry strategy types"""
    FIXED_DELAY = "fixed_delay"
    EXPONENTIAL_BACKOFF = "exponential_backoff" 
    LINEAR_BACKOFF = "linear_backoff"
    RANDOM_JITTER = "random_jitter"

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5           # Failures before opening
    recovery_timeout: float = 30.0       # Seconds before half-open
    success_threshold: int = 3           # Successes before closing
    timeout: float = 10.0                # Request timeout
    minimum_throughput: int = 10         # Minimum requests for evaluation
    
    def validate(self) -> bool:
        """Validate configuration"""
        return (
            self.failure_threshold > 0 and
            self.recovery_timeout > 0 and
            self.success_threshold > 0 and
            self.timeout > 0 and
            self.minimum_throughput > 0
        )

@dataclass
class RetryConfig:
    """Retry configuration"""
    max_attempts: int = 3
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    base_delay: float = 1.0              # Base delay in seconds
    max_delay: float = 60.0              # Maximum delay in seconds
    backoff_multiplier: float = 2.0      # Exponential backoff multiplier
    jitter_range: float = 0.1            # Random jitter range (0.0-1.0)
    
    def validate(self) -> bool:
        """Validate configuration"""
        return (
            self.max_attempts > 0 and
            self.base_delay >= 0 and
            self.max_delay >= self.base_delay and
            self.backoff_multiplier > 1.0 and
            0.0 <= self.jitter_range <= 1.0
        )

@dataclass
class BulkheadConfig:
    """Bulkhead isolation configuration"""
    max_concurrent_calls: int = 10
    queue_size: int = 100
    timeout: float = 30.0
    
    def validate(self) -> bool:
        """Validate configuration"""
        return (
            self.max_concurrent_calls > 0 and
            self.queue_size > 0 and
            self.timeout > 0
        )

class CircuitBreakerException(Exception):
    """Circuit breaker is open"""
    pass

class RetryExhaustedException(Exception):
    """All retry attempts exhausted"""
    pass

class BulkheadException(Exception):
    """Bulkhead capacity exceeded"""
    pass

class TimeoutException(Exception):
    """Operation timed out"""
    pass

class CircuitBreakerMetrics:
    """Circuit breaker metrics collection"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.requests = deque(maxlen=window_size)
        self.lock = threading.Lock()
    
    def record_success(self) -> None:
        """Record successful request"""
        with self.lock:
            self.requests.append(True)
    
    def record_failure(self) -> None:
        """Record failed request"""
        with self.lock:
            self.requests.append(False)
    
    def get_failure_rate(self) -> float:
        """Get current failure rate"""
        with self.lock:
            if len(self.requests) == 0:
                return 0.0
            failures = sum(1 for result in self.requests if not result)
            return failures / len(self.requests)
    
    def get_request_count(self) -> int:
        """Get total request count in window"""
        with self.lock:
            return len(self.requests)
    
    def clear(self) -> None:
        """Clear metrics"""
        with self.lock:
            self.requests.clear()

class CircuitBreaker:
    """
    Circuit breaker pattern implementation
    
    Prevents cascading failures by stopping requests to failing services
    and allowing them time to recover.
    """
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        if not config.validate():
            raise ValueError("Invalid circuit breaker configuration")
        
        self.name = name
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.metrics = CircuitBreakerMetrics()
        self.last_failure_time = None
        self.half_open_successes = 0
        self.lock = threading.Lock()
        
        logger.info(f"Circuit breaker '{name}' initialized in CLOSED state")
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerException: When circuit is open
            Exception: Original function exceptions
        """
        with self.lock:
            self._check_state()
            
            if self.state == CircuitBreakerState.OPEN:
                raise CircuitBreakerException(f"Circuit breaker '{self.name}' is OPEN")
        
        try:
            # Execute with timeout
            result = self._execute_with_timeout(func, *args, **kwargs)
            self._record_success()
            return result
            
        except Exception as e:
            self._record_failure()
            raise
    
    def _execute_with_timeout(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with timeout"""
        if asyncio.iscoroutinefunction(func):
            # Async function
            return asyncio.wait_for(func(*args, **kwargs), timeout=self.config.timeout)
        else:
            # Sync function - use threading for timeout
            result = [None]
            exception = [None]
            
            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e
            
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout=self.config.timeout)
            
            if thread.is_alive():
                raise TimeoutException(f"Function call timed out after {self.config.timeout}s")
            
            if exception[0]:
                raise exception[0]
            
            return result[0]
    
    def _check_state(self) -> None:
        """Check and update circuit breaker state"""
        now = time.time()
        
        if self.state == CircuitBreakerState.OPEN:
            # Check if recovery timeout has passed
            if (self.last_failure_time and 
                now - self.last_failure_time >= self.config.recovery_timeout):
                self.state = CircuitBreakerState.HALF_OPEN
                self.half_open_successes = 0
                logger.info(f"Circuit breaker '{self.name}' moved to HALF_OPEN state")
        
        elif self.state == CircuitBreakerState.CLOSED:
            # Check if we should open due to failures
            request_count = self.metrics.get_request_count()
            failure_rate = self.metrics.get_failure_rate()
            
            if (request_count >= self.config.minimum_throughput and 
                failure_rate >= (self.config.failure_threshold / request_count)):
                self.state = CircuitBreakerState.OPEN
                self.last_failure_time = now
                logger.warning(f"Circuit breaker '{self.name}' opened due to failures (rate: {failure_rate:.2f})")
    
    def _record_success(self) -> None:
        """Record successful request"""
        with self.lock:
            self.metrics.record_success()
            
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.half_open_successes += 1
                if self.half_open_successes >= self.config.success_threshold:
                    self.state = CircuitBreakerState.CLOSED
                    self.metrics.clear()  # Fresh start
                    logger.info(f"Circuit breaker '{self.name}' closed after successful recovery")
    
    def _record_failure(self) -> None:
        """Record failed request"""
        with self.lock:
            self.metrics.record_failure()
            
            if self.state == CircuitBreakerState.HALF_OPEN:
                # Return to open state on any failure during half-open
                self.state = CircuitBreakerState.OPEN
                self.last_failure_time = time.time()
                logger.warning(f"Circuit breaker '{self.name}' reopened after half-open failure")
    
    def get_state(self) -> CircuitBreakerState:
        """Get current circuit breaker state"""
        with self.lock:
            return self.state
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get circuit breaker metrics"""
        with self.lock:
            return {
                'name': self.name,
                'state': self.state.value,
                'failure_rate': self.metrics.get_failure_rate(),
                'request_count': self.metrics.get_request_count(),
                'last_failure_time': self.last_failure_time,
                'config': {
                    'failure_threshold': self.config.failure_threshold,
                    'recovery_timeout': self.config.recovery_timeout,
                    'success_threshold': self.config.success_threshold
                }
            }
    
    def force_open(self) -> None:
        """Force circuit breaker to open state"""
        with self.lock:
            self.state = CircuitBreakerState.OPEN
            self.last_failure_time = time.time()
            logger.info(f"Circuit breaker '{self.name}' forced to OPEN state")
    
    def force_close(self) -> None:
        """Force circuit breaker to closed state"""
        with self.lock:
            self.state = CircuitBreakerState.CLOSED
            self.metrics.clear()
            logger.info(f"Circuit breaker '{self.name}' forced to CLOSED state")

class RetryHandler:
    """
    Retry logic implementation with multiple strategies
    
    Automatically retries failed operations with configurable backoff strategies.
    """
    
    def __init__(self, name: str, config: RetryConfig):
        if not config.validate():
            raise ValueError("Invalid retry configuration")
        
        self.name = name
        self.config = config
        self.attempt_count = 0
        
        logger.info(f"Retry handler '{name}' initialized with {config.strategy.value} strategy")
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with retry logic
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            RetryExhaustedException: When all retry attempts fail
        """
        last_exception = None
        
        for attempt in range(self.config.max_attempts):
            self.attempt_count = attempt + 1
            
            try:
                logger.debug(f"Retry handler '{self.name}' attempt {self.attempt_count}/{self.config.max_attempts}")
                result = func(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(f"Retry handler '{self.name}' succeeded on attempt {self.attempt_count}")
                
                return result
                
            except Exception as e:
                last_exception = e
                logger.warning(f"Retry handler '{self.name}' failed on attempt {self.attempt_count}: {e}")
                
                # Don't wait after the last attempt
                if attempt < self.config.max_attempts - 1:
                    delay = self._calculate_delay(attempt)
                    logger.debug(f"Retry handler '{self.name}' waiting {delay:.2f}s before next attempt")
                    time.sleep(delay)
        
        # All attempts failed
        logger.error(f"Retry handler '{self.name}' exhausted all {self.config.max_attempts} attempts")
        raise RetryExhaustedException(
            f"All {self.config.max_attempts} retry attempts failed. Last error: {last_exception}"
        )
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay before next retry attempt"""
        if self.config.strategy == RetryStrategy.FIXED_DELAY:
            delay = self.config.base_delay
            
        elif self.config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = self.config.base_delay * (self.config.backoff_multiplier ** attempt)
            
        elif self.config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = self.config.base_delay * (attempt + 1)
            
        elif self.config.strategy == RetryStrategy.RANDOM_JITTER:
            base_delay = self.config.base_delay * (self.config.backoff_multiplier ** attempt)
            jitter = base_delay * self.config.jitter_range * (random.random() - 0.5)
            delay = base_delay + jitter
            
        else:
            delay = self.config.base_delay
        
        # Respect maximum delay
        return min(delay, self.config.max_delay)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get retry handler metrics"""
        return {
            'name': self.name,
            'current_attempt': self.attempt_count,
            'max_attempts': self.config.max_attempts,
            'strategy': self.config.strategy.value,
            'config': {
                'base_delay': self.config.base_delay,
                'max_delay': self.config.max_delay,
                'backoff_multiplier': self.config.backoff_multiplier
            }
        }

class BulkheadIsolation:
    """
    Bulkhead isolation pattern implementation
    
    Isolates resources to prevent cascading failures by limiting
    concurrent access to shared resources.
    """
    
    def __init__(self, name: str, config: BulkheadConfig):
        if not config.validate():
            raise ValueError("Invalid bulkhead configuration")
        
        self.name = name
        self.config = config
        self.semaphore = threading.Semaphore(config.max_concurrent_calls)
        self.request_queue = queue.Queue(maxsize=config.queue_size)
        self.active_calls = 0
        self.total_calls = 0
        self.rejected_calls = 0
        self.lock = threading.Lock()
        
        logger.info(f"Bulkhead '{name}' initialized with {config.max_concurrent_calls} max concurrent calls")
    
    @contextmanager
    def isolate(self):
        """Context manager for bulkhead isolation"""
        acquired = False
        
        try:
            # Try to acquire semaphore with timeout
            acquired = self.semaphore.acquire(timeout=self.config.timeout)
            
            if not acquired:
                with self.lock:
                    self.rejected_calls += 1
                raise BulkheadException(f"Bulkhead '{self.name}' capacity exceeded")
            
            with self.lock:
                self.active_calls += 1
                self.total_calls += 1
            
            logger.debug(f"Bulkhead '{self.name}' acquired ({self.active_calls} active)")
            yield
            
        finally:
            if acquired:
                self.semaphore.release()
                with self.lock:
                    self.active_calls -= 1
                logger.debug(f"Bulkhead '{self.name}' released ({self.active_calls} active)")
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with bulkhead isolation
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            BulkheadException: When bulkhead capacity is exceeded
        """
        with self.isolate():
            return func(*args, **kwargs)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get bulkhead metrics"""
        with self.lock:
            return {
                'name': self.name,
                'active_calls': self.active_calls,
                'total_calls': self.total_calls,
                'rejected_calls': self.rejected_calls,
                'rejection_rate': (self.rejected_calls / max(self.total_calls, 1)) * 100,
                'config': {
                    'max_concurrent_calls': self.config.max_concurrent_calls,
                    'queue_size': self.config.queue_size,
                    'timeout': self.config.timeout
                }
            }
    
    def get_available_capacity(self) -> int:
        """Get available capacity"""
        with self.lock:
            return self.config.max_concurrent_calls - self.active_calls

class ResilienceManager:
    """
    Comprehensive resilience pattern manager
    
    Combines circuit breaker, retry, and bulkhead patterns for robust operation.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_handlers: Dict[str, RetryHandler] = {}
        self.bulkheads: Dict[str, BulkheadIsolation] = {}
        self.lock = threading.Lock()
        
        logger.info(f"Resilience manager '{name}' initialized")
    
    def add_circuit_breaker(self, name: str, config: CircuitBreakerConfig) -> None:
        """Add circuit breaker"""
        with self.lock:
            self.circuit_breakers[name] = CircuitBreaker(name, config)
    
    def add_retry_handler(self, name: str, config: RetryConfig) -> None:
        """Add retry handler"""
        with self.lock:
            self.retry_handlers[name] = RetryHandler(name, config)
    
    def add_bulkhead(self, name: str, config: BulkheadConfig) -> None:
        """Add bulkhead isolation"""
        with self.lock:
            self.bulkheads[name] = BulkheadIsolation(name, config)
    
    def execute_with_resilience(
        self, 
        func: Callable, 
        *args,
        circuit_breaker: str = None,
        retry_handler: str = None,
        bulkhead: str = None,
        **kwargs
    ) -> Any:
        """
        Execute function with specified resilience patterns
        
        Args:
            func: Function to execute
            *args: Function arguments
            circuit_breaker: Name of circuit breaker to use
            retry_handler: Name of retry handler to use
            bulkhead: Name of bulkhead to use
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
        """
        def execute_func():
            # Apply bulkhead if specified
            if bulkhead and bulkhead in self.bulkheads:
                return self.bulkheads[bulkhead].execute(func, *args, **kwargs)
            else:
                return func(*args, **kwargs)
        
        def execute_with_circuit_breaker():
            # Apply circuit breaker if specified
            if circuit_breaker and circuit_breaker in self.circuit_breakers:
                return self.circuit_breakers[circuit_breaker].call(execute_func)
            else:
                return execute_func()
        
        # Apply retry if specified
        if retry_handler and retry_handler in self.retry_handlers:
            return self.retry_handlers[retry_handler].execute(execute_with_circuit_breaker)
        else:
            return execute_with_circuit_breaker()
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get metrics from all resilience components"""
        with self.lock:
            return {
                'manager_name': self.name,
                'circuit_breakers': {
                    name: cb.get_metrics() 
                    for name, cb in self.circuit_breakers.items()
                },
                'retry_handlers': {
                    name: rh.get_metrics() 
                    for name, rh in self.retry_handlers.items()
                },
                'bulkheads': {
                    name: bh.get_metrics() 
                    for name, bh in self.bulkheads.items()
                }
            }
    
    def health_check(self) -> Dict[str, str]:
        """Get health status of all components"""
        health = {}
        
        with self.lock:
            # Circuit breaker health
            for name, cb in self.circuit_breakers.items():
                state = cb.get_state()
                health[f"circuit_breaker_{name}"] = state.value
            
            # Bulkhead health
            for name, bh in self.bulkheads.items():
                capacity = bh.get_available_capacity()
                if capacity > 0:
                    health[f"bulkhead_{name}"] = "healthy"
                else:
                    health[f"bulkhead_{name}"] = "at_capacity"
        
        return health

# Convenience decorators
def with_circuit_breaker(name: str, config: CircuitBreakerConfig = None):
    """Decorator to add circuit breaker protection to a function"""
    def decorator(func):
        if config is None:
            cb_config = CircuitBreakerConfig()
        else:
            cb_config = config
        
        circuit_breaker = CircuitBreaker(name, cb_config)
        
        def wrapper(*args, **kwargs):
            return circuit_breaker.call(func, *args, **kwargs)
        
        wrapper._circuit_breaker = circuit_breaker
        return wrapper
    return decorator

def with_retry(name: str, config: RetryConfig = None):
    """Decorator to add retry logic to a function"""
    def decorator(func):
        if config is None:
            retry_config = RetryConfig()
        else:
            retry_config = config
        
        retry_handler = RetryHandler(name, retry_config)
        
        def wrapper(*args, **kwargs):
            return retry_handler.execute(func, *args, **kwargs)
        
        wrapper._retry_handler = retry_handler
        return wrapper
    return decorator

def with_bulkhead(name: str, config: BulkheadConfig = None):
    """Decorator to add bulkhead isolation to a function"""
    def decorator(func):
        if config is None:
            bh_config = BulkheadConfig()
        else:
            bh_config = config
        
        bulkhead = BulkheadIsolation(name, bh_config)
        
        def wrapper(*args, **kwargs):
            return bulkhead.execute(func, *args, **kwargs)
        
        wrapper._bulkhead = bulkhead
        return wrapper
    return decorator

def resilient(
    circuit_breaker_config: CircuitBreakerConfig = None,
    retry_config: RetryConfig = None,
    bulkhead_config: BulkheadConfig = None
):
    """Decorator to add comprehensive resilience patterns to a function"""
    def decorator(func):
        components = {}
        
        if circuit_breaker_config:
            cb = CircuitBreaker(f"{func.__name__}_cb", circuit_breaker_config)
            components['circuit_breaker'] = cb
        
        if retry_config:
            rh = RetryHandler(f"{func.__name__}_retry", retry_config)
            components['retry_handler'] = rh
        
        if bulkhead_config:
            bh = BulkheadIsolation(f"{func.__name__}_bulkhead", bulkhead_config)
            components['bulkhead'] = bh
        
        def wrapper(*args, **kwargs):
            def execute():
                if 'bulkhead' in components:
                    return components['bulkhead'].execute(func, *args, **kwargs)
                else:
                    return func(*args, **kwargs)
            
            def execute_with_cb():
                if 'circuit_breaker' in components:
                    return components['circuit_breaker'].call(execute)
                else:
                    return execute()
            
            if 'retry_handler' in components:
                return components['retry_handler'].execute(execute_with_cb)
            else:
                return execute_with_cb()
        
        wrapper._resilience_components = components
        return wrapper
    return decorator

if __name__ == "__main__":
    # Example usage and testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Testing resilience patterns...")
    
    # Test Circuit Breaker
    print("\n1. Testing Circuit Breaker:")
    cb_config = CircuitBreakerConfig(failure_threshold=3, recovery_timeout=2.0)
    circuit_breaker = CircuitBreaker("test_cb", cb_config)
    
    def failing_function():
        raise Exception("Service unavailable")
    
    def working_function():
        return "Success!"
    
    # Trigger failures to open circuit breaker
    for i in range(5):
        try:
            circuit_breaker.call(failing_function)
        except:
            print(f"  Failure {i+1} recorded")
    
    print(f"  Circuit breaker state: {circuit_breaker.get_state().value}")
    
    # Test Retry Handler
    print("\n2. Testing Retry Handler:")
    retry_config = RetryConfig(max_attempts=3, strategy=RetryStrategy.EXPONENTIAL_BACKOFF)
    retry_handler = RetryHandler("test_retry", retry_config)
    
    attempt_count = 0
    def flaky_function():
        global attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise Exception(f"Attempt {attempt_count} failed")
        return f"Success on attempt {attempt_count}!"
    
    try:
        result = retry_handler.execute(flaky_function)
        print(f"  Result: {result}")
    except RetryExhaustedException as e:
        print(f"  Retry failed: {e}")
    
    # Test Bulkhead Isolation
    print("\n3. Testing Bulkhead Isolation:")
    bulkhead_config = BulkheadConfig(max_concurrent_calls=2, timeout=1.0)
    bulkhead = BulkheadIsolation("test_bulkhead", bulkhead_config)
    
    def slow_function():
        time.sleep(0.5)
        return "Completed"
    
    # Test concurrent execution
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(bulkhead.execute, slow_function) for _ in range(5)]
        
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            try:
                result = future.result()
                print(f"  Task {i+1}: {result}")
            except BulkheadException as e:
                print(f"  Task {i+1}: {e}")
    
    # Test comprehensive resilience with decorators
    print("\n4. Testing Resilient Decorator:")
    
    @resilient(
        circuit_breaker_config=CircuitBreakerConfig(failure_threshold=2),
        retry_config=RetryConfig(max_attempts=3),
        bulkhead_config=BulkheadConfig(max_concurrent_calls=1)
    )
    def resilient_function():
        return "Resilient success!"
    
    try:
        result = resilient_function()
        print(f"  Result: {result}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test Resilience Manager
    print("\n5. Testing Resilience Manager:")
    manager = ResilienceManager("test_manager")
    manager.add_circuit_breaker("api_cb", CircuitBreakerConfig())
    manager.add_retry_handler("api_retry", RetryConfig())
    manager.add_bulkhead("api_bulkhead", BulkheadConfig())
    
    def api_call():
        return "API response"
    
    result = manager.execute_with_resilience(
        api_call,
        circuit_breaker="api_cb",
        retry_handler="api_retry",
        bulkhead="api_bulkhead"
    )
    print(f"  API call result: {result}")
    
    # Display metrics
    print("\n6. Resilience Metrics:")
    metrics = manager.get_all_metrics()
    print(f"  Manager: {metrics['manager_name']}")
    print(f"  Circuit Breakers: {len(metrics['circuit_breakers'])}")
    print(f"  Retry Handlers: {len(metrics['retry_handlers'])}")
    print(f"  Bulkheads: {len(metrics['bulkheads'])}")
    
    print("\nResilience patterns testing completed!")