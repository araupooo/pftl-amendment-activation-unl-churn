#!/usr/bin/env python3
"""collect_snapshots.py — fetch live PFTL testnet governance snapshots.

Fetches, with pure JSON bodies (no curl -w trailer, no added fields):
  * the published validator list (VL) from https://postfiat.org/testnet_vl.json
  * JSON-RPC from https://rpc.testnet.postfiat.org: server_info, feature,
    ledger (validated), ledger_entry for the Amendments object and for the
    NegativeUNL object (constant hex indexes)
  * Validator History Service from https://vhs.testnet.postfiat.org:
    root, /v1/network/validators/test, /v1/network/amendments/vote/test,
    /v1/network/amendments/info, /v1/network/validator_reports
  * a WebSocket upgrade probe of wss://ws.testnet.postfiat.org (via curl,
    best effort: raw sockets do not work through some egress proxies)
  * a Wayback Machine availability check for the VL URL (best effort)

Every fetch is saved under data/ with a UTC timestamp prefix shared by the
whole run, e.g. data/20261122T040000Z_rpc_feature.json. The run's timestamp
appears in filenames and in this script's stdout (the collector log) only;
nothing inside a saved JSON body is modified.

The live VL is compared byte-for-byte with the vendored reference copy
data/testnet_vl_20261120_reference.json (the 2026-11-20 fetch, sequence 30)
and the result is printed. Any difference is reported, not hidden: the
comparison line is part of the log either way.

Usage:
    python3 scripts/collect_snapshots.py [--offline] [--stamp STAMP]
    --offline  reuse the newest committed snapshot set instead of fetching;
               used by the fresh-copy reproduction so it does not depend on
               the network. The VL comparison still runs (reference copy
               against the newest committed VL file).
    --stamp    override the UTC timestamp prefix (format YYYYMMDDTHHMMSSZ).

Exit status: 0 only if every core fetch succeeds (VL, all RPC calls, all
VHS calls). Best-effort checks (WebSocket probe, Wayback) are reported as
WARN and never fail the run. In --offline mode exit 0 requires a committed
snapshot set to exist.
"""

import base64
import datetime
import hashlib
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

VL_URL = "https://postfiat.org/testnet_vl.json"
RPC_URL = "https://rpc.testnet.postfiat.org"
VHS_URL = "https://vhs.testnet.postfiat.org"
WS_HOST = "ws.testnet.postfiat.org"

AMENDMENTS_INDEX = "7DB0788C020F02780A673DC74757F23823FA3014C1866E72CC4CD8B226CD6EF4"
NEGATIVE_UNL_INDEX = "2E8A59AA9D3B5B186B0B9E0F62E6C02587CA74A4D778938E957B6357D364B244"

REFERENCE_VL = os.path.join(DATA, "testnet_vl_20261120_reference.json")

RPC_CALLS = [
    ("rpc_server_info", {"method": "server_info", "params": [{}]}),
    ("rpc_feature", {"method": "feature", "params": [{}]}),
    ("rpc_ledger_validated", {"method": "ledger", "params": [
        {"ledger_index": "validated", "transactions": False,
         "expand": False, "owner_funds": False}]}),
    ("rpc_ledger_entry_amendments", {"method": "ledger_entry", "params": [
        {"index": AMENDMENTS_INDEX, "ledger_index": "validated"}]}),
    ("rpc_ledger_entry_negativeunl", {"method": "ledger_entry", "params": [
        {"index": NEGATIVE_UNL_INDEX, "ledger_index": "validated"}]}),
]

VHS_CALLS = [
    ("vhs_root", "/"),
    ("vhs_validators_test", "/v1/network/validators/test"),
    ("vhs_amendments_vote_test", "/v1/network/amendments/vote/test"),
    ("vhs_amendments_info", "/v1/network/amendments/info"),
    ("vhs_validator_reports", "/v1/network/validator_reports"),
]


def utc_stamp():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def fetch_json(url, payload=None, timeout=60):
    """GET (payload None) or POST a JSON-RPC body; return (status, raw_bytes)."""
    if payload is None:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
    else:
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, resp.read()


def save(stamp, kind, raw):
    name = "%s_%s.json" % (stamp, kind)
    path = os.path.join(DATA, name)
    with open(path, "wb") as fh:
        fh.write(raw)
    return name


def vl_summary(raw):
    """Decode the VL blob; return (seq, n_validators, effective_iso, expiration_iso)."""
    doc = json.loads(raw)
    blob = json.loads(base64.b64decode(doc["blobs_v2"][0]["blob"]))
    epoch = datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)
    eff = (epoch + datetime.timedelta(seconds=blob["effective"])).isoformat()
    exp = (epoch + datetime.timedelta(seconds=blob["expiration"])).isoformat()
    return blob["sequence"], len(blob["validators"]), eff, exp


