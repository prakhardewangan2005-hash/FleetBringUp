# FleetBringUp — Server Bring-Up & Validation Framework

![CI Demo](https://github.com/prakhardewangan2005-hash/FleetBringUp/actions/workflows/fleetbringup-demo.yml/badge.svg)

**Live Demo (Streamlit):** https://fleetbringup-k9m6w5yyv3sgubkbdu755u.streamlit.app/ 
**One-Click CI Demo:** Actions → *FleetBringUp — Demo Validation Run* → Run workflow → Download artifact `fleetbringup-output`

---

## Overview

FleetBringUp is an internal-style hardware bring-up and system validation framework designed to emulate data-center lab workflows used during server lifecycle testing.

The tool focuses on automated validation of CPU, memory, network, power, and thermal subsystems, supports controlled failure injection, and produces artifact-based diagnostics for auditability and triage. It is built to mirror how large-scale infrastructure teams validate and debug hardware at fleet scale.

---

## Key Capabilities

- **Automated Bring-Up Validation**
  - CPU, memory, NIC, power, and thermal subsystem checks
  - Config-driven validation via YAML test plans
  - Single-server and fleet execution modes

- **Failure Injection (Exclusive)**
  - Thermal runaway / overheat simulation
  - ECC corrected-error storm simulation
  - Network packet-loss degradation
  - Adjustable severity per failure mode

- **Subsystem Pass/Fail Gating**
  - Deterministic health scoring per subsystem
  - PASS / WARN / FAIL classification
  - Clear failure attribution and triage hints

- **Fleet-Scale Triage**
  - Subsystem health heatmap across servers
  - Top-offenders ranking by overall health score
  - Per-server drill-down for root-cause analysis

- **Artifact-Based Diagnostics**
  - Timestamped telemetry (CPU, memory, thermal, power)
  - Validation summaries and fleet snapshots
  - JSON / CSV artifacts generated on every run

- **Reproducible Execution**
  - Manual CI runs via GitHub Actions
  - Public interactive demo via Streamlit
  - No local setup required

---

## Architecture

fleetbringup/
├─ simulators/  # Hardware and sensor simulation (CPU, memory, NIC, power, thermal)
├─ tests/       # Validation logic per subsystem
├─ runner/      # Test orchestration and execution engine
├─ configs/     # YAML-based validation plans
├─ reports/     # Generated reports (CI / local)
└─ main.py      # CLI entrypoint for bring-up validation
app.py          # Streamlit-based validation console (live demo)
.github/workflows/  # CI demo workflow (GitHub Actions)

---

## Live Demo (Recommended)

The Streamlit demo provides an interactive validation console:

1. Open the **Live Demo** link
2. Select `single` or `fleet` mode
3. Toggle failure modes (OVERHEAT / ECC_ERROR / PACKET_LOSS)
4. Run validation
5. Inspect:
   - Subsystem pass/fail summary
   - CPU / Memory / Thermal / Power charts
   - Fleet health heatmap and top offenders
   - Generated artifacts (audit trail)

This demo executes the same validation logic used in CI and always produces timestamped artifacts.

---

## CI Demo (Reproducible)

A manual GitHub Actions workflow is included to demonstrate reproducible bring-up validation:

1. Go to **Actions**
2. Select **FleetBringUp — Demo Validation Run**
3. Click **Run workflow**
4. Choose `single` or `fleet`
5. Download artifact **`fleetbringup-output`**

Artifacts include validation summaries, telemetry, and proof of execution.

---

## Generated Artifacts

Each run produces auditable outputs such as:

- `telemetry_timeseries.json`
- `validation_summary.json`
- `fleet_snapshot.csv`
- `top_offenders.json`
- `DEMO_PROOF.json` (fallback proof when CLI args differ)

Artifacts are designed to mirror internal lab diagnostics rather than academic outputs.

---

## Design Principles

- Infrastructure-first (no academic abstractions)
- Deterministic, repeatable validation
- Failure-mode driven testing
- Fleet-scale observability and triage
- Artifact-based auditing

---

## Use Cases

- Server bring-up validation
- Hardware lifecycle testing
- Failure-mode analysis and triage
- Fleet health inspection
- Infrastructure tooling demonstrations

---

## Resume-Ready Summary

FleetBringUp demonstrates hands-on systems engineering through automated hardware validation, failure injection, and fleet-scale diagnostics, delivered via reproducible CI workflows and a public interactive dashboard.

---

## License

MIT
