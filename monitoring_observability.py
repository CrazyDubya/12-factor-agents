#!/usr/bin/env python3
"""
Monitoring & Observability Framework
Comprehensive monitoring, metrics collection, and observability for GPT-OSS interfaces
"""

import time
import logging
import threading
import json
import sqlite3
import queue
import psutil
import socket
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from collections import deque, defaultdict
from enum import Enum
import weakref
from contextlib import contextmanager
import traceback
import os

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics that can be collected"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class MetricData:
    """Data structure for individual metrics"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'name': self.name,
            'value': self.value,
            'type': self.metric_type.value,
            'timestamp': self.timestamp.isoformat(),
            'tags': self.tags
        }

@dataclass
class AlertRule:
    """Configuration for monitoring alerts"""
    name: str
    metric_name: str
    threshold: float
    operator: str  # "gt", "lt", "eq", "gte", "lte"
    severity: AlertSeverity
    window_minutes: int = 5
    min_occurrences: int = 1
    enabled: bool = True
    
    def evaluate(self, values: List[float]) -> bool:
        """Evaluate if alert should trigger"""
        if not self.enabled or len(values) < self.min_occurrences:
            return False
        
        # Check against threshold
        if self.operator == "gt":
            return all(v > self.threshold for v in values[-self.min_occurrences:])
        elif self.operator == "gte":
            return all(v >= self.threshold for v in values[-self.min_occurrences:])
        elif self.operator == "lt":
            return all(v < self.threshold for v in values[-self.min_occurrences:])
        elif self.operator == "lte":
            return all(v <= self.threshold for v in values[-self.min_occurrences:])
        elif self.operator == "eq":
            return all(v == self.threshold for v in values[-self.min_occurrences:])
        
        return False

@dataclass
class Alert:
    """Active alert instance"""
    rule_name: str
    metric_name: str
    current_value: float
    threshold: float
    severity: AlertSeverity
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolved_at: Optional[datetime] = None

class MetricsStore:
    """Thread-safe metrics storage with retention policies"""
    
    def __init__(self, retention_hours: int = 24, max_metrics_per_name: int = 10000):
        self.retention_hours = retention_hours
        self.max_metrics_per_name = max_metrics_per_name
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_metrics_per_name))
        self.lock = threading.RLock()
        self.cleanup_interval = 3600  # 1 hour
        self.last_cleanup = time.time()
        
    def add_metric(self, metric: MetricData) -> None:
        """Add metric to store"""
        with self.lock:
            self.metrics[metric.name].append(metric)
            
            # Periodic cleanup
            if time.time() - self.last_cleanup > self.cleanup_interval:
                self._cleanup_old_metrics()
                self.last_cleanup = time.time()
    
    def get_metrics(
        self, 
        name: str, 
        since: Optional[datetime] = None, 
        limit: Optional[int] = None
    ) -> List[MetricData]:
        """Get metrics by name with optional filtering"""
        with self.lock:
            metrics = list(self.metrics[name])
            
            # Filter by time
            if since:
                metrics = [m for m in metrics if m.timestamp >= since]
            
            # Apply limit
            if limit:
                metrics = metrics[-limit:]
            
            return metrics
    
    def get_latest_value(self, name: str) -> Optional[float]:
        """Get latest value for a metric"""
        with self.lock:
            if name in self.metrics and self.metrics[name]:
                return self.metrics[name][-1].value
            return None
    
    def get_metric_names(self) -> List[str]:
        """Get all metric names"""
        with self.lock:
            return list(self.metrics.keys())
    
    def _cleanup_old_metrics(self) -> None:
        """Remove old metrics beyond retention period"""
        cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
        
        for name in self.metrics:
            # Remove old metrics
            while (self.metrics[name] and 
                   self.metrics[name][0].timestamp < cutoff_time):
                self.metrics[name].popleft()

class SystemMetricsCollector:
    """Collects system-level metrics"""
    
    def __init__(self, collection_interval: int = 10):
        self.collection_interval = collection_interval
        self.process = psutil.Process()
        self.collecting = False
        self.collector_thread = None
        
    def start_collection(self, metrics_store: MetricsStore) -> None:
        """Start collecting system metrics"""
        self.collecting = True
        self.collector_thread = threading.Thread(
            target=self._collect_loop, 
            args=(metrics_store,),
            daemon=True
        )
        self.collector_thread.start()
        logger.info("System metrics collection started")
    
    def stop_collection(self) -> None:
        """Stop collecting system metrics"""
        self.collecting = False
        if self.collector_thread:
            self.collector_thread.join(timeout=5)
        logger.info("System metrics collection stopped")
    
    def _collect_loop(self, metrics_store: MetricsStore) -> None:
        """Main collection loop"""
        while self.collecting:
            try:
                # CPU metrics
                cpu_percent = self.process.cpu_percent(interval=1)
                metrics_store.add_metric(MetricData(
                    "system.cpu.percent", cpu_percent, MetricType.GAUGE
                ))
                
                # Memory metrics
                memory_info = self.process.memory_info()
                metrics_store.add_metric(MetricData(
                    "system.memory.rss_mb", memory_info.rss / 1024 / 1024, MetricType.GAUGE
                ))
                metrics_store.add_metric(MetricData(
                    "system.memory.vms_mb", memory_info.vms / 1024 / 1024, MetricType.GAUGE
                ))
                
                # System-wide metrics
                system_cpu = psutil.cpu_percent(interval=1)
                system_memory = psutil.virtual_memory()
                
                metrics_store.add_metric(MetricData(
                    "system.cpu.system_percent", system_cpu, MetricType.GAUGE
                ))
                metrics_store.add_metric(MetricData(
                    "system.memory.system_percent", system_memory.percent, MetricType.GAUGE
                ))
                
                # Thread count
                try:
                    thread_count = threading.active_count()
                    metrics_store.add_metric(MetricData(
                        "system.threads.count", thread_count, MetricType.GAUGE
                    ))
                except:
                    pass
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
                time.sleep(self.collection_interval)

class ApplicationMetricsCollector:
    """Collects application-specific metrics"""
    
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.response_times = deque(maxlen=1000)
        self.lock = threading.Lock()
        
    def record_request(self, duration: float, success: bool = True) -> None:
        """Record a request with duration and success status"""
        with self.lock:
            self.request_count += 1
            self.response_times.append(duration)
            if not success:
                self.error_count += 1
    
    def get_metrics(self) -> Dict[str, MetricData]:
        """Get current application metrics"""
        with self.lock:
            metrics = {}
            
            # Request count
            metrics['app.requests.total'] = MetricData(
                "app.requests.total", self.request_count, MetricType.COUNTER
            )
            
            # Error count and rate
            metrics['app.errors.total'] = MetricData(
                "app.errors.total", self.error_count, MetricType.COUNTER
            )
            
            error_rate = (self.error_count / self.request_count * 100) if self.request_count > 0 else 0
            metrics['app.errors.rate'] = MetricData(
                "app.errors.rate", error_rate, MetricType.GAUGE
            )
            
            # Response time statistics
            if self.response_times:
                response_times = list(self.response_times)
                avg_response_time = sum(response_times) / len(response_times)
                max_response_time = max(response_times)
                min_response_time = min(response_times)
                
                metrics['app.response_time.avg'] = MetricData(
                    "app.response_time.avg", avg_response_time, MetricType.GAUGE
                )
                metrics['app.response_time.max'] = MetricData(
                    "app.response_time.max", max_response_time, MetricType.GAUGE
                )
                metrics['app.response_time.min'] = MetricData(
                    "app.response_time.min", min_response_time, MetricType.GAUGE
                )
            
            return metrics

class AlertManager:
    """Manages monitoring alerts and notifications"""
    
    def __init__(self, metrics_store: MetricsStore):
        self.metrics_store = metrics_store
        self.alert_rules: List[AlertRule] = []
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.lock = threading.Lock()
        self.checking = False
        self.check_thread = None
        
        # Default alert rules
        self._setup_default_rules()
        
    def _setup_default_rules(self) -> None:
        """Setup default monitoring rules"""
        default_rules = [
            AlertRule(
                "high_cpu", "system.cpu.percent", 80.0, "gt", 
                AlertSeverity.WARNING, window_minutes=2, min_occurrences=3
            ),
            AlertRule(
                "high_memory", "system.memory.rss_mb", 512.0, "gt",
                AlertSeverity.WARNING, window_minutes=1, min_occurrences=2
            ),
            AlertRule(
                "high_error_rate", "app.errors.rate", 5.0, "gt",
                AlertSeverity.ERROR, window_minutes=5, min_occurrences=2
            ),
            AlertRule(
                "slow_response", "app.response_time.avg", 5.0, "gt",
                AlertSeverity.WARNING, window_minutes=3, min_occurrences=3
            ),
        ]
        
        self.alert_rules.extend(default_rules)
    
    def add_rule(self, rule: AlertRule) -> None:
        """Add new alert rule"""
        with self.lock:
            self.alert_rules.append(rule)
    
    def remove_rule(self, rule_name: str) -> bool:
        """Remove alert rule by name"""
        with self.lock:
            for i, rule in enumerate(self.alert_rules):
                if rule.name == rule_name:
                    del self.alert_rules[i]
                    return True
            return False
    
    def start_monitoring(self, check_interval: int = 30) -> None:
        """Start alert monitoring"""
        self.checking = True
        self.check_thread = threading.Thread(
            target=self._monitoring_loop, 
            args=(check_interval,),
            daemon=True
        )
        self.check_thread.start()
        logger.info("Alert monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop alert monitoring"""
        self.checking = False
        if self.check_thread:
            self.check_thread.join(timeout=5)
        logger.info("Alert monitoring stopped")
    
    def _monitoring_loop(self, check_interval: int) -> None:
        """Main alert checking loop"""
        while self.checking:
            try:
                self._check_all_rules()
                time.sleep(check_interval)
            except Exception as e:
                logger.error(f"Error in alert monitoring: {e}")
                time.sleep(check_interval)
    
    def _check_all_rules(self) -> None:
        """Check all alert rules"""
        with self.lock:
            for rule in self.alert_rules:
                if not rule.enabled:
                    continue
                
                # Get recent metrics for this rule
                since = datetime.now() - timedelta(minutes=rule.window_minutes)
                metrics = self.metrics_store.get_metrics(rule.metric_name, since=since)
                
                if not metrics:
                    continue
                
                values = [m.value for m in metrics]
                
                if rule.evaluate(values):
                    self._trigger_alert(rule, values[-1])
                else:
                    self._resolve_alert(rule.name)
    
    def _trigger_alert(self, rule: AlertRule, current_value: float) -> None:
        """Trigger an alert"""
        alert_key = rule.name
        
        # Check if alert already active
        if alert_key in self.active_alerts:
            return
        
        alert = Alert(
            rule_name=rule.name,
            metric_name=rule.metric_name,
            current_value=current_value,
            threshold=rule.threshold,
            severity=rule.severity,
            message=f"{rule.metric_name} {rule.operator} {rule.threshold} (current: {current_value})"
        )
        
        self.active_alerts[alert_key] = alert
        self.alert_history.append(alert)
        
        logger.warning(f"ALERT TRIGGERED: {alert.message}")
        
        # Limit alert history
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-500:]
    
    def _resolve_alert(self, rule_name: str) -> None:
        """Resolve an active alert"""
        if rule_name in self.active_alerts:
            alert = self.active_alerts[rule_name]
            alert.resolved = True
            alert.resolved_at = datetime.now()
            
            del self.active_alerts[rule_name]
            logger.info(f"ALERT RESOLVED: {alert.message}")
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        with self.lock:
            return list(self.active_alerts.values())
    
    def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """Get alert history"""
        with self.lock:
            return self.alert_history[-limit:]

