"""Core test orchestration and execution logic."""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from tests.cpu_stress import CPUStressTest
from tests.memory_integrity import MemoryIntegrityTest
from tests.network_connectivity import NetworkConnectivityTest
from tests.thermal_power_sanity import ThermalPowerSanityTest


class TestOrchestrator:
    """Orchestrates execution of validation test suite."""
    
    TEST_REGISTRY = {
        'cpu_stress': CPUStressTest,
        'memory_integrity': MemoryIntegrityTest,
        'network_connectivity': NetworkConnectivityTest,
        'thermal_power_sanity': ThermalPowerSanityTest,
    }
    
    def __init__(self, server_id: str, test_plan: Dict[str, Any], output_dir: Path):
        self.server_id = server_id
        self.test_plan = test_plan
        self.output_dir = output_dir
        self.logger = logging.getLogger(f"orchestrator.{server_id}")
        
        self.results = {
            'server_id': server_id,
            'timestamp': datetime.now().isoformat(),
            'test_plan': test_plan['test_plan']['name'],
            'tests': [],
            'overall_status': 'PASS'
        }
    
    def run(self) -> Dict[str, Any]:
        """Execute all tests in the test plan."""
        self.logger.info(f"Executing test plan: {self.test_plan['test_plan']['name']}")
        
        tests = self.test_plan['test_plan']['tests']
        
        for test_config in tests:
            test_name = test_config['name']
            self.logger.info(f"Running test: {test_name}")
            
            try:
                result = self._run_test(test_name, test_config)
                self.results['tests'].append(result)
                
                if result['status'] == 'FAIL':
                    self.results['overall_status'] = 'FAIL'
                    self._build_failure_summary(result)
                    
            except Exception as e:
                self.logger.exception(f"Test {test_name} raised exception: {e}")
                self.results['tests'].append({
                    'name': test_name,
                    'status': 'ERROR',
                    'error': str(e)
                })
                self.results['overall_status'] = 'FAIL'
        
        self._write_results()
        return self.results
    
    def _run_test(self, test_name: str, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single test."""
        if test_name not in self.TEST_REGISTRY:
            raise ValueError(f"Unknown test: {test_name}")
        
        test_class = self.TEST_REGISTRY[test_name]
        test_instance = test_class(self.server_id, test_config)
        
        start_time = datetime.now()
        result = test_instance.execute()
        duration = (datetime.now() - start_time).total_seconds()
        
        result['duration_sec'] = round(duration, 2)
        return result
    
    def _build_failure_summary(self, failed_test: Dict[str, Any]) -> None:
        """Generate failure summary for triage."""
        self.results['failure_summary'] = {
            'subsystem': failed_test.get('subsystem', 'unknown'),
            'root_cause': failed_test.get('failure_reason', 'unknown'),
            'action': failed_test.get('recommended_action', 'Manual investigation required')
        }
    
    def _write_results(self) -> None:
        """Write results to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"{self.server_id}_{timestamp}_results.json"
        
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self.logger.info(f"Results written to {output_file}")
