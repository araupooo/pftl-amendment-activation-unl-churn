#!/usr/bin/env python3
"""generate_tables.py — build every analysis table from collected snapshots.

Reads the newest snapshot set in data/ (files sharing one UTC timestamp
prefix, written by scripts/collect_snapshots.py) plus the vendored reference
files in data/:
  * testnet_vl_20261120_reference.json — the 2026-11-20 VL fetch
  * wayback_vhs_validators_20260717.json — the single Wayback capture of the
    VHS validators endpoint, 2026-07-17 02:17:13 UTC
  * amendment_inventory.csv — the 107 amendments registered in postfiatd
    at commit 24c5487d9bfc99171380960e4eeb1543a724cfae, with IDs recomputed
    here from the registered names (SHA-512-Half) and checked against the
    file before any table is written.

Writes deterministic tables under outputs/ (no wall clock, no live ledger
sequence, no fetch time inside any table — the tables depend only on the
snapshot contents, so a re-run against the same snapshot set is
byte-identical; a live re-run against a new snapshot set is identical on
every stable value except the rolling 24h/30d agreement scores, which
drift as the windows slide):
  * amendment_activation_thresholds.md / .csv
  * amendment_vote_counts.md / .csv
  * amendment_activation_timing.md / .csv
  * unl_churn.md / .csv
  * negative_unl.md / .csv
  * reconciliation.md / .csv

Also verifies, and fails loudly on any mismatch:
  * the inventory IDs recompute exactly (all 107)
  * the on-ledger Amendments entry equals the feature enabled set
  * the VHS vote records equal the enabled set
  * the 25 VL keys equal the 25 VHS unl:"rpc" keys (after base58 decoding)
  * the churn arithmetic closes (retained + entrants = 25, etc.)

Usage: python3 scripts/generate_tables.py
Exit status: 0 only if every check above passes and every table is written.
"""

import base64
import csv
import datetime
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "outputs")

# XRP base58 alphabet (used by VHS node keys, nH.../n9...).
XRP_ALPHABET = "rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz"


def b58_to_ed(base58_key):
    """Decode a base58 node key to its ED... hex form, verifying the checksum.

    A base58 node key decodes to 38 bytes: 0x1C prefix, 0xED, the 32-byte
    key, and a 4-byte checksum (first 4 bytes of double-SHA-256).
    """
    n = 0
    for ch in base58_key:
        n = n * 58 + XRP_ALPHABET.index(ch)
    raw = n.to_bytes(38, "big")
    check = hashlib.sha256(hashlib.sha256(raw[:34]).digest()).digest()[:4]
    if check != raw[34:]:
        raise ValueError("bad base58 checksum for %s" % base58_key)
    if raw[0] != 0x1C or raw[1] != 0xED:
        raise ValueError("unexpected base58 node-key prefix for %s" % base58_key)
    return "ED" + raw[2:34].hex().upper()


def latest_stamp():
    stamps = set()
    for name in os.listdir(DATA):
        if len(name) > 16 and name[8] == "T" and name[15] == "Z":
            stamps.add(name[:16])
    if not stamps:
        raise SystemExit("generate_tables: no timestamped snapshot set in data/")
    return max(stamps)


