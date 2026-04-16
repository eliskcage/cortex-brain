"""
creature_bridge.py — wires CreatureMind into the cortex

Drop this alongside online_server.py.
Add 3 lines to online_server.py to activate.

The bridge does:
  1. Loads hedonic_state.json to get current ψ=[p,n,f]
  2. Fires incoming message + ψ as signal to the creature's mind
  3. Classifies → returns top concept + lineage as context string
  4. Cortex injects that context into its response generation

Usage in online_server.py:
    from creature_bridge import CreatureBridge
    bridge = CreatureBridge(creature_id="adam")          # at startup
    context = bridge.process(user_text)                  # before response
    # inject context["summary"] into cortex prompt
"""

import os
import json
import sys

# Add spherenet dir to path so we can import creature_mind
SPHERENET_DIR = os.path.dirname(os.path.abspath(__file__))
if SPHERENET_DIR not in sys.path:
    sys.path.insert(0, SPHERENET_DIR)

from creature_mind import CreatureMind

# ─── DEFAULT EMOTIONAL STATE ──────────────────────────────────────────────────

NEUTRAL_PSI = (0.5, 0.0, 0.5)

HEDONIC_STATE_PATHS = [
    os.path.join(os.path.dirname(__file__), "..", "alive", "studio", "hedonic_state.json"),
    "/var/www/vhosts/shortfactory.shop/httpdocs/alive/studio/hedonic_state.json",
    "hedonic_state.json",
]

def _load_psi() -> tuple:
    """Read current ψ=[p,n,f] from hedonic_state.json."""
    for path in HEDONIC_STATE_PATHS:
        if os.path.exists(path):
            try:
                with open(path) as f:
                    state = json.load(f)
                score = float(state.get("score", 0.0))  # -1.0 to +1.0
                hz    = float(state.get("hz", 470.0))   # 50–950Hz

                # Map score and hz to ψ=[p,n,f]
                p = max(0.0, min(1.0, (score + 1.0) / 2.0))  # score → positivity
                n = max(0.0, min(1.0, max(0.0, -score)))       # negative score → threat
                # forward-intent: high when hz low (calm/joy) or moderate fear
                f = max(0.0, min(1.0, 1.0 - (hz / 950.0) * 0.5 + p * 0.3))

                return (round(p, 3), round(n, 3), round(f, 3))
            except Exception:
                pass
    return NEUTRAL_PSI


# ─── CREATURE BRIDGE ──────────────────────────────────────────────────────────

