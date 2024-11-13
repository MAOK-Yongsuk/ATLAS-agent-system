from typing import Dict
import os
from dotenv import load_dotenv
import yaml
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def load_config() -> Dict:
    try:
        # Load environment variables
        load_dotenv()
        
        # Get config file path
        config_path = Path(__file__).parent.parent.parent/ "studi-pal-dev" / "config" / "config.yaml"
        
        # Ensure config file exists
        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found at {config_path}. "
                "Please ensure config.yaml exists in the config directory."
            )
        
        # Load YAML config
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        # Load environment-specific configuration
        env_config = {
            "llm": {
                "nemotron_70b_key": os.getenv("NEMOTRON_70B_KEY"),
                "nemotron_340b_key": os.getenv("NEMOTRON_340B_KEY"),
                "temperature": float(os.getenv("LLM_TEMPERATURE", "0.7")),
                "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "2048")),
            },
            "pinecone": {
                "api_key": os.getenv("PINECONE_API_KEY"),
            },
            "neo4j": {
                "uri": os.getenv("NEO4J_URI"),
                "user": os.getenv("NEO4J_USERNAME"),
                "password": os.getenv("NEO4J_PASSWORD"),
            },
            "embeddings": {
                "model_name": os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5"),
                "device": os.getenv("EMBEDDING_DEVICE", "cuda"),
            },
            "reranker": {
                "model_name": os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2"),
                "batch_size": int(os.getenv("RERANKER_BATCH_SIZE", "32")),
            }
        }
        
        # Deep merge configurations
        _deep_merge(config, env_config)
        
        # Validate configuration
        _validate_config(config)
        
        return config
        
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        raise

def _deep_merge(base: Dict, override: Dict) -> None:
    """Deep merge two dictionaries"""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value

def _validate_config(config: Dict) -> None:
    """Validate required configuration settings"""
    required_keys = [
        ('llm', 'nemotron_70b_key'),
        ('pinecone', 'api_key'),
        ('neo4j', 'uri'),
        ('neo4j', 'user'),
        ('neo4j', 'password')
    ]
    
    for section, key in required_keys:
        if not config.get(section, {}).get(key):
            raise ValueError(f"Missing required configuration: {section}.{key}")