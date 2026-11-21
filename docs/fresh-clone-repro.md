# Fresh-Clone Reproduction

Exact procedure for reproducing this pack's results from a fresh copy.
Network access to the public PFTL testnet endpoints is needed for the
live run; the offline run needs none.

## Prerequisites

- [FAKTA] python3 ≥ 3.9, standard library only; `curl` (for the WebSocket
  upgrade probe only); `sha256sum` (for the checksum step) and `bash`.
- A fresh copy of the pack: copy the whole pack directory to a new
  location (or clone the repository fresh) and work in the copy, so the
  committed `outputs/` are not overwritten in place.

## Commands

```sh
# 1. From the pack root, verify the pristine copy first.
#    This MUST run before the checks below: scripts/run_all.sh fetches a
#    new snapshot set under data/ and regenerates outputs/, so a checksum
#    check after the run would fail on the new files. The checksum step
#    proves checkout integrity; the run step proves the checks pass.
sha256sum -c SHA256SUMS

# 2. Run both scripts (captures unedited logs to outputs/).
bash scripts/run_all.sh

# 3. List the artifacts (the two unedited logs + six generated tables).
ls -la outputs/ data/
```

The CI workflow (`.github/workflows/verify.yml`) runs these steps in
exactly this order: checksum on the pristine checkout, then the run,
then upload of `outputs/` as the `run-logs` artifact.

## Expected outputs

- Step 1: every file reports `OK` (the checksum file lists every file
  in the pack except itself).
- Step 2: each script prints `PASS <name>` and the runner prints the
  final line:

  ```
  RUN_ALL RESULT: ALL CHECKS PASSED (2/2 scripts)
  ```

  The runner exits 0 only if both scripts exit 0; otherwise it prints
  `RUN_ALL RESULT: FAILED` and exits non-zero.
- Step 3: two logs in `outputs/` (`collect_snapshots.log`,
  `generate_tables.log`) and six generated tables
  (`amendment_activation_thresholds.md/.csv`,
  `amendment_vote_counts.md/.csv`,
  `amendment_activation_timing.md/.csv`, `unl_churn.md/.csv`,
  `negative_unl.md/.csv`, `reconciliation.md/.csv`).

Expected verdict lines (one per log):

```
COLLECTOR VERDICT: PASS -- 11 files fetched, 0 core failures
GENERATE VERDICT: PASS -- 6 tables written, all set checks passed
```

## Determinism and what is compared how

- [FAKTA] The six generated tables are deterministic functions of the
  snapshot set they are built from: they contain no wall clock, no fetch
  time, and no live ledger sequence. A re-run against the same snapshot
  set (offline mode, `PFTL_OFFLINE=1`) produces byte-identical tables
  and byte-identical logs. Compare them by hash against the committed
  values in `SHA256SUMS`.
- [FAKTA] A live re-run fetches a new snapshot set, so its tables are
  identical to the committed ones on every stable value, except the
  rolling 24h/30d agreement scores, which drift as the windows slide.
  That drift is a data change, not a code nondeterminism: a newly
  disabled validator's 24h agreement score falls as it keeps missing
  validations (ED372A9F… fell from 0.95438 to 0.91368 in ~12 minutes
  after its disable). When comparing a live re-run, expect differences
  only in the `agreement_24h` / `agreement_30d` fields of
  `unl_churn.csv` / `negative_unl.md` / `negative_unl.csv`; any other
  difference is a real state change to investigate.
- [FAKTA] The collector log is NOT byte-identical across live runs by
  design: it records the collection timestamp, the live ledger sequence,
  and the new snapshot filenames. Reproduce the collector by its verdict
  line (`COLLECTOR VERDICT: PASS`), its VL-comparison line
  (`VL-COMPARE: IDENTICAL`), and its per-fetch counts — not by its hash.
- [FAKTA] The data files a fresh live run writes carry a new timestamp
  prefix and a new live ledger sequence, so their hashes differ from the
  committed set by design. What must match is their content on every
  stable tabled value: VL SHA-256 `5d4f5a18…df59e7`, 101/64/37
  amendments, 64 activation records at ledger 86785, 66 VHS validators
  with 25 `unl: "rpc"`, and the NegativeUNL entries (which can
  legitimately gain entries over time — see the note in
  `outputs/negative_unl.md`).
- Offline mode: `PFTL_OFFLINE=1 bash scripts/run_all.sh` reuses the
  newest committed snapshot set instead of fetching. The collector still
  runs the VL comparison and the generator still verifies every set
  equality. The byte-identical reproduction check below uses the offline
  run; the live run is also performed, and is checked on verdicts and
  stable values.

