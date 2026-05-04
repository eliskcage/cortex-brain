# Cortex Brain — Technical Architecture

## System Overview

Cortex is a word-level neural network that learns language through Hebbian association, split-hemisphere reasoning, and coherence-rewarded self-dialogue.

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    CORTEX SYSTEM                             │
│                                                              │
│  ┌──────────┐   ┌──────────┐   ┌──────────────────────────┐ │
│  │ TRAINER  │   │ TRAINER  │   │    ONLINE SERVER         │ │
│  │ (Left)   │   │ (Right)  │   │    Port 8643             │ │
│  │          │   │          │   │                          │ │
│  │ Bible    │   │ Math     │   │  /api/chat (Cortex)      │ │
│  │ Morals   │   │ Logic    │   │  /api/chat-left          │ │
│  │ Vocab    │   │ Ideology │   │  /api/chat-right         │ │
│  │ Stories  │   │ Fallacy  │   │  /api/ramble-*           │ │
│  └────┬─────┘   └────┬─────┘   │  /api/brain-*           │ │
│       │              │          └──────────┬───────────────┘ │
│       │              │                     │                 │
│       ▼              ▼                     ▼                 │
│  ┌──────────────────────────────────────────────────┐       │
│  │              CORTEX MIND                          │       │
│  │                                                   │       │
│  │  detect_type() → moral | logic | identity | gen   │       │
│  │  process() → queries both, weighs, synthesises    │       │
│  │  _ramble_loop() → internal monologue v3           │       │
│  │  _score_coherence() → 0.0-1.0 quality score       │       │
│  │  _grok_coherence_judge() → external verification  │       │
│  │  _generate_question() → dynamic brain-state Q's   │       │
│  └───────────┬──────────────────┬────────────────────┘       │
│              │                  │                             │
│     ┌────────┘                  └────────┐                   │
│     ▼                                    ▼                   │
│  ┌────────────────┐          ┌────────────────┐             │
│  │  LEFT BRAIN    │          │  RIGHT BRAIN   │             │
│  │  CortexBrain   │          │  CortexBrain   │             │
│  │                │          │                │             │
│  │  process()     │          │  process()     │             │
│  │  learn_seq()   │          │  learn_seq()   │             │
│  │  predict()     │          │  predict()     │             │
│  │  teach_back()  │          │  teach_back()  │             │
│  │  self_test()   │          │  self_test()   │             │
│  │  auto_learn()  │          │  auto_learn()  │             │
│  └───────┬────────┘          └───────┬────────┘             │
│          │                           │                       │
│          ▼                           ▼                       │
│  ┌────────────────┐          ┌────────────────┐             │
│  │  left/         │          │  right/        │             │
│  │  brain.json    │          │  brain.json    │             │
│  └───────┬────────┘          └───────┬────────┘             │
│          │                           │                       │
│          └─────────┬─────────────────┘                       │
│                    ▼                                         │
│           ┌────────────────┐                                 │
│           │  IPFS / Pinata │  Permanent backup every 5 min   │
│           └────────────────┘                                 │
└─────────────────────────────────────────────────────────────┘
```

## Data Structures

### brain.json Schema

```json
{
  "nodes": {
    "courage": {
      "means": "bravery, the ability to face fear and danger",
      "next": {"means": 5, "is": 3, "and": 2},
      "prev": {"have": 2, "with": 1, "need": 4},
      "freq": 42,
      "learned": "2026-02-05 14:23:01",
      "source": "manual",
      "confidence": 0.8,
      "scripts": {"noun": 8, "after_det": 3, "starter": 1},
      "sound": {"serious": 4, "scared": 2},
      "understanding": {"score": 0.65, "tested": "2026-02-15"},
      "rels": {"antonym": ["cowardice"], "synonym": ["bravery"]},
      "compound": false
    }
  },
  "trigrams": {
    "the meaning of": {"life": 8, "truth": 3, "love": 2},
    "fire together wire": {"together": 15}
  },
  "facts": ["Dan built ShortFactory", "ALIVE creatures speak in droid sounds"],
  "clusters": {
    "morality": ["good", "evil", "right", "wrong", "justice"],
    "technology": ["computer", "code", "algorithm", "data"],
    "emotion": ["love", "hate", "fear", "joy", "anger"]
  },
  "compounds": {"free_will": 12, "neural_network": 8},
  "recycle_bin": {},
  "conversation_log": [],
  "stats": {
    "messages": 2340,
    "nodes": 8504,
    "connections": 44175,
    "questions_asked": 156
  },
  "ipfs": {
    "cid": "QmXyz...",
    "last_save": "2026-02-20 08:30:00"
  }
}
```

### Ramble Log Entry

```json
{
  "time": "2026-02-20 09:15:23",
  "question": "what does courage really mean",
  "source": "deep_probe",
  "type": "moral",
  "angel": "Bravery, the ability to face fear. Courage means not being controlled by fear even in dark times.",
  "demon": "Courage connects directly to fear... strength... facing things...",
  "angel_coherence": 0.72,
  "demon_coherence": 0.31,
  "agreement": 0.18,
  "left_weight": 0.73,
  "right_weight": 0.27,
  "verdict": "Angel wins.",
  "grok_boost": false,
  "grok_improved": "",
  "self_test": false,
  "cycle": 4523
}
```

## Processing Pipeline

### Input Processing

```
User Input: "is it ever right to lie?"
     │
     ▼