class StructuredLogger:
    """Structured logging with context and correlation"""
    
    def __init__(self, name: str = "gpt_oss"):
        self.logger = logging.getLogger(name)
        self.context_stack: List[Dict[str, Any]] = []
        self.correlation_id = None
        
    def set_correlation_id(self, correlation_id: str) -> None:
        """Set correlation ID for request tracing"""
        self.correlation_id = correlation_id
    
    @contextmanager
    def context(self, **kwargs):
        """Add context to all log messages within block"""
        self.context_stack.append(kwargs)
        try:
            yield
        finally:
            self.context_stack.pop()
    
    def _enrich_message(self, message: str, **kwargs) -> str:
        """Enrich log message with context"""
        context = {}
        
        # Add correlation ID
        if self.correlation_id:
            context['correlation_id'] = self.correlation_id
        
        # Add stacked context
        for ctx in self.context_stack:
            context.update(ctx)
        
        # Add provided context
        context.update(kwargs)
        
        if context:
            context_str = json.dumps(context, default=str)
            return f"{message} | {context_str}"
        
        return message
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message with context"""
        self.logger.info(self._enrich_message(message, **kwargs))
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with context"""
        self.logger.warning(self._enrich_message(message, **kwargs))
    
    def error(self, message: str, exception: Exception = None, **kwargs) -> None:
        """Log error message with context"""
        if exception:
            kwargs['exception_type'] = type(exception).__name__
            kwargs['exception_message'] = str(exception)
            kwargs['traceback'] = traceback.format_exc()
        
        self.logger.error(self._enrich_message(message, **kwargs))

