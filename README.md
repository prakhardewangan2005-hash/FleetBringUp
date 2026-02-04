# FleetBringUp

Automated server bring-up and validation framework for data center hardware lifecycle testing.

## Overview

FleetBringUp automates system-level hardware validation during server bring-up, post-repair verification, and periodic fleet health checks. Built for infrastructure labs running thousands of validation cycles per week.

**Core capabilities:**
- Automated bring-up test suites (CPU, memory, network, thermal, power)
- Failure injection and detection for hardware subsystem regression testing
- Config-driven test orchestration for reproducible validation workflows
- Structured failure reports for cross-functional triage (hardware, kernel, firmware teams)

## Why This Tool Exists

In large-scale data center operations, server bring-up and validation happens continuously:
- New hardware deployments (ODM qualification, rack-level bring-up)
- Post-repair validation (RMA returns, component swaps)
- Fleet health audits (detection of silent data corruption, thermal drift)

Manual validation doesn't scale. FleetBringUp provides:
- **Repeatability**: Consistent test execution across lab environments
- **Speed**: Parallel test execution, ~3-5 min per server
- **Traceability**: Structured logs for failure root cause analysis
- **Extensibility**: Modular design for integrating real BMC/IPMI/Redfish APIs

## Architecture
```
┌─────────────┐
│   CLI       │  ← main.py entry point
└──────┬──────┘
       │
┌──────▼───────────────────────────┐
│  Test Runner (runner/)           │
│  - Orchestrates test execution   │
│  - Loads YAML test plans         │
│  - Manages failure state         │
└──────┬───────────────────────────┘
       │
┌──────▼───────────────────────────┐
│  Hardware Simulators (simulators/)│
│  - CPU, Memory, NIC, Thermal     │
│  - Synthetic telemetry           │
│  - Controlled failure injection  │
└──────┬───────────────────────────┘
       │
┌──────▼───────────────────────────┐
│  Test Modules (tests/)           │
│  - cpu_stress                    │
│  - memory_integrity              │
│  - network_connectivity          │
│  - thermal_power_sanity          │
└──────────────────────────────────┘
```

## Installation
```bash
cd fleetbringup
pip install -r requirements.txt
```

## Usage

### Single Server Validation
```bash
python main.py validate --server-id svr-12345 --config configs/default_bringup.yaml
```

### Fleet Validation (Batch Mode)
```bash
python main.py validate-fleet --server-list configs/fleet_batch_01.txt --config configs/default_bringup.yaml
```

### Custom Test Plan
```bash
python main.py validate --server-id svr-12345 --config configs/stress_thermal.yaml
```

### Failure Injection (Lab Testing)
```bash
python main.py validate --server-id svr-12345 --config configs/inject_ecc_error.yaml
```

## Configuration

Test plans are defined in YAML. Example: `configs/default_bringup.yaml`
```yaml
test_plan:
  name: "Standard Bring-Up Validation"
  tests:
    - name: cpu_stress
      duration_sec: 60
      failure_threshold: 0.95
    - name: memory_integrity
      passes: 3
      inject_ecc_error: false
    - name: network_connectivity
      target_bandwidth_gbps: 10
      packet_loss_threshold: 0.01
    - name: thermal_power_sanity
      max_cpu_temp_c: 85
      max_dimm_temp_c: 75
```

## Output

Results are written to `reports/`:
```
reports/
  svr-12345_20260204_143022_results.json
  svr-12345_20260204_143022.log
```

Example report:
```json
{
  "server_id": "svr-12345",
  "timestamp": "2026-02-04T14:30:22Z",
  "test_plan": "default_bringup.yaml",
  "overall_status": "FAIL",
  "tests": [
    {
      "name": "cpu_stress",
      "status": "PASS",
      "duration_sec": 62.3
    },
    {
      "name": "memory_integrity",
      "status": "FAIL",
      "failure_reason": "ECC correctable error detected on DIMM slot 3",
      "subsystem": "memory"
    }
  ],
  "failure_summary": {
    "subsystem": "memory",
    "root_cause": "ECC correctable error",
    "action": "Replace DIMM slot 3, rerun validation"
  }
}
```

## Extending to Real Hardware

Current implementation uses simulators for portability. To integrate real hardware:

1. **BMC/IPMI Integration**: Replace `simulators/` with Redfish API calls
2. **Out-of-Band Management**: Use `pyghmi` or `sushy` for sensor reads
3. **Network Testing**: Replace synthetic NIC simulator with `iperf3` calls
4. **Thermal Telemetry**: Read `/sys/class/hwmon/` or parse `ipmitool sensor`

See `simulators/README.md` for interface contracts.

## Collaboration Model

This tool sits at the intersection of:
- **Hardware Engineering**: Validate ODM server specs, detect component defects
- **Kernel/Firmware**: Reproduce MCE storms, thermal throttling edge cases
- **Power Team**: Correlate power draw anomalies with workload profiles
- **SRE/Production**: Qualify servers before cluster deployment

Typical workflow:
1. Hardware team ships new server SKU to lab
2. FleetBringUp runs bring-up suite (30-50 servers in parallel)
3. Failures triaged: hardware defect vs. firmware bug vs. config issue
4. Logs shared with ODM vendor or escalated to kernel team

## Development
```bash
# Run single test module (dev mode)
python -m tests.cpu_stress

# Run all unit tests
python -m pytest tests/

# Format
black fleetbringup/
```

## License

Internal use only.
