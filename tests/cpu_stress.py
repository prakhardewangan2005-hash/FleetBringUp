"""CPU stress test module."""

import time
import logging
from typing import Dict, Any

from simulators.cpu_simulator import CPUSimulator


class CPUStressTest:
    """CPU stress and thermal stability validation."""
    
    def __init__(self, server_id: str, config: Dict[str, Any]):
        self.server_id = server_id
        self.config = config
        self.logger = logging.getLogger(f"test.cpu_stress.{server_id}")
        
        self.duration_sec = config.get('duration_sec', 60)
        self.failure_threshold = config.get('failure_threshold', 0.90)
        
        # Initialize hardware
        self.cpu = CPUSimulator(server_id)
    
    def execute(self) -> Dict[str, Any]:
        """Execute CPU stress test."""
        self.logger.info(f"CPU stress test: {self.duration_sec}s, threshold {self.failure_threshold}")
        
        # Inject failure if configured
        if self.config.get('inject_thermal_throttle', False):
            self.cpu.inject_failure('thermal_throttle', temp_c=95.0)
        
        # Run stress workload
        self.cpu.stress(self.duration_sec)
        time.sleep(0.5)  # Simulate test duration
        
        # Check results
        status = self.cpu.get_status()
        
        if status['throttled']:
            return {
                'name': 'cpu_stress',
                'status': 'FAIL',
                'failure_reason': f"CPU thermal throttle detected at {status['temperature_c']}°C",
                'subsystem': 'cpu',
                'recommended_action': 'Check thermal paste, verify fan operation'
            }
        
        if status['utilization'] < self.failure_threshold:
            return {
                'name': 'cpu_stress',
                'status': 'FAIL',
                'failure_reason': f"CPU utilization too low: {status['utilization']} < {self.failure_threshold}",
                'subsystem': 'cpu',
                'recommended_action': 'Check workload scheduler, verify CPU not in power-save mode'
            }
        
        return {
            'name': 'cpu_stress',
            'status': 'PASS',
            'cpu_utilization': status['utilization'],
            'cpu_temp_c': status['temperature_c']
        }
