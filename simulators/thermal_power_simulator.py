"""Thermal and power subsystem simulator for validation testing."""

import random
import logging
from typing import Dict, Any


class ThermalPowerSimulator:
    """Simulates thermal zones, power draw, and fan control."""
    
    def __init__(self, server_id: str):
        self.server_id = server_id
        self.logger = logging.getLogger(f"simulator.thermal_power.{server_id}")
        
        # Thermal zones
        self.cpu_temp_c = 50.0
        self.dimm_temp_c = 55.0
        self.inlet_temp_c = 25.0
        self.exhaust_temp_c = 35.0
        
        # Power
        self.power_draw_w = 350.0
        self.max_power_w = 1200.0
        
        # Fans
        self.fan_rpm = 5000
        self.fan_max_rpm = 15000
        
        self.failure_injected = None
    
    def get_status(self) -> Dict[str, Any]:
        """Get current thermal and power telemetry."""
        # Add noise
        cpu_temp = self.cpu_temp_c + random.uniform(-1.0, 1.0)
        dimm_temp = self.dimm_temp_c + random.uniform(-1.0, 1.0)
        power = self.power_draw_w + random.uniform(-10.0, 10.0)
        
        return {
            'temperatures_c': {
                'cpu': round(cpu_temp, 1),
                'dimm': round(dimm_temp, 1),
                'inlet': round(self.inlet_temp_c, 1),
                'exhaust': round(self.exhaust_temp_c, 1)
            },
            'power_draw_w': round(power, 1),
            'max_power_w': self.max_power_w,
            'fan_rpm': self.fan_rpm,
            'fan_max_rpm': self.fan_max_rpm
        }
    
    def check_thermal_sanity(self, max_cpu_temp_c: float, max_dimm_temp_c: float) -> bool:
        """Validate thermal readings are within acceptable thresholds."""
        self.logger.info(f"Thermal sanity check: CPU < {max_cpu_temp_c}°C, DIMM < {max_dimm_temp_c}°C")
        
        status = self.get_status()
        temps = status['temperatures_c']
        
        if temps['cpu'] > max_cpu_temp_c:
            self.logger.error(f"CPU temp out of range: {temps['cpu']}°C > {max_cpu_temp_c}°C")
            return False
        
        if temps['dimm'] > max_dimm_temp_c:
            self.logger.error(f"DIMM temp out of range: {temps['dimm']}°C > {max_dimm_temp_c}°C")
            return False
        
        return True
    
    def check_power_sanity(self, expected_idle_w: float, tolerance: float = 0.2) -> bool:
        """Validate power draw is within expected range."""
        self.logger.info(f"Power sanity check: expected ~{expected_idle_w}W ± {tolerance*100}%")
        
        status = self.get_status()
        power = status['power_draw_w']
        
        lower_bound = expected_idle_w * (1 - tolerance)
        upper_bound = expected_idle_w * (1 + tolerance)
        
        if power < lower_bound or power > upper_bound:
            self.logger.error(f"Power draw out of range: {power}W not in [{lower_bound}, {upper_bound}]")
            return False
        
        return True
    
    def inject_failure(self, failure_type: str, **params) -> None:
        """Inject controlled thermal/power failure."""
        self.failure_injected = failure_type
        
        if failure_type == 'cpu_overheat':
            self.cpu_temp_c = params.get('temp_c', 95.0)
            self.logger.warning(f"Injected CPU overheat: {self.cpu_temp_c}°C")
        
        elif failure_type == 'dimm_overheat':
            self.dimm_temp_c = params.get('temp_c', 85.0)
            self.logger.warning(f"Injected DIMM overheat: {self.dimm_temp_c}°C")
        
        elif failure_type == 'power_spike':
            self.power_draw_w = params.get('power_w', 900.0)
            self.logger.warning(f"Injected power spike: {self.power_draw_w}W")
        
        elif failure_type == 'fan_failure':
            self.fan_rpm = 0
            self.logger.error("Injected fan failure")
    
    def reset(self) -> None:
        """Reset to nominal state."""
        self.cpu_temp_c = 50.0
        self.dimm_temp_c = 55.0
        self.inlet_temp_c = 25.0
        self.exhaust_temp_c = 35.0
        self.power_draw_w = 350.0
        self.fan_rpm = 5000
        self.failure_injected = None
