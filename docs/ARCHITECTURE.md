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
