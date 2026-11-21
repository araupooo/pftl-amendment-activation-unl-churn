# Amendment activation thresholds

How many yes-votes an amendment needs, for a given number N of trusted
validations, under the two majority rules in postfiatd.
Post-fix rule applies live: `fixAmendmentMajorityCalc` is enabled
(see `amendment_vote_counts.csv`), so the live rule is the 67%% column.
Sources: `include/xrpl/protocol/SystemParameters.h:83-88`,
`src/xrpld/app/misc/detail/AmendmentTable.cpp:325-341` (threshold),
`AmendmentTable.cpp:360-377` (strict `>` post-fix, `>=` pre-fix).
Worked N=16 (11 votes) and N=10 (8 votes) are the values pinned by
the test suite (`src/test/app/AmendmentTable_test.cpp:1460-1467`).
The live UNL has 25 validators, so a live activation needs 17 yes-votes.

| trusted validations (N) | post-fix threshold floor(N*67/100) | post-fix votes needed (strict >) | pre-fix threshold floor(N*204/256) | pre-fix votes needed (>=) |
|---:|---:|---:|---:|---:|
| 1 | 1 | 2 | 1 | 1 |
| 2 | 1 | 2 | 1 | 1 |
| 3 | 2 | 3 | 2 | 2 |
| 10 | 6 | 7 | 7 | 7 |
| 16 | 10 | 11 | 12 | 12 |
| 25 | 16 | 17 | 19 | 19 |

Holding time: once a majority is first recorded, it must be held
continuously until `majorityTime + majorityTime_ <= closeTime`
(`AmendmentTable.cpp:918`); the code default is 2 weeks
(`SystemParameters.h:88`, `Config.h:248`) and the shipped PFTL testnet
configs set 3 days (`cfg/postfiatd-testnet-full.cfg:1467-1469`).
Whether the live validators run that 3-day value is not established
from ledger data (see `reconciliation.md`, NV5).

Flag ledgers: every 256th ledger (`Ledger.h:426`); votes are tallied
in the round after a flag ledger (`RCLConsensus.cpp:364-377`).
Consensus quorum is a different number: `server_info` reports a
`validation_quorum` that moves as participation changes (it was 17,
then 16, across two calls on 2026-11-21). Do not confuse it with the
amendment threshold above.
