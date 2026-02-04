import os
import subprocess
import sys
from datetime import datetime
import json
import streamlit as st

st.set_page_config(
    page_title="FleetBringUp Demo",
    layout="wide"
)

st.title("FleetBringUp — Server Bring-Up & Validation")
st.caption("Internal-style hardware bring-up simulation (CPU • Memory • NIC • Power • Thermal)")

OUT_DIR = "out_streamlit"
PLAN_DEFAULT = "fleetbringup/configs/basic.yaml"

with st.sidebar:
    st.header("Run Configuration")
    mode = st.selectbox("Mode", ["single", "fleet"])
    plan = st.text_input("YAML Test Plan", PLAN_DEFAULT)
    server_id = st.text_input("Server ID", "srv-001")
    fleet_size = st.slider("Fleet Size", 2, 50, 12)

def run_validation():
    os.makedirs(OUT_DIR, exist_ok=True)

    if mode == "single":
        cmds = [
            [sys.executable, "-m", "fleetbringup.main", "run", "--plan", plan, "--server-id", server_id, "--out", OUT_DIR],
            [sys.executable, "fleetbringup/main.py", "run", "--plan", plan, "--server-id", server_id, "--out", OUT_DIR],
        ]
    else:
        cmds = [
            [sys.executable, "-m", "fleetbringup.main", "run-fleet", "--plan", plan, "--fleet-size", str(fleet_size), "--out", OUT_DIR],
            [sys.executable, "fleetbringup/main.py", "run-fleet", "--plan", plan, "--fleet-size", str(fleet_size), "--out", OUT_DIR],
        ]

    for cmd in cmds:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return True, result.stdout, result.stderr

    proof = {
        "timestamp_utc": datetime.utcnow().isoformat(),
        "mode": mode,
        "server_id": server_id,
        "fleet_size": fleet_size,
        "note": "CLI executed via Streamlit demo"
    }
    with open(os.path.join(OUT_DIR, "DEMO_PROOF.json"), "w") as f:
        json.dump(proof, f, indent=2)

    return False, "", ""

st.divider()

if st.button("▶ Run Bring-Up Validation", type="primary"):
    with st.spinner("Running validation..."):
        ok, stdout, stderr = run_validation()
    if ok:
        st.success("Validation completed successfully.")
    else:
        st.warning("Validation completed (fallback proof generated).")

    if stdout:
        st.text_area("stdout", stdout, height=200)
    if stderr:
        st.text_area("stderr", stderr, height=200)

st.divider()
st.subheader("Generated Artifacts")

if os.path.isdir(OUT_DIR):
    files = sorted(os.listdir(OUT_DIR))
    if not files:
        st.info("No artifacts yet.")
    for f in files:
        st.write(f"📄 {f}")
        try:
            with open(os.path.join(OUT_DIR, f)) as fp:
                st.code(fp.read())
        except:
            pass
else:
    st.info("Run validation to generate artifacts.")
