#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
from pathlib import Path
import shutil

# ---------------------------------------------------------------------
# Utility: detect model root dynamically using git
# ---------------------------------------------------------------------
def detect_model_root():
    try:
        root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], stderr=subprocess.DEVNULL
        ).decode().strip()
        return Path(root)
    except subprocess.CalledProcessError:
        # fallback if not a git repo
        return Path(__file__).resolve().parents[1]

MODEL_ROOT = detect_model_root()
VERIF_ROOT = MODEL_ROOT / "verif"
RTL_ROOT = MODEL_ROOT / "rtl"
TARGET_ROOT = MODEL_ROOT / "target"

# ---------------------------------------------------------------------
# Command runner with logging
# ---------------------------------------------------------------------
def run_cmd(cmd, log_path=None, verbose=False):
    """Run a shell command and optionally tee output to a log file."""
    if verbose:
        print(f"[CMD] {' '.join(cmd)}")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out_lines = []
    for line in proc.stdout:
        sys.stdout.write(line)
        out_lines.append(line)
    proc.wait()
    if log_path:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "w") as f:
            f.writelines(out_lines)
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")

# ---------------------------------------------------------------------
# Discover legal DUTs
# ---------------------------------------------------------------------
def get_legal_duts():
    """Legal DUTs are directory names under verif/."""
    return [p.name for p in VERIF_ROOT.glob("*") if p.is_dir()]

# ---------------------------------------------------------------------
# Build flow
# ---------------------------------------------------------------------
def build(args):
    legal_duts = get_legal_duts()
    if args.dut not in legal_duts:
        print(f"[ERROR] Invalid DUT '{args.dut}'. Legal DUTs: {', '.join(legal_duts) or '(none found)'}")
        sys.exit(1)

    target_dir = TARGET_ROOT / args.dut
    work_dir = target_dir / "work"
    log_dir = target_dir / "log"
    log_dir.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------------------
    # CLEAN
    # -----------------------------------------------------------------
    if args.clean:
        if target_dir.exists():
            print(f"[CLEAN] Removing {target_dir}")
            shutil.rmtree(target_dir)
        return

    # -----------------------------------------------------------------
    # HARDWARE BUILD
    # -----------------------------------------------------------------
    if args.hw:
        log_file = log_dir / "hw_build.log"
        run_cmd(["echo", f"[HW] Building hardware for {args.dut}"], log_file, args.verbose)

    # -----------------------------------------------------------------
    # SIMULATION FLOW
    # -----------------------------------------------------------------
    if args.sim:
        top_name = args.top or f"{args.dut}_tb"

        # Step 1: fresh work library under target/<dut>/work
        if work_dir.exists():
            shutil.rmtree(work_dir)
        run_cmd(["vlib", str(work_dir)], log_dir / "vlib.log", args.verbose)

        # Step 2: compile RTL files
        rtl_dir = RTL_ROOT / args.dut
        rtl_sources = list(rtl_dir.glob("*.sv"))
        if rtl_sources:
            rtl_log = log_dir / "rtl_compile.log"
            for src in rtl_sources:
                run_cmd(["vlog", str(src)], rtl_log, args.verbose)
        else:
            print(f"[WARN] No RTL files found under rtl/{args.dut}/")

        # Step 3: compile testbench
        tb_path = VERIF_ROOT / args.dut / f"{top_name}.sv"
        if not tb_path.exists():
            print(f"[ERROR] Testbench file not found: {tb_path}")
            sys.exit(1)
        vlog_cmd = ["vlog", str(tb_path)]
        run_cmd(vlog_cmd, log_dir / "compile.log", args.verbose)

        # Step 4: run simulation
        vsim_cmd = ["vsim", "-voptargs=+acc", f"work.{top_name}"]
        if not args.gui:
            vsim_cmd.insert(1, "-c")
            vsim_cmd += ["-do", "run -all; quit -f"]
        run_cmd(vsim_cmd, log_dir / "sim.log", args.verbose)

    print(f"[INFO] Logs saved under: {log_dir}")

# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Systematic build manager for FPGA / simulation flows.")
    parser.add_argument("-dut", required=True, help="Design under test (DUT) name under verif/*")
    parser.add_argument("-top", help="Top-level module name (default: <dut>_tb)")
    parser.add_argument("-cfg", help="Optional configuration file name")
    parser.add_argument("-hw", action="store_true", help="Run hardware build")
    parser.add_argument("-sim", action="store_true", help="Run simulation")
    parser.add_argument("-gui", action="store_true", help="Open simulation GUI (vsim)")
    parser.add_argument("-clean", action="store_true", help="Clean target directory for DUT")
    parser.add_argument("-verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()
    try:
        build(args)
    except RuntimeError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
