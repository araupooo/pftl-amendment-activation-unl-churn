# Amendment activation

What the live PFTL testnet shows about which amendments are enabled, how
they got there, and what the activation rule is. Snapshot set
`20261121T211420Z` (2026-11-21 21:14:20 UTC), unless stated otherwise.
Tables: `outputs/amendment_activation_thresholds.*`,
`outputs/amendment_vote_counts.*`, `outputs/amendment_activation_timing.*`.
Sources: `docs/SOURCES.md`.

Labels: [FAKTA] verified against a named source, [ESTIMASI] modelled or
reported number, [ANALISIS] interpretation.

## The live state in one paragraph

[FAKTA] The testnet knows 101 amendments: 64 enabled, 37 disabled
(`feature` RPC, 2026-11-21 21:00 UTC). The on-ledger `Amendments` entry
lists exactly the same 64 IDs as the `feature` enabled set (set equality
verified by `scripts/generate_tables.py`). All 64 enabled amendments
activated in a single ledger, 86785, at 2026-02-09T14:31:12Z (VHS
activation records). No amendment is currently in voting. The switch
that selects the live majority rule, `fixAmendmentMajorityCalc`, is
itself enabled — so the live rule is the post-fix 67% rule, strict
greater-than. With the live UNL of 25 validators, an activation needs 17
yes-votes.

## Thresholds

[FAKTA] The two majority rules in postfiatd
(`SystemParameters.h:83-88`, `AmendmentTable.cpp:325-341`, `:360-377`):

| rule | threshold | pass condition |
|---|---|---|
| pre-fix (`fixAmendmentMajorityCalc` not enabled) | floor(N × 204/256) | votes >= threshold |
| post-fix (`fixAmendmentMajorityCalc` enabled) | floor(N × 67/100) | votes > threshold (strict) |

[FAKTA] Worked values (`outputs/amendment_activation_thresholds.csv`):

| N trusted validations | post-fix votes needed | pre-fix votes needed |
|---:|---:|---:|
| 1 | 2 | 1 |
| 2 | 2 | 2 |
| 3 | 3 | 3 |
| 10 | 8 | 8 |
| 16 | 11 | 12 |
| 25 (live UNL) | 17 | 19 |

[FAKTA] The N=16 (11 votes) and N=10 (8 votes) rows are the values pinned
by the test suite (`AmendmentTable_test.cpp:1460-1467`). Note the N=1 row:
with a single trusted validation, the pre-fix rule needs 1 vote while the
post-fix rule's strict `>` on threshold 1 needs 2 — which is why the code
treats `trustedValidations_ == 1` as an exception and uses `>=` there
(`AmendmentTable.cpp:372-374`). The N=2 and N=3 rows show the rounding
bite: at N=3 the post-fix rule needs unanimity.

[ANALISIS] The 67% rule is materially easier to satisfy than upstream's
80%: at the live UNL size of 25, activation needs 17 yes-votes instead of
the 21 that an 80% strict rule would need (floor(25×0.80) = 20, strictly
more → 21). A small validator set plus a lower threshold means a handful
of validators changing their vote can move an amendment across the line.

[FAKTA] Do not confuse the amendment threshold with the consensus
quorum: `server_info` in this snapshot set reports `validation_quorum`
16 (it was 17 in an earlier call the same evening and 16 in a later one;
it moves as participation changes). The quorum governs ledger validation,
not amendment voting.

## Vote counts and progression

[FAKTA] The public `feature` response carries no `majority` or `vetoed`
field for any of the 101 amendments, and no entry has `supported: false`.
Single-amendment probes (`feature` for Escrow and for
PF_ValidatorVoteTracking, 2026-11-21) return the same shape — enabled,
name, supported — and no vote data.

[FAKTA] The VHS vote endpoint returns 64 activation records and zero
items carrying a `voted` or `eta` field. The explorer's amendments page
treats `voted` as "in voting" and `eta` as "with ETA", so the live page
would show Enabled 64, In Voting 0, With ETA 0.

[FAKTA] Finding: no amendment is currently in voting. The evidence is
the absence itself, from two independent sources — but it is a negative
finding about the public surface, and it cannot independently prove the
negative beyond those two sources (NV2).

[FAKTA] Live per-amendment vote counts are not obtainable from any public
source tried: the public `feature` method omits majority/veto data by
design (admin-only fields, `Feature1.cpp:48-95`); the VHS vote endpoints
serve activation records only and answer 404 for a non-enabled amendment
(by name and by ID); the explorer reads the same VHS endpoint. This is
NV1 — the largest gap in the pack, stated plainly rather than filled with
an estimate.

[FAKTA] Both PFTL-only amendments are disabled: `PF_ValidatorVoteTracking`
(`213D9785EF1C34BC0F99BF190299B814AE0563E047DC457C9CB53B6FC02D4B70`) and
`PF_AccountExclusion`
(`56857392BEADCE1E4B0D754A91B73F1D053657AF4FDD585455D4FFBCD5307BE0`).
Both are registered `DefaultNo` in the code inventory, so no validator
votes for them unless its operator opts in via `[amendments]`.

[FAKTA] The 37 disabled amendments are listed by name in
`outputs/amendment_vote_counts.csv`. The split: of the 91 active code
amendments, 64 are enabled live, 21 are disabled live, and 6
(`Supported::no`) never reach the live set at all; all 16 retired
amendments are disabled live (16 + 21 = 37; see
`outputs/reconciliation.md`).

## Activation timing

[FAKTA] All 64 enabled amendments share one activation date
(2026-02-09T14:31:12.000Z) and one activation ledger (86785), each with
its own `EnableAmendment` transaction hash
(`outputs/amendment_activation_timing.csv`, 64 rows). There is no spread
of activation times to analyse and no per-amendment activation sequence:
the enabled set arrived together, in the network's early history.

[ANALISIS] A single-ledger activation of the whole enabled set is
consistent with a genesis-era bulk enablement rather than 64 separate
majority-and-hold cycles — but the genesis enabled set itself is not in
the source checkout (NV6), and the activation ledger predates the RPC
node's retained range, so this pack cannot distinguish "enabled at
genesis" from "enabled by 64 pseudo-transactions in one flag-ledger
round" from the data available. Both readings are consistent with the
single date and ledger; neither is asserted.

[FAKTA] The validated ledger at collection time was 8251750
(close 2026-11-21T21:14:21Z). Ledger 86785 cannot be re-read from this
node — the VHS date above is the source for the activation time.

[FAKTA] No majority-gained-then-lost history can be stated: whether any
amendment ever gained a majority and lost it (clock reset) needs ledger
history that is not available from the public endpoints tried (NV15).

## Holding time

[FAKTA] Once a majority is first recorded, it must be held continuously
until `majorityTime + majorityTime_ <= closeTime`
(`AmendmentTable.cpp:918`). The code default is 2 weeks
(`SystemParameters.h:88`); the shipped PFTL testnet configs set 3 days
(`cfg/postfiatd-testnet-full.cfg:1467-1469`).

[ANALISIS] With the 3-day shipped value, a PFTL testnet activation
timeline from first majority to enablement is on the order of 3 days
plus flag-ledger rounding (256 ledgers ≈ 13 minutes at ~3 s/ledger),
against 2 weeks upstream. But the holding time is a per-node local
configuration, and no operator config or observed majority→activation gap
is available — so the effective live holding time is not established
(NV5). Any future activation observed live would let the gap be measured
directly from the `Amendments` entry's `Majorities` CloseTime and the
activation ledger; that measurement is the way to close NV5.
