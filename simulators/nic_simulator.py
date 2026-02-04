"""Network interface simulator for validation testing."""

import random
import logging
from typing import Dict, Any


class NICSimulator:
    """Simulates NIC telemetry and link behavior."""
    
    def __init__(self, server_id: str):
        self.server_id = server_id
        self.logger = logging.getLogger(f"simulator.nic.{server_id}")
        
        # Synthetic NIC config
        self.interface_name = "eth0"
        self.link_speed_gbps = 25
        self.mac_address = f"00:1a:2b:{random.randint(0,255):02x}:{random.randint(0,255):02x}:{random.randint(0,255):02x}"
        
        # State
        self.link_up = True
        self.packet_loss_rate = 0.0
        self.current_bandwidth_gbps = 0.0
        
        self.failure_injected = None
    
    def get_status(self) -> Dict[str, Any]:
        """Get current NIC state and telemetry."""
        return {
            'interface': self.interface_name,
            'mac_address': self.mac_address,
            'link_speed_gbps': self.link_speed_gbps,
            'link_up': self.link_up,
            'packet_loss_rate': round(self.packet_loss_rate, 4),
            'current_bandwidth_gbps': round(self.current_bandwidth_gbps, 2)
        }
    
    def test_connectivity(self, target_bandwidth_gbps: float, duration_sec: int) -> bool:
        """Simulate network connectivity test (e.g., iperf3)."""
        self.logger.info(f"Testing connectivity: target {target_bandwidth_gbps} Gbps, duration {duration_sec}s")
        
        if not self.link_up:
            self.logger.error("Link down, connectivity test failed")
            return False
        
        # Simulate bandwidth test
        achieved_bandwidth = target_bandwidth_gbps * (1.0 - self.packet_loss_rate) * random.uniform(0.95, 1.0)
        self.current_bandwidth_gbps = achieved_bandwidth
        
        # Pass if within 90% of target
        success = achieved_bandwidth >= target_bandwidth_gbps * 0.9
        
        if not success:
            self.logger.error(f"Bandwidth test failed: {achieved_bandwidth:.2f} < {target_bandwidth_gbps * 0.9:.2f} Gbps")
        
        return success
    
    def inject_failure(self, failure_type: str, **params) -> None:
        """Inject controlled NIC failure."""
        self.failure_injected = failure_type
        
        if failure_type == 'link_down':
            self.link_up = False
            self.logger.warning("Injected link down")
        
        elif failure_type == 'packet_loss':
            loss_rate = params.get('loss_rate', 0.05)
            self.packet_loss_rate = loss_rate
            self.logger.warning(f"Injected packet loss: {loss_rate * 100:.2f}%")
        
        elif failure_type == 'degraded_bandwidth':
            degradation = params.get('degradation', 0.5)
            self.current_bandwidth_gbps = self.link_speed_gbps * degradation
            self.logger.warning(f"Injected bandwidth degradation: {self.current_bandwidth_gbps:.2f} Gbps")
    
    def reset(self) -> None:
        """Reset NIC to nominal state."""
        self.link_up = True
        self.packet_loss_rate = 0.0
        self.current_bandwidth_gbps = 0.0
        self.failure_injected = None
