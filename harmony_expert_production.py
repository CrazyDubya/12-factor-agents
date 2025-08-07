#!/usr/bin/env python3
"""
GPT-OSS Harmony Expert Production Interface
Security-hardened, production-ready interface with comprehensive validation

This version addresses all critical security vulnerabilities identified in
the system engineering review while maintaining full functionality.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import json
import re
import threading
import queue
import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
import sys
from pathlib import Path

# Import our security modules
sys.path.append(str(Path(__file__).parent))
from safe_math_parser import SafeMathEvaluator, MathSecurityError
from input_validator import InputValidator, ValidationError, SecurityViolationError

# Harmony Integration
try:
    from openai_harmony import (
        load_harmony_encoding,
        HarmonyEncodingName,
        Role,
        Message,
        Conversation,
        SystemContent,
        TextContent,
    )
    HARMONY_AVAILABLE = True
except ImportError:
    HARMONY_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('harmony_expert_production.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProductionError(Exception):
    """Base exception for production errors"""
    pass

class ConfigurationError(ProductionError):
    """Raised when configuration is invalid"""
    pass

class SecurityError(ProductionError):
    """Raised when security violation occurs"""
    pass

class ProductionConfig:
    """Production configuration management"""
    
    def __init__(self):
        self.ollama_url = self._get_env('OLLAMA_URL', 'http://localhost:11434')
        self.model_name = self._get_env('GPT_OSS_MODEL', 'gpt-oss:latest')
        self.request_timeout = int(self._get_env('REQUEST_TIMEOUT', '60'))
        self.max_input_length = int(self._get_env('MAX_INPUT_LENGTH', '2000'))
        self.max_response_length = int(self._get_env('MAX_RESPONSE_LENGTH', '10000'))
        self.rate_limit = int(self._get_env('RATE_LIMIT', '10'))  # requests per minute
        self.log_level = self._get_env('LOG_LEVEL', 'INFO')
        
        # Security settings
        self.enable_math_evaluation = self._get_bool_env('ENABLE_MATH_EVAL', True)
        self.enable_harmony_format = self._get_bool_env('ENABLE_HARMONY', True)
        self.strict_validation = self._get_bool_env('STRICT_VALIDATION', True)
        
        # Validate configuration
        self._validate_config()
    
    def _get_env(self, key: str, default: str) -> str:
        """Get environment variable with default"""
        import os
        return os.getenv(key, default)
    
    def _get_bool_env(self, key: str, default: bool) -> bool:
        """Get boolean environment variable"""
        import os
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    def _validate_config(self):
        """Validate configuration values"""
        if not self.ollama_url.startswith(('http://', 'https://')):
            raise ConfigurationError(f"Invalid Ollama URL format: {self.ollama_url}")
        
        if self.request_timeout <= 0 or self.request_timeout > 300:
            raise ConfigurationError(f"Invalid timeout: {self.request_timeout}s (must be 1-300)")
        
        if self.max_input_length <= 0 or self.max_input_length > 50000:
            raise ConfigurationError(f"Invalid max input length: {self.max_input_length}")
        
        logger.info(f"Production configuration loaded: {self.ollama_url}, timeout={self.request_timeout}s")

class RateLimiter:
    """Rate limiting for API requests"""
    
    def __init__(self, max_requests: int, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        self.lock = threading.Lock()
    
    def is_allowed(self) -> bool:
        """Check if request is allowed under rate limit"""
        now = time.time()
        
        with self.lock:
            # Remove old requests outside time window
            self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
            
            if len(self.requests) >= self.max_requests:
                return False
            
            self.requests.append(now)
            return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get current rate limit status"""
        now = time.time()
        
        with self.lock:
            active_requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
            return {
                'current_requests': len(active_requests),
                'max_requests': self.max_requests,
                'time_window': self.time_window,
                'available': self.max_requests - len(active_requests)
            }

