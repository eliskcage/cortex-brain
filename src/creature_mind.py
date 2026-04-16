"""
creature_mind.py — SphereNet intelligence layer for ALIVE creatures

A standalone lab module. No cortex, no UI, no server.
Just a creature with a growing mind.

Run it, talk to it, watch concepts form.
After 20 messages its mind is saved to creature_mind.json.

Usage:
    python creature_mind.py
    python creature_mind.py --creature killian
    python creature_mind.py --load  (loads existing mind from JSON)
"""

import json
import math
import uuid
import time
import argparse
import os
from datetime import datetime

# ─── PARAMETERS ───────────────────────────────────────────────────────────────

RESONANCE_RADIUS  = 0.45   # catch radius — 0.55 threshold works well for 384D semantic embeddings
DRIFT_RATE        = 0.06   # how far centre moves per signal (slow = stable concepts)
GROOVE_TO_MERGE   = 4      # grooves before merge-eligible
MERGE_THRESHOLD   = 0.65   # right value for 384D semantic space — 0.65+ is genuinely similar
BASE_TIMER        = 40     # ticks before unused sphere dissolves
DECAY_ACCEL       = 0.35   # decay multiplier when isolated
MAX_MERGES_TICK   = 5      # merge governor

# Emotional signal weight — auto-set per embedding mode after import
# sentence-transformers: 0.4 (language is meaningful, emotion colours it)
# hash fallback: 0.9 (language hash is noise, let emotion dominate)
PSI_WEIGHT        = 0.4    # overridden below after embed mode is known

TICK_EVERY        = 3      # run tick() every N messages
SAVE_EVERY        = 10     # save mind to JSON every N messages
MIND_FILE         = "creature_mind.json"

GREEK = list("αβγδεζηθικλμνξοπρστυφχψω")

# ─── EMBEDDING ────────────────────────────────────────────────────────────────
# Tries sentence-transformers first (real semantics, 384D).
# Falls back to hash embedding (no install, 40D, noisy).
# Both modes are tested — results compared in lab output.

try:
    from sentence_transformers import SentenceTransformer as _ST
    _encoder = _ST('all-MiniLM-L6-v2')
    DIM = 384
    EMBED_MODE = "sentence-transformers"
    def embed(text: str) -> list:
        return _encoder.encode(text, normalize_embeddings=True).tolist()
    PSI_WEIGHT = 0.15
    print("  ◈ embedding: sentence-transformers (384D) · psi_weight=0.15\n")
except ImportError:
    DIM = 40
    EMBED_MODE = "hash"
    PSI_WEIGHT = 0.9
    print("  ◈ embedding: hash fallback (40D) · psi_weight=0.9 — pip install sentence-transformers for real semantics\n")
    def embed(text: str) -> list:
        """Hash-based deterministic embedding."""
        words = text.lower().split()
        vec = [0.0] * DIM
        for word in words:
            for i, ch in enumerate(word):
                vec[i % DIM] += (ord(ch) - 96) / 26.0
                vec[(i * 7 + 3) % DIM] += math.sin(ord(ch) * 0.3)
                vec[(i * 13 + 11) % DIM] += math.cos(ord(ch) * 0.7)
        return normalise(vec)

def psi_embed(p: float, n: float, f: float) -> list:
    """Embed ψ=[p,n,f] into the same DIM space."""
    vec = [0.0] * DIM
    # Spread p, n, f across the vector space in distinct bands
    band = DIM // 3
    for i in range(band):
        vec[i]          = p * math.sin(i * 0.5)
        vec[i + band]   = n * math.cos(i * 0.5)
        vec[i + band*2] = f * math.sin(i * 0.3 + 1.0)
    return normalise(vec)

def blend(vec_a: list, vec_b: list, w: float) -> list:
    """Blend two vectors. w=0 → all a, w=1 → all b."""
    return normalise([a * (1 - w) + b * w for a, b in zip(vec_a, vec_b)])

def normalise(vec: list) -> list:
    mag = math.sqrt(sum(x*x for x in vec))
    if mag < 1e-10:
        return vec
    return [x / mag for x in vec]

def cosine(a: list, b: list) -> float:
    return sum(x*y for x, y in zip(a, b))

# ─── SPHERE ───────────────────────────────────────────────────────────────────

