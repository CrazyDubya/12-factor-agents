#!/usr/bin/env python3
"""
Performance Optimizations Module
Advanced performance optimizations for GPT-OSS interfaces including connection
pooling, memory management, caching, and resource monitoring.
"""

import threading
import time
import queue
import weakref
import gc
import psutil
from typing import Dict, List, Optional, Any, Callable, Tuple, Union
from dataclasses import dataclass, field
from collections import deque, OrderedDict
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import logging
import json
import hashlib
import tkinter as tk
from tkinter import scrolledtext

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics data class"""
    response_times: List[float] = field(default_factory=list)
    memory_usage: List[float] = field(default_factory=list)
    cpu_usage: List[float] = field(default_factory=list)
    cache_hits: int = 0
    cache_misses: int = 0
    active_connections: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    
    def add_response_time(self, duration: float) -> None:
        """Add response time measurement"""
        self.response_times.append(duration)
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-500:]
    
    def get_avg_response_time(self) -> float:
        """Get average response time"""
        return sum(self.response_times) / len(self.response_times) if self.response_times else 0.0
    
    def get_cache_hit_rate(self) -> float:
        """Get cache hit rate percentage"""
        total = self.cache_hits + self.cache_misses
        return (self.cache_hits / total * 100) if total > 0 else 0.0

class ConnectionPool:
    """
    Advanced HTTP connection pool with retry logic and health monitoring
    """
    
    def __init__(
        self,
        pool_connections: int = 10,
        pool_maxsize: int = 20,
        max_retries: int = 3,
        backoff_factor: float = 0.3,
        status_forcelist: List[int] = None
    ):
        """
        Initialize connection pool
        
        Args:
            pool_connections: Number of connection pools to cache
            pool_maxsize: Maximum number of connections in each pool
            max_retries: Maximum number of retry attempts
            backoff_factor: Backoff factor for retries
            status_forcelist: HTTP status codes to retry on
        """
        self.pool_connections = pool_connections
        self.pool_maxsize = pool_maxsize
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.status_forcelist = status_forcelist or [500, 502, 503, 504]
        
        # Create session with optimized settings
        self.session = requests.Session()
        self._setup_retries()
        self._setup_adapters()
        
        # Monitoring
        self.metrics = PerformanceMetrics()
        self.connection_stats = {}
        self.lock = threading.Lock()
        
        logger.info(f"Connection pool initialized: {pool_connections} pools, {pool_maxsize} max size")
    
    def _setup_retries(self) -> None:
        """Setup retry strategy"""
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=self.status_forcelist,
            method_whitelist=["HEAD", "GET", "POST"]
        )
        
        adapter = HTTPAdapter(
            pool_connections=self.pool_connections,
            pool_maxsize=self.pool_maxsize,
            max_retries=retry_strategy
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _setup_adapters(self) -> None:
        """Setup HTTP adapters with custom configurations"""
        # Configure connection pooling
        self.session.headers.update({
            'Connection': 'keep-alive',
            'User-Agent': 'GPT-OSS-Interface/1.0'
        })
    
    def request(
        self,
        method: str,
        url: str,
        timeout: float = 30.0,
        **kwargs
    ) -> requests.Response:
        """
        Make HTTP request with monitoring
        
        Args:
            method: HTTP method
            url: Request URL
            timeout: Request timeout
            **kwargs: Additional request arguments
            
        Returns:
            Response object
        """
        start_time = time.time()
        
        try:
            with self.lock:
                self.metrics.total_requests += 1
                self.metrics.active_connections += 1
            
            response = self.session.request(
                method=method,
                url=url,
                timeout=timeout,
                **kwargs
            )
            
            # Record successful request
            duration = time.time() - start_time
            with self.lock:
                self.metrics.add_response_time(duration)
            
            logger.debug(f"Request {method} {url} completed in {duration:.3f}s")
            return response
            
        except Exception as e:
            # Record failed request
            with self.lock:
                self.metrics.failed_requests += 1
            
            logger.error(f"Request {method} {url} failed: {e}")
            raise
        finally:
            with self.lock:
                self.metrics.active_connections -= 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        with self.lock:
            return {
                'total_requests': self.metrics.total_requests,
                'failed_requests': self.metrics.failed_requests,
                'active_connections': self.metrics.active_connections,
                'avg_response_time': self.metrics.get_avg_response_time(),
                'success_rate': (
                    (self.metrics.total_requests - self.metrics.failed_requests) /
                    self.metrics.total_requests * 100
                ) if self.metrics.total_requests > 0 else 0.0
            }
    
    def close(self) -> None:
        """Close connection pool"""
        self.session.close()
        logger.info("Connection pool closed")

class LRUCache:
    """
    Least Recently Used cache with TTL support and memory management
    """
    
    def __init__(self, maxsize: int = 1000, ttl_seconds: int = 300):
        """
        Initialize LRU cache
        
        Args:
            maxsize: Maximum number of items to cache
            ttl_seconds: Time to live for cached items
        """
        self.maxsize = maxsize
        self.ttl_seconds = ttl_seconds
        self.cache: OrderedDict = OrderedDict()
        self.timestamps: Dict[str, datetime] = {}
        self.lock = threading.RLock()
        self.hits = 0
        self.misses = 0
        
        logger.info(f"LRU Cache initialized: maxsize={maxsize}, ttl={ttl_seconds}s")
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired"""
        if key not in self.timestamps:
            return True
        
        age = datetime.now() - self.timestamps[key]
        return age.total_seconds() > self.ttl_seconds
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries"""
        now = datetime.now()
        expired_keys = [
            key for key, timestamp in self.timestamps.items()
            if (now - timestamp).total_seconds() > self.ttl_seconds
        ]
        
        for key in expired_keys:
            if key in self.cache:
                del self.cache[key]
            del self.timestamps[key]
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get item from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self.lock:
            if key in self.cache and not self._is_expired(key):
                # Move to end (most recently used)
                value = self.cache[key]
                del self.cache[key]
                self.cache[key] = value
                self.hits += 1
                return value
            else:
                # Remove expired entry
                if key in self.cache:
                    del self.cache[key]
                if key in self.timestamps:
                    del self.timestamps[key]
                
                self.misses += 1
                return None
    
    def put(self, key: str, value: Any) -> None:
        """
        Put item in cache
        
        Args:
            key: Cache key
            value: Value to cache
        """
        with self.lock:
            # Remove if already exists
            if key in self.cache:
                del self.cache[key]
            
            # Add new entry
            self.cache[key] = value
            self.timestamps[key] = datetime.now()
            
            # Enforce size limit
            while len(self.cache) > self.maxsize:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                if oldest_key in self.timestamps:
                    del self.timestamps[oldest_key]
            
            # Cleanup expired entries periodically
            if len(self.cache) % 100 == 0:
                self._cleanup_expired()
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0.0
            
            return {
                'size': len(self.cache),
                'maxsize': self.maxsize,
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': hit_rate,
                'utilization': len(self.cache) / self.maxsize * 100
            }

class MemoryManager:
    """
    Memory management and monitoring for GUI applications
    """
    
    def __init__(self, memory_limit_mb: int = 512):
        """
        Initialize memory manager
        
        Args:
            memory_limit_mb: Memory limit in megabytes
        """
        self.memory_limit_bytes = memory_limit_mb * 1024 * 1024
        self.process = psutil.Process()
        self.widget_registry: weakref.WeakSet = weakref.WeakSet()
        self.text_widgets: List[weakref.ref] = []
        self.monitoring_active = True
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_memory, daemon=True)
        self.monitor_thread.start()
        
        logger.info(f"Memory manager initialized: limit={memory_limit_mb}MB")
    
    def register_text_widget(self, widget: tk.Text) -> None:
        """
        Register text widget for memory management
        
        Args:
            widget: Text widget to manage
        """
        self.widget_registry.add(widget)
        self.text_widgets.append(weakref.ref(widget))
        
        # Set up automatic cleanup
        self._setup_widget_limits(widget)
    
    def _setup_widget_limits(self, widget: tk.Text) -> None:
        """Setup memory limits for text widget"""
        original_insert = widget.insert
        
        def limited_insert(index, chars, *args):
            # Check line count
            current_lines = int(widget.index('end-1c').split('.')[0])
            if current_lines > 10000:  # Limit to 10k lines
                # Remove old lines
                widget.delete('1.0', '5000.0')
            
            return original_insert(index, chars, *args)
        
        widget.insert = limited_insert
    
    def _monitor_memory(self) -> None:
        """Background memory monitoring"""
        while self.monitoring_active:
            try:
                memory_info = self.process.memory_info()
                memory_usage = memory_info.rss
                
                if memory_usage > self.memory_limit_bytes:
                    logger.warning(f"Memory usage high: {memory_usage / 1024 / 1024:.1f}MB")
                    self._cleanup_memory()
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Memory monitoring error: {e}")
                time.sleep(10)
    
    def _cleanup_memory(self) -> None:
        """Perform memory cleanup"""
        # Clean up text widgets
        for widget_ref in self.text_widgets[:]:
            widget = widget_ref()
            if widget is None:
                self.text_widgets.remove(widget_ref)
            else:
                try:
                    # Truncate large text widgets
                    content = widget.get('1.0', 'end')
                    if len(content) > 100000:  # 100KB limit
                        widget.delete('1.0', 'end')
                        widget.insert('1.0', content[-50000:])  # Keep last 50KB
                        logger.info(f"Truncated text widget content")
                except:
                    pass
        
        # Force garbage collection
        gc.collect()
        
        # Log memory usage after cleanup
        memory_info = self.process.memory_info()
        logger.info(f"Memory after cleanup: {memory_info.rss / 1024 / 1024:.1f}MB")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get current memory statistics"""
        try:
            memory_info = self.process.memory_info()
            cpu_percent = self.process.cpu_percent()
            
            return {
                'rss_mb': memory_info.rss / 1024 / 1024,
                'vms_mb': memory_info.vms / 1024 / 1024,
                'cpu_percent': cpu_percent,
                'memory_limit_mb': self.memory_limit_bytes / 1024 / 1024,
                'registered_widgets': len(self.widget_registry),
                'text_widgets': len([ref for ref in self.text_widgets if ref() is not None])
            }
        except:
            return {'error': 'Unable to get memory stats'}
    
    def stop_monitoring(self) -> None:
        """Stop memory monitoring"""
        self.monitoring_active = False

