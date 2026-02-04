"""CPU hardware simulator for validation testing."""

import random
import logging
from typing import Dict, Any


class CPUSimulator:
    """Simulates CPU telemetry and behavior."""
    
    def __init__(self, server_id: str):
        self.server_id = server_id
        self.logger = logging.getLogger(f"simulator.cpu.{server_id}")
        
        # Synthetic CPU config
        self.model = "Intel Xeon Platinum 8380"
        self.cores = 40
        self.base_freq_ghz = 2.3
        self.max_freq_ghz = 3.4
        
        # State
        self.utilization = 0.0
        self.current_freq_ghz = self.base_freq_ghz
        self.temperature_c = 45.0
        self.throttled = False
        
        self.failure_injected = None
    
    def get_status(self) -> Dict[str, Any]:
        """Get current CPU state and telemetry."""
        # Simulate some variance
        temp_noise = random.uniform(-2.0, 2.0)
        util_noise = random.uniform(-0.05, 0.05)
        
        current_temp = self.temperature_c + temp_noise
        current_util = max(0.0, min(1.0, self.utilization + util_noise))
        
        return {
            'model': self.model,
            'cores': self.cores,
            'frequency_ghz': self.current_freq_ghz,
            'utilization': round(current_util, 3),
            'temperature_c': round(current_temp, 1),
            'throttled': self.throttled
        }
    
    def stress(self, duration_sec: int) -> None:
        """Simulate CPU stress workload."""
        self.logger.info(f"CPU stress: {duration_sec}s")
        self.utilization = 0.95
        self.current_freq_ghz = self.max_freq_ghz
        self.temperature_c = 75.0  # Elevated under load
    
    def inject_failure(self, failure_type: str, **params) -> None:
        """Inject controlled CPU failure."""
        self.failure_injected = failure_type
        
        if failure_type == 'thermal_throttle':
            self.throttled = True
            self.temperature_c = params.get('temp_c', 95.0)
            self.current_freq_ghz = self.base_freq_ghz * 0.6  # Throttled
            self.logger.warning(f"Injected thermal throttle: {self.temperature_c}°C")
        
        elif failure_type == 'low_utilization':
            self.utilization = params.get('utilization', 0.3)
            self.logger.warning(f"Injected low utilization: {self.utilization}")
    
    def reset(self) -> None:
        """Reset CPU to nominal state."""
        self.utilization = 0.0
        self.current_freq_ghz = self.base_freq_ghz
        self.temperature_c = 45.0
        self.throttled = False
        self.failure_injected = None
