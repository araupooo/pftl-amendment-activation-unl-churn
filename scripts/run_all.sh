#!/usr/bin/env bash
# run_all.sh — reproduce every table in this pack from a fresh copy.
#
# What it needs (already installed on a normal dev machine):
#   python3 (>= 3.9, standard library only) and curl (for the WebSocket
#   upgrade probe only). Network access to the public PFTL testnet
#   endpoints for the live run; none for the offline run.
#
# What it runs (in order, each log unedited into outputs/):
#   1. collect_snapshots.py — re-fetch the live VL, RPC state
#      (server_info / feature / ledger / ledger_entry Amendments +
#      NegativeUNL) and VHS state (validators / amendments vote+info /
#      reports); save pure-JSON timestamped snapshots under data/;
#      compare the live VL byte-for-byte with the vendored 2026-11-20
#      reference copy. Log: outputs/collect_snapshots.log
#   2. generate_tables.py  — recompute every table from the newest
#      snapshot set (thresholds, vote counts, activation timing,
#      UNL churn, NegativeUNL, reconciliation) and verify every set
#      equality the pack asserts. Log: outputs/generate_tables.log
#
# Offline mode: PFTL_OFFLINE=1 reuses the newest committed snapshot set
# instead of fetching (the collector still runs the VL comparison).
# The fresh-copy reproduction uses the live run; the offline run is the
# fallback when the network is unavailable.
#
# Exit status: 0 only if both scripts exit 0; otherwise non-zero.
# Prints a final ALL CHECKS PASSED / FAILED summary.
#
# NOTE: scripts are invoked via `python3` (not `./`) on purpose: files
# uploaded through the GitHub web UI lose their executable bit, so a fresh
# clone would fail with exit 126 if run_all.sh called ./script.py directly.
#
# NOTE on determinism: the generated tables under outputs/ are
# deterministic functions of the snapshot set — they contain no wall
# clock, no fetch time, and no live ledger sequence, so a re-run against
# the same snapshot set (PFTL_OFFLINE=1) produces byte-identical tables.
# A live re-run is identical on every stable value except the rolling
# 24h/30d agreement scores, which drift as the windows slide. The
# collector log is NOT byte-identical across runs by design: it records
# the collection timestamp, the live ledger sequence, and the new
# snapshot filenames. Reproduce the collector by its verdict line
# ("COLLECTOR VERDICT: PASS") and its VL-comparison line, not by its
# hash. See docs/fresh-clone-repro.md.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
mkdir -p outputs data
echo "=== run_all.sh ==="
echo "python3: $(python3 --version 2>&1)"
echo "scripts: 2 python3 checks (see outputs/)"

FAILED=""
for script in collect_snapshots generate_tables; do
    log="outputs/${script}.log"
    echo "--- running scripts/${script}.py -> ${log} ---"
    if [ "$script" = "collect_snapshots" ] && [ "${PFTL_OFFLINE:-0}" = "1" ]; then
        if python3 "scripts/${script}.py" --offline > "$log" 2>&1; then
            echo "PASS ${script} (offline, see ${log})"
        else
            echo "FAIL ${script} (see ${log})"
            FAILED="$FAILED $script"
        fi
    else
        if python3 "scripts/${script}.py" > "$log" 2>&1; then
            echo "PASS ${script} (see ${log})"
        else
            echo "FAIL ${script} (see ${log})"
            FAILED="$FAILED $script"
        fi
    fi
    echo
done

if [ -n "$FAILED" ]; then
    echo "RUN_ALL RESULT: FAILED — failing scripts:$FAILED"
    exit 1
fi
echo "RUN_ALL RESULT: ALL CHECKS PASSED (2/2 scripts)"
exit 0
