# Amendment lifecycle — proposal through activation

How an amendment goes from a name in source code to a permanent rule on
the PFTL testnet, as implemented in postfiatd at commit
`24c5487d9bfc99171380960e4eeb1543a724cfae`. All file:line citations are to
that checkout and were verified with `grep -n` on 2026-11-22. Full source
list: `docs/SOURCES.md §3`.

Labels: [FAKTA] verified against a named source, [ESTIMASI] modelled or
reported number, [ANALISIS] interpretation. Nothing inferred is presented
as a verified fact.

## Step 1 — Registration: an amendment is born in code

[FAKTA] Amendments are registered at startup from
`include/xrpl/protocol/detail/features.macro` via
`src/libxrpl/protocol/Feature.cpp`. Each entry is `XRPL_FEATURE(name,
Supported, VoteBehavior)`, `XRPL_FIX(...)`, or `XRPL_RETIRE(name)`.
The inventory in this checkout is 107 registered amendments: 41 FEATURE +
50 FIX + 16 RETIRE (`data/amendment_inventory.csv`; IDs recomputed by
`scripts/generate_tables.py`, 0 mismatches).

[FAKTA] The ID is the SHA-512-Half of the registered name string:
`auto const f = sha512Half(Slice(name.data(), name.size()));`
(`Feature.cpp:266`). A FEATURE's ID is SHA-512-Half of `"Name"`; a FIX's
ID is SHA-512-Half of `"fixName"` — the `fix` prefix is part of the hashed
string. Registration macros are at `Feature.cpp:437-440`; retired
amendments go through `retireFeature()` (`Feature.cpp:417-421`).

[ANALISIS] There is no on-chain proposal transaction by which anyone can
invent an amendment ID: an ID only exists because the name is compiled
into the binary. "Proposing" an amendment on PFTL is, in practice,
shipping a code change (a new macro entry) plus validator coordination —
there is no permissionless on-ledger proposal mechanism in this code.

[FAKTA] New amendments go at the top of `features.macro` (reverse
chronological order). `docs/AmendmentDevelopment.md` documents the
workflow: register with `Supported::no` during development, flip to
`Supported::yes` when complete and tested, choose `DefaultNo` (validators
opt in via `[amendments]` in config) or `DefaultYes` (auto-vote). Retired
amendments stay registered forever because they may exist in ledger
history.

[FAKTA] Six amendments in this checkout are `Supported::no` and therefore
have no finished code in this build: BatchInnerSigs, DynamicMPT,
DelegateV1_1, Batch, PermissionDelegation, InvariantsV1_1. A validator
cannot vote for them even if configured. This is the whole explanation of
the 107 (code) vs 101 (live) gap — see `docs/claim-evidence-index.md` C12
and `outputs/reconciliation.md`.

## Step 2 — Voting: validators vote inside validation messages

[FAKTA] Only validators vote, and only votes from trusted validators
count. A validator advertises the amendments it supports by including
their IDs in the `sfAmendments` field of its `STValidation` messages.
Locally, the node decides what it votes for in
`AmendmentTableImpl::doValidation()` (`AmendmentTable.cpp:813-843`): it
votes for every supported, up-voted, not-yet-enabled amendment.

[FAKTA] The node's default vote comes from the macro: `DefaultYes` →
`AmendmentVote::up`, `DefaultNo` → `down`, `Obsolete` → `obsolete`.
Operators can override per amendment via the `[amendments]` (up-vote) and
`[veto_amendments]` (down-vote) config sections. A vetoed amendment is
never announced as supported.

[FAKTA] Votes are collected in `TrustedVotes` (`AmendmentTable.cpp:98-290`).
Two details matter: a validator's last-seen vote is held for 24 h after
its last validation (`static constexpr NetClock::duration expiresAfter =
24h;`, `AmendmentTable.cpp:172`), so a validator briefly going offline
near a flag ledger does not flap the count; and votes are keyed by
validator public key and only votes from validators in the trusted set
count.

[FAKTA] The `feature` RPC (`src/xrpld/rpc/handlers/Feature1.cpp`)
exposes per-amendment `supported` / `enabled` / `vetoed` / vote `count` /
`validations` / `threshold` — but the vote fields are admin-only
(`Feature1.cpp:48-95`). The public method returns only `enabled`, `name`,
`supported`. That is why this pack records enabled/disabled state and
activation records, but no live vote counts (NV1).