def ws_probe():
    """WebSocket upgrade probe via curl (handles egress proxies).

    Returns (status_or_None, note). curl -D - prints the response headers;
    the first status line is the upgrade result. --max-time bounds the
    wait: a successful upgrade leaves the connection open, so curl is
    killed by the timeout after the headers arrive.
    """
    cmd = ["curl", "-s", "-D", "-", "-o", "/dev/null", "--max-time", "15",
           "-H", "Connection: Upgrade", "-H", "Upgrade: websocket",
           "-H", "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==",
           "-H", "Sec-WebSocket-Version: 13",
           "https://%s/" % WS_HOST]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
    except (subprocess.SubprocessError, OSError) as exc:
        return None, "curl error: %s" % exc
    # Take the LAST status line: through an egress proxy the first line is
    # the proxy's "200 Connection Established" and the last is the origin's
    # answer (101 on success).
    last = None
    for line in proc.stdout.splitlines():
        if line.startswith("HTTP/"):
            parts = line.split()
            if len(parts) >= 2 and parts[1].isdigit():
                last = (int(parts[1]), line.strip())
    if last is not None:
        return last
    return None, "no HTTP status line in probe output (curl rc=%d)" % proc.returncode


def wayback_check():
    """Wayback availability for the VL URL. Returns (captures, note)."""
    url = ("https://archive.org/wayback/available?url="
           "postfiat.org/testnet_vl.json")
    try:
        status, raw = fetch_json(url, timeout=30)
        doc = json.loads(raw)
        snaps = doc.get("archived_snapshots", {})
        return len(snaps), "HTTP %d, archived_snapshots=%s" % (status, snaps)
    except Exception as exc:  # noqa: BLE001 - best effort, report and continue
        return None, "check failed: %s" % exc


def compare_vl(live_raw):
    """Compare live VL bytes with the vendored reference copy."""
    try:
        with open(REFERENCE_VL, "rb") as fh:
            ref = fh.read()
    except OSError as exc:
        print("VL-COMPARE: SKIP -- reference copy unreadable: %s" % exc)
        return None
    live_hash = sha256_hex(live_raw)
    ref_hash = sha256_hex(ref)
    identical = live_raw == ref
    print("VL-COMPARE: live SHA-256 %s" % live_hash)
    print("VL-COMPARE: reference SHA-256 %s (%d bytes)" % (ref_hash, len(ref)))
    print("VL-COMPARE: %s" % ("IDENTICAL" if identical else
                               "DIFFERENT -- live VL changed since the reference fetch"))
    return identical


def latest_stamp():
    stamps = set()
    for name in os.listdir(DATA):
        if len(name) > 16 and name[8] == "T" and name[15] == "Z":
            stamps.add(name[:16])
    return max(stamps) if stamps else None


