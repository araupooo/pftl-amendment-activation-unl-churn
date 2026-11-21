# Excerpts — claim index, not-verified list, key log lines

Verbatim, paste-ready excerpts from this pack: the full claim–evidence
index table, the complete not-verified list, and key log lines. These are
copies of `docs/claim-evidence-index.md`, `outputs/reconciliation.md`,
and the unedited logs in `outputs/` — the full documents are in the
repository; this file exists so the text can be quoted without fetching.

## Claim–evidence index (full table)

| # | Claim | Label | Evidence | Status |
|---|---|---|---|---|
| C1 | Published VL fetched live, HTTP 200, 14,781 bytes, SHA-256 `5d4f5a18a18fead4105e5dc00cf7e11a71b9be4bc140357d1b4ea12116df59e7`, sequence 30, 25 validators, publisher `ED3F1E0D…09E2`, effective 2026-11-17T20:10:08Z, expiration 2028-03-31T16:14:53Z | [FAKTA] | `outputs/collect_snapshots.log`: `FETCH testnet_vl: HTTP 200, 14781 bytes, SHA-256 5d4f5a18…df59e7`, `sequence 30, validators 25` | verified |
| C2 | Live VL byte-identical to the vendored 2026-11-20 reference copy; zero UNL churn 2026-11-20 → 2026-11-22 | [FAKTA] | `outputs/collect_snapshots.log`: `VL-COMPARE: IDENTICAL` | verified |
| C3 | JSON-RPC works: build 1.0.9, network ID 2025, `server_state` "full", validated ledger 8251750, `validation_quorum` 16, peers 21 at collection | [FAKTA] | `outputs/collect_snapshots.log`: `FETCH rpc_server_info: … build 1.0.9, network_id 2025, validated ledger 8251750, validation_quorum 16, peers 21` | verified |
| C4 | WebSocket host answers an upgrade probe with HTTP 101; the RPC host itself rejects WebSocket upgrades with 401 "Invalid protocol." | [FAKTA] | `outputs/collect_snapshots.log`: `PROBE websocket ws.testnet.postfiat.org: HTTP 101`; 401 probe 2026-11-21 20:25:41 UTC, `docs/SOURCES.md §1` | verified |
| C5 | VHS works: 66 validators observed, 25 with `unl: "rpc"`, 55 domain-verified, 0 revoked, 1 partial | [FAKTA] | `outputs/collect_snapshots.log`: `FETCH vhs_validators_test: … 66 validators, 25 with unl "rpc", 55 domain_verified` | verified |
| C6 | Explorer amendments page is a 2,454-byte JS SPA shell; its data comes from the VHS vote endpoint | [FAKTA] | `data/explorer_amendments_20261121.html`; `docs/SOURCES.md §1` | verified |
| C7 | The `postfiat.org` homepage embeds a stale network snapshot ("snapshot Sep 21, 2026: 53 validators") and must not be cited as live data | [FAKTA] | `docs/SOURCES.md §6` | verified |
| C8 | Live `feature`: 101 known, 64 enabled, 37 disabled; 0 entries carry a `majority` or `vetoed` field; 0 entries have `supported: false` | [FAKTA] | `outputs/collect_snapshots.log`: `FETCH rpc_feature: 101 known, 64 enabled, 37 disabled, 0 carry a majority/vetoed field` | verified |
| C9 | On-ledger Amendments entry (64 IDs) exactly equals the `feature` enabled set | [FAKTA] | `outputs/generate_tables.log`: `CHECK Amendments entry == feature enabled set: yes (64 IDs)` | verified |
| C10 | VHS vote records (64) exactly equal the enabled set; all share date 2026-02-09T14:31:12.000Z and ledger 86785; 0 items carry `voted`/`eta` | [FAKTA] | `outputs/collect_snapshots.log`: `FETCH vhs_amendments_vote_test: 64 activation records, distinct dates ['2026-02-09T14:31:12.000Z'], distinct ledger_index [86785], items with voted/eta fields 0` | verified |
| C11 | No amendment is currently in voting (negative finding from two sources) | [FAKTA] | C8 + C10; `outputs/amendment_vote_counts.md` | verified (as a negative finding) |
| C12 | Both PFTL-only amendments disabled: `PF_ValidatorVoteTracking` (`213D9785…`), `PF_AccountExclusion` (`56857392…`) | [FAKTA] | `outputs/amendment_vote_counts.csv` (both rows `disabled`) | verified |
| C13 | `fixAmendmentMajorityCalc` is enabled live, so the live majority rule is the post-fix 67% rule (strict greater-than) | [FAKTA] | `outputs/amendment_vote_counts.csv` (`fixAmendmentMajorityCalc` row `enabled`) | verified |
| C14 | All 64 enabled amendments activated in a single ledger, 86785, at 2026-02-09T14:31:12Z | [FAKTA] | `outputs/amendment_activation_timing.csv` (64 rows, one date, one ledger) | verified |
| C15 | Majority thresholds: pre-fix 204/256 (`>=`), post-fix 67/100 (strict `>`); holding default 2 weeks | [FAKTA] | `docs/SOURCES.md §3`: `SystemParameters.h:83-88`; `AmendmentTable.cpp:325-341`, `:360-377` | verified |
| C16 | Holding test is `majorityTime + majorityTime_ <= closeTime`; shipped PFTL testnet configs set 3 days; mainnet configs set no override (2-week default) | [FAKTA] | `docs/SOURCES.md §3`: `AmendmentTable.cpp:918`; `cfg/postfiatd-testnet-full.cfg:1467-1469` | verified |
| C17 | Flag ledger every 256 ledgers; votes tallied in the round after a flag ledger | [FAKTA] | `docs/SOURCES.md §3`: `Ledger.h:426`; `Ledger.cpp:970-983`; `RCLConsensus.cpp:364-377` | verified |
| C18 | Amendment ID = SHA-512-Half of the registered name (`"fix"+Name` for FIX entries) | [FAKTA] | `docs/SOURCES.md §3`: `Feature.cpp:266`; generator recomputes all 107 IDs, 0 mismatches | verified |
| C19 | Worked examples: 16 trusted validators → majority at 11 yes-votes, lost at 10; 10 validators → majority at 8 | [FAKTA] | `docs/SOURCES.md §3`: `AmendmentTable_test.cpp:1460-1467` | verified |
| C20 | Live UNL of 25 needs 17 yes-votes post-fix (floor(25×0.67)=16, strictly more); pre-fix it would need 19 | [FAKTA] | `outputs/amendment_activation_thresholds.csv` (N=25 row: 17 / 19) | verified |
| C21 | Trusted-vote cache expiry 24 h after a validator's last validation | [FAKTA] | `docs/SOURCES.md §3`: `AmendmentTable.cpp:172` | verified |
| C22 | Activation is one-way: once enabled, an amendment can never be disabled | [FAKTA] | `docs/SOURCES.md §3`: `AmendmentTable.cpp:292-300` | verified |
| C23 | Amendment-blocked is a local node state (`server_info` carries `amendment_blocked: true`); remedy is upgrading the build | [FAKTA] | `docs/SOURCES.md §3`: `NetworkOPs.cpp:1830`, `:2647`, `:2811-2812`; `Change.cpp:366-371` | verified |
| C24 | Code inventory: 107 amendments (41 FEATURE + 50 FIX + 16 RETIRE) at postfiatd commit 24c5487 | [FAKTA] | `data/amendment_inventory.csv` (107 rows); `outputs/generate_tables.log`: `CHECK inventory: 107 rows, … 0 mismatches` | verified |
| C25 | The 107 → 101 gap is exactly the six `Supported::no` amendments (BatchInnerSigs, DynamicMPT, DelegateV1_1, Batch, PermissionDelegation, InvariantsV1_1); every live ID is in the code inventory | [FAKTA] | `outputs/generate_tables.log`: `CHECK every live amendment ID is in the code inventory: yes (101/101)`; `CHECK code amendments absent from the live set: 6 -- … (supported=no)` | verified |
| C26 | VHS info knows 103 = 101 live + Batch + OrchardPrivacy (`FFAB002F…`), which is in neither the code inventory nor the live set | [FAKTA] | `outputs/generate_tables.log`: `CHECK VHS info amendments absent from the code inventory: 1 -- OrchardPrivacy` | verified |
| C27 | VHS marks 15 amendments deprecated; the code retires 16; the one retired amendment VHS does not flag deprecated is FlowCross | [FAKTA] | `outputs/collect_snapshots.log`: `FETCH vhs_amendments_info: 103 known amendments, 15 deprecated` | verified |
| C28 | The 25 VL keys are exactly the 25 VHS `unl: "rpc"` validators (after base58 decoding of VHS node keys) | [FAKTA] | `outputs/generate_tables.log`: `CHECK VL keys == VHS unl:"rpc" keys: yes (25 VL, 25 unl rpc, 66 VHS validators observed)` | verified |
| C29 | UNL churn 2026-07-17 → 2026-11-22: 20 → 25; retained 12, exits 8, entrants 13; observed validators 50 → 66 (added 22, removed 6) | [FAKTA] | `outputs/generate_tables.log`: `CHECK churn arithmetic: retained 12 + entrants 13 = 25; retained 12 + exits 8 = 20; observed 50 -> 66 = 50 - 6 + 22` | verified |
| C30 | Zero Wayback captures of the VL URL; the only historical validator snapshot is the single 2026-07-17 VHS capture | [FAKTA] | `outputs/collect_snapshots.log`: `CHECK wayback VL captures: count 0` | verified |
| C31 | NegativeUNL entry now lists two disabled validators, both VL members: ED4F62A8… (FirstLedgerSequence 8180480, 24h agreement 0.00000) and ED372A9F… (FirstLedgerSequence 8250880, 24h agreement 0.95438); no `ValidatorToDisable` pending | [FAKTA] | `outputs/generate_tables.log`: `TABLE negative_unl: 2 disabled validator(s), FirstLedgerSequences 8180480, 8250880, ValidatorToDisable none pending` | verified |
| C32 | The second disable executed between the 20:29 UTC fetch (one disabled + `ValidatorToDisable` ED372A9F…) and the 20:58 UTC fetch (two disabled, none pending) | [FAKTA] | `outputs/negative_unl.md`; `data/20261121T205824Z_rpc_ledger_entry_negativeunl.json` | verified |
| E1 | Ledger close cadence ≈ 3 s/ledger (2 ledgers per ~6.0 s) | [ESTIMASI] | `docs/SOURCES.md §6` | verified (as estimate) |
| E2 | Disable date of ED4F62A8… ≈ 2026-11-19T09:50:48Z (ledger gap 70,954 × ~3 s/ledger before validated ledger 8251434 of the earliest snapshot set in data/) | [ESTIMASI] | `outputs/reconciliation.md` (NV4) | verified (as estimate) |
| E3 | With the shipped 3-day holding time, a testnet activation timeline is ~3 days plus flag-ledger rounding (~13 min at ~3 s/ledger) | [ESTIMASI] | C16 + E1 | verified (as estimate) |

