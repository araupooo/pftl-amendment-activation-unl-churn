# NegativeUNL

On-ledger NegativeUNL entry (index
`2E8A59AA9D3B5B186B0B9E0F62E6C02587CA74A4D778938E957B6357D364B244`),
newest snapshot set in data/.

| field | value |
|---|---|
| disabled validators | 2 |
| ValidatorToDisable | none pending |
| PreviousTxnID | F56B2FE62632F8594A27CA061D8FE81D07E163450C0539536D2F09B159555480 |
| PreviousTxnLgrSeq | 8250624 |

Disabled validators:
- `ED4F62A8245E10D8543ED7530748755C41EBCFF16618A80F04E90AA962AD79B3AF`, FirstLedgerSequence 8180480, VHS domain `paymuslam.top`, 24h agreement `0.00000`
- `ED372A9FAC2AE88D4CABFB65022B0FB3E3ABE3DFBE27C8D5AC9EA557CA1CCCD2D6`, FirstLedgerSequence 8250880, VHS domain `dex3333.github.io`, 24h agreement `0.91368`

State change observed during collection: an earlier fetch at
2026-11-21 20:29 UTC showed one disabled validator (ED4F62A8…,
FirstLedgerSequence 8180480) and `ValidatorToDisable` ED372A9F…
(domain `dex3333.github.io`, 24h agreement 0.95438). In this snapshot
set ED372A9F… is a second disabled entry with FirstLedgerSequence
8250880, and no `ValidatorToDisable` is pending. All disabled keys
are members of the current VL (sequence 30).

The disable date of the first entry cannot be read from this RPC
node: ledger 8180480 is outside its retained range, and the node
answers `lgrNotFound` for it (verified 2026-11-21 20:35 UTC). An
estimate from the ledger gap is given in `reconciliation.md` (NV4)
and is labelled [ESTIMASI], not a measured date. The second entry's
FirstLedgerSequence (8250880) sits 26 ledgers after the validated
ledger of the 20:29 UTC fetch (8250854) and before the validated
ledger of the 20:58 UTC fetch (8251434) — consistent with the
disable executing between the two fetches.

Full table: `negative_unl.csv` (2 rows).
