# Claim–Evidence Index — PFTL amendment activation and UNL churn

Each numbered claim (C1–C32 verified; NV1–NV15 not verified) with the exact
evidence behind it: the script, the committed log file, and the exact PASS
line or figure — or the pinned source entry. Labels: [FAKTA] verified with
source + date, [ESTIMASI] modelled/reported number, [ANALISIS]
interpretation. Status is `verified` or `not verified`; nothing in the
NV section is presented as verified anywhere in this pack.

Log hashes are the committed values in `SHA256SUMS`. The generated tables
are byte-identical across runs against unchanged state; the collector log
is compared on its verdict and VL-comparison lines, not its hash (it
records the collection time and live ledger sequence — see
`docs/fresh-clone-repro.md`).

## A — Live endpoints and validator list

| # | Claim | Label | Evidence | Status |
|---|---|---|---|---|
| C1 | Published VL fetched live, HTTP 200, 14,781 bytes, SHA-256 `5d4f5a18a18fead4105e5dc00cf7e11a71b9be4bc140357d1b4ea12116df59e7`, sequence 30, 25 validators, publisher `ED3F1E0D…09E2`, effective 2026-11-17T20:10:08Z, expiration 2028-03-31T16:14:53Z | [FAKTA] | `scripts/collect_snapshots.py` → `outputs/collect_snapshots.log`: `FETCH testnet_vl: HTTP 200, 14781 bytes, SHA-256 5d4f5a18…df59e7`, `sequence 30, validators 25` | verified |
| C2 | Live VL byte-identical to the vendored 2026-11-20 reference copy; zero UNL churn 2026-11-20 → 2026-11-22 | [FAKTA] | `outputs/collect_snapshots.log`: `VL-COMPARE: IDENTICAL` (both SHA-256 `5d4f5a18…df59e7`) | verified |
| C3 | JSON-RPC `https://rpc.testnet.postfiat.org` works: build 1.0.9, network ID 2025, `server_state` "full", validated ledger 8251750, `validation_quorum` 16, peers 21 at collection | [FAKTA] | `outputs/collect_snapshots.log`: `FETCH rpc_server_info: … build 1.0.9, network_id 2025, validated ledger 8251750, validation_quorum 16, peers 21` | verified |
| C4 | WebSocket host `wss://ws.testnet.postfiat.org` answers an upgrade probe with HTTP 101; the RPC host itself rejects WebSocket upgrades with 401 "Invalid protocol." | [FAKTA] | `outputs/collect_snapshots.log`: `PROBE websocket ws.testnet.postfiat.org: HTTP 101`; 401 probe 2026-11-21 20:25:41 UTC, `docs/SOURCES.md §1` | verified |
| C5 | VHS `https://vhs.testnet.postfiat.org` works: 66 validators observed, 25 with `unl: "rpc"`, 55 domain-verified, 0 revoked, 1 partial | [FAKTA] | `outputs/collect_snapshots.log`: `FETCH vhs_validators_test: … 66 validators, 25 with unl "rpc", 55 domain_verified` | verified |
| C6 | Explorer amendments page is a 2,454-byte JS SPA shell; its data comes from the VHS vote endpoint (explorer source fetches `${VITE_DATA_URL}/amendments/vote/${network}`) | [FAKTA] | `data/explorer_amendments_20261121.html`; `docs/SOURCES.md §1` (explorer source, fetched 2026-11-21 20:34 UTC) | verified |
| C7 | The `postfiat.org` homepage embeds a stale network snapshot ("snapshot Sep 21, 2026: 53 validators") and must not be cited as live data | [FAKTA] | `docs/SOURCES.md §6` (fetched 2026-11-21 20:24 UTC; live VHS at the same time reported 66) | verified |

## B — Amendment state

