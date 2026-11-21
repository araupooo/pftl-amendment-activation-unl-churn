# Sources

- [FAKTA] All live-data access below is dated 2026-11-21/22. The committed
  snapshot set used by the tables in this pack is `20261121T211420Z`
  (2026-11-21 21:14:20 UTC / 2026-11-22 04:14:20 WIB), fetched by
  `scripts/collect_snapshots.py`; its unedited log is
  `outputs/collect_snapshots.log`. Earlier sets from the same evening
  (`20261121T205824Z`, `20261121T210022Z`, `20261121T211206Z`) are also in
  `data/`; the sets agree on every tabled value except the live ledger
  sequence and the rolling agreement scores.
- [FAKTA] Every substantive claim in this pack that rests on a source below
  carries its section, page, or line reference here, so the claim can be
  re-checked without re-doing the search.
- Scope note: this file is technical-only. It lists primary sources and
  access notes only.

## 1. Live endpoints (fetched by the collector, pure JSON bodies in `data/`)

- [FAKTA] Published validator list: `https://postfiat.org/testnet_vl.json`.
  Committed fetch: HTTP 200, 14,781 bytes, SHA-256
  `5d4f5a18a18fead4105e5dc00cf7e11a71b9be4bc140357d1b4ea12116df59e7`,
  sequence 30, 25 validators, publisher
  `ED3F1E0DA736FCF99BE2880A60DBD470715C0E04DD793FB862236B070571FC09E2`,
  effective 2026-11-17T20:10:08Z, expiration 2028-03-31T16:14:53Z.
  File: `data/20261121T211420Z_testnet_vl.json`.
- [FAKTA] JSON-RPC: `https://rpc.testnet.postfiat.org` (POST). Methods used:
  `server_info`, `feature`, `ledger` (validated), `ledger_entry` with the
  constant hex indexes `7DB0788C020F02780A673DC74757F23823FA3014C1866E72CC4CD8B226CD6EF4`
  (Amendments entry) and
  `2E8A59AA9D3B5B186B0B9E0F62E6C02587CA74A4D778938E957B6357D364B244`
  (NegativeUNL entry). Committed fetch: build `1.0.9`, network ID 2025,
  `server_state` "full", validated ledger 8251750 at collection time,
  `validation_quorum` 16, peers 21.
  Files: `data/20261121T211420Z_rpc_*.json`.
- [FAKTA] WebSocket: `wss://ws.testnet.postfiat.org`. Upgrade probe via curl:
  HTTP 101 Switching Protocols, `Server: postfiatd-1.0.9` (see the collector
  log). No method was executed over WebSocket. The JSON-RPC host itself
  rejects WebSocket upgrades with 401 "Invalid protocol." (probed
  2026-11-21 20:25:41 UTC, recorded in the research notes cited in §6).
- [FAKTA] Validator History Service: `https://vhs.testnet.postfiat.org`,
  version `0.0.1-beta.0`. Endpoints used: `/` (root),
  `/v1/network/validators/test`, `/v1/network/amendments/vote/test`,
  `/v1/network/amendments/info`, `/v1/network/validator_reports`.
  Files: `data/20261121T211420Z_vhs_*.json`.
- [FAKTA] Block explorer: `https://explorer.testnet.postfiat.org/amendments`
  returns HTTP 200 but a 2,454-byte JavaScript SPA shell; amendment data
  loads client-side from the VHS vote endpoint. File:
  `data/explorer_amendments_20261121.html` (fetched 2026-11-21 20:28 UTC).
  The explorer source (`postfiatorg/explorer`,
  `src/containers/Amendments/index.tsx`, fetched via GitHub API 2026-11-21
  20:34 UTC) fetches
  `` `${process.env.VITE_DATA_URL}/amendments/vote/${network}` `` and splits
  the list into "enabled" (`!a.voted`) and "voting" (`a.voted`) tabs.

## 2. Vendored reference files in `data/`

- [FAKTA] `data/testnet_vl_20261120_reference.json` — the live VL as fetched
  2026-11-20 (sequence 30, 14,781 bytes, SHA-256
  `5d4f5a18a18fead4105e5dc00cf7e11a71b9be4bc140357d1b4ea12116df59e7`).
  The collector compares each live fetch byte-for-byte against this copy.