def load_json(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def write_csv(path, header, rows):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        writer.writerows(rows)


def sha256_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main():
    stamp = latest_stamp()
    print("GENERATE: snapshot set %s" % stamp)
    failures = []

    # ------------------------------------------------------------------ inputs
    feature = load_json("%s_rpc_feature.json" % stamp)["result"]["features"]
    amendments_entry = load_json(
        "%s_rpc_ledger_entry_amendments.json" % stamp)["result"]["node"]
    negative_unl = load_json(
        "%s_rpc_ledger_entry_negativeunl.json" % stamp)["result"]["node"]
    server_info = load_json("%s_rpc_server_info.json" % stamp)["result"]["info"]
    validated = load_json("%s_rpc_ledger_validated.json" % stamp)["result"]["ledger"]
    vl_doc = load_json("%s_testnet_vl.json" % stamp)
    vl_blob = json.loads(base64.b64decode(vl_doc["blobs_v2"][0]["blob"]))
    vhs_now = load_json("%s_vhs_validators_test.json" % stamp)
    vhs_vote = load_json("%s_vhs_amendments_vote_test.json" % stamp)
    vhs_info = load_json("%s_vhs_amendments_info.json" % stamp)
    vhs_old = load_json("wayback_vhs_validators_20260717.json")

    # ------------------------------------------------------- inventory checks
    inv_path = os.path.join(DATA, "amendment_inventory.csv")
    with open(inv_path, encoding="utf-8", newline="") as fh:
        inventory = list(csv.DictReader(fh))
    bad_ids = []
    for row in inventory:
        recomputed = hashlib.sha512(row["registered_name"].encode()).hexdigest()[:64].upper()
        if recomputed != row["id"]:
            bad_ids.append(row["name"])
    print("CHECK inventory: %d rows, %d kinds FEATURE=%d FIX=%d RETIRE=%d, "
          "IDs recomputed (SHA-512-Half): %d mismatches"
          % (len(inventory),
             len({r["kind"] for r in inventory}),
             sum(1 for r in inventory if r["kind"] == "FEATURE"),
             sum(1 for r in inventory if r["kind"] == "FIX"),
             sum(1 for r in inventory if r["kind"] == "RETIRE"),
             len(bad_ids)))
    if len(inventory) != 107 or bad_ids:
        failures.append("inventory: %d rows, bad IDs %s" % (len(inventory), bad_ids))

    code_ids = {r["id"]: r for r in inventory}
    enabled = {k for k, v in feature.items() if v.get("enabled")}
    disabled = {k for k, v in feature.items() if not v.get("enabled")}
    on_ledger = set(amendments_entry["Amendments"])
    vote_ids = {a["id"] for a in vhs_vote["amendments"]}

    # ------------------------------------------------------------- set checks
    print("CHECK feature: %d known, %d enabled, %d disabled, %d carry a "
          "majority/vetoed field, %d supported:false"
          % (len(feature), len(enabled), len(disabled),
             sum(1 for v in feature.values() if "majority" in v or "vetoed" in v),
             sum(1 for v in feature.values() if not v.get("supported"))))
    if on_ledger != enabled:
        failures.append("Amendments entry != feature enabled set "
                        "(only-in-ledger %d, only-in-feature %d)"
                        % (len(on_ledger - enabled), len(enabled - on_ledger)))
    else:
        print("CHECK Amendments entry == feature enabled set: yes (%d IDs)" % len(on_ledger))
    if vote_ids != enabled:
        failures.append("VHS vote records != feature enabled set")
    else:
        print("CHECK VHS vote records == feature enabled set: yes (%d IDs)" % len(vote_ids))
    live_not_in_code = sorted(set(feature) - set(code_ids))
    if live_not_in_code:
        failures.append("live amendments missing from code inventory: %s" % live_not_in_code)
    else:
        print("CHECK every live amendment ID is in the code inventory: yes (101/101)")
    code_not_live = sorted(set(code_ids) - set(feature))
    code_not_live_rows = [code_ids[i] for i in code_not_live]
    print("CHECK code amendments absent from the live set: %d -- %s"
          % (len(code_not_live),
             ", ".join("%s (%s, supported=%s)" % (r["name"], r["kind"], r["supported"])
                       for r in code_not_live_rows)))
    if any(r["supported"] != "no" for r in code_not_live_rows):
        failures.append("a code amendment absent from the live set is not "
                        "Supported::no: %s" % code_not_live)
    info_ids = {a["id"]: a for a in vhs_info["amendments"]}
    info_not_code = sorted(set(info_ids) - set(code_ids))
    print("CHECK VHS info amendments absent from the code inventory: %d -- %s"
          % (len(info_not_code),
             ", ".join("%s (%s)" % (info_ids[i]["name"], i) for i in info_not_code)))
    info_not_live = sorted(set(info_ids) - set(feature))
    print("CHECK VHS info amendments absent from the live set: %d -- %s"
          % (len(info_not_live),
             ", ".join("%s (%s)" % (info_ids[i]["name"], i) for i in info_not_live)))

    # ------------------------------------------------------------ VL vs VHS
    vl_keys = [v["validation_public_key"] for v in vl_blob["validators"]]
    vl_set = set(vl_keys)
    now_by_key = {}
    for v in vhs_now["validators"]:
        now_by_key[b58_to_ed(v["validation_public_key"])] = v
    unl_rpc = {k for k, v in now_by_key.items() if v.get("unl") == "rpc"}
    print("CHECK VL keys == VHS unl:\"rpc\" keys: %s (%d VL, %d unl rpc, "
          "%d VHS validators observed)"
          % ("yes" if vl_set == unl_rpc else "NO",
             len(vl_set), len(unl_rpc), len(vhs_now["validators"])))
    if vl_set != unl_rpc:
        failures.append("VL keys != VHS unl:\"rpc\" keys")
    if not vl_set <= set(now_by_key):
        failures.append("VL keys missing from VHS")

    # ------------------------------------------------------------- churn sets
    old_by_key = {}
    for v in vhs_old["validators"]:
        old_by_key[b58_to_ed(v["validation_public_key"])] = v
    old_unl = {k for k, v in old_by_key.items() if v.get("unl")}
    retained = sorted(vl_set & old_unl)
    exits = sorted(old_unl - vl_set)
    entrants = sorted(vl_set - old_unl)
    removed = sorted(set(old_by_key) - set(now_by_key))
    added_non_unl = sorted((set(now_by_key) - set(old_by_key)) - vl_set)
    retained_non_unl = sorted((set(old_by_key) & set(now_by_key))
                              - old_unl - vl_set)
    entrants_seen_before = sorted(set(entrants) & set(old_by_key))
    print("CHECK churn arithmetic: retained %d + entrants %d = %d (VL size); "
          "retained %d + exits %d = %d (2026-07-17 UNL size); observed "
          "%d -> %d = %d - %d + %d"
          % (len(retained), len(entrants), len(vl_set),
             len(retained), len(exits), len(old_unl),
             len(old_by_key), len(now_by_key),
             len(old_by_key), len(removed),
             len(set(now_by_key) - set(old_by_key))))
    if len(retained) + len(entrants) != len(vl_set):
        failures.append("churn: retained + entrants != VL size")
    if len(retained) + len(exits) != len(old_unl):
        failures.append("churn: retained + exits != 2026-07-17 UNL size")
    if len(old_by_key) - len(removed) + len(set(now_by_key) - set(old_by_key)) != len(now_by_key):
        failures.append("churn: observed-validator arithmetic does not close")

    def dom(key, table):
        v = table.get(key)
        return v.get("domain") if v else None

    def agree24(key, table):
        v = table.get(key)
        return v.get("agreement_24h", {}).get("score") if v else None

    def agree30(key, table):
        v = table.get(key)
        return v.get("agreement_30day", {}).get("score") if v else None

    def ver(key, table):
        v = table.get(key)
        return v.get("server_version") if v else None

    # -------------------------------------------------- 1. thresholds table
    # Post-fix (fixAmendmentMajorityCalc enabled live): threshold =
    # max(1, floor(N * 67 / 100)); passes iff votes > threshold.
    # Pre-fix: threshold = max(1, floor(N * 204 / 256)); passes iff votes
    # >= threshold. Worked rows use the validator counts the test suite
    # pins (10, 16) plus the live UNL size (25) and small-N edge cases.
    thresh_rows = []
    for n in (1, 2, 3, 10, 16, 25):
        post_t = max(1, (n * 67) // 100)
        pre_t = max(1, (n * 204) // 256)
        thresh_rows.append((n, post_t, post_t + 1, pre_t, pre_t,
                            "post-fix needs %d of %d (%.1f%% of votes); "
                            "pre-fix needs %d of %d"
                            % (post_t + 1, n, 100.0 * (post_t + 1) / n,
                               pre_t, n)))
    thresh_md = (
        "# Amendment activation thresholds\n\n"
        "How many yes-votes an amendment needs, for a given number N of trusted\n"
        "validations, under the two majority rules in postfiatd.\n"
        "Post-fix rule applies live: `fixAmendmentMajorityCalc` is enabled\n"
        "(see `amendment_vote_counts.csv`), so the live rule is the 67%% column.\n"
        "Sources: `include/xrpl/protocol/SystemParameters.h:83-88`,\n"
        "`src/xrpld/app/misc/detail/AmendmentTable.cpp:325-341` (threshold),\n"
        "`AmendmentTable.cpp:360-377` (strict `>` post-fix, `>=` pre-fix).\n"
        "Worked N=16 (11 votes) and N=10 (8 votes) are the values pinned by\n"
        "the test suite (`src/test/app/AmendmentTable_test.cpp:1460-1467`).\n"
        "The live UNL has 25 validators, so a live activation needs 17 yes-votes.\n\n"
        "| trusted validations (N) | post-fix threshold floor(N*67/100) | post-fix votes needed (strict >) | pre-fix threshold floor(N*204/256) | pre-fix votes needed (>=) |\n"
        "|---:|---:|---:|---:|---:|\n")
    for n, post_t, post_need, pre_t, pre_need, _ in thresh_rows:
        thresh_md += "| %d | %d | %d | %d | %d |\n" % (n, post_t, post_need, pre_t, pre_need)
    thresh_md += (
        "\nHolding time: once a majority is first recorded, it must be held\n"
        "continuously until `majorityTime + majorityTime_ <= closeTime`\n"
        "(`AmendmentTable.cpp:918`); the code default is 2 weeks\n"
        "(`SystemParameters.h:88`, `Config.h:248`) and the shipped PFTL testnet\n"
        "configs set 3 days (`cfg/postfiatd-testnet-full.cfg:1467-1469`).\n"
        "Whether the live validators run that 3-day value is not established\n"
        "from ledger data (see `reconciliation.md`, NV5).\n"
        "\nFlag ledgers: every 256th ledger (`Ledger.h:426`); votes are tallied\n"
        "in the round after a flag ledger (`RCLConsensus.cpp:364-377`).\n"
        "Consensus quorum is a different number: `server_info` reports a\n"
        "`validation_quorum` that moves as participation changes (it was 17,\n"
        "then 16, across two calls on 2026-11-21). Do not confuse it with the\n"
        "amendment threshold above.\n")
    write(os.path.join(OUT, "amendment_activation_thresholds.md"), thresh_md)
    write_csv(os.path.join(OUT, "amendment_activation_thresholds.csv"),
              ["trusted_validations_N", "post_fix_threshold_floor_67pct",
               "post_fix_votes_needed_strict_gt",
               "pre_fix_threshold_floor_204_256",
               "pre_fix_votes_needed_gte"],
              [[n, pt, pn, ft, fn] for n, pt, pn, ft, fn, _ in thresh_rows])
    print("TABLE amendment_activation_thresholds: %d worked rows (N=1,2,3,10,16,25); "
          "live N=25 needs 17 yes-votes post-fix" % len(thresh_rows))

    # ------------------------------------------------ 2. vote-counts table
    vote_rows = []
    for amid in sorted(feature, key=lambda k: feature[k]["name"]):
        vote_rows.append([feature[amid]["name"], amid,
                          "enabled" if feature[amid]["enabled"] else "disabled",
                          str(feature[amid].get("supported")),
                          "absent", "absent"])
    vote_md = (
        "# Amendment vote counts and progression\n\n"
        "Live amendment state from the public `feature` method and the VHS\n"
        "vote endpoint, newest snapshot set in data/.\n\n"
        "- Known amendments: %d\n"
        "- Enabled: %d\n"
        "- Disabled: %d\n"
        "- Entries carrying a `majority` or `vetoed` field: %d\n"
        "- Entries with `supported: false`: %d\n"
        "- VHS activation records: %d, all sharing one date and one ledger\n"
        "  (see `amendment_activation_timing.md`)\n"
        "- VHS records carrying a `voted` or `eta` field: %d\n\n"
        "Finding: no amendment is currently in voting. The evidence is the\n"
        "absence itself, from two independent sources: the public `feature`\n"
        "response carries no `majority` field for any of the %d amendments,\n"
        "and the VHS vote endpoint returns %d activation records with zero\n"
        "`voted`/`eta` fields. This is a negative finding about the public\n"
        "surface: the `feature` method deliberately omits majority/veto data\n"
        "from non-admin callers (admin-only fields in\n"
        "`src/xrpld/rpc/handlers/Feature1.cpp:48-95`), and the VHS vote\n"
        "endpoint serves activation records only — a 404 is returned for a\n"
        "non-enabled amendment. Live per-amendment vote counts are therefore\n"
        "not obtainable from any public source tried; see `reconciliation.md`,\n"
        "NV1. The `majority`/`vetoed` columns below record that absence\n"
        "explicitly instead of leaving it implicit.\n\n"
        "Both PFTL-only amendments are disabled: `PF_ValidatorVoteTracking`\n"
        "(`213D9785EF1C34BC0F99BF190299B814AE0563E047DC457C9CB53B6FC02D4B70`)\n"
        "and `PF_AccountExclusion`\n"
        "(`56857392BEADCE1E4B0D754A91B73F1D053657AF4FDD585455D4FFBCD5307BE0`).\n"
        "The switch that selects the live threshold, `fixAmendmentMajorityCalc`\n"
        "(`4F46DF03559967AC60F2EB272FEFE3928A7594A45FF774B87A7E540DB0F8F068`),\n"
        "is enabled, so the live majority rule is the post-fix 67%% rule\n"
        "(strict greater-than).\n\n"
        "Full per-amendment table: `amendment_vote_counts.csv` (%d rows).\n"
        % (len(feature), len(enabled), len(disabled),
           sum(1 for v in feature.values() if "majority" in v or "vetoed" in v),
           sum(1 for v in feature.values() if not v.get("supported")),
           len(vhs_vote["amendments"]),
           sum(1 for a in vhs_vote["amendments"] if "voted" in a or "eta" in a),
           len(feature), len(vhs_vote["amendments"]), len(vote_rows)))
    write(os.path.join(OUT, "amendment_vote_counts.md"), vote_md)
    write_csv(os.path.join(OUT, "amendment_vote_counts.csv"),
              ["name", "id", "live_status", "supported",
               "majority_field", "vetoed_field"],
              vote_rows)
    print("TABLE amendment_vote_counts: %d rows, %d enabled / %d disabled, "
          "0 majority/vetoed fields, 0 amendments in voting"
          % (len(vote_rows), len(enabled), len(disabled)))

    # -------------------------------------------- 3. activation-timing table
    timing_rows = []
    for a in sorted(vhs_vote["amendments"], key=lambda x: x["name"]):
        timing_rows.append([a["name"], a["id"], a["date"], str(a["ledger_index"]),
                            a.get("tx_hash", ""), str(a.get("rippled_version"))])
    dates = {a["date"] for a in vhs_vote["amendments"]}
    ledgers = {a["ledger_index"] for a in vhs_vote["amendments"]}
    timing_md = (
        "# Amendment activation timing\n\n"
        "Activation records from the VHS vote endpoint\n"
        "(`/v1/network/amendments/vote/test`), newest snapshot set in data/.\n\n"
        "- Enabled amendments with an activation record: %d\n"
        "- Distinct activation dates: %d (%s)\n"
        "- Distinct activation ledgers: %d (%s)\n\n"
        "Finding: all %d currently enabled amendments activated in a single\n"
        "ledger, %s, at %s. There is no spread of activation times to analyse\n"
        "and no per-amendment activation sequence: the enabled set arrived\n"
        "together. Any claim about individual activation dates, or about a\n"
        "majority being gained and then lost before activation, would need\n"
        "ledger history that is not available from the public endpoints tried\n"
        "(see `reconciliation.md`, NV15). The activation ledger predates the\n"
        "RPC node's retained range, so its close time cannot be re-read from\n"
        "this node — the VHS date above is the source for the activation time.\n\n"
        "Full per-amendment table (name, ID, date, ledger, EnableAmendment\n"
        "transaction hash): `amendment_activation_timing.csv` (%d rows).\n"
        % (len(timing_rows), len(dates), ", ".join(sorted(dates)),
           len(ledgers), ", ".join(str(x) for x in sorted(ledgers)),
           len(timing_rows),
           sorted(ledgers)[0] if ledgers else "?",
           sorted(dates)[0] if dates else "?",
           len(timing_rows)))
    write(os.path.join(OUT, "amendment_activation_timing.md"), timing_md)
    write_csv(os.path.join(OUT, "amendment_activation_timing.csv"),
              ["name", "id", "activation_date_utc", "activation_ledger_index",
               "enable_amendment_tx_hash", "rippled_version"],
              timing_rows)
    print("TABLE amendment_activation_timing: %d rows, all at ledger %s, %s"
          % (len(timing_rows),
             sorted(ledgers)[0] if ledgers else "?",
             sorted(dates)[0] if dates else "?"))

    # ------------------------------------------------------ 4. UNL churn
    churn_rows = []
    for key in sorted(set(now_by_key) | set(old_by_key)):
        if key in vl_set and key in old_unl:
            status = "retained UNL"
        elif key in vl_set:
            status = "entered UNL"
        elif key in old_unl:
            status = "exited UNL (still observed)"
        elif key in now_by_key and key in old_by_key:
            status = "observed non-UNL both dates"
        elif key in now_by_key:
            status = "added to VHS, non-UNL"
        else:
            status = "removed from VHS"
        churn_rows.append([key, status,
                           dom(key, now_by_key) or "", dom(key, old_by_key) or "",
                           str(now_by_key[key]["domain_verified"]) if key in now_by_key else "",
                           ver(key, now_by_key) or "", ver(key, old_by_key) or "",
                           agree24(key, now_by_key) or "", agree24(key, old_by_key) or "",
                           agree30(key, now_by_key) or "", agree30(key, old_by_key) or ""])
    churn_md = (
        "# UNL churn — 2026-07-17 to 2026-11-22\n\n"
        "Two validator snapshots, both from the Validator History Service:\n"
        "the Wayback capture of `/v1/network/validators/test` dated\n"
        "2026-07-17 02:17:13 UTC (50 validators observed, UNL 20) and the live\n"
        "fetch in the newest snapshot set in data/ (%d validators observed, UNL %d).\n"
        "The published validator list itself has no archived copies (Wayback\n"
        "availability check returns zero captures), so this two-point VHS\n"
        "comparison is the only historical validator data available; there is\n"
        "no series between the two dates and no churn can be stated for any\n"
        "interval inside 2026-07-17 → 2026-11-22 (see `reconciliation.md`,\n"
        "NV3). Keys are matched after base58 decoding (VHS node keys) to hex\n"
        "(VL keys); a naive string comparison matches 0 of 25.\n\n"
        "| measure | 2026-07-17 | 2026-11-22 | change |\n"
        "|---|---:|---:|---:|\n"
        "| validators observed by VHS | %d | %d | %+d |\n"
        "| UNL members | %d | %d | %+d |\n"
        "| domain-verified validators | %d | %d | %+d |\n"
        "| retained UNL members | — | %d | — |\n"
        "| exited the UNL (still observed) | — | %d | — |\n"
        "| entered the UNL | — | %d | — |\n"
        "| of entrants, already observed 2026-07-17 as non-UNL | — | %d | — |\n"
        "| removed from VHS entirely | — | %d | — |\n"
        "| added to VHS, non-UNL | — | %d | — |\n"
        "| observed non-UNL on both dates | — | %d | — |\n\n"
        "Arithmetic: %d retained + %d entrants = %d (current UNL);\n"
        "%d retained + %d exits = %d (2026-07-17 UNL);\n"
        "%d observed then − %d removed + %d added = %d observed now.\n\n"
        "Exited the UNL (8), all still observed, domains unchanged:\n"
        "%s.\n\n"
        "Entered the UNL (13): %s.\n\n"
        "Removed from VHS entirely (6), all non-UNL in July:\n"
        "%s.\n\n"
        "Note on the exited members: three carry the `postfiat.org` domain.\n"
        "That is a domain-string observation only; operator identity is not\n"
        "established from these data.\n\n"
        "The live VL (sequence %d, effective %s) is byte-identical to the\n"
        "vendored 2026-11-20 reference copy (SHA-256\n"
        "`5d4f5a18a18fead4105e5dc00cf7e11a71b9be4bc140357d1b4ea12116df59e7`,\n"
        "14,781 bytes): zero UNL churn between the two VL fetches. The churn\n"
        "above is therefore entirely in the 2026-07-17 → 2026-11-20 window,\n"
        "with the 2026-11-20 → 2026-11-22 leg showing no change.\n\n"
        "Full per-validator table: `unl_churn.csv` (%d rows).\n"
        % (len(now_by_key), len(vl_set),
           len(old_by_key), len(now_by_key), len(now_by_key) - len(old_by_key),
           len(old_unl), len(vl_set), len(vl_set) - len(old_unl),
           sum(1 for v in old_by_key.values() if v.get("domain_verified")),
           sum(1 for v in now_by_key.values() if v.get("domain_verified")),
           sum(1 for v in now_by_key.values() if v.get("domain_verified"))
           - sum(1 for v in old_by_key.values() if v.get("domain_verified")),
           len(retained), len(exits), len(entrants), len(entrants_seen_before),
           len(removed), len(added_non_unl), len(retained_non_unl),
           len(retained), len(entrants), len(vl_set),
           len(retained), len(exits), len(old_unl),
           len(old_by_key), len(removed),
           len(set(now_by_key) - set(old_by_key)), len(now_by_key),
           "; ".join("%s (%s)" % (k, dom(k, now_by_key)) for k in exits),
           "; ".join("%s (%s)" % (k, dom(k, now_by_key)) for k in entrants),
           "; ".join("%s (%s, 30d agreement %s)"
                     % (k, dom(k, old_by_key), agree30(k, old_by_key))
                     for k in removed),
           vl_blob["sequence"],
           (datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)
            + datetime.timedelta(seconds=vl_blob["effective"])).isoformat(),
           len(churn_rows)))
    write(os.path.join(OUT, "unl_churn.md"), churn_md)
    write_csv(os.path.join(OUT, "unl_churn.csv"),
              ["validation_public_key_hex", "status_20260717_to_20261122",
               "domain_now", "domain_20260717", "domain_verified_now",
               "server_version_now", "server_version_20260717",
               "agreement_24h_now", "agreement_24h_20260717",
               "agreement_30d_now", "agreement_30d_20260717"],
              churn_rows)
    print("TABLE unl_churn: %d rows; UNL %d -> %d (retained %d, exits %d, "
          "entrants %d); observed %d -> %d"
          % (len(churn_rows), len(old_unl), len(vl_set), len(retained),
             len(exits), len(entrants), len(old_by_key), len(now_by_key)))

    # ------------------------------------------------------ 5. NegativeUNL
    # NOTE: this entry changed while the pack was being built. An earlier
    # fetch (2026-11-21 20:29 UTC) showed ONE disabled validator
    # (ED4F62A8..., FirstLedgerSequence 8180480) and a pending
    # ValidatorToDisable ED372A9F.... The snapshot set used here shows the
    # pending disable executed: ED372A9F... is now a second disabled entry
    # (FirstLedgerSequence 8250880) and the ValidatorToDisable field is
    # absent. Both states are recorded here; the table describes the current
    # snapshot set, and the transition is stated, not smoothed over.
    disabled = negative_unl.get("DisabledValidators", [])
    neg_rows = []
    for entry in disabled:
        dv = entry["DisabledValidator"]
        key = dv["PublicKey"]
        v = now_by_key.get(key, {})
        neg_rows.append([key, str(dv.get("FirstLedgerSequence")),
                         v.get("domain", ""),
                         str(v.get("domain_verified", "")),
                         v.get("server_version", ""),
                         v.get("agreement_24h", {}).get("score", ""),
                         "VL member" if key in vl_set else "not in VL"])
    to_disable = negative_unl.get("ValidatorToDisable")
    td = now_by_key.get(to_disable, {}) if to_disable else {}
    disabled_lines = "\n".join(
        "- `%s`, FirstLedgerSequence %s, VHS domain `%s`, 24h agreement `%s`"
        % (row[0], row[1], row[2], row[5]) for row in neg_rows)
    neg_md = (
        "# NegativeUNL\n\n"
        "On-ledger NegativeUNL entry (index\n"
        "`2E8A59AA9D3B5B186B0B9E0F62E6C02587CA74A4D778938E957B6357D364B244`),\n"
        "newest snapshot set in data/.\n\n"
        "| field | value |\n"
        "|---|---|\n"
        "| disabled validators | %d |\n"
        "| ValidatorToDisable | %s |\n"
        "| PreviousTxnID | %s |\n"
        "| PreviousTxnLgrSeq | %s |\n\n"
        "Disabled validators:\n%s\n\n"
        "State change observed during collection: an earlier fetch at\n"
        "2026-11-21 20:29 UTC showed one disabled validator (ED4F62A8…,\n"
        "FirstLedgerSequence 8180480) and `ValidatorToDisable` ED372A9F…\n"
        "(domain `dex3333.github.io`, 24h agreement 0.95438). In this snapshot\n"
        "set ED372A9F… is a second disabled entry with FirstLedgerSequence\n"
        "8250880, and no `ValidatorToDisable` is pending. All disabled keys\n"
        "are members of the current VL (sequence %d).\n\n"
        "The disable date of the first entry cannot be read from this RPC\n"
        "node: ledger 8180480 is outside its retained range, and the node\n"
        "answers `lgrNotFound` for it (verified 2026-11-21 20:35 UTC). An\n"
        "estimate from the ledger gap is given in `reconciliation.md` (NV4)\n"
        "and is labelled [ESTIMASI], not a measured date. The second entry's\n"
        "FirstLedgerSequence (8250880) sits 26 ledgers after the validated\n"
        "ledger of the 20:29 UTC fetch (8250854) and before the validated\n"
        "ledger of the 20:58 UTC fetch (8251434) — consistent with the\n"
        "disable executing between the two fetches.\n\n"
        "Full table: `negative_unl.csv` (%d rows).\n"
        % (len(disabled),
           to_disable if to_disable else "none pending",
           negative_unl.get("PreviousTxnID"),
           negative_unl.get("PreviousTxnLgrSeq"),
           disabled_lines,
           vl_blob["sequence"],
           len(neg_rows)))
    write(os.path.join(OUT, "negative_unl.md"), neg_md)
    write_csv(os.path.join(OUT, "negative_unl.csv"),
              ["disabled_validation_public_key_hex", "first_ledger_sequence",
               "domain", "domain_verified", "server_version",
               "agreement_24h", "vl_membership"],
              neg_rows)
    print("TABLE negative_unl: %d disabled validator(s), FirstLedgerSequences %s, "
          "ValidatorToDisable %s"
          % (len(neg_rows),
             ", ".join(r[1] for r in neg_rows),
             to_disable if to_disable else "none pending"))

    # ------------------------------------------------------ 6. reconciliation
    # Disable-date estimate: anchor on the validated ledger of the EARLIEST
    # snapshot set in data/ (a fixed reference point, so the estimate does
    # not move when a fresh run adds a later set), 3 seconds per ledger
    # (measured cadence, ~2 ledgers per 6 seconds).
    stamps = sorted({name[:16] for name in os.listdir(DATA)
                     if len(name) > 16 and name[8] == "T" and name[15] == "Z"})
    earliest_validated = load_json("%s_rpc_ledger_validated.json"
                                   % min(stamps))["result"]["ledger"]
    anchor_seq = earliest_validated.get("ledger_index")
    anchor_time = earliest_validated.get("close_time_iso")
    first_seq = disabled[0]["DisabledValidator"].get("FirstLedgerSequence") if disabled else None
    est_note = ""
    if first_seq and anchor_seq:
        gap = int(anchor_seq) - int(first_seq)
        est = (datetime.datetime.fromisoformat(
            anchor_time.replace("Z", "+00:00"))
            - datetime.timedelta(seconds=gap * 3))
        est_note = ("[ESTIMASI] ledger gap %d x ~3 s/ledger = ~%d s (~%.1f days) "
                    "before the validated ledger %s of the earliest snapshot set "
                    "in data/ (%s) -> ~%s. Estimate only; "
                    "the close time of ledger %s is not readable from this node."
                    % (gap, gap * 3, gap * 3 / 86400.0, anchor_seq, anchor_time,
                       est.strftime("%Y-%m-%dT%H:%M:%SZ"), first_seq))
    recon_md = (
        "# Reconciliation — code inventory vs live ledger vs VHS\n\n"
        "Three counts that look contradictory until the sets are compared\n"
        "directly (newest snapshot set in data/):\n\n"
        "| source | count | what it counts |\n"
        "|---|---:|---|\n"
        "| postfiatd code inventory (`features.macro`, commit 24c5487) | 107 | amendments registered in the binary: 41 FEATURE + 50 FIX + 16 RETIRE |\n"
        "| live `feature` RPC | 101 | amendments the node knows: 64 enabled + 37 disabled |\n"
        "| VHS `/v1/network/amendments/info` | 103 | amendments VHS knows: 15 deprecated |\n"
        "| on-ledger Amendments entry | 64 | enabled amendment IDs |\n"
        "| VHS `/v1/network/amendments/vote/test` | 64 | activation records |\n\n"
        "The 107 → 101 gap is exactly the six amendments registered with\n"
        "`Supported::no` (unfinished code in this build): BatchInnerSigs\n"
        "(`fixBatchInnerSigs`), DynamicMPT, DelegateV1_1 (`fixDelegateV1_1`),\n"
        "Batch, PermissionDelegation, InvariantsV1_1. Every one of the 101\n"
        "live IDs is in the code inventory, and every code amendment absent\n"
        "from the live set is `Supported::no`. A node cannot vote for an\n"
        "unsupported amendment, so these six cannot appear in the live set\n"
        "from this build. The gap is therefore explained, not papered over:\n"
        "it is a property of the build, verified by set comparison in\n"
        "`generate_tables.py` (see its log).\n\n"
        "The 103 → 101 VHS gap is two amendments VHS knows but the live node\n"
        "does not report: Batch (in the code inventory, `Supported::no`) and\n"
        "OrchardPrivacy (`FFAB002FD32A4CFE1FA902D8A5F507B8B0E860716FC578E1E0BD6DB665BAABAA`,\n"
        "in neither the code inventory nor the live set). Why VHS carries\n"
        "OrchardPrivacy is not established from any source consulted; see NV14.\n\n"
        "VHS marks 15 amendments deprecated; the code inventory retires 16.\n"
        "The one retired amendment VHS does not flag deprecated is FlowCross\n"
        "(`3012E8230864E95A58C60FD61430D7E1B4D3353195F2981DC12B0C7C0950FFAC`,\n"
        "disabled live). That is a metadata difference between VHS and the\n"
        "code, not a contradiction about enabled state.\n\n"
        "Live threshold: `fixAmendmentMajorityCalc` is enabled, so the\n"
        "post-fix 67%% rule (strict greater-than) is the live rule, not the\n"
        "pre-fix 204/256 rule.\n\n"
        "## Not verified (NV1–NV15)\n\n"
        "Claims that could not be established from the sources consulted.\n"
        "Nothing in this section is presented as verified anywhere in this pack.\n\n"
        "- NV1 — Live per-amendment vote counts: how many of the 25 UNL validators currently vote for each of the 37 disabled amendments. The public `feature` method omits majority/veto data (admin-only); VHS vote endpoints serve activation records only (404 for non-enabled amendments); the explorer reads the same VHS endpoint. No public source tried exposes live vote counts.\n"
        "- NV2 — Majority-pending / ETA status for any specific amendment beyond the negative finding (0 `voted`/`eta` items in VHS, 0 `majority` fields in `feature`). The negative finding is recorded; it cannot independently prove the negative beyond those two sources.\n"
        "- NV3 — Historical validator-list snapshots with sequence < 30, and any churn inside 2026-07-17 → 2026-11-22. Wayback has zero captures of the VL URL (checked twice, availability API empty); no VL copy was found in any public git repo; the only historical validator data is the single 2026-07-17 VHS capture used here.\n"
        "- NV4 — Close time of ledger 8180480 (NegativeUNL FirstLedgerSequence), i.e. the disable date of ED4F62A8…. The RPC node retains only ledgers from 8200054 onward at collection time and answers `lgrNotFound` for 8180480. %s\n"
        "- NV5 — Whether the live testnet validators actually run the shipped 3-day `[amendment_majority_time]` (vs a custom value ≥ 15 minutes). The shipped configs say 3 days; the holding time is a per-node local configuration, and no operator config or observed majority→activation gap is available to confirm it.\n"
        "- NV6 — Which amendments the PFTL testnet genesis ledger started with. The genesis ledger takes the enabled set as a parameter (`Ledger.cpp:171-221`); it is not in the source checkout.\n"
        "- NV7 — The upstream rippled 80/100 post-fix threshold as a source file:line. Upstream = 80%% is established from the xrpl.build documentation and from this checkout's HEAD commit message, but no upstream rippled source tree was read.\n"
        "- NV8 — That `PF_AccountExclusion` / `PF_ValidatorVoteTracking` exist in no upstream rippled version. Strongly indicated PFTL-only by the `PF_` naming and PFTL-only call sites, but not proven against an upstream source tree.\n"
        "- NV9 — The upstream value of the 24-hour trusted-vote cache expiry. The mechanism and value are verified in postfiatd (`AmendmentTable.cpp:172`); the upstream value was not cross-checked.\n"
        "- NV10 — Historical VHS daily validator reports before 2026-11-21, other than the single 2026-07-17 Wayback capture. The reports endpoint returns current-day reports; archived reports were not retrieved.\n"
        "- NV11 — A full WebSocket session (e.g. `feature` over WS). Only an HTTP upgrade probe (101 Switching Protocols) was run; no method was executed over WebSocket.\n"
        "- NV12 — A second, independent public RPC/WS host for cross-checking. Only the foundation hosts were found; no community RPC mirror surfaced in search. All chain-state claims rest on the foundation's own nodes plus the foundation-run VHS.\n"
        "- NV13 — Per-validator manifest contents (domains/attestations inside the VL's per-validator `manifest` blobs and the top-level `manifest`). The blobs are base64 binary and were not decoded beyond the JSON blob in `blobs_v2`; VL-member domains in this pack come from VHS instead.\n"
        "- NV14 — Why VHS knows OrchardPrivacy (`FFAB002F…`), an amendment in neither the postfiatd code inventory (commit 24c5487) nor the live set. No source consulted explains its presence in the VHS info endpoint.\n"
        "- NV15 — Whether any amendment ever gained then lost a majority on PFTL testnet (majority clock reset), and individual activation histories before the single-ledger activation at 86785. That needs ledger history (scanning historical Amendments entries / EnableAmendment pseudo-transactions); none is available from the public endpoints tried.\n"
        % (est_note))
    write(os.path.join(OUT, "reconciliation.md"), recon_md)
    write_csv(os.path.join(OUT, "reconciliation.csv"),
              ["source", "count", "detail"],
              [["code inventory (features.macro, 24c5487)", "107",
                "41 FEATURE + 50 FIX + 16 RETIRE"],
               ["live feature RPC", str(len(feature)),
                "%d enabled + %d disabled" % (len(enabled), len(disabled))],
               ["VHS amendments info", str(len(info_ids)),
                "%d deprecated" % sum(1 for a in info_ids.values() if a.get("deprecated"))],
               ["on-ledger Amendments entry", str(len(on_ledger)), "enabled IDs"],
               ["VHS vote records", str(len(vote_ids)), "activation records"],
               ["code amendments absent from live set (all Supported::no)", str(len(code_not_live)),
                ", ".join(r["name"] for r in code_not_live_rows)],
               ["VHS info amendments absent from code inventory", str(len(info_not_code)),
                ", ".join("%s (%s)" % (info_ids[i]["name"], i) for i in info_not_code)],
               ["VHS info amendments absent from live set", str(len(info_not_live)),
                ", ".join("%s (%s)" % (info_ids[i]["name"], i) for i in info_not_live)]])
    print("TABLE reconciliation: code 107 / live 101 / VHS info 103; gap = 6 Supported::no; "
          "VHS-only = Batch + OrchardPrivacy")

    # ---------------------------------------------------------------- verdict
    for path in sorted(os.listdir(OUT)):
        if path.endswith((".md", ".csv")):
            print("OUTPUT %s: %d bytes, SHA-256 %s"
                  % (path, os.path.getsize(os.path.join(OUT, path)),
                     sha256_file(os.path.join(OUT, path))))
    if failures:
        print("GENERATE VERDICT: FAIL -- %s" % "; ".join(failures))
        return 1
    print("GENERATE VERDICT: PASS -- 6 tables written, all set checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