| # | Claim | Label | Evidence | Status |
|---|---|---|---|---|
| C8 | Live `feature`: 101 amendments known, 64 enabled, 37 disabled; 0 entries carry a `majority` or `vetoed` field; 0 entries have `supported: false` | [FAKTA] | `outputs/collect_snapshots.log`: `FETCH rpc_feature: 101 known, 64 enabled, 37 disabled, 0 carry a majority/vetoed field`; `outputs/generate_tables.log`: `CHECK feature: 101 known, 64 enabled, 37 disabled` | verified |
| C9 | On-ledger Amendments entry (64 IDs) exactly equals the `feature` enabled set | [FAKTA] | `outputs/generate_tables.log`: `CHECK Amendments entry == feature enabled set: yes (64 IDs)` | verified |
| C10 | VHS vote records (64) exactly equal the enabled set; all share date 2026-02-09T14:31:12.000Z and ledger 86785; 0 items carry `voted`/`eta` | [FAKTA] | `outputs/collect_snapshots.log`: `FETCH vhs_amendments_vote_test: 64 activation records, distinct dates ['2026-02-09T14:31:12.000Z'], distinct ledger_index [86785], items with voted/eta fields 0` | verified |
| C11 | No amendment is currently in voting (negative finding from two sources: 0 `majority` fields in `feature`, 0 `voted`/`eta` items in VHS) | [FAKTA] | C8 + C10; `outputs/amendment_vote_counts.md` | verified (as a negative finding) |
| C12 | Both PFTL-only amendments disabled: `PF_ValidatorVoteTracking` (`213D9785…`), `PF_AccountExclusion` (`56857392…`) | [FAKTA] | `outputs/amendment_vote_counts.csv` (both rows `disabled`); `docs/SOURCES.md §3` (macro entries, `DefaultNo`) | verified |
| C13 | `fixAmendmentMajorityCalc` is enabled live, so the live majority rule is the post-fix 67% rule (strict greater-than) | [FAKTA] | `outputs/amendment_vote_counts.csv` (`fixAmendmentMajorityCalc` row `enabled`); `docs/amendment-activation.md` | verified |
| C14 | All 64 enabled amendments activated in a single ledger, 86785, at 2026-02-09T14:31:12Z | [FAKTA] | `outputs/amendment_activation_timing.csv` (64 rows, one date, one ledger) | verified |

## C — Thresholds and lifecycle (pinned source)

| # | Claim | Label | Evidence | Status |
|---|---|---|---|---|
| C15 | Majority thresholds: pre-fix 204/256 (`>=`), post-fix 67/100 (strict `>`); holding default 2 weeks | [FAKTA] | `docs/SOURCES.md §3`: `SystemParameters.h:83-88`; `AmendmentTable.cpp:325-341`, `:360-377` | verified |
| C16 | Holding test is `majorityTime + majorityTime_ <= closeTime`; shipped PFTL testnet configs set 3 days; mainnet configs set no override (2-week default) | [FAKTA] | `docs/SOURCES.md §3`: `AmendmentTable.cpp:918`; `cfg/postfiatd-testnet-full.cfg:1467-1469`; `Config.h:248`; `Config.cpp:872-901` | verified |
| C17 | Flag ledger every 256 ledgers; votes tallied in the round after a flag ledger | [FAKTA] | `docs/SOURCES.md §3`: `Ledger.h:426`; `Ledger.cpp:970-983`; `RCLConsensus.cpp:364-377` | verified |
| C18 | Amendment ID = SHA-512-Half of the registered name (`"fix"+Name` for FIX entries) | [FAKTA] | `docs/SOURCES.md §3`: `Feature.cpp:266`, `:437-440`; `scripts/generate_tables.py` recomputes all 107 IDs, 0 mismatches | verified |
| C19 | Worked examples: 16 trusted validators → majority at 11 yes-votes, lost at 10; 10 validators → majority at 8 | [FAKTA] | `docs/SOURCES.md §3`: `AmendmentTable_test.cpp:1460-1467` | verified |
| C20 | Live UNL of 25 needs 17 yes-votes post-fix (floor(25×0.67)=16, strictly more); pre-fix it would need 19 | [FAKTA] | `outputs/amendment_activation_thresholds.csv` (N=25 row: 17 / 19), computed by `scripts/generate_tables.py` | verified |
| C21 | Trusted-vote cache expiry 24 h after a validator's last validation | [FAKTA] | `docs/SOURCES.md §3`: `AmendmentTable.cpp:172` | verified |
| C22 | Activation is one-way: once enabled, an amendment can never be disabled | [FAKTA] | `docs/SOURCES.md §3`: `AmendmentTable.cpp:292-300` | verified |
| C23 | Amendment-blocked is a local node state (`server_info` carries `amendment_blocked: true`); remedy is upgrading the build | [FAKTA] | `docs/SOURCES.md §3`: `NetworkOPs.cpp:1830`, `:2647`, `:2811-2812`; `Change.cpp:366-371` | verified |