## Step 3 — The flag ledger: votes are tallied only around every 256th ledger

[FAKTA] `std::uint32_t constexpr FLAG_LEDGER_INTERVAL = 256;`
(`Ledger.h:426`). A ledger is a flag ledger when `info_.seq %
FLAG_LEDGER_INTERVAL == 0` (`Ledger.cpp:970-973`); the ledger before it
is the voting ledger (`Ledger.cpp:975-978`).

[FAKTA] The voting round is driven from consensus in
`RCLConsensus.cpp:364-377`: when the previous ledger was a flag ledger
and enough trusted validations are present (`validations.size() >=
app_.validators().quorum()`), the node calls
`app_.getAmendmentTable().doVoting(...)`, which injects `EnableAmendment`
pseudo-transactions (`ttAMENDMENT`) into the next open ledger.

[FAKTA] The local table only re-examines validated ledgers when a
flag-ledger boundary may have been crossed:
`return ((ledgerSeq - 1) / 256) != ((lastUpdateSeq_ - 1) / 256);`
(`AmendmentTable.cpp:944-949`, `needValidatedLedger`).

## Step 4 — Majority math: the 67% threshold

[FAKTA] `include/xrpl/protocol/SystemParameters.h:79-88`:

```cpp
constexpr std::ratio<204, 256> preFixAmendmentMajorityCalcThreshold;
constexpr std::ratio<67, 100> postFixAmendmentMajorityCalcThreshold;
constexpr std::chrono::seconds const defaultAmendmentMajorityTime = std::chrono::weeks{2};
```

[FAKTA] Which threshold applies depends on whether
`fixAmendmentMajorityCalc` itself is enabled in the ledger
(`AmendmentTable.cpp:325-341`, `computeThreshold`). The pass predicate is
strict once the fix is active (`AmendmentTable.cpp:360-377`): pre-fix an
amendment needs votes `>=` threshold; post-fix it needs votes `>`
threshold, where threshold = floor(67% × N) for N trusted validations.

[FAKTA] Upstream rippled 2.5.0 uses 80/100 post-fix — per the HEAD commit
message of this checkout and the xrpl.build documentation (fetched
2026-11-22). The upstream 80/100 constant was not read from an upstream
source tree (NV7). Pre-fix, PFTL and upstream agree (204/256 ≈ 80%).

[FAKTA] Worked boundary examples from the test suite
(`AmendmentTable_test.cpp:1460-1467`): with 16 trusted validators,
post-fix majority is first reached at 11 yes-votes (11 > floor(16×0.67)
= 10) and lost when yes-votes drop to 10; with 10 validators, 8
yes-votes are already a majority. The live threshold matters because
`fixAmendmentMajorityCalc` is enabled on the live testnet (see
`docs/amendment-activation.md`): the live rule is the 67% rule, and with
the live UNL of 25 validators an activation needs 17 yes-votes.

[ANALISIS] With a small validator set the integer rounding is decisive:
with 3 trusted validators, floor(3×0.67) = 2, so 3 votes are needed —
strictly more than 2 — i.e. unanimity. Do not quote "67%" without the
strict-greater-than and floor arithmetic.

## Step 5 — Majority gained / lost: the Amendments entry and the holding clock

[FAKTA] The on-ledger record is the single `Amendments` ledger entry,
which carries `sfAmendments` (enabled IDs) and `sfMajorities` (array of
`{Amendment, CloseTime}` for amendments holding a majority but not yet
enabled) — read back by `getEnabledAmendments()` /
`getMajorityAmendments()` in `src/libxrpl/ledger/View.cpp:1000-1041`.

[FAKTA] The three outcomes are decided in `AmendmentTableImpl::doVoting()`
(`AmendmentTable.cpp:847-941`) and executed by the `EnableAmendment`
pseudo-transaction handler `Change::applyAmendment()`
(`src/xrpld/app/tx/detail/Change.cpp:286-397`):