## Not verified (complete list, NV1–NV15)

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

## Key log lines (verbatim, from the committed unedited logs)

From `outputs/collect_snapshots.log` (snapshot set `20261121T211420Z`):

```
COLLECTOR: live run, stamp 20261121T211420Z
COLLECTOR: endpoints VL=https://postfiat.org/testnet_vl.json RPC=https://rpc.testnet.postfiat.org VHS=https://vhs.testnet.postfiat.org
FETCH testnet_vl: HTTP 200, 14781 bytes, SHA-256 5d4f5a18a18fead4105e5dc00cf7e11a71b9be4bc140357d1b4ea12116df59e7 -> 20261121T211420Z_testnet_vl.json
FETCH testnet_vl: sequence 30, validators 25, effective 2026-11-17T20:10:08+00:00, expiration 2028-03-31T16:14:53+00:00
VL-COMPARE: live SHA-256 5d4f5a18a18fead4105e5dc00cf7e11a71b9be4bc140357d1b4ea12116df59e7
VL-COMPARE: reference SHA-256 5d4f5a18a18fead4105e5dc00cf7e11a71b9be4bc140357d1b4ea12116df59e7 (14781 bytes)
VL-COMPARE: IDENTICAL
FETCH rpc_server_info: HTTP 200, 1170 bytes, SHA-256 32e0f040da9608c7471dd98b746daa16f99465e29afa36f9a7d9296cdc8e599d -> 20261121T211420Z_rpc_server_info.json
FETCH rpc_server_info: build 1.0.9, network_id 2025, validated ledger 8251750, validation_quorum 16, peers 21
FETCH rpc_feature: HTTP 200, 12817 bytes, SHA-256 70585f308ab55dfdc84093e95a21c3859099dcbf1c5b04f1f00cea3a6785984f -> 20261121T211420Z_rpc_feature.json
FETCH rpc_feature: 101 known, 64 enabled, 37 disabled, 0 carry a majority/vetoed field
FETCH rpc_ledger_validated: HTTP 200, 761 bytes, SHA-256 5de1de665a83a438cac3a4baba811581adc48b0e59d6dca2e314bb71b41b0150 -> 20261121T211420Z_rpc_ledger_validated.json
FETCH rpc_ledger_validated: ledger_index 8251750, close_time_iso 2026-11-21T21:14:21Z, hash 4775C3D33BF4D16232CAA11F2F2C50BD2EB3A072244E3519FE10EBD20390D2CD
FETCH rpc_ledger_entry_amendments: HTTP 200, 4658 bytes, SHA-256 4e6813aabd83e339578f4d325fa9bbf41dbdf7f359f6787e862c9cf5a655de38 -> 20261121T211420Z_rpc_ledger_entry_amendments.json
FETCH rpc_ledger_entry_amendments: 64 amendment IDs in the Amendments entry, ledger 8251751
FETCH rpc_ledger_entry_negativeunl: HTTP 200, 760 bytes, SHA-256 e718cbcdd7add1dc02a63b3c92e4b66ff638f9dad6d2ff47fe62fab1f84cce96 -> 20261121T211420Z_rpc_ledger_entry_negativeunl.json
FETCH rpc_ledger_entry_negativeunl: 2 disabled validator(s), ValidatorToDisable none pending, ledger 8251751
FETCH vhs_root: HTTP 200, 2690 bytes, SHA-256 0f61e791be3d0147af69cbe50f573c2794b01d8b842f7f2985785f462d94a188 -> 20261121T211420Z_vhs_root.json
FETCH vhs_validators_test: HTTP 200, 51431 bytes, SHA-256 3cb33893ec9c344c481e947963653aedb65ae1a7ec40c2b282bdc5fb1167b292 -> 20261121T211420Z_vhs_validators_test.json
FETCH vhs_validators_test: 66 validators, 25 with unl "rpc", 55 domain_verified
FETCH vhs_amendments_vote_test: HTTP 200, 17549 bytes, SHA-256 b93ef492b7737928b165823d78603ed2077b189514c189be851f6c1ca721427a -> 20261121T211420Z_vhs_amendments_vote_test.json
FETCH vhs_amendments_vote_test: 64 activation records, distinct dates ['2026-02-09T14:31:12.000Z'], distinct ledger_index [86785], items with voted/eta fields 0
FETCH vhs_amendments_info: HTTP 200, 14554 bytes, SHA-256 f4e9d57b540a27301a506af2a383d23715f3db19de11493f1ba5137fced73021 -> 20261121T211420Z_vhs_amendments_info.json
FETCH vhs_amendments_info: 103 known amendments, 15 deprecated
FETCH vhs_validator_reports: HTTP 200, 12927 bytes, SHA-256 6739fda7177a6c5e9744ecf9823e35d12e7724952974381daf53ef7b365bd982 -> 20261121T211420Z_vhs_validator_reports.json
FETCH vhs_validator_reports: 66 daily reports
PROBE websocket ws.testnet.postfiat.org: HTTP 101 -- HTTP/1.1 101 Switching Protocols
CHECK wayback VL captures: count 0 -- HTTP 200, archived_snapshots={}
COLLECTOR VERDICT: PASS -- 11 files fetched, 0 core failures
```

