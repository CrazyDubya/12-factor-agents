"""
Configuration management for the Finetune system.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class ModelConfig:
    """Configuration for language models."""
    name: str
    size: str  # "1B", "3B", "7B"
    model_id: str  # HuggingFace model ID
    max_length: int = 8192
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50

@dataclass
class TrainingConfig:
    """Configuration for finetuning."""
    learning_rate: float = 2e-4
    batch_size: int = 4
    gradient_accumulation_steps: int = 4
    num_epochs: int = 3
    warmup_steps: int = 100
    save_steps: int = 500
    eval_steps: int = 250
    logging_steps: int = 10

    # LoRA/QLoRA settings
    lora_r: int = 32
    lora_alpha: int = 16
    lora_dropout: float = 0.1
    use_qlora: bool = True
    bits: int = 4

@dataclass
class Neo4jConfig:
    """Configuration for Neo4j database."""
    uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user: str = os.getenv("NEO4J_USER", "neo4j")
    password: str = os.getenv("NEO4J_PASSWORD", "password")
    database: str = os.getenv("NEO4J_DATABASE", "narrative")

@dataclass
class SystemConfig:
    """Main system configuration."""

    # Directories
    project_root: Path = Path(__file__).parent.parent
    data_dir: Path = project_root / "data"
    models_dir: Path = project_root / "models"
    outputs_dir: Path = project_root / "outputs"
    logs_dir: Path = project_root / "logs"

    # Generation settings
    max_documents_per_world: int = 100
    max_characters_per_world: int = 20
    max_locations_per_world: int = 15

    # Agent settings
    agent_timeout: int = 300  # seconds
    max_retries: int = 3
    consistency_threshold: float = 0.85

    # Quality control
    min_document_length: int = 500
    max_document_length: int = 5000
    coherence_threshold: float = 0.8

    def __post_init__(self):
        """Create directories if they don't exist."""
        for directory in [self.data_dir, self.models_dir, self.outputs_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)

# Default model configurations
SUPPORTED_MODELS = {
    "qwen-1.5b": ModelConfig(
        name="Qwen-2",
        size="1.5B",
        model_id="Qwen/Qwen2-1.5B-Instruct",
        max_length=8192
    ),
    "qwen-7b": ModelConfig(
        name="Qwen-2",
        size="7B",
        model_id="Qwen/Qwen2-7B-Instruct",
        max_length=8192
    ),
    "llama-3b": ModelConfig(
        name="Llama-3.2",
        size="3B",
        model_id="meta-llama/Llama-3.2-3B-Instruct",
        max_length=8192
    ),
    "mistral-7b": ModelConfig(
        name="Mistral",
        size="7B",
        model_id="mistralai/Mistral-7B-Instruct-v0.3",
        max_length=8192
    ),
}

# Document type templates
DOCUMENT_TYPES = {
    "chronicle": "Historical record documenting events over time",
    "diary": "Personal account from a character's perspective",
    "letter": "Correspondence between characters",
    "law": "Legal document or decree",
    "treaty": "Agreement between factions or nations",
    "map": "Geographical description with locations and features",
    "inventory": "List of items, resources, or people",
    "report": "Official account of events or investigations",
    "song": "Cultural artifact with lyrics or poetry",
    "recipe": "Instructions for creating something",
    "manual": "Technical guide or instruction document",
    "newspaper": "News article or public announcement",
}

class ConfigManager:
    """Manages configuration loading and access."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or (Path(__file__).parent.parent / "config.yaml")
        self._config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self):
        """Load configuration from YAML file if it exists."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self._config = yaml.safe_load(f) or {}

    def save_config(self):
        """Save current configuration to YAML file."""
        with open(self.config_path, 'w') as f:
            yaml.dump(self._config, f, default_flow_style=False)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """Set configuration value."""
        keys = key.split('.')
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

# Global configuration instances
config_manager = ConfigManager()
system_config = SystemConfig()
training_config = TrainingConfig()
neo4j_config = Neo4jConfig()