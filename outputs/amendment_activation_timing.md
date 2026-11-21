# Amendment activation timing

Activation records from the VHS vote endpoint
(`/v1/network/amendments/vote/test`), newest snapshot set in data/.

- Enabled amendments with an activation record: 64
- Distinct activation dates: 1 (2026-02-09T14:31:12.000Z)
- Distinct activation ledgers: 1 (86785)

Finding: all 64 currently enabled amendments activated in a single
ledger, 86785, at 2026-02-09T14:31:12.000Z. There is no spread of activation times to analyse
and no per-amendment activation sequence: the enabled set arrived
together. Any claim about individual activation dates, or about a
majority being gained and then lost before activation, would need
ledger history that is not available from the public endpoints tried
(see `reconciliation.md`, NV15). The activation ledger predates the
RPC node's retained range, so its close time cannot be re-read from
this node — the VHS date above is the source for the activation time.

Full per-amendment table (name, ID, date, ledger, EnableAmendment
transaction hash): `amendment_activation_timing.csv` (64 rows).
