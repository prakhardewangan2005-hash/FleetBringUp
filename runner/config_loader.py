"""YAML test plan configuration loader."""

import yaml
from pathlib import Path
from typing import Dict, Any


class ConfigLoader:
    """Loads and validates test plan configurations from YAML."""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
    
    def load(self) -> Dict[str, Any]:
        """Load test plan from YAML file."""
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self._validate(config)
        return config
    
    def _validate(self, config: Dict[str, Any]) -> None:
        """Validate config structure."""
        if 'test_plan' not in config:
            raise ValueError("Config must contain 'test_plan' key")
        
        test_plan = config['test_plan']
        
        if 'name' not in test_plan:
            raise ValueError("test_plan must contain 'name'")
        
        if 'tests' not in test_plan or not isinstance(test_plan['tests'], list):
            raise ValueError("test_plan must contain 'tests' list")
        
        for test in test_plan['tests']:
            if 'name' not in test:
                raise ValueError("Each test must have a 'name' field")