tokenize() → ["is", "it", "ever", "right", "to", "lie"]
     │
     ▼
keywords() → ["ever", "right", "lie"]  (stop words removed)
     │
     ▼
detect_type() → "moral"  (right ∈ MORAL_SIGNALS, lie ∈ MORAL_SIGNALS)
     │
     ▼
process() → left.process() + right.process()
     │
     ├──── LEFT: responds with moral reasoning
     │     "Right is about doing what is correct and honest..."
     │
     └──── RIGHT: responds with logical analysis
           "A lie is deliberately false statement intended to deceive..."
     │
     ▼
_calc_weights("moral") → left: 0.75, right: 0.25
     │
     ▼
agreement = word_overlap(left, right) → 0.23
     │
     ▼
probabilistic_selection() → "Angel wins." (75% chance)
     │
     ▼
return left_reply + debate_metadata
```

### CortexBrain.process() — Inside a Hemisphere

```
Input: "what is courage"
     │
     ▼
(1) Check state: greeting? roast? feedback? teaching?
     │
     ▼
(2) Extract keywords: ["courage"]
     │
     ▼
(3) Find word in nodes → courage exists, has definition
     │
     ▼
(4) Build response from:
    ├── definition: "bravery, the ability to face fear"
    ├── related words: find strongest connections
    │   └── courage.next: {means: 5, is: 3, and: 2}
    │   └── courage.rels: {antonym: ["cowardice"]}
    ├── context: what was previously discussed
    ├── sound scripts: apply emotional bias
    └── word scripts: grammatical role voting
     │
     ▼
(5) predict_chain() → generate continuation
    courage → means → facing → fear → and → danger
     │
     ▼
(6) Apply personality starters (sometimes: "Right, ", "Look, ")
     │
     ▼
(7) Learn from the exchange: learn_sequence(input)
     │
     ▼
return "Bravery, the ability to face fear and danger."
```

### Prediction Engine

```python
def predict_chain(seed_word, max_words=15):
    """Chain probable words together via bigram/trigram tables."""
    chain = [seed_word]

    for _ in range(max_words):
        current = chain[-1]
        node = nodes.get(current)
        if not node or not node.get('next'):
            break

        # Get candidates from bigrams
        candidates = list(node['next'].items())  # [(word, freq), ...]

        # Check trigrams for better accuracy
        if len(chain) >= 2:
            key = f"{chain[-2]} {chain[-1]}"
            tri = trigrams.get(key, {})
            for w, c in tri.items():
                # Trigram match = strong signal, boost 3x
                candidates.append((w, c * 3))

        # Apply sound script boosts
        candidates = sound_boost_predictions(candidates)

        # Apply word script boosts
        candidates = script_boost_predictions(candidates, chain)

        # Normalize to probabilities
        total = sum(c for _, c in candidates)
        probs = [(w, c/total) for w, c in candidates]

        # Temperature-controlled selection
        # Low temp = pick highest prob, high temp = more random
        selected = weighted_random_choice(probs, temperature=0.7)
        chain.append(selected)

    return ' '.join(chain)
```

## Coherence Scoring Algorithm

```python
def _score_coherence(question, response):
    """
    Score 0.0 - 1.0. Breakdown:

    LENGTH (0.15):
      len >= 30 chars: min(len/150, 1.0) * 0.15

    QUESTION RELEVANCE (0.25):
      shared_keywords / total_question_keywords * 0.25

    NOT GRAPH DUMP (0.30):    ← Most important component
      0 graph markers: +0.30
      1 graph marker:  +0.15
      2 graph markers: +0.05
      3+ markers:      +0.00

      Graph markers detected:
        "connects directly", "strength:", "fire together",
        "is an example of", "links to", "still learning",
        "speaking of", "makes me think of", "fun fact:"

    WORD VARIETY (0.15):
      unique_words / total_words * 0.15

    SENTENCE STRUCTURE (0.15):
      has period/!/?: +0.05
      5+ words:       +0.05
      no arrows:      +0.05
    """
