"""Read N for a kill-run set's key from the committed timestamp proofs (KILL_TEST.md section 3, KT-14, KT-31).

    uv run --no-project --with opentimestamps==0.5.0 python kill-test/read_set_a_key.py [MANIFEST]

MANIFEST defaults to freeze/killtest-code-v1-set-A.sha256. Run it in a
checkout of main with its history (it reads commit times with git). It only
reads the proofs the timestamp Action committed:

- freeze/<manifest>.ots, the first proof, names every calendar with a
  pending attestation;
- freeze/upgrades/<manifest>.<run>.ots, the Action's upgrades of that proof.

Section 3's rule, as written: N is read from the first upgrade, committed
within 7 days of the manifest's push, in which every calendar with a pending
attestation in the first proof has given its Bitcoin attestation. If there is
none, N is read from the last upgrade committed within those 7 days that holds
any Bitcoin attestation, or, if none does, from the first later upgrade that
does. N is the lowest block height among the Bitcoin attestations in that
upgrade. The key then comes from block N + 6's hash, read once that block has
6 confirmations (KT-31): kill-test/e1_kill_run.py kill-run A <hash> ...

A calendar has given its Bitcoin attestation when, in the upgrade, the branch
of the proof that ends in its pending attestation also holds a Bitcoin block
header attestation. The opentimestamps library (not a project dependency) is
used only to read the proof files; anyone can check the result with the `ots`
client and a block explorer.
"""

import datetime as dt
import pathlib
import subprocess
import sys

from opentimestamps.core.notary import BitcoinBlockHeaderAttestation, PendingAttestation
from opentimestamps.core.serialize import StreamDeserializationContext
from opentimestamps.core.timestamp import DetachedTimestampFile

ROOT = pathlib.Path(__file__).resolve().parents[1]
WINDOW = dt.timedelta(days=7)


def load(path):
    with open(path, "rb") as f:
        return DetachedTimestampFile.deserialize(StreamDeserializationContext(f)).timestamp


def nodes(ts):
    yield ts
    for sub in ts.ops.values():
        yield from nodes(sub)


def heights(ts):
    return sorted({a.height for n in nodes(ts) for a in n.attestations if isinstance(a, BitcoinBlockHeaderAttestation)})


def calendars(ts):
    """{calendar URI: the node holding its pending attestation}."""
    out = {}
    for n in nodes(ts):
        for a in n.attestations:
            if isinstance(a, PendingAttestation):
                out[a.uri] = n
    return out


def attested(upgrade, uri):
    """The Bitcoin heights under this calendar's branch of the upgrade, if it has any."""
    for n in nodes(upgrade):
        if any(isinstance(a, PendingAttestation) and a.uri == uri for a in n.attestations):
            return heights(n)
    return []


def committed_at(path):
    out = subprocess.run(["git", "log", "--diff-filter=A", "--format=%cI", "--", str(path)], cwd=ROOT,
                         capture_output=True, text=True).stdout.split()
    if not out:
        raise SystemExit(f"{path} has no commit in this checkout's history")
    return dt.datetime.fromisoformat(out[-1])


def read(manifest="freeze/killtest-code-v1-set-A.sha256", now=None):
    name = pathlib.Path(manifest).name
    first = ROOT / "freeze" / f"{name}.ots"
    pushed = committed_at(ROOT / "freeze" / name)
    cals = sorted(calendars(load(first)))
    ups = sorted((ROOT / "freeze" / "upgrades").glob(f"{name}.*.ots"))
    rows = []
    for u in ups:
        t = load(u)
        per = {c: attested(t, c) for c in cals}
        rows.append({"file": u.name, "committed": committed_at(u), "per_calendar": per, "heights": heights(t),
                     "complete": all(per[c] for c in cals)})
    within = [r for r in rows if r["committed"] - pushed <= WINDOW]
    pick, why = None, ""
    complete = [r for r in within if r["complete"]]
    if complete:
        pick, why = complete[0], "the first upgrade within 7 days in which every calendar has attested"
    else:
        now = now or dt.datetime.now(dt.timezone.utc)
        if now - pushed <= WINDOW:
            why = "no upgrade yet in which every calendar has attested, and the 7 days are not over: wait"
        else:
            some = [r for r in within if r["heights"]]
            later = [r for r in rows if r["committed"] - pushed > WINDOW and r["heights"]]
            if some:
                pick, why = some[-1], "the last upgrade within 7 days holding any Bitcoin attestation"
            elif later:
                pick, why = later[0], "the first later upgrade holding a Bitcoin attestation"
            else:
                why = "no upgrade holds a Bitcoin attestation yet: wait"
    return {"manifest": name, "pushed": pushed.isoformat(), "calendars": cals, "upgrades": rows, "pick": pick,
            "why": why, "N": pick["heights"][0] if pick else None}


def main(argv) -> int:
    res = read(*(argv[1:2] or []))
    print(f"manifest {res['manifest']}, pushed {res['pushed']}")
    print(f"calendars in the first proof: {', '.join(res['calendars'])}")
    for r in res["upgrades"]:
        mark = "every calendar" if r["complete"] else ", ".join(c.split("//")[1].split(".")[0] + (" yes" if h else " no")
                                                               for c, h in r["per_calendar"].items())
        print(f"  {r['file']} committed {r['committed'].isoformat()}: heights {r['heights']} ({mark})")
    print(res["why"])
    if res["N"] is not None:
        print(f"N = {res['N']} (from {res['pick']['file']}); the key comes from block {res['N'] + 6}'s hash, "
              f"once it has 6 confirmations (block {res['N'] + 11} exists).")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
