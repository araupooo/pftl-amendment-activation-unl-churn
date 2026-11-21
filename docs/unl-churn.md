# UNL churn

How the PFTL testnet validator set changed between the only two
validator snapshots available: the Wayback capture of the Validator
History Service validators endpoint (2026-07-17 02:17:13 UTC) and the
live fetch in snapshot set `20261121T211420Z` (2026-11-21 21:14:20 UTC).
Tables: `outputs/unl_churn.*`, `outputs/negative_unl.*`.
Sources: `docs/SOURCES.md`.

Labels: [FAKTA] verified against a named source, [ESTIMASI] modelled or
reported number, [ANALISIS] interpretation.

## The two snapshots

[FAKTA] 2026-07-17 (Wayback capture, `data/wayback_vhs_validators_20260717.json`):
50 validators observed by VHS, UNL 20, 36 domain-verified,
`current_index` 4599220, versions 1.0.4-era.

[FAKTA] 2026-11-21 (live fetch, `data/20261121T211420Z_vhs_validators_test.json`):
66 validators observed, UNL 25, 55 domain-verified, versions 1.0.9 ×54,
1.0.4 ×9, 1.0.0 ×2, 1.0.8 ×1, 0 revoked, 1 partial.

[FAKTA] The UNL is identified two independent ways and they agree
exactly: the 25 keys in the published validator list (sequence 30) are
exactly the 25 validators VHS marks `unl: "rpc"` (set equality verified
by `scripts/generate_tables.py` after base58 decoding of the VHS node
keys — the VL uses `ED…` hex, VHS uses base58 `nH…`/`n9…` keys; a naive
string comparison matches 0 of 25).

[FAKTA] The published validator list itself has no archived copies:
the Wayback availability API returns zero captures for
`postfiat.org/testnet_vl.json`. The two-point VHS comparison below is
therefore the only historical validator data available. There is no
series between the two dates, and no churn can be stated for any interval
inside 2026-07-17 → 2026-11-22 (NV3).

## Churn, 2026-07-17 → 2026-11-22

[FAKTA] UNL: 20 → 25. Retained 12, exited 8, entered 13.
Arithmetic: 12 + 13 = 25; 12 + 8 = 20.

[FAKTA] Observed validators: 50 → 66. Added 22, removed 6.
Arithmetic: 50 − 6 + 22 = 66. Of the 22 added, 10 are UNL entrants and 12
are non-UNL additions; of the 13 entrants, 3 were already observed in
July as non-UNL members (ED154DB8…, ED18B80C…, ED2DB294…).

[FAKTA] Retained UNL members (12): ED004DBF… (jollydinger.com),
ED123A54… (pftmeech.xyz), ED21D237… (sendoeth.com), ED518DF3…
(pft.bigwoodnode.com), ED6F750D… (pft.akirax.xyz), ED937429…
(validator.pftperry.com), ED988B29… (auri0x.io), EDA76CF4…
(pft.whiteguy.eu), EDAC24E2… (lc66validator.postfiatcn.org), EDD81DA4…
(pft.wizbubba.xyz), EDE79A06… (postfiat.live), EDE8F9E7…
(snakespartan.pftoligarchy.com).

[FAKTA] Exited the UNL (8) — all still observed in VHS, all with
unchanged domains: ED2B7028… (moonli.me), ED39BF92… (framatrading.com),
ED5BA98C… (postfiat.org), ED5CDCBA… (preaware.org), EDA5D70E…
(postfiat.org), EDB711D2… (postfiat.org), EDC4CD3A… (pfthaploid.com),
EDFED771… (pft.xbtseal.com).

[FAKTA] Entered the UNL (13): ED154DB8… (qwerky2233.github.io),
ED18B80C… (pft.hit0ri.xyz), ED201FD4… (iopo545454-del.github.io),
ED2DB294… (pft.permanentupperclass.com), ED372A9F… (dex3333.github.io),
ED4D4244… (app.w.ai), ED4F62A8… (paymuslam.top), ED50A48C…
(postfiat.maro.dpdns.org), ED62AA9F… (local-maxi.github.io), ED6B25E4…
(parshant.com), ED921B11… (pft.thedarkmatter.xyz), EDCE5B0D…
(hamedminasli.duckdns.org), EDEF0DC9… (postfiatd.devflows.dedyn.io).

