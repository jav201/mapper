"""Capture the 8 prescan refusal strings by RUNNING the base store.py (4 kinds x 2 call sites)."""
import sys, tempfile, pathlib
from mapper.store import MapStore, MapStoreError
import mapper.store
MMD = "graph TD\n    a[raiz]\n"
def nested(n):
    t = "0"
    for _ in range(n):
        t = "{k: " + t + "}"
    return t
ARMS = {
    "short_anchor": "a: &x 1\n",
    "alias": "b: *zz\n",
    "long_anchor": "a: &" + "g" * 5000 + " 1\n",
    "depth_65": nested(65),
}
print("# store:", mapper.store.__file__, file=sys.stderr)
for name, yml in ARMS.items():
    with tempfile.TemporaryDirectory() as d:
        ws = pathlib.Path(d)
        (ws / "m.mmd").write_text(MMD, encoding="utf-8")
        (ws / "m_nodos.yml").write_text(yml, encoding="utf-8")
        store = MapStore(ws)
        for site, call in (("load", lambda: store.load("m")),
                           ("side", lambda: store._capped_side_graph("m", MMD, yml))):
            try:
                call()
                msg = "<<NO REFUSAL>>"
            except MapStoreError as exc:
                msg = str(exc)
            print(f"{name}.{site} = {ascii(msg)}")