- [FAKTA] `data/wayback_vhs_validators_20260717.json` — the single Wayback
  Machine capture of the VHS validators endpoint, timestamp
  20260717021713 (2026-07-17 02:17:13 UTC), HTTP 200, 38,850 bytes,
  50 validators, UNL 20, `current_index` 4599220. Fetched via
  `https://web.archive.org/web/20260717021713id_/https://vhs.testnet.postfiat.org/v1/network/validators/test`.
- [FAKTA] `data/amendment_inventory.csv` — 107 amendments registered in
  postfiatd at commit 24c5487 (see §3), with IDs recomputed as SHA-512-Half
  of the registered name. `scripts/generate_tables.py` recomputes all 107
  IDs and fails the run on any mismatch (0 mismatches in the committed run).

## 3. postfiatd source (pinned commit)

- [FAKTA] Checkout: postfiatd at commit
  `24c5487d9bfc99171380960e4eeb1543a724cfae` ("Update AmendmentTable
  boundary tests for the 67% majority threshold", 13 Nov 2026). All
  file:line citations below were verified with `grep -n` on that checkout
  on 2026-11-22.
- [FAKTA] Thresholds: `include/xrpl/protocol/SystemParameters.h:83`
  (`preFixAmendmentMajorityCalcThreshold`, 204/256), `:85`
  (`postFixAmendmentMajorityCalcThreshold`, 67/100), `:88`
  (`defaultAmendmentMajorityTime`, 2 weeks).
- [FAKTA] ID derivation: `src/libxrpl/protocol/Feature.cpp:266`
  (`sha512Half` of the registered name); registration macros `:437-440`;
  retired amendments via `retireFeature()` (`:417-421`).
- [FAKTA] Threshold application and pass rule:
  `src/xrpld/app/misc/detail/AmendmentTable.cpp:325-341`
  (`computeThreshold`), `:360-377` (`passes`: `>=` pre-fix, strict `>`
  post-fix), `:172` (trusted-vote cache `expiresAfter = 24h`),
  `:813-843` (`doValidation`), `:847-941` (`doVoting`), `:908`/`914`
  (`tfGotMajority` / `tfLostMajority`), `:918` (holding test
  `(*majorityTime + majorityTime_) <= closeTime`), `:944-949`
  (`needValidatedLedger`), `:955-990` (`doValidatedLedger`), `:292-300`
  (one-way switch comment).
- [FAKTA] Pseudo-transaction flags:
  `include/xrpl/protocol/TxFlags.h:128-129` (`tfGotMajority = 0x00010000`,
  `tfLostMajority = 0x00020000`).
- [FAKTA] EnableAmendment application:
  `src/xrpld/app/tx/detail/Change.cpp:340-347` (majority CloseTime),
  `:355-359` (append to `sfAmendments`), `:366-371` (unsupported amendment
  activated → `setAmendmentBlocked()`).
- [FAKTA] Flag ledgers: `src/xrpld/app/ledger/Ledger.h:426`
  (`FLAG_LEDGER_INTERVAL = 256`); `src/xrpld/app/ledger/Ledger.cpp:970-983`
  (`isFlagLedger`, `isVotingLedger`); voting round driven from
  `src/xrpld/app/consensus/RCLConsensus.cpp:364-377`.
- [FAKTA] Amendments ledger entry:
  `src/libxrpl/ledger/View.cpp:1000-1041` (`getEnabledAmendments`,
  `getMajorityAmendments`); genesis seeding
  `src/xrpld/app/ledger/Ledger.cpp:171-221`.
- [FAKTA] Holding-time configuration: `src/xrpld/core/Config.h:248`
  (`AMENDMENT_MAJORITY_TIME`, default 2 weeks);
  `src/xrpld/core/detail/Config.cpp:872-901` (`[amendment_majority_time]`
  parsing, minimum 15 minutes); wired in
  `src/xrpld/app/main/Application.cpp:1286-1291`.
- [FAKTA] Shipped testnet holding time: `cfg/postfiatd-testnet-full.cfg:1467-1469`
  (`[amendment_majority_time]`, `3 days`; identical in `-light` and
  `-medium`). Devnet configs set 2 hours; mainnet configs
  (`cfg/postfiatd-mainnet-*.cfg`) contain no `[amendment_majority_time]`
  section, so mainnet falls back to the 2-week code default.
- [FAKTA] Network IDs: `cfg/postfiatd-testnet-full.cfg:1464-1465`
  (`[network_id] 2025`); `cfg/postfiatd-mainnet-full.cfg:1459-1460` (2026).
- [FAKTA] Amendment-blocked state: `src/xrpld/app/misc/NetworkOPs.cpp:1830`
  (`isBlocked`), `:1834-1840`, `:2647`, `:2811-2812`
  (`amendment_blocked: true` in `server_info`).
- [FAKTA] Admin-only vote fields: `src/xrpld/rpc/handlers/Feature1.cpp:48-95`
  (majority status and `vetoed` handling; the public method omits them).
- [FAKTA] Worked threshold examples: `src/test/app/AmendmentTable_test.cpp:1460-1467`
  (11/16 yes-votes a majority only under the 67% rule).
- [FAKTA] Amendment inventory: `include/xrpl/protocol/detail/features.macro`
  (41 `XRPL_FEATURE` + 50 `XRPL_FIX` + 16 `XRPL_RETIRE` = 107, counted by
  anchored `grep -c` on 2026-11-22).

## 4. Wayback Machine

- [FAKTA] VL URL availability:
  `https://archive.org/wayback/available?url=postfiat.org/testnet_vl.json`
  returns `{"archived_snapshots": {}}` (checked 2026-11-21 20:24 and 20:35
  UTC, and again by the collector on 2026-11-21 21:00 UTC). CDX query
  `https://web.archive.org/cdx/search/cdx?url=postfiat.org/testnet_vl.json&output=json&fl=timestamp,original,statuscode,digest,length&collapse=digest`
  returns `[]`. Zero captures.
- [FAKTA] VHS validators endpoint CDX query returned exactly one capture:
  timestamp 20260717021713, status 200 (see §2).

## 5. Upstream XRPL documentation (fetched 2026-11-22)

- [FAKTA] `https://www.xrpl.build/docs/concepts/networks-and-servers/amendments`
  ("more than 80% support for two weeks", flag-ledger process, amendment-blocked
  servers). This is the source for the upstream 80% / 2-week figures; no
  upstream rippled source tree was read (see NV7 in `docs/claim-evidence-index.md`).
- [FAKTA] `https://xrpl.org/docs/references/protocol/ledger-data/ledger-entry-types/amendments`
  (Amendments entry format; the constant entry indexes used by the collector;
  six amendment IDs spot-checked against it match the SHA-512-Half derivation).

## 6. Collection notes relied on (2026-11-21/22 research)

- [FAKTA] The 2026-11-21 ~20:24–20:35 UTC collection window: the 401
  WebSocket-upgrade response from the RPC host (20:25:41 UTC), the
  single-amendment `feature` probes (Escrow, PF_ValidatorVoteTracking —
  neither carries `majority`/`vetoed`), the VHS 404 for a non-enabled
  amendment by name and by ID, the `lgrNotFound` response for ledger
  8180480, the `malformedRequest` responses for the `"index": "Amendments"`
  and `{"amendments": true}` shortcuts, the ledger close cadence
  (~2 ledgers per 6.0 s, i.e. ~3 s/ledger), the postfiat.org homepage's
  stale embedded snapshot ("snapshot Sep 21, 2026: 53 validators"), and
  the NegativeUNL state at 20:29 UTC (one disabled validator, ED4F62A8…,
  plus pending `ValidatorToDisable` ED372A9F…) were all observed in that
  window and are recorded in the research notes
  (`~/workspace/research_notes/pftl-governance-live-data-20261122/endpoints-and-data.md`).
  The pack's own collector re-verified the live state at 21:00 UTC; the
  NegativeUNL entry had changed by then (see `outputs/negative_unl.md`).
- [FAKTA] The amendment-lifecycle research
  (`~/workspace/research_notes/pftl-governance-lifecycle-20261122/lifecycle.md`)
  inventoried the same 107 amendments and the same thresholds from the
  same pinned checkout; every file:line it cites was re-verified with
  `grep -n` on 2026-11-22 before being used here.