[FAKTA] Removed from VHS entirely (6), all non-UNL in July: ED0C3BCD…
(shakeislucky.github.io, 30d agreement 1.00000), ED6932E7… (no domain,
1.00000), ED93B3C0… (validator.jackieluong.com, not domain-verified, 30d
0.97901), EDAFC530… (app.w.ai, 30d 0.99880), EDD7D579… (agtico.github.io,
30d 0.97656), EDF268F7… (bees13.kiryuuki.space, 30d 0.91306).

[FAKTA] Added to VHS, non-UNL (12): ED1E4ECB… (pf-chika2.ligaya.online),
ED21D751… (paperlantern.cloud), ED5F7E8F… (asename.space), ED663ADC…
(pf-ten3.ligaya.online), ED6F500A… (pf-ten2.ligaya.online), ED9743AF…
(pf-chika1.ligaya.online), ED9ADFCE… (pft.gammaphoenix.com), ED9CDBD9…
(pf-one.kiryuuki.space), EDAE0B84… (no domain), EDB46691…
(pf-ten1.ligaya.online), EDBD3988… (pf-two.kiryuuki.space), EDEA5F55…
(pf-chika3.ligaya.online).

[FAKTA] 15 of the current 25 VL keys were present in the July snapshot at
all; 10 are new to VHS entirely. 21 validators were observed non-UNL on
both dates.

[ANALISIS] Three of the eight exited UNL members carry the `postfiat.org`
domain. That is an inference from the domain string, not a confirmed
operator identity — the domains are self-asserted in validator manifests
and VHS domain verification only proves control of the domain, not who
operates the node.

[ANALISIS] The churn is large for a four-month window — 40% of the July
UNL left it, and over half the current UNL joined it — but with only two
snapshots it is impossible to say whether the turnover was gradual or
concentrated in one reconfiguration, or how many validators entered and
left between the two dates without being visible in either. The numbers
are a lower bound on total movement, not a complete history.

## Zero churn in the short leg

[FAKTA] The live VL (sequence 30) is byte-identical to the vendored
2026-11-20 reference copy (SHA-256
`5d4f5a18a18fead4105e5dc00cf7e11a71b9be4bc140357d1b4ea12116df59e7`,
14,781 bytes): zero UNL churn between the 2026-11-20 and 2026-11-21/22
fetches. All of the churn above therefore falls in the 2026-07-17 →
2026-11-20 window; the 2026-11-20 → 2026-11-22 leg shows no change.

## NegativeUNL

[FAKTA] The on-ledger NegativeUNL entry now lists two disabled
validators, both members of the current VL:

- ED4F62A8… (paymuslam.top), FirstLedgerSequence 8180480, 24h agreement
  0.00000 — fully offline in the last 24 hours.
- ED372A9F… (dex3333.github.io), FirstLedgerSequence 8250880, 24h
  agreement 0.95438.

[FAKTA] The second disable happened while this pack was being built: an
earlier fetch at 2026-11-21 20:29 UTC showed one disabled validator and
`ValidatorToDisable` ED372A9F…; the 20:58 UTC fetch showed the disable
executed (FirstLedgerSequence 8250880) and no validator pending disable.
The second entry's FirstLedgerSequence (8250880) sits 26 ledgers after
the validated ledger of the 20:29 UTC fetch (8250854) and before the
validated ledger of the 20:58 UTC fetch (8251434) — consistent with the
disable executing between the two fetches.

[FAKTA] The disable date of the first entry cannot be read from this RPC
node (ledger 8180480 is outside its retained range; the node answers
`lgrNotFound`). [ESTIMASI] From the ledger gap (70,954 ledgers × ~3
s/ledger ≈ 2.5 days before the validated ledger 8251434 of the earliest
snapshot set in data/, close 2026-11-21T20:58:30Z), the disable happened
around 2026-11-19T09:50:48Z.
Estimate only; see NV4.

[ANALISIS] A disabled-but-still-UNL validator is the normal NegativeUNL
state: the entry removes the validator from the effective UNL for
consensus while it stays in the published list, so the list and the
effective set differ by exactly the disabled keys. Both disabled keys
here are still VHS `unl: "rpc"` — the VHS `unl` field reflects the
published list, not the NegativeUNL-filtered effective set.
