"""Network connectivity validation test module."""

import time
import logging
from typing import Dict, Any

from simulators.nic_simulator import NICSimulator


class NetworkConnectivityTest:
    """Network link and bandwidth validation."""
    
    def __init__(self, server_id: str, config: Dict[str, Any]):
        self.server_id = server_id
        self.config = config
        self.logger = logging.getLogger(f"test.network_connectivity.{server_id}")
        
        self.target_bandwidth_gbps = config.get('target_bandwidth_gbps', 10.0)
        self.packet_loss_threshold = config.get('packet_loss_threshold', 0.01)
        self.test_duration_sec = config.get('test_duration_sec', 10)
        
        # Initialize hardware
        self.nic = NICSimulator(server_id)
    
    def execute(self) -> Dict[str, Any]:
        """Execute network connectivity test."""
        self.logger.info(f"Network test: target {self.target_bandwidth_gbps} Gbps")
        
        # Inject failure if configured
        if self.config.get('inject_link_down', False):
            self.nic.inject_failure('link_down')
        
        if self.config.get('inject_packet_loss', False):
            loss_rate = self.config.get('packet_loss_rate', 0.05)
            self.nic.inject_failure('packet_loss', loss_rate=loss_rate)
        
        # Check link status
        status = self.nic.get_status()
        
        if not status['link_up']:
            return {
                'name': 'network_connectivity',
                'status': 'FAIL',
                'failure_reason': f"Link down on {status['interface']}",
                'subsystem': 'network',
                'recommended_action': 'Check cable, verify switch port configuration'
            }
        
        # Run bandwidth test
        time.sleep(0.3)  # Simulate test duration
        success = self.nic.test_connectivity(self.target_bandwidth_gbps, self.test_duration_sec)
        
        status = self.nic.get_status()
        
        if not success:
            return {
                'name': 'network_connectivity',
                'status': 'FAIL',
                'failure_reason': f"Bandwidth test failed: {status['current_bandwidth_gbps']} Gbps < {self.target_bandwidth_gbps * 0.9} Gbps",
                'subsystem': 'network',
                'recommended_action': 'Check NIC firmware, verify switch configuration, inspect cable'
            }
        
        # Check packet loss
        if status['packet_loss_rate'] > self.packet_loss_threshold:
            return {
                'name': 'network_connectivity',
                'status': 'FAIL',
                'failure_reason': f"Excessive packet loss: {status['packet_loss_rate'] * 100:.2f}%",
                'subsystem': 'network',
                'recommended_action': 'Check cable integrity, inspect switch port'
            }
        
        return {
            'name': 'network_connectivity',
            'status': 'PASS',
            'bandwidth_gbps': status['current_bandwidth_gbps'],
            'packet_loss_rate': status['packet_loss_rate']
        }