## Expected SHA-256 of each committed generated table

[FAKTA] These are the committed values from `SHA256SUMS` (snapshot set
`20261121T211420Z`). Every table below must match byte-for-byte after a
fresh run against unchanged state.

```
0611b71dd401a4d0aa095d6f2f21ee4531eeb8c582e89b7d3e23662339983547  outputs/amendment_activation_thresholds.csv
32dfef6ddc8f4c18f99b78bdb5f759233281e5d57553405ac67c6167cd584cc8  outputs/amendment_activation_thresholds.md
1274cecf20a45ecf0de9b0fd1f1e3905ea35562a0bf6e76ab7cc4256a62d2058  outputs/amendment_activation_timing.csv
c8ee3eaf163b6851518e58d588ad2a8fc82dd4f59670d192fe005ce0136db077  outputs/amendment_activation_timing.md
652120833ea2387603a6a4aed74093815aa94c50fe3fd32c22b0797ccbc90cff  outputs/amendment_vote_counts.csv
431d278b65b9396c61764c263c6d0484ba06c7c110e3d2b7a6de2b8b10a5bc65  outputs/amendment_vote_counts.md
4a0556bc41c30546c797cd4279aed234ab26bfc09efcff19f5c7433454d04a1e  outputs/negative_unl.csv
2d5c4c48059b3d05f9394d05744de5b91a20ba1dc4519ad7aa9e01b752272dd4  outputs/negative_unl.md
0adda74ec4cb7e9c4492c52abe4e335b4184d6cd6f086a37e70b7d719704f51f  outputs/reconciliation.csv
830bb945c2f69501b130978c67140f950cf84fa75e800161ee6b8a34ff1e3597  outputs/reconciliation.md
1f97f460c0c0f29f051f22400775c30ed0400bf5a7a4a64d9c6636dff0a7d0a3  outputs/unl_churn.csv
5fac0b58e80a941811385d88d3f17f9a15cac5e5752aefb155039f9c80d671b6  outputs/unl_churn.md
```

## If a check fails

- A failure in `generate_tables.py` is a real regression: the set
  equalities it checks (Amendments entry == enabled set, VL keys ==
  VHS `unl: "rpc"` keys, churn arithmetic) must hold on any honest
  snapshot set. Report the failing log verbatim.
- A `COLLECTOR VERDICT: FAIL` names the failed fetch. Re-run once (the
  public endpoints occasionally time out through an egress proxy); if a
  fetch still fails, the log shows exactly which endpoint and error.
- A table hash mismatch after a fresh run means the live state changed
  (e.g. a new amendment enabled, a new NegativeUNL entry, VL churn).
  That is a finding, not flakiness: read the new collector log, note what
  changed, and do not "fix" it by editing a committed table or
  `SHA256SUMS` by hand.
- Do not "fix" a failing reproduction by editing a committed log or by
  editing `SHA256SUMS` by hand; report the failing log verbatim.

## This run

Record of the fresh-copy reproduction run for this copy of the pack
(22 Nov 2026, ~04:20 WIB / 21 Nov 2026 ~21:20 UTC):

- Method: `cp -r pack /tmp/pftl-gov-fresh-live` and `/tmp/pftl-gov-fresh`,
  `rm -rf outputs` in each copy. Live copy: `bash scripts/run_all.sh`
  (live fetch). Offline copy: `PFTL_OFFLINE=1 bash scripts/run_all.sh`
  (reuse the newest committed snapshot set `20261121T211420Z`). Python 3.12.3.
- Result: **ALL CHECKS PASSED (2/2 scripts)**, exit 0, in both copies
  (live runtime 25 s, offline runtime <1 s).
  Full run stdout for both copies is in `repro/fresh-clone-run.log`
  (SHA-256 `dbd60d88e0c7ee42e8635ba8b84a3baa91028cee4f9619281c75b996bf54d3db`).
- Comparison against the committed `outputs/`: the live copy produced all
  12 generated tables byte-identical (no differing fields at all in this
  run, including the agreement scores); the offline copy produced all 12
  generated tables plus `generate_tables.log` byte-identical. The offline
  copy's `collect_snapshots.log` differs from the committed (live)
  collector log only in the mode lines — it records `offline reuse of
  snapshot set 20261121T211420Z` instead of a live fetch — and its
  VL-comparison line is `VL-COMPARE: IDENTICAL`, matching the committed
  log. Both copies' logs carry `COLLECTOR VERDICT: PASS` and
  `GENERATE VERDICT: PASS`.