class ResponseCache:
    """
    Intelligent response caching with content-based hashing
    """
    
    def __init__(self, cache_size: int = 500, ttl_seconds: int = 1800):
        """
        Initialize response cache
        
        Args:
            cache_size: Maximum number of responses to cache
            ttl_seconds: Time to live for cached responses (30 minutes default)
        """
        self.cache = LRUCache(maxsize=cache_size, ttl_seconds=ttl_seconds)
        self.content_hashes: Dict[str, str] = {}
        
    def _hash_content(self, content: str) -> str:
        """Create hash of content for cache key"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_cached_response(self, prompt: str, model_config: Dict[str, Any]) -> Optional[str]:
        """
        Get cached response if available
        
        Args:
            prompt: User prompt
            model_config: Model configuration
            
        Returns:
            Cached response or None
        """
        # Create cache key from prompt and model config
        config_str = json.dumps(model_config, sort_keys=True)
        cache_key = self._hash_content(prompt + config_str)
        
        return self.cache.get(cache_key)
    
    def cache_response(
        self, 
        prompt: str, 
        response: str, 
        model_config: Dict[str, Any]
    ) -> None:
        """
        Cache response
        
        Args:
            prompt: User prompt
            response: Model response
            model_config: Model configuration
        """
        config_str = json.dumps(model_config, sort_keys=True)
        cache_key = self._hash_content(prompt + config_str)
        
        self.cache.put(cache_key, response)
        logger.debug(f"Cached response for prompt: {prompt[:50]}...")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.cache.get_stats()
    
    def clear(self) -> None:
        """Clear cache"""
        self.cache.clear()

class BackgroundTaskManager:
    """
    Background task manager for non-blocking operations
    """
    
    def __init__(self, max_workers: int = 3):
        """
        Initialize task manager
        
        Args:
            max_workers: Maximum number of worker threads
        """
        self.max_workers = max_workers
        self.task_queue: queue.Queue = queue.Queue()
        self.workers: List[threading.Thread] = []
        self.shutdown_event = threading.Event()
        self.active_tasks = 0
        self.completed_tasks = 0
        self.failed_tasks = 0
        self.lock = threading.Lock()
        
        # Start worker threads
        for i in range(max_workers):
            worker = threading.Thread(target=self._worker, daemon=True)
            worker.start()
            self.workers.append(worker)
        
        logger.info(f"Background task manager started with {max_workers} workers")
    
    def _worker(self) -> None:
        """Worker thread function"""
        while not self.shutdown_event.is_set():
            try:
                # Get task with timeout
                task = self.task_queue.get(timeout=1.0)
                
                if task is None:  # Shutdown signal
                    break
                
                with self.lock:
                    self.active_tasks += 1
                
                try:
                    # Execute task
                    func, args, kwargs, callback = task
                    result = func(*args, **kwargs)
                    
                    # Call completion callback if provided
                    if callback:
                        callback(result, None)
                    
                    with self.lock:
                        self.completed_tasks += 1
                        
                except Exception as e:
                    logger.error(f"Background task failed: {e}")
                    
                    # Call error callback if provided
                    if callback:
                        try:
                            callback(None, e)
                        except:
                            pass
                    
                    with self.lock:
                        self.failed_tasks += 1
                
                finally:
                    with self.lock:
                        self.active_tasks -= 1
                    self.task_queue.task_done()
                    
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Worker thread error: {e}")
    
    def submit_task(
        self,
        func: Callable,
        *args,
        callback: Optional[Callable] = None,
        **kwargs
    ) -> None:
        """
        Submit task for background execution
        
        Args:
            func: Function to execute
            *args: Function arguments
            callback: Optional completion callback
            **kwargs: Function keyword arguments
        """
        task = (func, args, kwargs, callback)
        self.task_queue.put(task)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get task manager statistics"""
        with self.lock:
            return {
                'active_tasks': self.active_tasks,
                'completed_tasks': self.completed_tasks,
                'failed_tasks': self.failed_tasks,
                'queue_size': self.task_queue.qsize(),
                'success_rate': (
                    self.completed_tasks / 
                    (self.completed_tasks + self.failed_tasks) * 100
                ) if (self.completed_tasks + self.failed_tasks) > 0 else 0.0
            }
    
    def shutdown(self) -> None:
        """Shutdown task manager"""
        self.shutdown_event.set()
        
        # Send shutdown signal to all workers
        for _ in range(len(self.workers)):
            self.task_queue.put(None)
        
        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=5)
        
        logger.info("Background task manager shutdown complete")

