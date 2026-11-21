# Claims

Every substantive claim in this pack, with its label and where its evidence
lives. The compact paste-ready table is `docs/claim-evidence-index.md`
(C1–C32 verified, E1–E3 estimates, NV1–NV15 not verified); this file is
the fuller record, grouped by subject. Labels: [FAKTA] verified with
source + date, [ESTIMASI] modelled/reported number, [ANALISIS]
interpretation. Nothing labelled [ANALISIS] or [ESTIMASI] is presented as
a measured fact, and nothing in the NV section is presented as verified.

## Live endpoints and validator list

- [FAKTA] C1–C7 (see the claim-evidence index): the VL, JSON-RPC,
  WebSocket, VHS, and explorer endpoints exist, answer, and return the
  values recorded in the collector log. The `postfiat.org` homepage's
  embedded network numbers are a stale snapshot and are not cited as
  live data.
- [ANALISIS] The public surface is: JSON-RPC on `rpc.testnet.postfiat.org`,
  WebSocket on `ws.testnet.postfiat.org`, REST (VHS) on
  `vhs.testnet.postfiat.org`, explorer on `explorer.testnet.postfiat.org`.
  There is no single host serving both JSON-RPC and WebSocket.

## Amendment state

- [FAKTA] C8–C14: 101 known / 64 enabled / 37 disabled; the on-ledger
  Amendments entry equals the enabled set; the VHS vote records equal the
  enabled set; all 64 activated at ledger 86785 on 2026-02-09T14:31:12Z;
  no amendment is in voting; both PFTL-only amendments are disabled;
  `fixAmendmentMajorityCalc` is enabled, so the live rule is post-fix 67%.
- [ANALISIS] The single-ledger activation of the whole enabled set is
  consistent with a genesis-era bulk enablement, but the genesis enabled
  set is not in the source checkout (NV6) and the activation ledger
  predates the RPC node's retained range, so "enabled at genesis" and
  "enabled by 64 pseudo-transactions in one flag-ledger round" cannot be
  distinguished from the data available. Neither is asserted.
- [ANALISIS] A validator set of 25 with a 67% strict rule needs 17
  yes-votes; a handful of validators changing their vote can move an
  amendment across the line. The 67% rule is materially easier than
  upstream's 80% (21 votes at N=25).

## Thresholds and lifecycle

- [FAKTA] C15–C23: the threshold constants, the holding test, the 3-day
  shipped testnet value, the 256-ledger flag interval, the SHA-512-Half ID
  derivation, the worked test-suite examples, the 24-hour vote cache, the
  one-way switch, and the amendment-blocked local state — all pinned to
  postfiatd commit 24c5487 file:line citations in `docs/SOURCES.md §3`.
- [ANALISIS] The holding time is a per-node local configuration, so the
  effective network holding time is a property of the validator set's real
  configs, not of the ledger alone (NV5). The ledger records only the
  majority timestamp.
- [ANALISIS] "Amendment blocked" is a local node state, not a network
  state. The 67% threshold makes it easier for an amendment to activate
  while some nodes are still on old builds.

## Inventory reconciliation

- [FAKTA] C24–C27: code 107, live 101, VHS info 103. The 107 → 101 gap is
  exactly the six `Supported::no` amendments. VHS knows two amendments the
  live node does not report: Batch (in code, `Supported::no`) and
  OrchardPrivacy (in neither code nor live). VHS marks 15 deprecated vs 16
  retired in code; FlowCross is the difference.
- [ANALISIS] The reconciliation is a set comparison, not a narrative: every
  ID in each set was compared mechanically by
  `scripts/generate_tables.py`, and the run fails on any mismatch. The one
  item the comparison cannot explain is OrchardPrivacy (NV14).

## UNL churn and NegativeUNL

- [FAKTA] C28–C32: VL keys equal VHS `unl: "rpc"` keys; churn 20 → 25
  (retained 12, exits 8, entrants 13); observed 50 → 66; zero Wayback
  captures of the VL URL; NegativeUNL now lists two disabled validators;
  the second disable executed between the 20:29 and 20:58 UTC fetches.
- [ANALISIS] The churn numbers are a lower bound on total movement: with
  only two snapshots, validators that entered and left between the two
  dates are invisible. Whether turnover was gradual or concentrated in
  one reconfiguration cannot be stated.
- [ANALISIS] Three of the eight exited UNL members carry the
  `postfiat.org` domain. That is a domain-string observation only;
  operator identity is not established from these data.
- [ANALISIS] A disabled-but-still-UNL validator is the normal NegativeUNL
  state: the entry removes the validator from the effective UNL for
  consensus while it stays in the published list. VHS `unl: "rpc"`
  reflects the published list, not the NegativeUNL-filtered effective set.
- [ESTIMASI] E1–E3: close cadence ~3 s/ledger; the ED4F62A8… disable date
  ≈ 2026-11-19T09:50:48Z; a 3-day holding time implies ~3-day activation
  timelines. Estimates, with methods stated.

## Not verified (NV1–NV15)

As listed in full in `docs/claim-evidence-index.md` and
`outputs/reconciliation.md`. In short: live per-amendment vote counts
(NV1); majority-pending/ETA beyond the negative finding (NV2); historical
VL snapshots and intra-window churn (NV3); the ledger-8180480 close time
(NV4); whether live validators run the shipped 3-day holding time (NV5);
the genesis enabled set (NV6); the upstream 80/100 file:line (NV7); the
PF_ amendments' absence upstream (NV8); the upstream 24-hour cache value
(NV9); historical VHS daily reports (NV10); a full WebSocket session
(NV11); a second independent RPC host (NV12); VL manifest contents (NV13);
OrchardPrivacy's presence in VHS (NV14); any majority-gained-then-lost
history (NV15).