class Sphere:
    def __init__(self, centre: list, label: str = None, parents: list = None):
        self.id         = str(uuid.uuid4())[:8]
        self.centre     = centre
        self.label      = label or "?"
        self.groove     = 0
        self.timer      = float(BASE_TIMER)
        self.generation = 0 if parents is None else max(p.generation for p in parents) + 1
        self.parents    = [p.id for p in parents] if parents else []
        self.born       = datetime.now().isoformat()

    def resonate(self, signal: list) -> float:
        sim = cosine(self.centre, signal)
        if sim >= (1.0 - RESONANCE_RADIUS):
            self.groove += 1
            self.timer   = float(BASE_TIMER)
            # Drift toward signal
            self.centre = normalise([
                c + DRIFT_RATE * (s - c)
                for c, s in zip(self.centre, signal)
            ])
            return sim
        return 0.0

    def tick(self) -> bool:
        """Returns False if sphere should dissolve."""
        self.timer -= DECAY_ACCEL
        return self.timer > 0

    def to_dict(self) -> dict:
        return {
            "id": self.id, "label": self.label, "groove": self.groove,
            "timer": round(self.timer, 2), "generation": self.generation,
            "parents": self.parents, "born": self.born,
            "centre": [round(x, 4) for x in self.centre]
        }

# ─── CREATURE MIND ─────────────────────────────────────────────────────────────

