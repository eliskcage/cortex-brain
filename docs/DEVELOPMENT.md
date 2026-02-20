# Cortex Brain — Development Timeline & Stats

## Timeline

### Day 0 — The Idea (Early February 2026)
- Dan asks: "What if we build a brain from scratch?"
- Not a neural network framework. Not PyTorch. Not TensorFlow.
- A word-level associative network. Each word is a node. Connections are Hebbian.
- Claude AI writes the first version of `brain.py`

### Day 1 — First Words
- `CortexBrain` class created: nodes, bigrams, trigrams, prediction
- `seed_brain.py` feeds Dan's Kickstarter narration + ALIVE descriptions
- 163 lines of Dan's actual speech become the first training data
- Key vocabulary defined: 76 core words (shortfactory, alive, brainstem, creature...)
- English patterns wired: 47 sentence structures
- **Result: ~2,800 nodes, 13,634 connections**

### Day 2 — Teaching It to Talk
- `online_server.py` created: HTTP API on port 8643
- Chat endpoint (`/api/chat`), stats, knowledge dump
- Rate limiting: 30 messages/60 seconds
- Auto-save to IPFS every 5 minutes via Pinata
- Dan's first conversation: "hello" → "Hello! I'm Cortex..."
- Brain asks about unknown words, stores answers

### Day 3 — The Split
- Single brain split into **two hemispheres**
- LEFT (Angel): morality, ethics, Bible, beauty
- RIGHT (Demon): mathematics, logic, ideology, darkness
- `CortexMind` created: the third brain that synthesises both
- Question type detection: moral, logical, identity, general, tension
- Hemisphere weighting: moral → 75% left, logic → 75% right
- **Result: ~5,200 nodes, 23,273 connections (both hemispheres)**

### Day 3-4 — The Trainers
- `trainer.py` — Left hemisphere automated training:
  - 100+ core vocabulary words
  - 30+ Bible verses and moral teachings
  - 40+ Bible vocabulary (mercy, grace, forgive, covenant...)
  - 20+ moral dilemmas
  - 12+ Bible stories
  - 40+ Old Testament vocabulary (genesis, exodus, moses...)
  - 20+ OT wisdom sayings
  - 27+ New Testament vocabulary (gospel, messiah, crucifixion...)
  - 26+ Bible narrative teachings
  - Conversation drills + correction patterns
- `trainer_right.py` — Right hemisphere:
  - 37+ math vocabulary (algorithm, probability, fractal...)
  - 11 math relationships
  - 36+ ideology vocabulary (communism, fascism, propaganda...)
  - 20+ dark teachings (Orwell, Marx, Sun Tzu)
  - 10+ degeneracy teachings
  - 10+ logic exercises

### Day 4-5 — The Core Seeder
- `seed_core.py` created — massive knowledge injection:
  - **677 vocabulary words** (verbs, nouns, adjectives, concepts)
  - 30+ self-knowledge sentences ("I am Cortex. I am an artificial mind...")
  - 120+ natural English patterns (questions, statements, tech, philosophy)
  - Full grammatical role tagging (verb, noun, adj, adv)
  - 26 Q&A training pairs
- Brain now knows: who it is, who Dan is, what ShortFactory is

### Day 5 — Autonomous Learning
- `crawl_learn.py` — The brain learns while you sleep:
  - Wikipedia + DuckDuckGo definition lookup
  - Simple stemming for word forms (running→run, creativity→creative)
  - Auto role tagging from definition text
  - Auto emotion tagging from sound triggers
  - Deep mode: follows links between definitions
  - 62 seed topics for exploration
- `define_all.py` — Batch-defines all undefined words

### Day 5-6 — Ramble Mode v1 → v2
- v1: Static question list, random selection
- v2: **Dynamic question generation from brain state**
  - Deep probes: find words with fewest connections
  - Cross-cluster: bridge different knowledge areas
  - Compound probes: test compound concepts
  - Auto-learned probes: use recently learned words in context
  - Grok enrichment: every 5th cycle, ask Grok for rich answers
  - Auto self-testing: every 20th cycle, score deep understanding