class HarmonyExpertProductionGUI:
    """
    Production-hardened GPT-OSS Harmony Expert interface
    
    Security features:
    - Safe mathematical evaluation (no eval/exec)
    - Comprehensive input validation
    - Rate limiting and resource protection
    - Security audit logging
    - Error handling and recovery
    """
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("GPT-OSS Harmony Expert (Production)")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f5f5f5')
        
        # Initialize production components
        try:
            self.config = ProductionConfig()
            self.input_validator = InputValidator()
            self.math_evaluator = SafeMathEvaluator(max_length=1000)
            self.rate_limiter = RateLimiter(self.config.rate_limit, 60)
            
            logger.info("Production components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize production components: {e}")
            messagebox.showerror("Configuration Error", f"Failed to initialize: {e}")
            self.root.quit()
            return
        
        # Harmony integration
        self.enc = None
        if HARMONY_AVAILABLE and self.config.enable_harmony_format:
            try:
                self.enc = load_harmony_encoding(HarmonyEncodingName.HARMONY_GPT_OSS)
                logger.info("Harmony encoding initialized")
            except Exception as e:
                logger.warning(f"Harmony initialization failed: {e}")
        
        # Threading components
        self.update_queue = queue.Queue()
        self.is_processing = False
        self.processing_lock = threading.Lock()
        
        # Placeholder management
        self.placeholder_active = True
        
        # Security monitoring
        self.security_events = []
        self.request_history = []
        
        # Initialize GUI
        self.setup_gui()
        self.setup_bindings()
        self.start_update_loop()
        self.test_connection()
        
        logger.info("Production GUI initialized successfully")
    
    def setup_gui(self):
        """Setup production-grade GUI with security indicators"""
        # Main layout
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Input and controls
        left_frame = tk.Frame(main_paned, bg='#f5f5f5', width=350)
        main_paned.add(left_frame, weight=1)
        
        # Right panel - Tabbed output
        right_frame = tk.Frame(main_paned, bg='#f5f5f5')
        main_paned.add(right_frame, weight=2)
        
        self.setup_input_panel(left_frame)
        self.setup_output_tabs(right_frame)
        self.setup_status_bar()
        
        # Security indicator
        self.setup_security_panel(left_frame)
    
    def setup_security_panel(self, parent):
        """Setup security monitoring panel"""
        security_frame = tk.LabelFrame(parent, text="🛡️ Security Status", bg='#f5f5f5', 
                                     fg='#2E7D32', font=('Arial', 9, 'bold'), padx=10, pady=10)
        security_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Security indicators
        harmony_status = "✅ Available" if HARMONY_AVAILABLE else "❌ Not Available"
        tk.Label(security_frame, text=f"Harmony: {harmony_status}", bg='#f5f5f5',
                font=('Arial', 8), anchor='w').pack(fill=tk.X)
        
        validation_status = "✅ Active" if self.config.strict_validation else "⚠️ Relaxed"
        tk.Label(security_frame, text=f"Validation: {validation_status}", bg='#f5f5f5',
                font=('Arial', 8), anchor='w').pack(fill=tk.X)
        
        math_status = "✅ Safe AST" if self.config.enable_math_evaluation else "❌ Disabled"
        tk.Label(security_frame, text=f"Math Eval: {math_status}", bg='#f5f5f5',
                font=('Arial', 8), anchor='w').pack(fill=tk.X)
        
        # Rate limit status
        self.rate_limit_label = tk.Label(security_frame, text="Rate Limit: OK", bg='#f5f5f5',
                                       font=('Arial', 8), anchor='w')
        self.rate_limit_label.pack(fill=tk.X)
    
    def setup_input_panel(self, parent):
        """Setup input panel with validation indicators"""
        # Input section
        input_frame = tk.LabelFrame(parent, text="Input (Production Mode)", bg='#f5f5f5', 
                                   fg='#1976D2', font=('Arial', 10, 'bold'), padx=10, pady=10)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.input_text = scrolledtext.ScrolledText(input_frame, height=8, bg='white',
                                                   relief=tk.FLAT, borderwidth=2,
                                                   highlightthickness=1, highlightcolor='#2196F3')
        self.input_text.pack(fill=tk.BOTH, expand=True)
        
        # Placeholder text with security info
        placeholder = f"""Enter questions for GPT-OSS (Max: {self.config.max_input_length} chars)

Security Features Active:
• Safe mathematical evaluation (no eval/exec)
• Comprehensive input validation
• Rate limiting ({self.config.rate_limit}/min)
• Security audit logging

Examples:
• What is quantum computing?
• Calculate sqrt(16) + sin(pi/2)
• Explain machine learning concepts"""
        
        self.input_text.insert("1.0", placeholder)
        self.input_text.config(fg='#666666')
        self.input_text.bind('<FocusIn>', self.on_input_focus)
        self.input_text.bind('<FocusOut>', self.on_input_unfocus)
        self.input_text.bind('<KeyRelease>', self.on_input_change)
        
        # Input validation indicator
        self.validation_frame = tk.Frame(input_frame, bg='#f5f5f5')
        self.validation_frame.pack(fill=tk.X, pady=5)
        
        self.validation_label = tk.Label(self.validation_frame, text="", bg='#f5f5f5', 
                                       font=('Arial', 8))
        self.validation_label.pack(side=tk.LEFT)
        
        self.char_count_label = tk.Label(self.validation_frame, text="", bg='#f5f5f5', 
                                        font=('Arial', 8))
        self.char_count_label.pack(side=tk.RIGHT)
        
        # Control buttons
        button_frame = tk.Frame(input_frame, bg='#f5f5f5')
        button_frame.pack(fill=tk.X, pady=10)
        
        self.send_btn = tk.Button(button_frame, text="Send (Secure)", command=self.send_message,
                                 bg='#4CAF50', fg='white', font=('Arial', 11, 'bold'),
                                 height=2, width=15, relief=tk.FLAT, cursor='hand2')
        self.send_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(button_frame, text="Stop", command=self.stop_processing,
                                 bg='#F44336', fg='white', font=('Arial', 11, 'bold'),
                                 height=2, width=8, relief=tk.FLAT, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Clear", command=self.clear_all,
                 bg='#9E9E9E', fg='white', font=('Arial', 10),
                 height=1, width=8, relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
    
    def setup_output_tabs(self, parent):
        """Setup output tabs with security context"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Conversation tab
        conv_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(conv_frame, text="💬 Conversation")
        
        self.conversation_text = scrolledtext.ScrolledText(conv_frame, bg='#fafafa', font=('Segoe UI', 10),
                                                          wrap=tk.WORD, state=tk.DISABLED)
        self.conversation_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure text tags
        self.conversation_text.tag_config('user', foreground='#1976D2', font=('Segoe UI', 10, 'bold'))
        self.conversation_text.tag_config('assistant', foreground='#388E3C', font=('Segoe UI', 10))
        self.conversation_text.tag_config('analysis', foreground='#7B1FA2', font=('Segoe UI', 9, 'italic'))
        self.conversation_text.tag_config('tool', foreground='#F57C00', font=('Consolas', 9))
        self.conversation_text.tag_config('security', foreground='#D32F2F', font=('Segoe UI', 9, 'bold'))
        self.conversation_text.tag_config('system', foreground='#455A64', font=('Segoe UI', 9, 'italic'))
        
        # Security events tab
        security_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(security_frame, text="🛡️ Security Log")
        
        self.security_text = scrolledtext.ScrolledText(security_frame, bg='#fff3e0', 
                                                      font=('Consolas', 9), wrap=tk.WORD, state=tk.DISABLED)
        self.security_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Token stream tab
        stream_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(stream_frame, text="📡 Token Stream")
        
        self.stream_text = scrolledtext.ScrolledText(stream_frame, bg='#1e1e1e', fg='#d4d4d4',
                                                    font=('Consolas', 9), wrap=tk.WORD, state=tk.DISABLED)
        self.stream_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Harmony channels tab
        channels_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(channels_frame, text="🎭 Harmony Channels")
        
        channels_notebook = ttk.Notebook(channels_frame)
        channels_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Analysis channel
        analysis_frame = tk.Frame(channels_notebook, bg='#f5f5f5')
        channels_notebook.add(analysis_frame, text="Analysis")
        self.analysis_text = scrolledtext.ScrolledText(analysis_frame, bg='#f3e5f5', fg='#7B1FA2',
                                                      font=('Segoe UI', 9, 'italic'), wrap=tk.WORD, state=tk.DISABLED)
        self.analysis_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Commentary channel
        commentary_frame = tk.Frame(channels_notebook, bg='#f5f5f5')
        channels_notebook.add(commentary_frame, text="Commentary")
        self.commentary_text = scrolledtext.ScrolledText(commentary_frame, bg='#fff3e0', fg='#F57C00',
                                                        font=('Consolas', 9), wrap=tk.WORD, state=tk.DISABLED)
        self.commentary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Final channel
        final_frame = tk.Frame(channels_notebook, bg='#f5f5f5')
        channels_notebook.add(final_frame, text="Final")
        self.final_text = scrolledtext.ScrolledText(final_frame, bg='#e8f5e8', fg='#388E3C',
                                                   font=('Segoe UI', 10), wrap=tk.WORD, state=tk.DISABLED)
        self.final_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tools tab
        tools_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(tools_frame, text="🛠 Safe Tools")
        
        self.tools_text = scrolledtext.ScrolledText(tools_frame, bg='#fff8e1', font=('Consolas', 9),
                                                   wrap=tk.WORD, state=tk.DISABLED)
        self.tools_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_status_bar(self):
        """Setup enhanced status bar with production info"""
        status_frame = tk.Frame(self.root, bg='#e9ecef', relief=tk.SUNKEN, borderwidth=1)
        status_frame.pack(fill=tk.X)
        
        # Main status
        self.status_label = tk.Label(status_frame, text="🔒 Production Mode Ready", 
                                   bg='#e9ecef', anchor=tk.W, padx=10, pady=5,
                                   font=('Arial', 9, 'bold'))
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Security events counter
        self.security_counter_label = tk.Label(status_frame, text="Security Events: 0", 
                                             bg='#e9ecef', padx=10)
        self.security_counter_label.pack(side=tk.RIGHT)
        
        # Token counter
        self.token_label = tk.Label(status_frame, text="Tokens: 0", bg='#e9ecef', padx=10)
        self.token_label.pack(side=tk.RIGHT)
        
        # Model info
        model_text = f"Model: {self.config.model_name}"
        if HARMONY_AVAILABLE and self.config.enable_harmony_format:
            model_text += " (Harmony)"
        tk.Label(status_frame, text=model_text, bg='#e9ecef', padx=10, 
                font=('Arial', 8)).pack(side=tk.RIGHT)
    
    def setup_bindings(self):
        """Setup keyboard shortcuts"""
        self.root.bind('<Control-Return>', lambda e: self.send_message())
        self.root.bind('<Control-q>', lambda e: self.safe_shutdown())
        self.root.bind('<Control-l>', lambda e: self.clear_all())
        self.input_text.bind('<Control-a>', self.select_all_input)
        
        # Set initial focus
        self.root.after(100, lambda: self.input_text.focus_set())
    
    def on_input_focus(self, event):
        """Handle input focus with security validation"""
        if self.placeholder_active:
            self.input_text.delete("1.0", tk.END)
            self.input_text.config(fg='black')
            self.placeholder_active = False
            self.update_validation_status("")
    
    def on_input_unfocus(self, event):
        """Handle input unfocus"""
        current_text = self.input_text.get("1.0", tk.END).strip()
        if not current_text:
            # Restore placeholder
            placeholder = f"""Enter questions for GPT-OSS (Max: {self.config.max_input_length} chars)

Security Features Active:
• Safe mathematical evaluation (no eval/exec)
• Comprehensive input validation
• Rate limiting ({self.config.rate_limit}/min)
• Security audit logging

Examples:
• What is quantum computing?
• Calculate sqrt(16) + sin(pi/2)
• Explain machine learning concepts"""
            
            self.input_text.insert("1.0", placeholder)
            self.input_text.config(fg='#666666')
            self.placeholder_active = True
            self.update_validation_status("")
    
    def on_input_change(self, event):
        """Handle input changes with real-time validation"""
        if self.placeholder_active:
            return
        
        current_text = self.input_text.get("1.0", tk.END).strip()
        char_count = len(current_text)
        
        # Update character count
        self.char_count_label.config(text=f"{char_count}/{self.config.max_input_length}")
        
        # Real-time validation
        if char_count > 0:
            try:
                self.input_validator.validate_text_input(current_text, 
                                                       max_length=self.config.max_input_length,
                                                       context="prompt")
                self.update_validation_status("✅ Valid", "#4CAF50")
            except SecurityViolationError:
                self.update_validation_status("🛡️ Security Block", "#F44336")
                self.log_security_event("Real-time input validation blocked dangerous pattern")
            except ValidationError as e:
                self.update_validation_status("⚠️ Invalid", "#FF9800")
        else:
            self.update_validation_status("", "#666666")
    
    def update_validation_status(self, text: str, color: str = "#666666"):
        """Update validation status indicator"""
        self.validation_label.config(text=text, fg=color)
    
    def select_all_input(self, event):
        """Select all input text"""
        if not self.placeholder_active:
            self.input_text.tag_add(tk.SEL, "1.0", tk.END)
        return 'break'
    
    def log_security_event(self, event: str, severity: str = "WARNING"):
        """Log security events with timestamp"""
        timestamp = datetime.now().isoformat()
        event_data = {
            'timestamp': timestamp,
            'event': event,
            'severity': severity
        }
        
        self.security_events.append(event_data)
        
        # Log to file
        logger.warning(f"SECURITY EVENT: {event}")
        
        # Update security display
        self.display_security_event(event_data)
        
        # Update counter
        self.security_counter_label.config(text=f"Security Events: {len(self.security_events)}")
    
    def display_security_event(self, event_data: Dict[str, Any]):
        """Display security event in security log tab"""
        self.security_text.config(state=tk.NORMAL)
        timestamp = datetime.fromisoformat(event_data['timestamp']).strftime("%H:%M:%S")
        self.security_text.insert(tk.END, f"[{timestamp}] {event_data['severity']}: {event_data['event']}\n")
        self.security_text.config(state=tk.DISABLED)
        self.security_text.see(tk.END)
    
    def safe_math_eval(self, expression: str) -> str:
        """Safely evaluate mathematical expression"""
        if not self.config.enable_math_evaluation:
            return "Math evaluation disabled in configuration"
        
        try:
            # Validate as math expression
            validated_expr = self.input_validator.validate_text_input(expression, 
                                                                    max_length=1000,
                                                                    context="math")
            
            # Use safe evaluator
            result = self.math_evaluator.evaluate(validated_expr)
            self.log_security_event(f"Safe math evaluation: {expression} = {result}", "INFO")
            return str(result)
            
        except (MathSecurityError, SecurityViolationError) as e:
            self.log_security_event(f"Math evaluation security block: {e}")
            return f"Security Error: {e}"
        except (ValidationError, ValueError, ArithmeticError) as e:
            return f"Math Error: {e}"
        except Exception as e:
            logger.error(f"Unexpected math evaluation error: {e}")
            return f"Unexpected Error: {e}"
    
    def is_math_expression(self, text: str) -> bool:
        """Check if text appears to be a mathematical expression"""
        try:
            self.input_validator.validate_text_input(text, max_length=1000, context="math")
            return True
        except (ValidationError, SecurityViolationError):
            return False
    
    def test_connection(self):
        """Test connection to Ollama with enhanced error handling"""
        def test_async():
            try:
                response = requests.get(f"{self.config.ollama_url}/api/tags", 
                                      timeout=5)
                if response.status_code == 200:
                    models = response.json().get('models', [])
                    model_found = any(self.config.model_name.split(':')[0] in model.get('name', '') 
                                    for model in models)
                    
                    if model_found:
                        self.update_queue.put(('status', ('🟢 Connected to GPT-OSS', 'success')))
                        logger.info(f"Successfully connected to {self.config.ollama_url}")
                    else:
                        self.update_queue.put(('status', (f'🟡 Connected but {self.config.model_name} not found', 'warning')))
                        logger.warning(f"Model {self.config.model_name} not found")
                else:
                    self.update_queue.put(('status', (f'🔴 HTTP {response.status_code}', 'error')))
                    
            except requests.exceptions.Timeout:
                self.update_queue.put(('status', ('🔴 Connection timeout', 'error')))
                logger.error("Connection to Ollama timed out")
            except Exception as e:
                self.update_queue.put(('status', (f'🔴 Connection failed: {e}', 'error')))
                logger.error(f"Connection failed: {e}")
        
        threading.Thread(target=test_async, daemon=True).start()
    
    def update_status(self, text: str, status_type: str = 'info'):
        """Update status with color coding"""
        colors = {
            'success': '#388E3C',
            'error': '#D32F2F', 
            'warning': '#F57C00',
            'info': '#1976D2',
            'processing': '#F57C00'
        }
        self.status_label.config(text=text, fg=colors.get(status_type, 'black'))
    
    def check_rate_limit(self) -> bool:
        """Check rate limit with status update"""
        if not self.rate_limiter.is_allowed():
            status = self.rate_limiter.get_status()
            self.rate_limit_label.config(text=f"Rate Limit: {status['current_requests']}/{status['max_requests']}", 
                                       fg='#F44336')
            return False
        
        status = self.rate_limiter.get_status()
        self.rate_limit_label.config(text=f"Rate Limit: {status['available']} available", 
                                   fg='#4CAF50')
        return True
    
    def create_harmony_prompt(self, user_input: str) -> str:
        """Create Harmony formatted prompt with validation"""
        if not self.enc or not self.config.enable_harmony_format:
            return f"User: {user_input}\nAssistant:"
        
        try:
            messages = [
                Message.from_role_and_content(Role.SYSTEM, SystemContent.new()),
                Message.from_role_and_content(Role.USER, TextContent(text=user_input))
            ]
            
            convo = Conversation.from_messages(messages)
            tokens = self.enc.render_conversation_for_completion(convo, Role.ASSISTANT)
            
            logger.info("Harmony prompt created successfully")
            return self.enc.decode(tokens)
            
        except Exception as e:
            logger.warning(f"Harmony prompt creation failed, using fallback: {e}")
            return f"User: {user_input}\nAssistant:"
    
    def send_message(self):
        """Send message with comprehensive security validation"""
        # Check if already processing
        with self.processing_lock:
            if self.is_processing:
                messagebox.showwarning("Processing", "Another request is already being processed")
                return
        
        # Get and validate input
        user_input = self.input_text.get("1.0", tk.END).strip()
        if not user_input or self.placeholder_active:
            return
        
        try:
            # Comprehensive input validation
            validated_input = self.input_validator.validate_text_input(
                user_input,
                max_length=self.config.max_input_length,
                context="prompt"
            )
            
            # Rate limiting check
            if not self.check_rate_limit():
                messagebox.showwarning("Rate Limited", 
                                     f"Rate limit exceeded. Maximum {self.config.rate_limit} requests per minute.")
                self.log_security_event(f"Rate limit exceeded")
                return
            
            # Log request
            self.request_history.append({
                'timestamp': datetime.now().isoformat(),
                'input_length': len(validated_input),
                'input_preview': validated_input[:100]
            })
            
        except SecurityViolationError as e:
            self.log_security_event(f"Input blocked: {e}")
            messagebox.showerror("Security Violation", 
                               "Input blocked due to security policy violation.")
            return
        except ValidationError as e:
            messagebox.showerror("Invalid Input", str(e))
            return
        
        # Handle math expressions locally
        if self.is_math_expression(validated_input):
            result = self.safe_math_eval(validated_input)
            self.add_to_conversation("USER", validated_input, 'user')
            self.add_to_conversation("MATH", f"🧮 Result: {result}", 'tool')
            self.log_security_event(f"Local math evaluation completed", "INFO")
            return
        
        # Start processing
        with self.processing_lock:
            self.is_processing = True
        
        self.send_btn.config(state=tk.DISABLED, text="Processing...", bg='#FF9800')
        self.stop_btn.config(state=tk.NORMAL)
        self.update_status("🔒 Secure processing...", 'processing')
        
        # Add user input to conversation
        self.add_to_conversation("USER", validated_input, 'user')
        
        # Start background processing
        threading.Thread(target=self.process_message, args=(validated_input,), daemon=True).start()
    
    def process_message(self, user_input: str):
        """Process message with enhanced error handling and security"""
        try:
            # Create secure prompt
            prompt = self.create_harmony_prompt(user_input)
            
            # Send request with comprehensive error handling
            logger.info(f"Sending request to {self.config.ollama_url}")
            
            response = requests.post(
                f"{self.config.ollama_url}/api/generate",
                json={
                    "model": self.config.model_name,
                    "prompt": prompt,
                    "raw": bool(self.enc and self.config.enable_harmony_format),
                    "stream": True,
                    "options": {
                        "num_predict": min(2048, self.config.max_response_length)
                    }
                },
                stream=True,
                timeout=self.config.request_timeout
            )
            
            if response.status_code != 200:
                self.update_queue.put(('error', f"HTTP {response.status_code}: {response.text}"))
                return
            
            full_response = ""
            token_count = 0
            
            for line in response.iter_lines():
                if not self.is_processing:
                    break
                
                if line:
                    try:
                        chunk = json.loads(line)
                        if 'response' in chunk:
                            text = chunk['response']
                            
                            # Validate response content
                            if len(full_response + text) > self.config.max_response_length:
                                logger.warning("Response length limit exceeded, truncating")
                                break
                            
                            full_response += text
                            token_count += 1
                            
                            # Update displays
                            self.update_queue.put(('stream', text))
                            self.update_queue.put(('token_count', token_count))
                            
                            if chunk.get('done', False):
                                break
                                
                    except json.JSONDecodeError:
                        continue
            
            # Process complete response
            if full_response:
                # Validate response before display
                try:
                    safe_response = self.input_validator.validate_text_input(
                        full_response, 
                        max_length=self.config.max_response_length,
                        context="general"
                    )
                    self.update_queue.put(('complete_response', safe_response))
                    
                    logger.info(f"Response processed successfully: {len(safe_response)} characters")
                    
                except SecurityViolationError as e:
                    self.log_security_event(f"Response blocked: {e}")
                    self.update_queue.put(('error', "Response blocked due to security policy"))
            
        except requests.exceptions.Timeout:
            self.update_queue.put(('error', f"Request timed out after {self.config.request_timeout}s"))
        except requests.exceptions.ConnectionError:
            self.update_queue.put(('error', "Connection failed. Check if Ollama is running."))
        except Exception as e:
            logger.error(f"Request processing error: {e}")
            self.update_queue.put(('error', f"Processing error: {str(e)}"))
        finally:
            self.update_queue.put(('processing_complete', None))
    
    def parse_harmony_response(self, response_text: str) -> Dict[str, str]:
        """Parse Harmony format response into channels"""
        channels = {'analysis': '', 'commentary': '', 'final': ''}
        
        patterns = {
            'analysis': r'<\|channel\|>analysis<\|message\|>(.*?)(?:<\|end\|>|<\|start\|>|$)',
            'commentary': r'<\|channel\|>commentary<\|message\|>(.*?)(?:<\|end\|>|<\|start\|>|$)',
            'final': r'<\|channel\|>final<\|message\|>(.*?)(?:<\|end\|>|<\|start\|>|$)'
        }
        
        for channel, pattern in patterns.items():
            matches = re.findall(pattern, response_text, re.DOTALL)
            if matches:
                channels[channel] = '\n'.join(matches).strip()
        
        return channels
    
    def extract_tools(self, commentary_text: str) -> List[Tuple[str, str]]:
        """Extract tool calls from commentary channel"""
        tools = []
        tool_pattern = r'to=([^\s<]+).*?<\|message\|>(.*?)(?:<\|call\|>|<\|end\|>)'
        
        for match in re.finditer(tool_pattern, commentary_text, re.DOTALL):
            tool_name = match.group(1).replace('functions.', '')
            arguments = match.group(2).strip()
            tools.append((tool_name, arguments))
        
        return tools
    
    def execute_tool(self, tool_name: str, arguments: str) -> str:
        """Execute tools safely with comprehensive validation"""
        try:
            # Validate tool arguments
            safe_args = self.input_validator.validate_text_input(arguments, 
                                                               max_length=1000,
                                                               context="general")
            
            self.log_security_event(f"Tool execution: {tool_name} with args: {safe_args[:50]}", "INFO")
            
            if tool_name in ['math', 'calculator']:
                return self.safe_math_eval(safe_args)
            
            elif tool_name == 'text_analysis':
                word_count = len(safe_args.split())
                char_count = len(safe_args)
                line_count = len(safe_args.splitlines())
                return f"Text Analysis: {word_count} words, {char_count} characters, {line_count} lines"
            
            else:
                return f"Tool '{tool_name}' executed safely (simulation): {safe_args[:100]}"
                
        except SecurityViolationError as e:
            self.log_security_event(f"Tool execution blocked: {tool_name} - {e}")
            return f"Tool execution blocked: Security violation detected"
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return f"Tool execution error: {str(e)}"
    
    def stop_processing(self):
        """Stop current processing safely"""
        with self.processing_lock:
            self.is_processing = False
        
        self.send_btn.config(state=tk.NORMAL, text="Send (Secure)", bg='#4CAF50')
        self.stop_btn.config(state=tk.DISABLED)
        self.update_status("🛑 Processing stopped", 'warning')
        
        logger.info("Processing stopped by user")
    
    def start_update_loop(self):
        """Process update queue with enhanced error handling"""
        try:
            while not self.update_queue.empty():
                try:
                    update_type, data = self.update_queue.get_nowait()
                    
                    if update_type == 'stream':
                        self.stream_text.config(state=tk.NORMAL)
                        self.stream_text.insert(tk.END, data)
                        self.stream_text.config(state=tk.DISABLED)
                        self.stream_text.see(tk.END)
                    
                    elif update_type == 'token_count':
                        self.token_label.config(text=f"Tokens: {data}")
                    
                    elif update_type == 'complete_response':
                        self.handle_complete_response(data)
                    
                    elif update_type == 'error':
                        self.handle_error(data)
                    
                    elif update_type == 'status':
                        status_text, status_type = data
                        self.update_status(status_text, status_type)
                    
                    elif update_type == 'processing_complete':
                        self.handle_processing_complete()
                
                except Exception as e:
                    logger.error(f"Update queue processing error: {e}")
        
        except queue.Empty:
            pass
        
        # Schedule next update
        self.root.after(100, self.start_update_loop)
    
    def handle_complete_response(self, response_text: str):
        """Handle complete response with Harmony parsing and security validation"""
        try:
            # Parse Harmony channels if enabled
            if self.enc and self.config.enable_harmony_format:
                channels = self.parse_harmony_response(response_text)
                
                # Display channels safely
                if channels['analysis']:
                    self.display_in_text_widget(self.analysis_text, channels['analysis'])
                    self.add_to_conversation("ANALYSIS", channels['analysis'], 'analysis')
                
                if channels['commentary']:
                    self.display_in_text_widget(self.commentary_text, channels['commentary'])
                    
                    # Extract and execute tools
                    tools = self.extract_tools(channels['commentary'])
                    if tools:
                        tool_results = []
                        for tool_name, arguments in tools:
                            result = self.execute_tool(tool_name, arguments)
                            tool_results.append(f"🛠 {tool_name}: {result}")
                        
                        self.display_in_text_widget(self.tools_text, '\n'.join(tool_results))
                
                if channels['final']:
                    self.display_in_text_widget(self.final_text, channels['final'])
                    self.add_to_conversation("ASSISTANT", channels['final'], 'assistant')
                else:
                    # Fallback if no final channel
                    self.add_to_conversation("ASSISTANT", response_text[:1000], 'assistant')
            else:
                # Non-Harmony response
                self.add_to_conversation("ASSISTANT", response_text, 'assistant')
            
            self.update_status("✅ Response processed securely", 'success')
            
        except Exception as e:
            logger.error(f"Response handling error: {e}")
            self.add_to_conversation("SYSTEM", f"Error processing response: {e}", 'security')
    
    def handle_error(self, error_message: str):
        """Handle errors with security logging"""
        self.add_to_conversation("SYSTEM", f"❌ Error: {error_message}", 'security')
        self.update_status(f"❌ Error: {error_message[:50]}", 'error')
        
        # Log error for monitoring
        logger.error(f"System error: {error_message}")
    
    def handle_processing_complete(self):
        """Handle processing completion"""
        with self.processing_lock:
            self.is_processing = False
        
        self.send_btn.config(state=tk.NORMAL, text="Send (Secure)", bg='#4CAF50')
        self.stop_btn.config(state=tk.DISABLED)
        self.update_status("🔒 Ready (Secure)", 'success')
    
    def display_in_text_widget(self, widget, text: str):
        """Safely display text in widget"""
        try:
            # Additional validation for display
            safe_text = self.input_validator.validate_text_input(text, 
                                                               max_length=50000,
                                                               context="general")
            
            widget.config(state=tk.NORMAL)
            widget.delete("1.0", tk.END)
            widget.insert("1.0", safe_text)
            widget.config(state=tk.DISABLED)
            widget.see(tk.END)
            
        except SecurityViolationError:
            # Display security warning instead
            widget.config(state=tk.NORMAL)
            widget.delete("1.0", tk.END)
            widget.insert("1.0", "⚠️ Content blocked due to security policy")
            widget.config(state=tk.DISABLED)
            self.log_security_event("Display content blocked")
    
    def add_to_conversation(self, role: str, content: str, tag: str):
        """Add message to conversation with security validation"""
        try:
            # Validate content before display
            safe_content = self.input_validator.validate_text_input(content, 
                                                                   max_length=10000,
                                                                   context="general")
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            self.conversation_text.config(state=tk.NORMAL)
            self.conversation_text.insert(tk.END, f"\n[{timestamp}] ")
            self.conversation_text.insert(tk.END, f"{role}: ", tag)
            self.conversation_text.insert(tk.END, f"{safe_content}\n")
            self.conversation_text.config(state=tk.DISABLED)
            self.conversation_text.see(tk.END)
            
        except SecurityViolationError:
            # Log security event and show warning
            self.log_security_event(f"Conversation content blocked for role: {role}")
            
            self.conversation_text.config(state=tk.NORMAL)
            self.conversation_text.insert(tk.END, f"\n[{datetime.now().strftime('%H:%M:%S')}] ")
            self.conversation_text.insert(tk.END, f"{role}: ", 'security')
            self.conversation_text.insert(tk.END, "⚠️ Content blocked by security policy\n")
            self.conversation_text.config(state=tk.DISABLED)
            self.conversation_text.see(tk.END)
    
    def clear_all(self):
        """Clear all displays with confirmation"""
        if messagebox.askyesno("Clear All", "Clear all conversation and logs?"):
            widgets = [self.conversation_text, self.stream_text, self.analysis_text, 
                      self.commentary_text, self.final_text, self.tools_text, self.security_text]
            
            for widget in widgets:
                widget.config(state=tk.NORMAL)
                widget.delete("1.0", tk.END)
                widget.config(state=tk.DISABLED)
            
            self.token_label.config(text="Tokens: 0")
            self.security_events.clear()
            self.security_counter_label.config(text="Security Events: 0")
            self.update_status("🔄 Cleared", 'info')
            
            logger.info("All displays cleared by user")
    
    def safe_shutdown(self):
        """Safely shutdown application"""
        if self.is_processing:
            if messagebox.askyesno("Shutdown", "Processing in progress. Force shutdown?"):
                self.stop_processing()
            else:
                return
        
        # Log shutdown
        logger.info(f"Application shutdown - Security events: {len(self.security_events)}")
        
        self.root.quit()

def main():
    """Main application entry point with error handling"""
    try:
        root = tk.Tk()
        
        # Set application icon if available
        try:
            root.iconname("GPT-OSS Production")
        except:
            pass
        
        # Create application
        app = HarmonyExpertProductionGUI(root)
        
        # Run main loop
        root.mainloop()
        
    except Exception as e:
        logger.critical(f"Application startup failed: {e}")
        messagebox.showerror("Critical Error", f"Application failed to start: {e}")

if __name__ == "__main__":
    main()