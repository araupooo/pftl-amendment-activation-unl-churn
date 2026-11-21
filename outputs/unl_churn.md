# UNL churn — 2026-07-17 to 2026-11-22

Two validator snapshots, both from the Validator History Service:
the Wayback capture of `/v1/network/validators/test` dated
2026-07-17 02:17:13 UTC (50 validators observed, UNL 20) and the live
fetch in the newest snapshot set in data/ (66 validators observed, UNL 25).
The published validator list itself has no archived copies (Wayback
availability check returns zero captures), so this two-point VHS
comparison is the only historical validator data available; there is
no series between the two dates and no churn can be stated for any
interval inside 2026-07-17 → 2026-11-22 (see `reconciliation.md`,
NV3). Keys are matched after base58 decoding (VHS node keys) to hex
(VL keys); a naive string comparison matches 0 of 25.

| measure | 2026-07-17 | 2026-11-22 | change |
|---|---:|---:|---:|
| validators observed by VHS | 50 | 66 | +16 |
| UNL members | 20 | 25 | +5 |
| domain-verified validators | 36 | 55 | +19 |
| retained UNL members | — | 12 | — |
| exited the UNL (still observed) | — | 8 | — |
| entered the UNL | — | 13 | — |
| of entrants, already observed 2026-07-17 as non-UNL | — | 3 | — |
| removed from VHS entirely | — | 6 | — |
| added to VHS, non-UNL | — | 12 | — |
| observed non-UNL on both dates | — | 21 | — |

Arithmetic: 12 retained + 13 entrants = 25 (current UNL);
12 retained + 8 exits = 20 (2026-07-17 UNL);
50 observed then − 6 removed + 22 added = 66 observed now.

Exited the UNL (8), all still observed, domains unchanged:
ED2B7028ECA94BB9037B26A9DFFD41B07241E727DFED21FAB049605CCC1F364A29 (moonli.me); ED39BF926D790DE77106064B4CF75617B766B07CA9D44AA07DB3CE2CBC344ECA6D (framatrading.com); ED5BA98C3D29F25ACAF011886A20AC8A57C4F8DDA6F2C0F16AA06C608AD04F86B0 (postfiat.org); ED5CDCBAA5617BE6436A8580F9AC87439D79030CE888B6108CA4ADF42AA0075544 (preaware.org); EDA5D70ED39138C923DBECDB1E60806ADFD25E16B05CA468E0CC01BA2E852F0381 (postfiat.org); EDB711D22AE5BFE95086264B7B74CBF22BAB2F78ACCD35B6704224DB1739AC7408 (postfiat.org); EDC4CD3A67B03A38891CF5D3004C6B0F6AC66BA9E89AEEB3FFAC242672C0629548 (pfthaploid.com); EDFED771CC629E5632AFE1499F5D556732FBF31634F1A5F1A0491011F1F50AE1CA (pft.xbtseal.com).

Entered the UNL (13): ED154DB8240191EED3FC5702FF029219945A879249EAA939B137D59B9415B75C3D (qwerky2233.github.io); ED18B80CFF66576DAA5AE73F96ADB3098FA49D244C2FB73DC99792702811C28576 (pft.hit0ri.xyz); ED201FD47A90901392A58BAD808EDA79AD739B304B3240FFD1F52C8B997AC9BB94 (iopo545454-del.github.io); ED2DB2949D5B399444E061314E400798E4EBA348A03E23763E5F7D3591D4609982 (pft.permanentupperclass.com); ED372A9FAC2AE88D4CABFB65022B0FB3E3ABE3DFBE27C8D5AC9EA557CA1CCCD2D6 (dex3333.github.io); ED4D4244B734459A6D88DA611B2F2D94951181E422381AB078FAF75A41F0470A59 (app.w.ai); ED4F62A8245E10D8543ED7530748755C41EBCFF16618A80F04E90AA962AD79B3AF (paymuslam.top); ED50A48CC2489D0B41F8E5EE9D5148FBA93BE628F9508431A160FD84C40FA803CB (postfiat.maro.dpdns.org); ED62AA9FB11485503BF7D1878F175888463DB4559480DCF5F1E8C972E89E52C19B (local-maxi.github.io); ED6B25E466E4DC2CC3979995F8A6A8D7551B39F384FC0304E7279D95CBF2E45175 (parshant.com); ED921B111B30DE15BF1D7D0CF7267FF8357045C4F7FE83D220F48C97A6C5B7D974 (pft.thedarkmatter.xyz); EDCE5B0D1AA64FED94E00D9AB446567F84A3FFC22C598CDB3183459794081A3658 (hamedminasli.duckdns.org); EDEF0DC9039DF38468BEDFA1AB0A28173874CC2DA36E669971F5445396D9166857 (postfiatd.devflows.dedyn.io).

Removed from VHS entirely (6), all non-UNL in July:
ED0C3BCDC5018BADB409E743EE9A5D13F46FDF2696670D3A4EC3DF42F469DA4076 (shakeislucky.github.io, 30d agreement 1.00000); ED6932E77B2FB640D2C12870F681E5C651EAEE4AF16C5BB523B7A32758B118E478 (None, 30d agreement 1.00000); ED93B3C09A98C715BAA3C5F10F613AFF8504584DB9AF3733931E49EE3B25EE9A95 (validator.jackieluong.com, 30d agreement 0.97901); EDAFC530DD5F623F21E8874183713A50DAEFE2E9220D320F1462983E1B80A24043 (app.w.ai, 30d agreement 0.99880); EDD7D5792A81E0AE97D481EF68502080BF178CDF6E95D65B5898C80508025C390D (agtico.github.io, 30d agreement 0.97656); EDF268F7829F29390128FEE605833E6FB95C5192EC5A0E762B06EAE6C0A598FC8E (bees13.kiryuuki.space, 30d agreement 0.91306).

Note on the exited members: three carry the `postfiat.org` domain.
That is a domain-string observation only; operator identity is not
established from these data.

The live VL (sequence 30, effective 2026-11-17T20:10:08+00:00) is byte-identical to the
vendored 2026-11-20 reference copy (SHA-256
`5d4f5a18a18fead4105e5dc00cf7e11a71b9be4bc140357d1b4ea12116df59e7`,
14,781 bytes): zero UNL churn between the two VL fetches. The churn
above is therefore entirely in the 2026-07-17 → 2026-11-20 window,
with the 2026-11-20 → 2026-11-22 leg showing no change.

Full per-validator table: `unl_churn.csv` (72 rows).
