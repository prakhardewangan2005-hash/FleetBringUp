"""Memory subsystem simulator for validation testing."""

import random
import logging
from typing import Dict, Any, List


class MemorySimulator:
    """Simulates DIMM telemetry and ECC behavior."""
    
    def __init__(self, server_id: str):
        self.server_id = server_id
        self.logger = logging.getLogger(f"simulator.memory.{server_id}")
        
        # Synthetic memory config
        self.dimm_slots = 12
        self.dimm_capacity_gb = 32
        self.total_capacity_gb = self.dimm_slots * self.dimm_capacity_gb
        
        # ECC error tracking
        self.ecc_correctable_errors = {slot: 0 for slot in range(self.dimm_slots)}
        self.ecc_uncorrectable_errors = {slot: 0 for slot in range(self.dimm_slots)}
        
        # Temperature per DIMM
        self.dimm_temps_c = {slot: 55.0 for slot in range(self.dimm_slots)}
        
        self.failure_injected = None
    
    def get_status(self) -> Dict[str, Any]:
        """Get current memory state and telemetry."""
        return {
            'total_capacity_gb': self.total_capacity_gb,
            'dimm_slots': self.dimm_slots,
            'ecc_correctable_errors': dict(self.ecc_correctable_errors),
            'ecc_uncorrectable_errors': dict(self.ecc_uncorrectable_errors),
            'dimm_temperatures_c': {k: round(v, 1) for k, v in self.dimm_temps_c.items()}
        }
    
    def run_integrity_check(self) -> bool:
        """Simulate memory integrity test (e.g., memtest)."""
        self.logger.info("Running memory integrity check")
        
        # Check for injected failures
        if self.failure_injected == 'ecc_correctable':
            return False  # Fail due to ECC errors
        
        if self.failure_injected == 'ecc_uncorrectable':
            return False  # Critical failure
        
        # Nominal case: pass
        return True
    
    def inject_failure(self, failure_type: str, **params) -> None:
        """Inject controlled memory failure."""
        self.failure_injected = failure_type
        
        if failure_type == 'ecc_correctable':
            slot = params.get('slot', 3)
            error_count = params.get('error_count', 15)
            self.ecc_correctable_errors[slot] = error_count
            self.logger.warning(f"Injected ECC correctable errors: slot {slot}, count {error_count}")
        
        elif failure_type == 'ecc_uncorrectable':
            slot = params.get('slot', 7)
            self.ecc_uncorrectable_errors[slot] = 1
            self.logger.error(f"Injected ECC uncorrectable error: slot {slot}")
        
        elif failure_type == 'overheat':
            slot = params.get('slot', 5)
            temp = params.get('temp_c', 85.0)
            self.dimm_temps_c[slot] = temp
            self.logger.warning(f"Injected DIMM overheat: slot {slot}, {temp}°C")
    
    def reset(self) -> None:
        """Reset memory to nominal state."""
        self.ecc_correctable_errors = {slot: 0 for slot in range(self.dimm_slots)}
        self.ecc_uncorrectable_errors = {slot: 0 for slot in range(self.dimm_slots)}
        self.dimm_temps_c = {slot: 55.0 for slot in range(self.dimm_slots)}
        self.failure_injected = None