class PerformanceOptimizer:
    """
    Comprehensive performance optimization manager
    """
    
    def __init__(
        self,
        connection_pool_size: int = 10,
        cache_size: int = 500,
        memory_limit_mb: int = 512,
        background_workers: int = 3
    ):
        """
        Initialize performance optimizer
        
        Args:
            connection_pool_size: Size of HTTP connection pool
            cache_size: Size of response cache
            memory_limit_mb: Memory limit in MB
            background_workers: Number of background worker threads
        """
        self.connection_pool = ConnectionPool(
            pool_connections=connection_pool_size,
            pool_maxsize=connection_pool_size * 2
        )
        
        self.response_cache = ResponseCache(cache_size=cache_size)
        self.memory_manager = MemoryManager(memory_limit_mb=memory_limit_mb)
        self.task_manager = BackgroundTaskManager(max_workers=background_workers)
        
        # Performance monitoring
        self.start_time = time.time()
        self.optimization_active = True
        
        logger.info("Performance optimizer initialized")
    
    def optimized_request(
        self,
        method: str,
        url: str,
        use_cache: bool = True,
        cache_ttl: int = 1800,
        **kwargs
    ) -> requests.Response:
        """
        Make optimized HTTP request with caching and pooling
        
        Args:
            method: HTTP method
            url: Request URL
            use_cache: Whether to use response caching
            cache_ttl: Cache time to live in seconds
            **kwargs: Additional request arguments
            
        Returns:
            Response object
        """
        # For GET requests, check cache first
        if method.upper() == 'GET' and use_cache:
            cache_key = f"{method}:{url}:{str(sorted(kwargs.items()))}"
            cached_response = self.response_cache.cache.get(cache_key)
            if cached_response:
                logger.debug(f"Cache hit for {method} {url}")
                return cached_response
        
        # Make request through connection pool
        response = self.connection_pool.request(method, url, **kwargs)
        
        # Cache successful GET responses
        if method.upper() == 'GET' and use_cache and response.status_code == 200:
            cache_key = f"{method}:{url}:{str(sorted(kwargs.items()))}"
            self.response_cache.cache.put(cache_key, response)
            logger.debug(f"Cached response for {method} {url}")
        
        return response
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        uptime = time.time() - self.start_time
        
        return {
            'uptime_seconds': uptime,
            'connection_pool': self.connection_pool.get_stats(),
            'response_cache': self.response_cache.get_stats(),
            'memory': self.memory_manager.get_memory_stats(),
            'background_tasks': self.task_manager.get_stats(),
            'optimization_active': self.optimization_active
        }
    
    def register_text_widget(self, widget: tk.Text) -> None:
        """Register text widget for memory management"""
        self.memory_manager.register_text_widget(widget)
    
    def submit_background_task(
        self,
        func: Callable,
        *args,
        callback: Optional[Callable] = None,
        **kwargs
    ) -> None:
        """Submit task for background execution"""
        self.task_manager.submit_task(func, *args, callback=callback, **kwargs)
    
    def cleanup_caches(self) -> None:
        """Manual cache cleanup"""
        self.response_cache.clear()
        logger.info("Caches cleared manually")
    
    def shutdown(self) -> None:
        """Shutdown performance optimizer"""
        self.optimization_active = False
        self.task_manager.shutdown()
        self.memory_manager.stop_monitoring()
        self.connection_pool.close()
        logger.info("Performance optimizer shutdown complete")