## D — Inventory reconciliation

| # | Claim | Label | Evidence | Status |
|---|---|---|---|---|
| C24 | Code inventory: 107 amendments (41 FEATURE + 50 FIX + 16 RETIRE) at postfiatd commit 24c5487 | [FAKTA] | `data/amendment_inventory.csv` (107 rows); `outputs/generate_tables.log`: `CHECK inventory: 107 rows, … 0 mismatches` | verified |
| C25 | The 107 → 101 gap is exactly the six `Supported::no` amendments (BatchInnerSigs, DynamicMPT, DelegateV1_1, Batch, PermissionDelegation, InvariantsV1_1); every live ID is in the code inventory | [FAKTA] | `outputs/generate_tables.log`: `CHECK every live amendment ID is in the code inventory: yes (101/101)`; `CHECK code amendments absent from the live set: 6 -- … (supported=no)` | verified |
| C26 | VHS info knows 103 = 101 live + Batch + OrchardPrivacy (`FFAB002F…`), which is in neither the code inventory nor the live set | [FAKTA] | `outputs/generate_tables.log`: `CHECK VHS info amendments absent from the code inventory: 1 -- OrchardPrivacy`; `… absent from the live set: 2 -- Batch, OrchardPrivacy` | verified |
| C27 | VHS marks 15 amendments deprecated; the code retires 16; the one retired amendment VHS does not flag deprecated is FlowCross | [FAKTA] | `outputs/collect_snapshots.log`: `FETCH vhs_amendments_info: 103 known amendments, 15 deprecated`; `outputs/reconciliation.md` | verified |

## E — UNL churn and NegativeUNL

| # | Claim | Label | Evidence | Status |
|---|---|---|---|---|
| C28 | The 25 VL keys are exactly the 25 VHS `unl: "rpc"` validators (after base58 decoding of VHS node keys) | [FAKTA] | `outputs/generate_tables.log`: `CHECK VL keys == VHS unl:"rpc" keys: yes (25 VL, 25 unl rpc, 66 VHS validators observed)` | verified |
| C29 | UNL churn 2026-07-17 → 2026-11-22: 20 → 25; retained 12, exits 8, entrants 13; observed validators 50 → 66 (added 22, removed 6) | [FAKTA] | `outputs/generate_tables.log`: `CHECK churn arithmetic: retained 12 + entrants 13 = 25; retained 12 + exits 8 = 20; observed 50 -> 66 = 50 - 6 + 22`; `outputs/unl_churn.csv` (72 rows) | verified |
| C30 | Zero Wayback captures of the VL URL; the only historical validator snapshot is the single 2026-07-17 VHS capture | [FAKTA] | `outputs/collect_snapshots.log`: `CHECK wayback VL captures: count 0`; `data/wayback_vhs_validators_20260717.json` | verified |
| C31 | NegativeUNL entry now lists two disabled validators, both VL members: ED4F62A8… (FirstLedgerSequence 8180480, 24h agreement 0.00000) and ED372A9F… (FirstLedgerSequence 8250880, 24h agreement 0.95438); no `ValidatorToDisable` pending | [FAKTA] | `outputs/generate_tables.log`: `TABLE negative_unl: 2 disabled validator(s), FirstLedgerSequences 8180480, 8250880, ValidatorToDisable none pending`; `outputs/negative_unl.csv` | verified |
| C32 | The second disable executed between the 20:29 UTC fetch (one disabled + `ValidatorToDisable` ED372A9F…) and the 20:58 UTC fetch (two disabled, none pending) | [FAKTA] | `outputs/negative_unl.md` (both states stated); `data/20261121T205824Z_rpc_ledger_entry_negativeunl.json` already shows 2 disabled | verified |

## F — Estimates (labelled, not measured facts)

| # | Claim | Label | Evidence | Status |
|---|---|---|---|---|
| E1 | Ledger close cadence ≈ 3 s/ledger (2 ledgers per ~6.0 s) | [ESTIMASI] | `docs/SOURCES.md §6` (close-time samples 2026-11-21 20:25–20:33 UTC) | verified (as estimate) |
| E2 | Disable date of ED4F62A8… ≈ 2026-11-19T09:50:48Z (ledger gap 70,954 × ~3 s/ledger before validated ledger 8251434 of the earliest snapshot set in data/) | [ESTIMASI] | `outputs/reconciliation.md` (NV4); method stated, not a measured date | verified (as estimate) |
| E3 | With the shipped 3-day holding time, a testnet activation timeline is ~3 days plus flag-ledger rounding (~13 min at ~3 s/ledger) | [ESTIMASI] | C16 + E1; `docs/amendment-activation.md` | verified (as estimate) |