class CreatureMind:
    def __init__(self, creature_id: str = "anon"):
        self.creature_id  = creature_id
        self.spheres      = []
        self.tick_count   = 0
        self.msg_count    = 0
        self.merge_count  = 0
        self._greek_idx   = 0
        self._last_psi    = (0.5, 0.0, 0.5)  # neutral start

        print(f"\n◈ CREATURE MIND — {creature_id}")
        print(f"  dim={DIM} · resonance={1-RESONANCE_RADIUS:.2f} · drift={DRIFT_RATE}")
        print(f"  psi_weight={PSI_WEIGHT} · merge_threshold={MERGE_THRESHOLD}\n")

    # ── SIGNAL ────────────────────────────────────────────────────────────────

    def signal(self, text: str, psi: tuple = None) -> dict:
        """Send a text signal (+ optional emotional state) to the mind."""
        self.msg_count += 1

        p, n, f = psi if psi else self._last_psi
        self._last_psi = (p, n, f)

        # Blend language embedding with emotional embedding
        lang_vec = embed(text)
        psi_vec  = psi_embed(p, n, f)
        signal   = blend(lang_vec, psi_vec, PSI_WEIGHT)

        # Find resonating spheres
        best_sphere = None
        best_sim    = 0.0

        for sphere in self.spheres:
            sim = sphere.resonate(signal)
            if sim > best_sim:
                best_sim    = sim
                best_sphere = sphere

        # If nothing resonated, birth a new sphere
        if best_sphere is None:
            new = Sphere(centre=signal)
            self.spheres.append(new)
            result = {
                "event": "born",
                "id": new.id,
                "label": "?",
                "msg": f"new sphere born (id={new.id[:4]})"
            }
        else:
            result = {
                "event": "resonated",
                "id": best_sphere.id,
                "label": best_sphere.label,
                "confidence": round(best_sim, 3),
                "groove": best_sphere.groove,
                "msg": f"→ {best_sphere.label} (conf={best_sim:.3f}, groove={best_sphere.groove})"
            }

        # Tick every N messages
        if self.msg_count % TICK_EVERY == 0:
            self._tick()

        # Save every N messages
        if self.msg_count % SAVE_EVERY == 0:
            self.save()

        return result

    # ── TICK ──────────────────────────────────────────────────────────────────

    def _tick(self, debug=False):
        self.tick_count += 1

        # Decay
        self.spheres = [s for s in self.spheres if s.tick()]

        # Merge check — find eligible pairs
        merges_this_tick = 0
        merged_ids = set()

        eligible = [s for s in self.spheres if s.groove >= GROOVE_TO_MERGE]

        if debug and eligible:
            print(f"\n  [tick debug — {len(eligible)} merge-eligible spheres]")
            for i, a in enumerate(eligible):
                for b in eligible[i+1:]:
                    sim = cosine(a.centre, b.centre)
                    marker = "✦ CLOSE" if sim >= MERGE_THRESHOLD else f"  {sim:.3f}"
                    print(f"    {marker}  {a.label}({a.groove}) × {b.label}({b.groove})")

        for i, a in enumerate(self.spheres):
            if merges_this_tick >= MAX_MERGES_TICK:
                break
            if a.id in merged_ids:
                continue
            if a.groove < GROOVE_TO_MERGE:
                continue

            for b in self.spheres[i+1:]:
                if b.id in merged_ids:
                    continue
                if b.groove < GROOVE_TO_MERGE:
                    continue

                sim = cosine(a.centre, b.centre)
                if sim >= MERGE_THRESHOLD:
                    child = self._merge(a, b)
                    merged_ids.add(a.id)
                    merged_ids.add(b.id)
                    merges_this_tick += 1
                    self.merge_count += 1
                    print(f"  ✦ MERGE: {a.label} + {b.label} → {child.label} (gen {child.generation})")
                    break

    def _merge(self, a: Sphere, b: Sphere) -> Sphere:
        child_centre = normalise([x + y for x, y in zip(a.centre, b.centre)])
        child = Sphere(centre=child_centre, parents=[a, b])
        child.label = self._next_greek()
        self.spheres.append(child)
        # Parents reset — they don't die
        a.groove = 0
        b.groove = 0
        return child

    def _next_greek(self) -> str:
        label = GREEK[self._greek_idx % len(GREEK)]
        self._greek_idx += 1
        return label

    # ── SEED ──────────────────────────────────────────────────────────────────

    def seed(self, text: str, label: str, psi: tuple = None):
        """Plant a named concept directly."""
        p, n, f = psi if psi else (0.5, 0.0, 0.5)
        lang_vec = embed(text)
        psi_vec  = psi_embed(p, n, f)
        centre   = blend(lang_vec, psi_vec, PSI_WEIGHT)
        sphere   = Sphere(centre=centre, label=label)
        sphere.groove = GROOVE_TO_MERGE  # born grooved
        self.spheres.append(sphere)
        print(f"  ◈ seeded: {label}")

    # ── CLASSIFY ──────────────────────────────────────────────────────────────

    def classify(self, text: str, psi: tuple = None, prefer_named: bool = True) -> dict:
        """What concept does this text map to?

        prefer_named=True: named spheres (not '?') win ties with unnamed ones.
        This prevents unnamed ephemeral spheres from drowning out seeded concepts.
        """
        p, n, f = psi if psi else self._last_psi
        lang_vec = embed(text)
        psi_vec  = psi_embed(p, n, f)
        signal   = blend(lang_vec, psi_vec, PSI_WEIGHT)

        best_named   = None
        best_named_sim = 0.0
        best_any     = None
        best_any_sim = 0.0

        for sphere in self.spheres:
            sim = cosine(sphere.centre, signal)
            if sim > best_any_sim:
                best_any_sim = sim
                best_any     = sphere
            if sphere.label != "?" and sim > best_named_sim:
                best_named_sim = sim
                best_named     = sphere

        # Prefer named if it's within 15% of the best match
        if prefer_named and best_named and best_named_sim >= best_any_sim * 0.85:
            best     = best_named
            best_sim = best_named_sim
        else:
            best     = best_any
            best_sim = best_any_sim

        if best is None:
            return {"concept": None, "confidence": 0.0}

        return {
            "concept": best.label,
            "confidence": round(best_sim, 3),
            "groove": best.groove,
            "generation": best.generation,
            "parents": best.parents
        }

    # ── EXPLAIN ───────────────────────────────────────────────────────────────

    def explain(self, label: str) -> list:
        """Full lineage of a concept."""
        sphere_map = {s.id: s for s in self.spheres}
        target = next((s for s in self.spheres if s.label == label), None)
        if not target:
            return []

        chain = []
        queue = [target]
        seen  = set()
        while queue:
            s = queue.pop(0)
            if s.id in seen:
                continue
            seen.add(s.id)
            chain.append(s.to_dict())
            for pid in s.parents:
                if pid in sphere_map:
                    queue.append(sphere_map[pid])
        return chain

    # ── STATE ─────────────────────────────────────────────────────────────────

    def state(self) -> dict:
        return {
            "creature": self.creature_id,
            "spheres": len(self.spheres),
            "ticks": self.tick_count,
            "messages": self.msg_count,
            "merges": self.merge_count,
            "concepts": sorted(
                [{"label": s.label, "groove": s.groove, "gen": s.generation}
                 for s in self.spheres],
                key=lambda x: -x["groove"]
            )
        }

    # ── SAVE / LOAD ───────────────────────────────────────────────────────────

    def save(self, path: str = None):
        path = path or f"creature_{self.creature_id}_mind.json"
        data = {
            "creature_id":  self.creature_id,
            "saved":        datetime.now().isoformat(),
            "tick_count":   self.tick_count,
            "msg_count":    self.msg_count,
            "merge_count":  self.merge_count,
            "greek_idx":    self._greek_idx,
            "last_psi":     list(self._last_psi),
            "spheres":      [s.to_dict() for s in self.spheres]
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"  💾 mind saved → {path} ({len(self.spheres)} spheres)")

    @classmethod
    def load(cls, path: str) -> "CreatureMind":
        with open(path) as f:
            data = json.load(f)

        mind = cls(creature_id=data["creature_id"])
        mind.tick_count  = data["tick_count"]
        mind.msg_count   = data["msg_count"]
        mind.merge_count = data["merge_count"]
        mind._greek_idx  = data["greek_idx"]
        mind._last_psi   = tuple(data["last_psi"])

        for sd in data["spheres"]:
            s = Sphere(centre=sd["centre"], label=sd["label"])
            s.id         = sd["id"]
            s.groove     = sd["groove"]
            s.timer      = sd["timer"]
            s.generation = sd["generation"]
            s.parents    = sd["parents"]
            s.born       = sd["born"]
            mind.spheres.append(s)

        print(f"  ◈ loaded mind: {len(mind.spheres)} spheres, {mind.msg_count} messages")
        return mind