| Situation | Action (pseudo-tx flag) | On-ledger effect |
|---|---|---|
| Validators say yes, ledger shows no majority, local vote is up | `tfGotMajority` (`0x00010000`, `TxFlags.h:128`) | Majority entry added with `CloseTime` = parent close time; the holding clock starts (`Change.cpp:340-347`) |
| Validators say no, ledger shows a majority | `tfLostMajority` (`0x00020000`, `TxFlags.h:129`) | Majority entry removed; clock discarded, restarts from zero if support returns |
| Ledger shows a majority AND `majorityTime + majorityTime_ <= closeTime` AND local vote is up | no flag | Amendment appended to `sfAmendments` (permanently enabled); entry removed from `Majorities` |

[FAKTA] The holding test is exactly
`(*majorityTime + majorityTime_) <= closeTime`
(`AmendmentTable.cpp:918`). `majorityTime_` is the per-node configured
holding period, wired from `config().AMENDMENT_MAJORITY_TIME` in
`Application.cpp:1286-1291`. The code default is 2 weeks (`Config.h:248`),
but it is overridable per node in config (`[amendment_majority_time]`,
`Config.cpp:872-901`, units minutes/hours/days/weeks, minimum 15 minutes).

[FAKTA] PFTL testnet ships a 3-day holding time, not 2 weeks:
`cfg/postfiatd-testnet-full.cfg:1467-1469` (also `-light` / `-medium`).
Devnet configs set 2 hours; mainnet configs set no override, so mainnet
falls back to the 2-week code default. This is a config-level divergence,
not a code-level one.

[ANALISIS] The holding period is a local node configuration, so different
validators could in principle run different values; the ledger records
only the majority timestamp, and activation happens when a node that
votes "up" sees `majorityTime + its own majorityTime_ <= closeTime`.
Whether the live validators run the shipped 3-day value is not
established from ledger data (NV5).

[FAKTA] Edge case: if an amendment loses majority in the same round its
holding period completes, both pseudo-transactions are produced but the
amendment is ultimately enabled (the `doVoting` branches are evaluated
independently per amendment). Amendments can gain and lose a majority any
number of times before they become permanently enabled.

## Step 6 — Activation: permanent, one-way, applies from flag ledger +2

[FAKTA] Once enabled, an amendment cannot be disabled — "This is a
one-way switch: once an amendment is enabled it can never be disabled,
but it can be superseded by a subsequent amendment"
(`AmendmentTable.cpp:292-300`, `AmendmentState` comment). The enabled set
is read from the ledger into `Rules` for every subsequent ledger; the new
rules apply from the ledger after the enabling one.

[FAKTA] Activation is recorded in two places: on-ledger, the ID is
appended to the `Amendments` entry's `sfAmendments` vector
(`Change.cpp:355-359`); in-memory, `AmendmentTableImpl::enable()` sets
`s.enabled = true` (`AmendmentTable.cpp:762`). `doValidatedLedger()`
(`AmendmentTable.cpp:955-990`) then syncs the table from each validated
ledger.

[FAKTA] Genesis: a fresh network starts with the amendments passed to the
genesis ledger constructor (`Ledger.cpp:171-221`), which are the node's
desired amendments. Which amendments the PFTL testnet genesis actually
enabled is a ledger-data question, not answerable from source (NV6).

## Step 7 — Amendment blocked: what happens when the network enables something this node doesn't understand

[FAKTA] Two distinct states, both in `NetworkOPs`
(`src/xrpld/app/misc/NetworkOPs.cpp:1830-1860`):

- **Warned**: an amendment this node does not support has reached a
  majority. The node keeps working; the operator is warned with the
  expected activation time (`firstUnsupportedExpected_`).
- **Blocked**: an amendment this node does not support has been enabled.
  Set from `Change::applyAmendment()` (`Change.cpp:366-371`: "Unsupported
  amendment ... activated: server blocked.") and from
  `LedgerMaster::setValidLedger()`.

[FAKTA] A blocked server stops participating normally.
`NetworkOPsImp::isBlocked()` returns `isAmendmentBlocked() ||
isUNLBlocked()` (`NetworkOPs.cpp:1830`). The `server_info` output carries
`amendment_blocked: true` and the warning "This server is amendment
blocked, and must be updated to be able to stay in sync with the network."
(`NetworkOPs.cpp:2647`, `2811`). The only remedy is upgrading to a build
that supports the amendment.

[ANALISIS] "Amendment blocked" is a local node state, not a network
state — the network keeps going; the blocked node is the one left
behind. The PFTL relevance is sharp because the 67% threshold makes it
easier for an amendment to activate while some nodes are still on old
builds.