def run_live(stamp):
    failures = []
    fetched = {}

    print("COLLECTOR: live run, stamp %s" % stamp)
    print("COLLECTOR: endpoints VL=%s RPC=%s VHS=%s" % (VL_URL, RPC_URL, VHS_URL))

    # --- validator list -------------------------------------------------
    try:
        status, raw = fetch_json(VL_URL)
        name = save(stamp, "testnet_vl", raw)
        seq, n, eff, exp = vl_summary(raw)
        print("FETCH testnet_vl: HTTP %d, %d bytes, SHA-256 %s -> %s"
              % (status, len(raw), sha256_hex(raw), name))
        print("FETCH testnet_vl: sequence %d, validators %d, effective %s, "
              "expiration %s" % (seq, n, eff, exp))
        fetched["testnet_vl"] = raw
        compare_vl(raw)
    except Exception as exc:  # noqa: BLE001 - record and continue to report all
        print("FETCH testnet_vl: FAIL -- %s" % exc)
        failures.append("testnet_vl")

    # --- JSON-RPC --------------------------------------------------------
    for kind, payload in RPC_CALLS:
        try:
            status, raw = fetch_json(RPC_URL, payload)
            doc = json.loads(raw)
            name = save(stamp, kind, raw)
            result = doc.get("result", {})
            note = ""
            if kind == "rpc_server_info":
                info = result.get("info", {})
                note = ("build %s, network_id %s, validated ledger %s, "
                        "validation_quorum %s, peers %s"
                        % (info.get("build_version"), info.get("network_id"),
                           info.get("validated_ledger", {}).get("seq"),
                           info.get("validation_quorum"), info.get("peers")))
            elif kind == "rpc_feature":
                feats = result.get("features", {})
                note = ("%d known, %d enabled, %d disabled, %d carry a "
                        "majority/vetoed field"
                        % (len(feats),
                           sum(1 for v in feats.values() if v.get("enabled")),
                           sum(1 for v in feats.values() if not v.get("enabled")),
                           sum(1 for v in feats.values()
                               if "majority" in v or "vetoed" in v)))
            elif kind == "rpc_ledger_validated":
                led = result.get("ledger", {})
                note = ("ledger_index %s, close_time_iso %s, hash %s"
                        % (led.get("ledger_index"), led.get("close_time_iso"),
                           led.get("ledger_hash")))
            elif kind == "rpc_ledger_entry_amendments":
                node = result.get("node", {})
                note = ("%d amendment IDs in the Amendments entry, ledger %s"
                        % (len(node.get("Amendments", [])),
                           result.get("ledger_index")))
            elif kind == "rpc_ledger_entry_negativeunl":
                node = result.get("node", {})
                note = ("%d disabled validator(s), ValidatorToDisable %s, "
                        "ledger %s"
                        % (len(node.get("DisabledValidators", [])),
                           node.get("ValidatorToDisable", "none pending"),
                           result.get("ledger_index")))
            print("FETCH %s: HTTP %d, %d bytes, SHA-256 %s -> %s"
                  % (kind, status, len(raw), sha256_hex(raw), name))
            if note:
                print("FETCH %s: %s" % (kind, note))
            fetched[kind] = raw
        except Exception as exc:  # noqa: BLE001
            print("FETCH %s: FAIL -- %s" % (kind, exc))
            failures.append(kind)

    # --- Validator History Service ---------------------------------------
    for kind, path in VHS_CALLS:
        try:
            status, raw = fetch_json(VHS_URL + path)
            doc = json.loads(raw)
            name = save(stamp, kind, raw)
            note = ""
            if kind == "vhs_validators_test":
                note = ("%d validators, %d with unl \"rpc\", %d domain_verified"
                        % (doc.get("count"),
                           sum(1 for v in doc.get("validators", [])
                               if v.get("unl") == "rpc"),
                           sum(1 for v in doc.get("validators", [])
                               if v.get("domain_verified"))))
            elif kind == "vhs_amendments_vote_test":
                items = doc.get("amendments", [])
                note = ("%d activation records, distinct dates %s, distinct "
                        "ledger_index %s, items with voted/eta fields %d"
                        % (doc.get("count"),
                           sorted({a.get("date") for a in items}),
                           sorted({a.get("ledger_index") for a in items}),
                           sum(1 for a in items
                               if "voted" in a or "eta" in a)))
            elif kind == "vhs_amendments_info":
                note = ("%d known amendments, %d deprecated"
                        % (doc.get("count"),
                           sum(1 for a in doc.get("amendments", [])
                               if a.get("deprecated"))))
            elif kind == "vhs_validator_reports":
                note = "%d daily reports" % doc.get("count")
            print("FETCH %s: HTTP %d, %d bytes, SHA-256 %s -> %s"
                  % (kind, status, len(raw), sha256_hex(raw), name))
            if note:
                print("FETCH %s: %s" % (kind, note))
            fetched[kind] = raw
        except Exception as exc:  # noqa: BLE001
            print("FETCH %s: FAIL -- %s" % (kind, exc))
            failures.append(kind)

    # --- best-effort checks (never fail the run) -------------------------
    status, note = ws_probe()
    print("PROBE websocket %s: %s"
          % (WS_HOST, ("HTTP %d -- %s" % (status, note)) if status
             else ("WARN -- %s" % note)))
    n, note = wayback_check()
    print("CHECK wayback VL captures: %s -- %s"
          % (("count %d" % n) if n is not None else "WARN", note))

    if failures:
        print("COLLECTOR VERDICT: FAIL -- failed fetches: %s" % ", ".join(failures))
        return 1
    print("COLLECTOR VERDICT: PASS -- %d files fetched, 0 core failures"
          % len(fetched))
    return 0


def run_offline():
    stamp = latest_stamp()
    if stamp is None:
        print("COLLECTOR VERDICT: FAIL -- offline mode but no committed "
              "snapshot set exists in data/")
        return 1
    print("COLLECTOR: offline mode, reusing committed snapshot set %s" % stamp)
    vl_name = "%s_testnet_vl.json" % stamp
    try:
        with open(os.path.join(DATA, vl_name), "rb") as fh:
            live_raw = fh.read()
    except OSError as exc:
        print("COLLECTOR VERDICT: FAIL -- committed VL unreadable: %s" % exc)
        return 1
    print("FETCH testnet_vl: OFFLINE -- reused %s (%d bytes, SHA-256 %s)"
          % (vl_name, len(live_raw), sha256_hex(live_raw)))
    compare_vl(live_raw)
    print("COLLECTOR VERDICT: PASS -- offline reuse of snapshot set %s" % stamp)
    return 0


def main(argv):
    offline = "--offline" in argv
    stamp = utc_stamp()
    if "--stamp" in argv:
        stamp = argv[argv.index("--stamp") + 1]
    os.makedirs(DATA, exist_ok=True)
    if offline:
        return run_offline()
    return run_live(stamp)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
