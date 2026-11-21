# Reconciliation — code inventory vs live ledger vs VHS

Three counts that look contradictory until the sets are compared
directly (newest snapshot set in data/):

| source | count | what it counts |
|---|---:|---|
| postfiatd code inventory (`features.macro`, commit 24c5487) | 107 | amendments registered in the binary: 41 FEATURE + 50 FIX + 16 RETIRE |
| live `feature` RPC | 101 | amendments the node knows: 64 enabled + 37 disabled |
| VHS `/v1/network/amendments/info` | 103 | amendments VHS knows: 15 deprecated |
| on-ledger Amendments entry | 64 | enabled amendment IDs |
| VHS `/v1/network/amendments/vote/test` | 64 | activation records |

The 107 → 101 gap is exactly the six amendments registered with
`Supported::no` (unfinished code in this build): BatchInnerSigs
(`fixBatchInnerSigs`), DynamicMPT, DelegateV1_1 (`fixDelegateV1_1`),
Batch, PermissionDelegation, InvariantsV1_1. Every one of the 101
live IDs is in the code inventory, and every code amendment absent
from the live set is `Supported::no`. A node cannot vote for an
unsupported amendment, so these six cannot appear in the live set
from this build. The gap is therefore explained, not papered over:
it is a property of the build, verified by set comparison in
`generate_tables.py` (see its log).

The 103 → 101 VHS gap is two amendments VHS knows but the live node
does not report: Batch (in the code inventory, `Supported::no`) and
OrchardPrivacy (`FFAB002FD32A4CFE1FA902D8A5F507B8B0E860716FC578E1E0BD6DB665BAABAA`,
in neither the code inventory nor the live set). Why VHS carries
OrchardPrivacy is not established from any source consulted; see NV14.

VHS marks 15 amendments deprecated; the code inventory retires 16.
The one retired amendment VHS does not flag deprecated is FlowCross
(`3012E8230864E95A58C60FD61430D7E1B4D3353195F2981DC12B0C7C0950FFAC`,
disabled live). That is a metadata difference between VHS and the
code, not a contradiction about enabled state.

Live threshold: `fixAmendmentMajorityCalc` is enabled, so the
post-fix 67% rule (strict greater-than) is the live rule, not the
pre-fix 204/256 rule.

## Not verified (NV1–NV15)

Claims that could not be established from the sources consulted.
Nothing in this section is presented as verified anywhere in this pack.

- NV1 — Live per-amendment vote counts: how many of the 25 UNL validators currently vote for each of the 37 disabled amendments. The public `feature` method omits majority/veto data (admin-only); VHS vote endpoints serve activation records only (404 for non-enabled amendments); the explorer reads the same VHS endpoint. No public source tried exposes live vote counts.
- NV2 — Majority-pending / ETA status for any specific amendment beyond the negative finding (0 `voted`/`eta` items in VHS, 0 `majority` fields in `feature`). The negative finding is recorded; it cannot independently prove the negative beyond those two sources.
- NV3 — Historical validator-list snapshots with sequence < 30, and any churn inside 2026-07-17 → 2026-11-22. Wayback has zero captures of the VL URL (checked twice, availability API empty); no VL copy was found in any public git repo; the only historical validator data is the single 2026-07-17 VHS capture used here.
- NV4 — Close time of ledger 8180480 (NegativeUNL FirstLedgerSequence), i.e. the disable date of ED4F62A8…. The RPC node retains only ledgers from 8200054 onward at collection time and answers `lgrNotFound` for 8180480. [ESTIMASI] ledger gap 70954 x ~3 s/ledger = ~212862 s (~2.5 days) before the validated ledger 8251434 of the earliest snapshot set in data/ (2026-11-21T20:58:30Z) -> ~2026-11-19T09:50:48Z. Estimate only; the close time of ledger 8180480 is not readable from this node.
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