class PerformanceProfiler:
    """Code performance profiling and timing"""
    
    def __init__(self):
        self.profiles: Dict[str, List[float]] = defaultdict(list)
        self.lock = threading.Lock()
    
    @contextmanager
    def profile(self, name: str):
        """Profile code execution time"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            with self.lock:
                self.profiles[name].append(duration)
                
                # Limit profile history
                if len(self.profiles[name]) > 1000:
                    self.profiles[name] = self.profiles[name][-500:]
    
    def get_profile_stats(self, name: str) -> Dict[str, float]:
        """Get performance statistics for a profile"""
        with self.lock:
            if name not in self.profiles or not self.profiles[name]:
                return {}
            
            times = self.profiles[name]
            return {
                'count': len(times),
                'total': sum(times),
                'average': sum(times) / len(times),
                'min': min(times),
                'max': max(times),
                'p50': sorted(times)[len(times) // 2],
                'p95': sorted(times)[int(len(times) * 0.95)],
                'p99': sorted(times)[int(len(times) * 0.99)]
            }
    
    def get_all_profiles(self) -> Dict[str, Dict[str, float]]:
        """Get all profile statistics"""
        with self.lock:
            return {name: self.get_profile_stats(name) for name in self.profiles}

class HealthChecker:
    """System health monitoring and checks"""
    
    def __init__(self):
        self.health_checks: Dict[str, Callable] = {}
        self.last_results: Dict[str, Dict[str, Any]] = {}
        
        # Register default health checks
        self._register_default_checks()
    
    def _register_default_checks(self) -> None:
        """Register default health checks"""
        self.health_checks.update({
            'memory_usage': self._check_memory_usage,
            'disk_space': self._check_disk_space,
            'thread_count': self._check_thread_count,
            'network_connectivity': self._check_network_connectivity,
        })
    
    def register_check(self, name: str, check_func: Callable) -> None:
        """Register custom health check"""
        self.health_checks[name] = check_func
    
    def run_check(self, name: str) -> Dict[str, Any]:
        """Run individual health check"""
        if name not in self.health_checks:
            return {'status': 'unknown', 'message': 'Check not found'}
        
        try:
            result = self.health_checks[name]()
            self.last_results[name] = result
            return result
        except Exception as e:
            error_result = {
                'status': 'error',
                'message': f'Health check failed: {e}',
                'exception': str(e)
            }
            self.last_results[name] = error_result
            return error_result
    
    def run_all_checks(self) -> Dict[str, Dict[str, Any]]:
        """Run all registered health checks"""
        results = {}
        for name in self.health_checks:
            results[name] = self.run_check(name)
        return results
    
    def get_overall_status(self) -> str:
        """Get overall system health status"""
        results = self.run_all_checks()
        
        statuses = [result.get('status', 'unknown') for result in results.values()]
        
        if any(status == 'critical' for status in statuses):
            return 'critical'
        elif any(status == 'error' for status in statuses):
            return 'error'
        elif any(status == 'warning' for status in statuses):
            return 'warning'
        elif all(status == 'healthy' for status in statuses):
            return 'healthy'
        else:
            return 'unknown'
    
    def _check_memory_usage(self) -> Dict[str, Any]:
        """Check memory usage health"""
        try:
            memory = psutil.virtual_memory()
            process = psutil.Process()
            process_memory = process.memory_info()
            
            if memory.percent > 90:
                return {
                    'status': 'critical',
                    'message': f'System memory usage critical: {memory.percent}%'
                }
            elif memory.percent > 80:
                return {
                    'status': 'warning',
                    'message': f'System memory usage high: {memory.percent}%'
                }
            else:
                return {
                    'status': 'healthy',
                    'message': f'Memory usage normal: {memory.percent}%',
                    'system_memory_percent': memory.percent,
                    'process_memory_mb': process_memory.rss / 1024 / 1024
                }
        except Exception as e:
            return {'status': 'error', 'message': f'Memory check failed: {e}'}
    
    def _check_disk_space(self) -> Dict[str, Any]:
        """Check disk space health"""
        try:
            disk_usage = psutil.disk_usage('/')
            usage_percent = (disk_usage.used / disk_usage.total) * 100
            
            if usage_percent > 95:
                return {
                    'status': 'critical',
                    'message': f'Disk space critical: {usage_percent:.1f}%'
                }
            elif usage_percent > 85:
                return {
                    'status': 'warning',
                    'message': f'Disk space low: {usage_percent:.1f}%'
                }
            else:
                return {
                    'status': 'healthy',
                    'message': f'Disk space normal: {usage_percent:.1f}%',
                    'usage_percent': usage_percent,
                    'free_gb': disk_usage.free / (1024**3)
                }
        except Exception as e:
            return {'status': 'error', 'message': f'Disk check failed: {e}'}
    
    def _check_thread_count(self) -> Dict[str, Any]:
        """Check thread count health"""
        try:
            thread_count = threading.active_count()
            
            if thread_count > 100:
                return {
                    'status': 'warning',
                    'message': f'High thread count: {thread_count}'
                }
            else:
                return {
                    'status': 'healthy',
                    'message': f'Thread count normal: {thread_count}',
                    'thread_count': thread_count
                }
        except Exception as e:
            return {'status': 'error', 'message': f'Thread check failed: {e}'}
    
    def _check_network_connectivity(self) -> Dict[str, Any]:
        """Check basic network connectivity"""
        try:
            # Test localhost connectivity
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', 11434))  # Ollama default port
            sock.close()
            
            if result == 0:
                return {
                    'status': 'healthy',
                    'message': 'Ollama service reachable'
                }
            else:
                return {
                    'status': 'warning',
                    'message': 'Ollama service not reachable'
                }
        except Exception as e:
            return {'status': 'error', 'message': f'Network check failed: {e}'}

class MonitoringFramework:
    """Main monitoring and observability framework"""
    
    def __init__(self, retention_hours: int = 24):
        # Core components
        self.metrics_store = MetricsStore(retention_hours=retention_hours)
        self.system_collector = SystemMetricsCollector()
        self.app_collector = ApplicationMetricsCollector()
        self.alert_manager = AlertManager(self.metrics_store)
        self.logger = StructuredLogger()
        self.profiler = PerformanceProfiler()
        self.health_checker = HealthChecker()
        
        # State
        self.started = False
        self.start_time = datetime.now()
        
        logger.info("Monitoring framework initialized")
    
    def start(self) -> None:
        """Start all monitoring components"""
        if self.started:
            return
        
        self.system_collector.start_collection(self.metrics_store)
        self.alert_manager.start_monitoring()
        self.started = True
        
        logger.info("Monitoring framework started")
    
    def stop(self) -> None:
        """Stop all monitoring components"""
        if not self.started:
            return
        
        self.system_collector.stop_collection()
        self.alert_manager.stop_monitoring()
        self.started = False
        
        logger.info("Monitoring framework stopped")
    
    def record_request(self, duration: float, success: bool = True, **context) -> None:
        """Record application request metrics"""
        self.app_collector.record_request(duration, success)
        
        # Store as metrics
        self.metrics_store.add_metric(MetricData(
            "app.request.duration", duration, MetricType.TIMER, tags=context
        ))
        
        if not success:
            self.metrics_store.add_metric(MetricData(
                "app.request.error", 1, MetricType.COUNTER, tags=context
            ))
    
    def record_custom_metric(self, name: str, value: float, metric_type: MetricType = MetricType.GAUGE, **tags) -> None:
        """Record custom application metric"""
        self.metrics_store.add_metric(MetricData(
            name, value, metric_type, tags=tags
        ))
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        # Get recent metrics (last hour)
        since = datetime.now() - timedelta(hours=1)
        
        dashboard_data = {
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
            'system_metrics': {},
            'application_metrics': {},
            'active_alerts': [asdict(alert) for alert in self.alert_manager.get_active_alerts()],
            'health_status': self.health_checker.get_overall_status(),
            'health_checks': self.health_checker.run_all_checks(),
            'performance_profiles': self.profiler.get_all_profiles()
        }
        
        # System metrics
        for metric_name in ['system.cpu.percent', 'system.memory.rss_mb', 'system.threads.count']:
            latest_value = self.metrics_store.get_latest_value(metric_name)
            if latest_value is not None:
                dashboard_data['system_metrics'][metric_name] = latest_value
        
        # Application metrics
        app_metrics = self.app_collector.get_metrics()
        for metric_name, metric_data in app_metrics.items():
            dashboard_data['application_metrics'][metric_name] = metric_data.value
        
        return dashboard_data
    
    def export_metrics(self, format_type: str = "json") -> str:
        """Export metrics in specified format"""
        if format_type == "json":
            return self._export_json()
        elif format_type == "prometheus":
            return self._export_prometheus()
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    def _export_json(self) -> str:
        """Export metrics as JSON"""
        metrics_data = {}
        
        for metric_name in self.metrics_store.get_metric_names():
            recent_metrics = self.metrics_store.get_metrics(
                metric_name, 
                since=datetime.now() - timedelta(hours=1),
                limit=100
            )
            metrics_data[metric_name] = [m.to_dict() for m in recent_metrics]
        
        return json.dumps(metrics_data, indent=2)
    
    def _export_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        output = []
        
        for metric_name in self.metrics_store.get_metric_names():
            latest_value = self.metrics_store.get_latest_value(metric_name)
            if latest_value is not None:
                # Convert metric name to Prometheus format
                prom_name = metric_name.replace('.', '_')
                output.append(f"{prom_name} {latest_value}")
        
        return "\n".join(output)

# Convenience decorators
def monitor_performance(name: str = None):
    """Decorator to monitor function performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            profile_name = name or f"{func.__module__}.{func.__name__}"
            
            # Get monitoring framework instance (assume global)
            monitoring = getattr(func, '_monitoring_framework', None)
            if monitoring and hasattr(monitoring, 'profiler'):
                with monitoring.profiler.profile(profile_name):
                    return func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator

def monitor_requests():
    """Decorator to monitor request metrics"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                
                # Record metrics (assume monitoring framework available)
                monitoring = getattr(func, '_monitoring_framework', None)
                if monitoring:
                    monitoring.record_request(duration, success, function=func.__name__)
        
        return wrapper
    return decorator

if __name__ == "__main__":
    # Example usage and testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create monitoring framework
    monitoring = MonitoringFramework()
    monitoring.start()
    
    try:
        # Simulate some activity
        print("Testing monitoring framework...")
        
        # Record some metrics
        for i in range(10):
            monitoring.record_request(0.1 + i * 0.05, success=i % 7 != 0)
            monitoring.record_custom_metric("test.counter", i, MetricType.COUNTER)
            time.sleep(0.1)
        
        # Test performance profiling
        with monitoring.profiler.profile("test_operation"):
            time.sleep(0.2)
        
        # Get dashboard data
        dashboard = monitoring.get_dashboard_data()
        print("\nDashboard Data:")
        print(json.dumps(dashboard, indent=2, default=str))
        
        # Export metrics
        print("\nJSON Export (first 500 chars):")
        json_export = monitoring.export_metrics("json")
        print(json_export[:500] + "..." if len(json_export) > 500 else json_export)
        
        print("\nPrometheus Export:")
        prom_export = monitoring.export_metrics("prometheus")
        print(prom_export[:500] + "..." if len(prom_export) > 500 else prom_export)
        
    finally:
        monitoring.stop()
        print("\nMonitoring framework test completed!")