# ─── LAB TEST ─────────────────────────────────────────────────────────────────

def run_lab_test(mind: CreatureMind):
    """Automated emergence test — runs without user input."""
    print("\n━━━ LAB TEST — EMOTIONAL CONCEPT EMERGENCE ━━━\n")

    # Seed core emotional poles
    mind.seed("love warmth connection care", "LOVE",    psi=(0.9, 0.0, 0.7))
    mind.seed("fear terror panic threat",   "FEAR",    psi=(0.1, 0.9, 0.1))
    mind.seed("rage fury anger hatred",     "RAGE",    psi=(0.2, 0.8, 0.9))
    mind.seed("calm peace stillness quiet", "CALM",    psi=(0.7, 0.0, 0.3))
    mind.seed("joy delight happy laugh",    "JOY",     psi=(1.0, 0.0, 0.8))
    mind.seed("grief loss pain absence",    "GRIEF",   psi=(0.1, 0.7, 0.1))

    print("\n── Phase 1: reinforce poles ──")
    signals = [
        ("i love you so much",              (0.9, 0.0, 0.8)),
        ("you mean everything to me",       (0.85, 0.0, 0.7)),
        ("i am terrified right now",        (0.1, 0.95, 0.1)),
        ("something is coming and i'm scared", (0.15, 0.85, 0.2)),
        ("pure calm breathing slowly",      (0.7, 0.0, 0.4)),
        ("nothing is wrong everything is fine", (0.75, 0.0, 0.3)),
        ("laughing so hard can't breathe", (1.0, 0.0, 0.9)),
        ("this is the best day ever",       (0.95, 0.0, 0.85)),
        ("i miss you so much it hurts",     (0.2, 0.6, 0.15)),
        ("grief is love with nowhere to go",(0.15, 0.65, 0.1)),
    ]
    for text, psi in signals:
        r = mind.signal(text, psi=psi)
        print(f"  '{text[:40]}' {r['msg']}")

    print("\n── Phase 2: signals at intersections ──")
    intersections = [
        ("scared but i know it will be ok",        (0.5, 0.5, 0.5)),
        ("afraid but moving forward anyway",        (0.4, 0.6, 0.6)),
        ("loving someone even when it hurts",       (0.5, 0.4, 0.5)),
        ("tender and raw and open",                 (0.55, 0.35, 0.55)),
        ("angry but trying to stay calm",           (0.4, 0.5, 0.5)),
        ("fury turning into something quieter",     (0.45, 0.45, 0.45)),
        ("joy mixed with sadness at the same time", (0.6, 0.3, 0.6)),
        ("happy tears at the end of something",     (0.65, 0.25, 0.55)),
    ]
    for text, psi in intersections:
        r = mind.signal(text, psi=psi)
        print(f"  '{text[:40]}' {r['msg']}")

    print("\n── Phase 3: hammer an intersection to force emergence ──")
    # Send many variations of the same emotional region — courage/fear boundary
    courage_signals = [
        ("scared but doing it anyway",              (0.45, 0.55, 0.75)),
        ("fear that moves forward",                 (0.4,  0.6,  0.8)),
        ("terrified but refusing to stop",          (0.35, 0.65, 0.7)),
        ("walking into the dark on purpose",        (0.4,  0.55, 0.75)),
        ("shaking but still standing",              (0.45, 0.5,  0.7)),
        ("the fear is real but so is the will",     (0.5,  0.5,  0.8)),
        ("i am afraid and i am going anyway",       (0.4,  0.6,  0.75)),
        ("courage is not the absence of fear",      (0.5,  0.5,  0.7)),
        ("moving through the terror not around it", (0.45, 0.55, 0.8)),
        ("feel the fear do it anyway",              (0.4,  0.6,  0.7)),
    ]
    for text, psi in courage_signals:
        r = mind.signal(text, psi=psi)
        print(f"  '{text[:42]}' {r['msg']}")

    # Force ticks to trigger merges — debug on to see actual similarities
    print("\n  [ticking with debug...]")
    for _ in range(5):
        mind._tick(debug=True)

    print("\n── Classification test ──")
    tests = [
        ("courage is fear that kept going", (0.5, 0.5, 0.7)),
        ("bittersweet memories",            (0.5, 0.3, 0.4)),
        ("fierce protective love",          (0.7, 0.3, 0.8)),
        ("peaceful acceptance",             (0.7, 0.1, 0.3)),
    ]
    for text, psi in tests:
        c = mind.classify(text, psi=psi)
        print(f"  '{text}' → {c['concept']} (conf={c['confidence']})")

    print("\n── Mind state ──")
    s = mind.state()
    print(f"  spheres: {s['spheres']} · merges: {s['merges']} · messages: {s['messages']}")
    print(f"  concepts by groove:")
    for c in s['concepts'][:10]:
        gen_marker = "◈" if c['gen'] > 0 else "·"
        print(f"    {gen_marker} {c['label']:8} groove={c['groove']}  gen={c['gen']}")

    mind.save()
    print("\n━━━ LAB TEST COMPLETE ━━━\n")