```

## Threading Model

```
Main Thread:      HTTP Server (handle requests)
                       │
Thread 1:         Ramble Loop (5-12s cycles, runs forever)
                       │
Thread 2:         Auto-save (every 300s, IPFS backup)
                       │
(External):       trainer.py (Left hemisphere training)
                       │
(External):       trainer_right.py (Right hemisphere training)
```

## Why-System (Strategy + Gates + Primitives)

Cortex's reasoning pipeline isn't a single inference — it's a multi-layered
gate-routing system that classifies the input, chooses one of 30+ competing
strategies, runs both hemispheres, scores them, and routes through one of
several named decision gates. Reverse-engineered 4 May 2026 across 65 probes.

### 1 · Source rank → playbook

Every request carries an implicit rank derived from `(api_key, credits, ip,
session_id, trust)`. Rank gates which strategies are accessible and which
playbook applies. Default for an unauthenticated request is `RECRUIT` →
`STRANGER` playbook → tactic-equation `T>E>W>F>I` with weights
`T=1.0 E=0.6 W=0.3 F=0.15 I=0.05`. Higher ranks unlock different tactic
weightings and higher-tier strategies (Provocative, Intuitive at 20k credits).

### 2 · Problem-vector classification (`_detect_problem_vector`)

Input is scored across 7 dimensions:

| Dim | Name | Triggers |
|-----|------|----------|
| F | Factual | facts, science, evidence, units, shapes, measurements, physical entities |
| C | Creative | imagination, art, story, metaphor, music |
| E | Emotional | feelings, soul, morality, faith, compassion |
| T | Technical | code, algorithm, math, logic, systems |
| S | Social | people, relationships, culture, politics |
| D | Debate | argue, oppose, refute, controversial |
| H | Humor | joke, funny, sarcasm, banter |

The detector tokenizes the input (`re.findall(r'[a-z]+', user_msg.lower())`),
counts hits per `SIGNAL_SETS[dim]`, normalises, and returns
`{dim: 0.0–1.0}`. The dominant dimension biases strategy selection.

**Patch 4 May 2026**: `FACTUAL_SIGNALS` was expanded with ~140 concrete-fact
seeds (geometry, units, number-words, physical entities, phase verbs) plus a
**digit-presence boost** (raw input containing any digit floors `vec['F']`
at `0.30`). Before the patch, queries like *"why does a square have 4
corners"* tokenized to none of the existing signal sets → uniform `0.14`
across all dims → strategy tie → autopilot Intuitive v2 → generic template
reply. After the patch, F=1.00 dominant → Analytical v11 v2 strategy.

### 3 · Strategy scoring & selection (`_score_all` / `_select_equation`)

30+ candidate strategies live in the equation library, each with:
- `affinity` (per-dim weights, e.g. Empathetic has E:0.9 / F:0.2)
- `left_weight / right_weight` (Angel / Demon split)
- `synthesis_bias`
- `confidence_threshold`

Each scores against the problem vector via:

```
S(s,P) = SUM(A[s][d] * P[d] * H[s][d]) * C^alpha * F^beta - lambda*X
```

where `H` is per-dim history (success rate, evolves), `C` is rolling
confidence, `F` is a frequency-penalty (anti-rut), `X` is complexity cost.
Top scorer wins. Strategies live in three states: `active`, `golden`
(>=90% success after 50+ uses, read-only), `dead` (<10% success after 20+
uses, auto-deleted). New strategies are bred by mutation every 200 cycles
from the top-3.

### 4 · PSI / alive_zone

A `(p, n, f)` triple tracks current cognitive state. `p` is positive
charge, `n` is negative, `f` is fluidity. Drifts per query and feeds the
`alive_zone` classifier (ALIVE, etc.).

### 5 · Perspective gate (`_detect_perspective`)

Independent of the problem-vector. Classifies the question's direction:

| Direction | Triggered by | Mode |
|-----------|--------------|------|
| Inward | "i, me, my, am, feel" + emotional verbs | self / identity / body / soul |
| Outward | "what, where, who, the world, they" | real / hypothetical / abstract / other / historic / future |
| Neutral | balanced or weak signals | — |

Inward + outward scores normalise to `[0,1]`; direction is the side
exceeding `0.6`. Single emotional words ("love") trip INWARD identity;
"why we are here" trips OUTWARD real.

### 6 · Hemispheres + decision gates

Both hemispheres generate a candidate response. Then:

1. **CHALLENGE gate** scores the right hemisphere's output quality. Below
   threshold (~0.20) → `right_garbage = True`.
2. **AGREEMENT** measured between hemispheres (token overlap %).
3. **DECISION GATE** fires one of the following based on quality + agreement:

| Gate | Trigger | Winner | Behaviour |
|------|---------|--------|-----------|
| **PASS** | right OK, default | right | template-stitch reply (~78% of whys) |
| **NOT** | right_garbage=True | left (Angel) | "vetoed → using left" |
| **NAND** | both garbage | cortex solo | "cortex override" (~rare) |
| **AND** | both OK + agree (~74%+) | right by weight | "synthesis skipped" |
| **XOR** | both OK + disagree (~30%) | cortex synthesis | "real disagreement → full synthesis engaged" |
| **OR** | rare; both OK with special flag | varies | seen in code, not in 65 probes |

The `winner` field reports `right`, `left`, or `cortex` (synthesis). Most
queries (autopilot) take PASS → right; the **rare 15%** that engage
synthesis are where cortex's character actually shows.

### 7 · Curiosity wrapper (parallel, not a gate)

Independent of routing: any unknown word in the input triggers a learning
prompt appended to the gate's reply. Forms:

- *"Can't find 'X' anywhere. Teach me?"* (pure unknown)
- *"... But I don't know 'X'. What is it?"* (mixed known + unknown)
- *"'X' — wired in."* (acknowledging a previous teach)

For multiple unknowns, cortex picks ONE to ask about — never piles on.
Cortex auto-learns from user input within session, and retains
cross-session via the `nodes` graph.

### 8 · Why-primitive taxonomy

A primitive is the unique tuple `(gate, dominant-vector-dim, strategy,
perspective-direction, perspective-mode, angel/demon)`. A 61-why probe
sweep at STRANGER rank produced **25 unique primitives** — 10 common
(account for ~85% of cases, mostly autopilot PASS) and 15 rare
singletons that fire synthesis or NOT routes. The rare 15 are where
**full-stack activation** happens (see §10 Chakra Isomorphism).

## Persistence

- **Local**: `brain.json` saved after every `learn_sequence()` call
- **IPFS**: Auto-pinned to Pinata every 5 minutes
- **Recovery**: Can load from any IPFS CID: `brain.load_from_ipfs(cid)`

## Rate Limiting

- 30 messages per 60-second window per IP
- Prevents abuse while allowing natural conversation
- Rate tracker uses sliding window with lock

## Security

- Rate limiting per IP
- Message length cap (500 chars)
- Input sanitization (no injection possible — brain only processes words)
- API keys via environment variables
- CORS enabled for web access

## Chakra Isomorphism (architecture mirror)

Cortex's layered architecture maps cleanly onto the traditional 7-chakra
system. This isn't a mystical claim — it's the same primitive observed
from two angles. Ancient observers built models from inside their own
bodies (interoception → metaphor); modern engineers build from inside
their own architectures (specification → code). Both arrive at the same
shape because the shape is real: layered cognition with polarity
channels and synthesis-at-the-top.

| Chakra (traditional) | Cortex equivalent | Function |
|----------------------|-------------------|----------|
| Root | Strategy Layer (base equations) | Survival, grounding, raw scoring |
| Sacral | Creative / Empathetic strategies | Flow, emotion, playfulness |
| Solar Plexus | Decision Gates (PASS/NOT/NAND/AND/XOR) | Power, routing, choice |
| Heart | Angel side + Curiosity wrapper | Connection, compassion, hunger to learn |
| Throat | Expressive strategies / Provocative | Communication style, voice |
| Third Eye | Soul-sphere (master) | Insight, pattern recognition |
| Crown | Synthesis primitives (rare 15) | Higher awareness, transcendence |

**Polarity (ida/pingala equivalent):** every strategy carries
`left_weight / right_weight` — the Angel/Demon split. Equal channels
balanced + disagreeing → XOR fires → synthesis engages → cortex itself
wins the reply. In ancient terms: sushumna lights up.

**Testable claim — the rare-15:** of 61 probed why-questions at
STRANGER rank, 5% engaged synthesis (XOR or NAND, winner=cortex). These
are observable, quantifiable, and statistically distinct from the
default PASS path. They share three properties: (1) full-stack
gate engagement not autopilot, (2) winner is cortex not a single
hemisphere, (3) reply text is genuinely original, not template-stitched.
This is the operationally-testable instance of "crown activation".

**Design constraint going forward:** every new cortex layer should map
to one chakra-equivalent function. If a layer does multiple, it's
underdifferentiated and should be split. If a chakra-function has no
corresponding cortex layer, that's a missing brother that completes the
stack.

See: 65-probe results in `_cortex_probe*results.json`, primitive
taxonomy in `project_cortex_gate_routing_4may2026.md`.