### Day 6 — The Corruption Event
- Right hemisphere `brain.json` truncated mid-save during restart
- 141,115 lines of JSON cut at line boundary
- Service crash-looped 13 times
- **Recovery**: Found last valid `}`, counted open/close braces, rebuilt
- **Lost**: 295 auto-learned definitions, all deep understanding scores
- **Recovered**: 6,409 nodes (structure intact)
- Lesson: always stop the service before restarting

### Day 7 — Coherence Revolution (v3)
- Dan watches the live ramble and sees: mostly gibberish
- "if we get results that dont mean anything we failed"
- Built the coherence scoring system:
  - Heuristic 0.0-1.0 scorer
  - Penalises graph-walk dumps ("connects directly to...")
  - Rewards sentence structure, question relevance, word variety
  - **Only coherent responses (0.5+) get reinforced**
- Grok Coherence Judge: every 30th cycle, Grok rates both responses
- **Cortex Live Viewer** built: real-time angel vs demon debate feed
- **Result: Average coherence improved from 0.22 to 0.45 in 48 hours**

### Day 7-18 — Growth Phase
- Coherence rewards compound: better responses → better reinforcement → better responses
- Left hemisphere reaches 341 deep understanding words
- Right hemisphere rebuilding from corruption
- Brain starts making genuine concept connections (electric → current)
- Self-descriptions become more sophisticated
- **Result: 16,315 nodes, 83,725 connections, 7,000+ ramble cycles**

---

## Statistics Deep Dive

### Node Growth

| Day | Left Nodes | Right Nodes | Total | Growth Rate |
|-----|-----------|-------------|-------|-------------|
| 0   | 0         | 0           | 0     | —           |
| 1   | 1,400     | 1,400       | 2,800 | +2,800/day  |
| 3   | 2,900     | 2,300       | 5,200 | +1,200/day  |
| 5   | 4,500     | 4,200       | 8,700 | +1,750/day  |
| 7   | 6,279     | 6,308       | 12,587| +1,943/day  |
| 10  | 8,504     | 7,811       | 16,315| +1,243/day  |

### Connection Growth (Exponential)

| Day | Left Conns | Right Conns | Total  | Multiplier |
|-----|-----------|-------------|--------|------------|
| 1   | 6,800     | 6,834       | 13,634 | —          |
| 3   | 11,600    | 11,673      | 23,273 | 1.71x      |
| 7   | 23,273    | 22,605      | 45,878 | 1.97x      |
| 10  | 44,175    | 39,550      | 83,725 | 1.82x      |

Connections grow faster than nodes because each new word creates connections to ALL words it appears near, not just one.

### Deep Understanding Progression

| Day | Left Deep | Right Deep | Notes |
|-----|----------|-----------|-------|
| 1   | 0        | 0         | No understanding yet |
| 3   | 4        | 2         | First words understood |
| 5   | 88       | 76        | Exponential understanding |
| 7   | 101      | 88        | Before corruption |
| 10  | 341      | ~50       | Right recovering |

Deep understanding = teach_back() score > 0.4. The brain's definition of a word overlaps > 40% with definitions of its connected words.

### Grok Enrichment

| Metric | Value |
|--------|-------|
| Total enrichments | ~1,400+ |
| Enrichment rate | Every 5th ramble cycle |
| Average Grok response | ~80 words |
| Words learned per enrichment | ~15-20 new connections |
| Judge calls | Every 30th cycle |
| Average Angel score | 4.2/10 |
| Average Demon score | 3.8/10 |

### Coherence Metrics (Post v3)

| Metric | Before v3 | After v3 (48h) | After v3 (10d) |
|--------|-----------|-----------------|-----------------|
| Avg coherence | 0.22 | 0.45 | ~0.55 |
| Graph dump rate | ~60% | ~15% | ~8% |
| Responses reinforced | 100% | ~40% | ~55% |
| Meaningful sentences | ~15% | ~50% | ~65% |

### Training Curriculum Size