# ─── INTERACTIVE MODE ─────────────────────────────────────────────────────────

def interactive(mind: CreatureMind):
    print("\nInteractive mode. Commands:")
    print("  /state          — show mind state")
    print("  /explain LABEL  — lineage of a concept")
    print("  /classify TEXT  — classify text against current concepts")
    print("  /psi P N F      — set emotional state (0-1 each)")
    print("  /save           — save mind now")
    print("  /quit           — exit\n")

    psi = (0.5, 0.0, 0.5)

    while True:
        try:
            raw = input(f"  ψ=({psi[0]:.1f},{psi[1]:.1f},{psi[2]:.1f}) > ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not raw:
            continue

        if raw == "/quit":
            mind.save()
            break
        elif raw == "/state":
            s = mind.state()
            print(f"\n  ◈ {s['creature']} — {s['spheres']} spheres · {s['merges']} merges · {s['messages']} msgs")
            for c in s['concepts'][:12]:
                gen_marker = "◈" if c['gen'] > 0 else "·"
                print(f"    {gen_marker} {c['label']:10} groove={c['groove']}  gen={c['gen']}")
            print()
        elif raw.startswith("/explain "):
            label = raw[9:].strip()
            chain = mind.explain(label)
            if not chain:
                print(f"  concept '{label}' not found\n")
            else:
                print(f"\n  lineage for {label}:")
                for node in chain:
                    indent = "  " * node['generation']
                    parents = f" ← [{', '.join(node['parents'])}]" if node['parents'] else " (origin)"
                    print(f"    {indent}{node['label']} (gen {node['generation']}, groove {node['groove']}){parents}")
                print()
        elif raw.startswith("/classify "):
            text = raw[10:].strip()
            c = mind.classify(text, psi=psi)
            print(f"  → {c['concept']} (conf={c['confidence']}, groove={c['groove']}, gen={c['generation']})\n")
        elif raw.startswith("/psi "):
            parts = raw[5:].split()
            if len(parts) == 3:
                psi = (float(parts[0]), float(parts[1]), float(parts[2]))
                print(f"  emotional state → p={psi[0]:.2f} n={psi[1]:.2f} f={psi[2]:.2f}\n")
        elif raw == "/save":
            mind.save()
        else:
            r = mind.signal(raw, psi=psi)
            print(f"  {r['msg']}\n")

# ─── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Creature Mind — SphereNet intelligence lab")
    parser.add_argument("--creature", default="anon", help="Creature ID")
    parser.add_argument("--load",     action="store_true", help="Load existing mind from JSON")
    parser.add_argument("--lab",      action="store_true", help="Run automated lab test")
    args = parser.parse_args()

    mind_file = f"creature_{args.creature}_mind.json"

    if args.load and os.path.exists(mind_file):
        mind = CreatureMind.load(mind_file)
    else:
        mind = CreatureMind(creature_id=args.creature)

    if args.lab:
        run_lab_test(mind)
    else:
        interactive(mind)