## Not verified (NV1–NV15)

Claims that could not be established from the sources consulted. Nothing
in this section is presented as verified anywhere in this pack.

- NV1 — Live per-amendment vote counts: how many of the 25 UNL validators currently vote for each of the 37 disabled amendments. The public `feature` method omits majority/veto data (admin-only); VHS vote endpoints serve activation records only (404 for non-enabled amendments); the explorer reads the same VHS endpoint. No public source tried exposes live vote counts.
- NV2 — Majority-pending / ETA status for any specific amendment beyond the negative finding (0 `voted`/`eta` items in VHS, 0 `majority` fields in `feature`). The negative finding is recorded; it cannot independently prove the negative beyond those two sources.
- NV3 — Historical validator-list snapshots with sequence < 30, and any churn inside 2026-07-17 → 2026-11-22. Wayback has zero captures of the VL URL (checked twice, availability API empty); no VL copy was found in any public git repo; the only historical validator data is the single 2026-07-17 VHS capture used here.
- NV4 — Close time of ledger 8180480 (NegativeUNL FirstLedgerSequence), i.e. the disable date of ED4F62A8…. The RPC node retains only ledgers from 8200054 onward at collection time and answers `lgrNotFound` for 8180480. [ESTIMASI] ledger gap 70,954 × ~3 s/ledger ≈ 2.5 days before the validated ledger 8251434 of the earliest snapshot set in data/ (2026-11-21T20:58:30Z) → ~2026-11-19T09:50:48Z. Estimate only.
- NV5 — Whether the live testnet validators actually run the shipped 3-day `[amendment_majority_time]` (vs a custom value ≥ 15 minutes). The shipped configs say 3 days; the holding time is a per-node local configuration, and no operator config or observed majority→activation gap is available to confirm it.
- NV6 — Which amendments the PFTL testnet genesis ledger started with. The genesis ledger takes the enabled set as a parameter (`Ledger.cpp:171-221`); it is not in the source checkout.
- NV7 — The upstream rippled 80/100 post-fix threshold as a source file:line. Upstream = 80% is established from the xrpl.build documentation and from this checkout's HEAD commit message, but no upstream rippled source tree was read.
- NV8 — That `PF_AccountExclusion` / `PF_ValidatorVoteTracking` exist in no upstream rippled version. Strongly indicated PFTL-only by the `PF_` naming and PFTL-only call sites, but not proven against an upstream source tree.
- NV9 — The upstream value of the 24-hour trusted-vote cache expiry. The mechanism and value are verified in postfiatd (`AmendmentTable.cpp:172`); the upstream value was not cross-checked.
- NV10 — Historical VHS daily validator reports before 2026-11-21, other than the single 2026-07-17 Wayback capture. The reports endpoint returns current-day reports; archived reports were not retrieved.
- NV11 — A full WebSocket session (e.g. `feature` over WS). Only an HTTP upgrade probe (101 Switching Protocols) was run; no method was executed over WebSocket.
- NV12 — A second, independent public RPC/WS host for cross-checking. Only the foundation hosts were found; no community RPC mirror surfaced in search. All chain-state claims rest on the foundation's own nodes plus the foundation-run VHS.
- NV13 — Per-validator manifest contents (domains/attestations inside the VL's per-validator `manifest` blobs and the top-level `manifest`). The blobs are base64 binary and were not decoded beyond the JSON blob in `blobs_v2`; VL-member domains in this pack come from VHS instead.
- NV14 — Why VHS knows OrchardPrivacy (`FFAB002F…`), an amendment in neither the postfiatd code inventory (commit 24c5487) nor the live set. No source consulted explains its presence in the VHS info endpoint.
- NV15 — Whether any amendment ever gained then lost a majority on PFTL testnet (majority clock reset), and individual activation histories before the single-ledger activation at 86785. That needs ledger history (scanning historical Amendments entries / EnableAmendment pseudo-transactions); none is available from the public endpoints tried.
