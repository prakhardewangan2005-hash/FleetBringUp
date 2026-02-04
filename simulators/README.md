# Hardware Simulators

This directory contains synthetic hardware simulators for portable testing.

## Purpose

Simulators provide consistent, reproducible behavior for development and CI/CD without requiring physical hardware access.

## Interface Contract

All simulators implement a common interface:
```python
class HardwareComponent:
    def get_status(self) -> Dict[str, Any]:
        """Return current component state and telemetry."""
        pass
    
    def inject_failure(self, failure_type: str, **params) -> None:
        """Inject a controlled failure condition."""
        pass
    
    def reset(self) -> None:
        """Reset component to nominal state."""
        pass
```

## Extending to Real Hardware

To integrate real BMC/IPMI/Redfish APIs:

1. Implement the same interface contract
2. Replace synthetic data with actual sensor reads
3. Swap simulator import in test modules

Example (memory):
```python
# Current (simulator)
from simulators.memory_simulator import MemorySimulator
memory = MemorySimulator(server_id)

# Real hardware (via IPMI)
from hardware.memory_ipmi import MemoryIPMI
memory = MemoryIPMI(bmc_address, credentials)
```

## Simulator Modules

- `cpu_simulator.py`: CPU utilization, frequency, temperature
- `memory_simulator.py`: DIMM capacity, ECC errors, temperature
- `nic_simulator.py`: Link state, packet loss, bandwidth
- `thermal_power_simulator.py`: Thermal zones, power draw, fan RPM
