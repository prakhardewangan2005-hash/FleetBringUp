"""Memory integrity validation test module."""

import time
import logging
from typing import Dict, Any

from simulators.memory_simulator import MemorySimulator


class MemoryIntegrityTest:
    """Memory integrity and ECC validation."""
    
    def __init__(self, server_id: str, config: Dict[str, Any]):
        self.server_id = server_id
        self.config = config
        self.logger = logging.getLogger(f"test.memory_integrity.{server_id}")
        
        self.passes = config.get('passes', 3)
        self.ecc_error_threshold = config.get('ecc_error_threshold', 10)
        
        # Initialize hardware
        self.memory = MemorySimulator(server_id)
    
    def execute(self) -> Dict[str, Any]:
        """Execute memory integrity test."""
        self.logger.info(f"Memory integrity test: {self.passes} passes")
        
        # Inject failure if configured
        if self.config.get('inject_ecc_error', False):
            slot = self.config.get('ecc_error_slot', 3)
            self.memory.inject_failure('ecc_correctable', slot=slot, error_count=15)
        
        # Run integrity check
        for pass_num in range(self.passes):
            self.logger.info(f"Memory test pass {pass_num + 1}/{self.passes}")
            time.sleep(0.2)  # Simulate test duration
            
            if not self.memory.run_integrity_check():
                return self._build_failure_result()
        
        # Check ECC error counts
        status = self.memory.get_status()
        
        for slot, count in status['ecc_correctable_errors'].items():
            if count > self.ecc_error_threshold:
                return {
                    'name': 'memory_integrity',
                    'status': 'FAIL',
                    'failure_reason': f"ECC correctable error detected on DIMM slot {slot}",
                    'subsystem': 'memory',
                    'recommended_action': f"Replace DIMM slot {slot}, rerun validation"
                }
        
        for slot, count in status['ecc_uncorrectable_errors'].items():
            if count > 0:
                return {
                    'name': 'memory_integrity',
                    'status': 'FAIL',
                    'failure_reason': f"ECC UNCORRECTABLE error on DIMM slot {slot}",
                    'subsystem': 'memory',
                    'recommended_action': f"CRITICAL: Replace DIMM slot {slot} immediately"
                }
        
        return {
            'name': 'memory_integrity',
            'status': 'PASS',
            'passes_completed': self.passes,
            'total_capacity_gb': status['total_capacity_gb']
        }
    
    def _build_failure_result(self) -> Dict[str, Any]:
        """Build failure result from memory status."""
        status = self.memory.get_status()
        
        # Find first slot with errors
        for slot, count in status['ecc_correctable_errors'].items():
            if count > 0:
                return {
                    'name': 'memory_integrity',
                    'status': 'FAIL',
                    'failure_reason': f"Memory integrity check failed: ECC errors on slot {slot}",
                    'subsystem': 'memory',
                    'recommended_action': f"Replace DIMM slot {slot}"
                }
        
        return {
            'name': 'memory_integrity',
            'status': 'FAIL',
            'failure_reason': "Memory integrity check failed",
            'subsystem': 'memory',
            'recommended_action': "Run extended memory diagnostics"
        }