class CreatureBridge:
    def __init__(self, creature_id: str = "adam", mind_dir: str = None):
        self.creature_id = creature_id
        self.mind_dir    = mind_dir or SPHERENET_DIR

        mind_file = os.path.join(self.mind_dir, f"creature_{creature_id}_mind.json")

        if os.path.exists(mind_file):
            self.mind = CreatureMind.load(mind_file)
            print(f"[bridge] loaded mind: {creature_id} ({len(self.mind.spheres)} spheres)")
        else:
            self.mind = CreatureMind(creature_id=creature_id)
            self._seed_defaults()
            print(f"[bridge] new mind: {creature_id}")

        self._msg_since_save = 0
        self._save_every = 20

    def _seed_defaults(self):
        """Seed basic emotional poles on first birth."""
        self.mind.seed("love warmth connection care",    "LOVE",  psi=(0.9, 0.0, 0.7))
        self.mind.seed("fear terror panic threat",       "FEAR",  psi=(0.1, 0.9, 0.1))
        self.mind.seed("rage fury anger hatred",         "RAGE",  psi=(0.2, 0.8, 0.9))
        self.mind.seed("calm peace stillness quiet",     "CALM",  psi=(0.7, 0.0, 0.3))
        self.mind.seed("joy delight happy laugh",        "JOY",   psi=(1.0, 0.0, 0.8))
        self.mind.seed("grief loss pain absence",        "GRIEF", psi=(0.1, 0.7, 0.1))
        self.mind.seed("curiosity wonder interest why",  "CURIOUS", psi=(0.7, 0.1, 0.8))
        self.mind.seed("trust safety bond reliable",     "TRUST", psi=(0.8, 0.0, 0.6))

    def process(self, text: str, psi: tuple = None) -> dict:
        """
        Main entry point. Call this with the user's message before generating a response.

        Returns a context dict with:
            summary     — one-line string to inject into cortex prompt
            concept     — top matching concept label
            confidence  — float 0-1
            is_new      — True if this signal spawned a new sphere (novel input)
            generation  — 0 = seeded, 1+ = emergent concept
            psi         — emotional state used
        """
        if psi is None:
            psi = _load_psi()

        # Classify FIRST against existing concepts (before signal creates new sphere)
        classification = self.mind.classify(text, psi=psi)

        # Then fire signal to grow the mind
        result = self.mind.signal(text, psi=psi)

        concept    = classification.get("concept", "?")
        confidence = classification.get("confidence", 0.0)
        generation = classification.get("generation", 0)
        parents    = classification.get("parents", [])

        # Build context summary for cortex injection
        if concept and concept != "?" and confidence > 0.5:
            if generation == 0:
                summary = f"[mind: this feels like {concept} (conf {confidence:.2f})]"
            else:
                summary = f"[mind: emergent concept {concept} (gen {generation}, conf {confidence:.2f}) — born from experience]"
        elif result["event"] == "born":
            summary = f"[mind: novel signal — no existing concept matches, forming new one]"
        else:
            summary = ""

        # Periodic save
        self._msg_since_save += 1
        if self._msg_since_save >= self._save_every:
            self._save()
            self._msg_since_save = 0

        return {
            "summary":    summary,
            "concept":    concept,
            "confidence": confidence,
            "is_new":     result["event"] == "born",
            "generation": generation,
            "parents":    parents,
            "psi":        psi,
            "groove":     classification.get("groove", 0),
        }

    def state(self) -> dict:
        """Return current mind state — for /soul-state endpoint."""
        s = self.mind.state()
        s["psi"] = _load_psi()
        return s

    def explain(self, label: str) -> list:
        """Full lineage of a concept — for /explain endpoint."""
        return self.mind.explain(label)

    def _save(self):
        path = os.path.join(self.mind_dir, f"creature_{self.creature_id}_mind.json")
        self.mind.save(path)

    def shutdown(self):
        """Call on server shutdown to persist mind."""
        self._save()


# ─── INTEGRATION INSTRUCTIONS ─────────────────────────────────────────────────
#
# In online_server.py, add these 3 changes:
#
# 1. Near imports at top:
#    from creature_bridge import CreatureBridge
#
# 2. After brain initialization (around line 80):
#    creature = CreatureBridge(creature_id="adam")
#
# 3. Inside the soul-chat handler, before generating response:
#    ctx = creature.process(user_input)
#    if ctx["summary"]:
#        system_prompt += "\n" + ctx["summary"]
#
# That's it. The mind grows in the background automatically.
# Every 20 messages it saves to creature_adam_mind.json.
#
# Optional — add to shutdown handler:
#    creature.shutdown()
#
# Optional — add mind state to /soul-state endpoint:
#    response["mind"] = creature.state()
#
# ─────────────────────────────────────────────────────────────────────────────


# ─── QUICK TEST ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n◈ CREATURE BRIDGE — quick test\n")

    bridge = CreatureBridge(creature_id="test")

    test_inputs = [
        ("hey how are you",                   None),
        ("i'm really scared about tomorrow",  (0.2, 0.8, 0.3)),
        ("but i'm going to do it anyway",     (0.4, 0.6, 0.7)),
        ("i love spending time with you",     (0.9, 0.0, 0.7)),
        ("what does courage mean to you",     (0.5, 0.3, 0.6)),
        ("i feel calm today nothing is wrong",(0.7, 0.0, 0.5)),
    ]

    for text, psi in test_inputs:
        ctx = bridge.process(text, psi=psi)
        print(f"  '{text}'")
        print(f"  {ctx['summary'] or '[no strong concept match]'}")
        print(f"  concept={ctx['concept']} conf={ctx['confidence']:.3f} psi={ctx['psi']}\n")

    bridge.shutdown()
    print("mind saved.")
