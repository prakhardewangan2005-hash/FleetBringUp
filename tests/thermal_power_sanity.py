"""Thermal and power sanity validation test module."""

import time
import logging
from typing import Dict, Any

from simulators.thermal_power_simulator import ThermalPowerSimulator


class ThermalPowerSanityTest:
    """Thermal and power telemetry sanity checks."""
    
    def __init__(self, server_id: str, config: Dict[str, Any]):
        self.server_id = server_id
        self.config = config
        self.logger = logging.getLogger(f"test.thermal_power.{server_id}")
        
        self.max_cpu_temp_c = config.get('max_cpu_temp_c', 85.0)
        self.max_dimm_temp_c = config.get('max_dimm_temp_c', 75.0)
        self.expected_idle_power_w = config.get('expected_idle_power_w', 350.0)
        self.power_tolerance = config.get('power_tolerance', 0.3)
        
        # Initialize hardware
        self.thermal_power = ThermalPowerSimulator(server_id)
    
    def execute(self) -> Dict[str, Any]:
        """Execute thermal and power sanity tests."""
        self.logger.info("Thermal and power sanity check")
        
        # Inject failure if configured
        if self.config.get('inject_cpu_overheat', False):
            self.thermal_power.inject_failure('cpu_overheat', temp_c=92.0)
        
        if self.config.get('inject_dimm_overheat', False):
            self.thermal_power.inject_failure('dimm_overheat', temp_c=82.0)
        
        if self.config.get('inject_power_spike', False):
            self.thermal_power.inject_failure('power_spike', power_w=850.0)
        
        time.sleep(0.2)  # Simulate sensor read
        
        # Check thermal sanity
        thermal_ok = self.thermal_power.check_thermal_sanity(
            self.max_cpu_temp_c,
            self.max_dimm_temp_c
        )
        
        if not thermal_ok:
            status = self.thermal_power.get_status()
            temps = status['temperatures_c']
            
            if temps['cpu'] > self.max_cpu_temp_c:
                return {
                    'name': 'thermal_power_sanity',
                    'status': 'FAIL',
                    'failure_reason': f"CPU temperature out of range: {temps['cpu']}°C > {self.max_cpu_temp_c}°C",
                    'subsystem': 'thermal',
                    'recommended_action': 'Check CPU heatsink, verify fan operation, inspect thermal paste'
                }
            
            if temps['dimm'] > self.max_dimm_temp_c:
                return {
                    'name': 'thermal_power_sanity',
                    'status': 'FAIL',
                    'failure_reason': f"DIMM temperature out of range: {temps['dimm']}°C > {self.max_dimm_temp_c}°C",
                    'subsystem': 'thermal',
                    'recommended_action': 'Check airflow, verify fan operation'
                }
        
        # Check power sanity
        power_ok = self.thermal_power.check_power_sanity(
            self.expected_idle_power_w,
            self.power_tolerance
        )
        
        if not power_ok:
            status = self.thermal_power.get_status()
            return {
                'name': 'thermal_power_sanity',
                'status': 'FAIL',
                'failure_reason': f"Power draw anomaly: {status['power_draw_w']}W (expected ~{self.expected_idle_power_w}W)",
                'subsystem': 'power',
                'recommended_action': 'Check PSU health, verify no rogue processes, inspect power cabling'
            }
        
        status = self.thermal_power.get_status()
        return {
            'name': 'thermal_power_sanity',
            'status': 'PASS',
            'cpu_temp_c': status['temperatures_c']['cpu'],
            'dimm_temp_c': status['temperatures_c']['dimm'],
            'power_draw_w': status['power_draw_w']
        }