From `outputs/generate_tables.log`:

```
GENERATE: snapshot set 20261121T211420Z
CHECK inventory: 107 rows, 3 kinds FEATURE=41 FIX=50 RETIRE=16, IDs recomputed (SHA-512-Half): 0 mismatches
CHECK feature: 101 known, 64 enabled, 37 disabled, 0 carry a majority/vetoed field, 0 supported:false
CHECK Amendments entry == feature enabled set: yes (64 IDs)
CHECK VHS vote records == feature enabled set: yes (64 IDs)
CHECK every live amendment ID is in the code inventory: yes (101/101)
CHECK code amendments absent from the live set: 6 -- BatchInnerSigs (FIX, supported=no), DelegateV1_1 (FIX, supported=no), DynamicMPT (FEATURE, supported=no), Batch (FEATURE, supported=no), PermissionDelegation (FEATURE, supported=no), InvariantsV1_1 (FEATURE, supported=no)
CHECK VHS info amendments absent from the code inventory: 1 -- OrchardPrivacy (FFAB002FD32A4CFE1FA902D8A5F507B8B0E860716FC578E1E0BD6DB665BAABAA)
CHECK VHS info amendments absent from the live set: 2 -- Batch (894646DD5284E97DECFE6674A6D6152686791C4A95F8C132CCA9BAF9E5812FB6), OrchardPrivacy (FFAB002FD32A4CFE1FA902D8A5F507B8B0E860716FC578E1E0BD6DB665BAABAA)
CHECK VL keys == VHS unl:"rpc" keys: yes (25 VL, 25 unl rpc, 66 VHS validators observed)
CHECK churn arithmetic: retained 12 + entrants 13 = 25 (VL size); retained 12 + exits 8 = 20 (2026-07-17 UNL size); observed 50 -> 66 = 50 - 6 + 22
TABLE amendment_activation_thresholds: 6 worked rows (N=1,2,3,10,16,25); live N=25 needs 17 yes-votes post-fix
TABLE amendment_vote_counts: 101 rows, 64 enabled / 37 disabled, 0 majority/vetoed fields, 0 amendments in voting
TABLE amendment_activation_timing: 64 rows, all at ledger 86785, 2026-02-09T14:31:12.000Z
TABLE unl_churn: 72 rows; UNL 20 -> 25 (retained 12, exits 8, entrants 13); observed 50 -> 66
TABLE negative_unl: 2 disabled validator(s), FirstLedgerSequences 8180480, 8250880, ValidatorToDisable none pending
TABLE reconciliation: code 107 / live 101 / VHS info 103; gap = 6 Supported::no; VHS-only = Batch + OrchardPrivacy
OUTPUT amendment_activation_thresholds.csv: 220 bytes, SHA-256 0611b71dd401a4d0aa095d6f2f21ee4531eeb8c582e89b7d3e23662339983547
OUTPUT amendment_activation_thresholds.md: 1835 bytes, SHA-256 32dfef6ddc8f4c18f99b78bdb5f759233281e5d57553405ac67c6167cd584cc8
OUTPUT amendment_activation_timing.csv: 11837 bytes, SHA-256 1274cecf20a45ecf0de9b0fd1f1e3905ea35562a0bf6e76ab7cc4256a62d2058
OUTPUT amendment_activation_timing.md: 1064 bytes, SHA-256 c8ee3eaf163b6851518e58d588ad2a8fc82dd4f59670d192fe005ce0136db077
OUTPUT amendment_vote_counts.csv: 11112 bytes, SHA-256 652120833ea2387603a6a4aed74093815aa94c50fe3fd32c22b0797ccbc90cff
OUTPUT amendment_vote_counts.md: 1803 bytes, SHA-256 431d278b65b9396c61764c263c6d0484ba06c7c110e3d2b7a6de2b8b10a5bc65
OUTPUT negative_unl.csv: 366 bytes, SHA-256 4a0556bc41c30546c797cd4279aed234ab26bfc09efcff19f5c7433454d04a1e
OUTPUT negative_unl.md: 1747 bytes, SHA-256 2d5c4c48059b3d05f9394d05744de5b91a20ba1dc4519ad7aa9e01b752272dd4
OUTPUT reconciliation.csv: 751 bytes, SHA-256 0adda74ec4cb7e9c4492c52abe4e335b4184d6cd6f086a37e70b7d719704f51f
OUTPUT reconciliation.md: 6333 bytes, SHA-256 830bb945c2f69501b130978c67140f950cf84fa75e800161ee6b8a34ff1e3597
OUTPUT unl_churn.csv: 11438 bytes, SHA-256 1f97f460c0c0f29f051f22400775c30ed0400bf5a7a4a64d9c6636dff0a7d0a3
OUTPUT unl_churn.md: 4728 bytes, SHA-256 5fac0b58e80a941811385d88d3f17f9a15cac5e5752aefb155039f9c80d671b6
GENERATE VERDICT: PASS -- 6 tables written, all set checks passed
```

Run result:

```
RUN_ALL RESULT: ALL CHECKS PASSED (2/2 scripts)
```
