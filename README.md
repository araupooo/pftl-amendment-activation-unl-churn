# PFTL amendment activation and UNL churn

Live PFTL testnet validator governance, made inspectable: which
amendments are enabled and how they got there, what the activation rule
is, and how the validator set changed between the only two validator
snapshots available. Every substantive claim is labelled [FAKTA]
(verified, source + date), [ESTIMASI] (modelled/reported number), or
[ANALISIS] (interpretation), and every claim is mapped to a runnable
check and a pinned primary source in `docs/CLAIMS.md` and
`docs/claim-evidence-index.md`. The lifecycle is
`docs/amendment-lifecycle.md`, the activation analysis is
`docs/amendment-activation.md`, the churn analysis is `docs/unl-churn.md`,
and the reproduction procedure is `docs/fresh-clone-repro.md`.

## What the data shows

[FAKTA] The testnet knows 101 amendments: 64 enabled, 37 disabled. The
on-ledger `Amendments` entry lists exactly the same 64 IDs as the
`feature` enabled set. All 64 enabled amendments activated in a single
ledger, 86785, at 2026-02-09T14:31:12Z. No amendment is currently in
voting — the public `feature` response carries no `majority` field for any
amendment, and the VHS vote endpoint returns zero `voted`/`eta` items.

[FAKTA] The switch that selects the live majority rule,
`fixAmendmentMajorityCalc`, is itself enabled, so the live rule is the
post-fix 67% rule (strict greater-than), not the pre-fix 204/256 rule and
not upstream's 80%. With the live UNL of 25 validators, an activation
needs 17 yes-votes.

[FAKTA] The code inventory is 107 amendments (41 FEATURE + 50 FIX + 16
RETIRE) at postfiatd commit 24c5487. The 107 → 101 gap is exactly the six
amendments registered with `Supported::no` (unfinished code in this
build). VHS knows 103 amendments: the 101 live ones plus Batch (in code,
`Supported::no`) and OrchardPrivacy, which is in neither the code
inventory nor the live set.

[FAKTA] UNL churn 2026-07-17 → 2026-11-22: 20 → 25 (retained 12, exited
8, entered 13); observed validators 50 → 66. The live validator list is
byte-identical to the 2026-11-20 fetch, so there was zero churn in the
short leg. The NegativeUNL entry lists two disabled validators, both
still VL members; the second disable executed while this pack was being
built (between the 20:29 and 20:58 UTC fetches on 2026-11-21).

[FAKTA] The largest gap is stated plainly, not filled in: live
per-amendment vote counts are not obtainable from any public source tried
(the public `feature` method omits majority/veto data by design, and the
VHS vote endpoints serve activation records only). See NV1–NV15 in
`docs/claim-evidence-index.md`.

## How to run it

```sh
bash scripts/run_all.sh
```

Python 3.9+ standard library only, plus `curl` (for the WebSocket upgrade
probe only). The collector fetches the live VL, RPC state, and VHS state
and saves pure-JSON timestamped snapshots under `data/`; the generator
recomputes every table from the newest snapshot set and verifies every
set equality the pack asserts. Each script prints PASS/FAIL per step and
writes its unedited stdout to `outputs/<script>.log`. The runner exits
non-zero if any script fails and prints a final `ALL CHECKS PASSED` /
`FAILED` summary.

Offline mode (no network): `PFTL_OFFLINE=1 bash scripts/run_all.sh`
reuses the newest committed snapshot set; the collector still runs the VL
comparison and the generator still verifies every set equality.

Determinism note: the generated tables under `outputs/` are deterministic
functions of the snapshot set they are built from — they contain no wall
clock, no fetch time, and no live ledger sequence, so a re-run against
the same snapshot set (offline mode) produces byte-identical tables. A
live re-run fetches a new snapshot set: the tables are then identical on
every stable value, except the rolling 24h/30d agreement scores, which
drift as the windows slide (a data change, not a code nondeterminism —
most visibly for a newly disabled validator, whose 24h score falls as it
keeps missing validations). The collector log is not byte-identical
across runs by design (it records the collection time and live ledger
sequence); reproduce it by its verdict line and its VL-comparison line.
See `docs/fresh-clone-repro.md`.

## File map

```
README.md
SHA256SUMS
.github/workflows/verify.yml      # checksums first, then run_all.sh, then upload logs
scripts/
  collect_snapshots.py            # live fetch: VL, RPC, VHS, WS probe, Wayback check
  generate_tables.py              # all tables + set-equality verification
  run_all.sh                      # collector, then generator; exit 0 only if both pass
data/
  testnet_vl_20261120_reference.json   # vendored 2026-11-20 VL (VL comparison anchor)
  wayback_vhs_validators_20260717.json # single Wayback VHS capture, 2026-07-17
  amendment_inventory.csv              # 107 amendments, IDs recomputed by the generator
  explorer_amendments_20261121.html    # explorer SPA shell
  20261121T2*_*.json                  # snapshot sets (2026-11-21 20:58–21:14 UTC; newest used by the tables)
outputs/
  collect_snapshots.log           # unedited collector log
  generate_tables.log             # unedited generator log
  amendment_activation_thresholds.md/.csv
  amendment_vote_counts.md/.csv
  amendment_activation_timing.md/.csv
  unl_churn.md/.csv
  negative_unl.md/.csv
  reconciliation.md/.csv         # includes the not-verified list (NV1–NV15)
docs/
  SOURCES.md                      # precise citations, recorded before drafting claims
  amendment-lifecycle.md          # proposal → voting → flag ledger → majority → activation
  amendment-activation.md         # thresholds, vote counts, activation timing
  unl-churn.md                    # churn analysis + NegativeUNL
  claim-evidence-index.md         # C1–C32, E1–E3, NV1–NV15 with evidence per claim
  CLAIMS.md                       # fuller claim record, grouped by subject
  EXCERPTS.md          # verbatim claim index + not-verified list + key log lines
  fresh-clone-repro.md            # reproduction procedure + this run's record
repro/
  fresh-clone-run.log             # unedited stdout of the fresh-copy reproduction run
```

## Limitations

- Live data was collected in a single window, 2026-11-21 ~20:58–21:00 UTC,
  from one egress path. No second independent public RPC host was found to
  cross-check against, so all chain-state claims rest on the foundation's
  own nodes plus the foundation-run Validator History Service.
- Historical validator data is limited to one third-party archive capture
  (Wayback Machine, VHS validators endpoint, 2026-07-17); the validator-list
  URL itself has no archived copies.
- The public `feature` method deliberately omits amendment majority/veto
  information (admin-only), and neither the VHS vote endpoints nor the
  explorer publish live per-amendment vote counts — so the pack records
  enabled/disabled state and activation records, but cannot state live vote
  counts or majority status for pending amendments.
- Ledger-level facts outside the RPC node's retained range
  (`complete_ledgers` starting at 8200054 at collection time) are unavailable
  from that node and are estimated only where marked [ESTIMASI].
- The shipped testnet holding time (3 days) is config-level only: whether
  the live validators run it is not established from ledger data (NV5).