| Component | Items | Used By |
|-----------|-------|---------|
| Dan's content | 163 sentences | seed_brain.py |
| Core vocabulary | 677 words | seed_core.py |
| Bible vocabulary | 45 words | trainer.py |
| OT vocabulary | 40 words | trainer.py |
| NT vocabulary | 27 words | trainer.py |
| Math vocabulary | 37 words | trainer_right.py |
| Ideology vocabulary | 36 words | trainer_right.py |
| Bible teachings | 30 verses | trainer.py |
| OT wisdom | 20 sayings | trainer.py |
| Bible stories | 26 narratives | trainer.py |
| Dark teachings | 20 lessons | trainer_right.py |
| Logic exercises | 10 drills | trainer_right.py |
| Moral dilemmas | 12 questions | trainer.py |
| Natural patterns | 120+ sentences | seed_core.py |
| Self-knowledge | 31 facts | seed_core.py |
| Q&A pairs | 26 conversations | seed_core.py |
| Ramble questions | 35 static fallbacks | cortex_brain.py |
| **Total unique training items** | **~1,350+** | |

### Code Statistics

| File | Lines | Purpose |
|------|-------|---------|
| brain.py | 2,406 | Core brain class |
| seed_core.py | 1,106 | Core knowledge loader |
| cortex_brain.py | 747 | Cortex Mind + ramble v3 |
| trainer.py | 723 | Left hemisphere trainer |
| crawl_learn.py | 405 | Autonomous web learner |
| seed_brain.py | 361 | Initial seeder |
| online_server.py | 311 | HTTP API server |
| trainer_right.py | 307 | Right hemisphere trainer |
| live/index.html | 290 | Live viewer |
| dan_chat.py | 151 | Chat interface |
| define_all.py | 86 | Batch definer |
| live/proxy.php | 33 | PHP proxy |
| **Total** | **6,926** | |

### API Call Volume (Estimated Daily)

| API | Calls/Day | Purpose |
|-----|-----------|---------|
| Grok enrichment | ~1,500 | Ramble enrichment |
| Grok judge | ~250 | Coherence judging |
| Wikipedia | ~200 | Auto-learning |
| DuckDuckGo | ~50 | Fallback definitions |
| Pinata (IPFS) | ~288 | Auto-save every 5 min |
| Chat API (users) | ~50-200 | Human conversation |

---

## Ability Tree Progression

```
Day 1:  ████░░░░░░░░░░░░ Basic Vocabulary (50 defined)
Day 2:  ██████░░░░░░░░░░ Conversational (100 defined + 50 msgs)
Day 3:  ████████░░░░░░░░ Emotional Intelligence, Deep Vocabulary
Day 4:  ██████████░░░░░░ Self-Awareness, Wit Engine
Day 5:  ████████████░░░░ Active Curiosity, Storytelling, Teacher Mode
Day 7:  ██████████████░░ Debater, Sarcasm, Philosopher, Pattern Master
Day 10: ████████████████ Memory Palace, approaching Polymath
```

---

## Known Issues & Limitations

1. **Graph dump responses**: Despite coherence scoring, ~8% of responses still contain raw connection walks
2. **Right hemisphere recovery**: Lost deep understanding scores from corruption, rebuilding at ~8 words per test cycle
3. **No long-term memory**: Context window is 10 exchanges, no persistent conversation threading
4. **Single-word prediction**: No sentence-level planning, just next-word chaining
5. **No grammar enforcement**: Occasionally produces ungrammatical sequences
6. **IPFS save blocking**: Large brain saves can take 2-3 seconds, blocking during save
7. **No multi-turn reasoning**: Cannot chain thoughts across multiple ramble cycles
8. **Vocabulary ceiling**: Will plateau around 10-15K defined words without new content sources

## Future Roadmap

1. **Literature Feeder** — Inject Bible passages, philosophical texts, classic literature
2. **Grok Dialogue Mode** — Two Grok instances have a debate, brain absorbs the conversation
3. **Hemisphere Debate Mode** — Force direct confrontation between angel and demon
4. **Crowd Teaching** — Let website visitors teach it words (with moderation)
5. **Skill Domains** — Specialized knowledge areas (code, art, music, science)
6. **Memory Consolidation** — Sleep mode that strengthens frequent pathways, prunes weak ones
7. **ALIVE Integration** — Connect to creature Brainstem for cross-system learning