def create_optimized_text_widget(
    parent,
    optimizer: PerformanceOptimizer,
    max_lines: int = 5000,
    **kwargs
) -> scrolledtext.ScrolledText:
    """
    Create memory-optimized text widget
    
    Args:
        parent: Parent widget
        optimizer: Performance optimizer instance
        max_lines: Maximum number of lines to keep
        **kwargs: Additional widget arguments
        
    Returns:
        Optimized scrolled text widget
    """
    widget = scrolledtext.ScrolledText(parent, **kwargs)
    
    # Register for memory management
    optimizer.register_text_widget(widget)
    
    # Add automatic line limiting
    original_insert = widget.insert
    
    def limited_insert(index, chars, *args):
        result = original_insert(index, chars, *args)
        
        # Check and limit lines
        current_lines = int(widget.index('end-1c').split('.')[0])
        if current_lines > max_lines:
            # Remove excess lines from beginning
            excess = current_lines - max_lines + 100  # Remove extra buffer
            widget.delete('1.0', f'{excess}.0')
        
        return result
    
    widget.insert = limited_insert
    
    return widget

if __name__ == "__main__":
    # Performance optimization testing
    logging.basicConfig(level=logging.INFO)
    
    # Test connection pool
    print("Testing connection pool...")
    pool = ConnectionPool(pool_connections=2, pool_maxsize=4)
    
    try:
        response = pool.request('GET', 'http://httpbin.org/get')
        print(f"Response status: {response.status_code}")
    except:
        print("Connection test failed (expected if no internet)")
    
    stats = pool.get_stats()
    print(f"Connection pool stats: {stats}")
    
    # Test cache
    print("\nTesting LRU cache...")
    cache = LRUCache(maxsize=3, ttl_seconds=2)
    
    cache.put("key1", "value1")
    cache.put("key2", "value2")
    print(f"Cache get key1: {cache.get('key1')}")
    print(f"Cache stats: {cache.get_stats()}")
    
    # Test memory manager
    print("\nTesting memory manager...")
    memory_mgr = MemoryManager(memory_limit_mb=100)
    time.sleep(1)  # Let monitoring start
    stats = memory_mgr.get_memory_stats()
    print(f"Memory stats: {stats}")
    
    # Test performance optimizer
    print("\nTesting performance optimizer...")
    optimizer = PerformanceOptimizer()
    comprehensive_stats = optimizer.get_comprehensive_stats()
    print(f"Comprehensive stats: {comprehensive_stats}")
    
    # Cleanup
    pool.close()
    memory_mgr.stop_monitoring()
    optimizer.shutdown()
    
    print("Performance optimization tests completed!")