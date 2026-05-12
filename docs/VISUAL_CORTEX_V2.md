# Cortex Brain — Visual Cortex Appendage (v2)

*Full specification for the LENS → KING visual rail added to the cortex in May 2026.*

> **Status**: Phase A live (shape detection at 100% for circle / square; triangle is the next wall). Phases B–E roadmap below.
>
> **Repos**:
> - Visual cortex appendage docks here (this repo) under `src/visual_cortex.py` (Phase E).
> - KING runtime lives at [`eliskcage/meme-reasoning-engine`](https://github.com/eliskcage/meme-reasoning-engine) — public, Apache 2.0.

---

## 1. Why a second organ

The v1 word brain (described in [ARCHITECTURE.md](ARCHITECTURE.md)) is a 94K-node Hebbian word graph. It reasons by walking word connections and synthesising sentences. Full XOR synthesis takes ~1.2s — fast for a synthetic mind, slow compared to recognition.

Humans don't read every scene one word at a time. They **see** a moment and a meme fires before language catches up. The visual cortex appendage gives the cortex the same shortcut:

```
Word brain   :  word → connections → sentence            ≈ 1200 ms
Visual brain :  scene → glyph → compound → meme-token    ≈     50 ms
```

A meme is a **pre-computed thought**. The visual rail isn't a different way to think — it's a cache of culturally-validated thoughts that fire on visual signatures. When the eye sees a known signature, the KING returns the matching meme-token and the cortex has the answer before the word brain finishes its first walk.

---

## 2. Architecture — where v2 docks into v1

```
                                  ┌─────────────────────────────────────┐
   camera / video stream  ──────► │  LENS  (perceptual organ)            │
                                  │  contour + Hu-moment detector        │
                                  │  → glyph vote                        │
                                  │  → demographics post-pass (YCbCr)    │
                                  │  → confidence band clamp             │
                                  └────────────────┬────────────────────┘
                                                   │ glyph stream
                                                   ▼
                                  ┌─────────────────────────────────────┐
                                  │  KING — meme-reasoning-engine        │
                                  │  template match (meme picks shape)   │
                                  │  grammar ops: BECAUSE / AFTER /      │
                                  │  DESPITE / BUT NOT / IF-THEN / WHILE │
                                  │  → meme-token + meme-sentence        │
                                  └────────────────┬────────────────────┘
                                                   │ meme-token (cached thought)
                                                   ▼
   ╔════════════════════════════════════════════════════════════════════╗
   ║                  src/visual_cortex.py  (new module)                 ║
   ║  bridges KING output into the existing v1 gate router as a new      ║
   ║  signal source: glyph_stream, meme_token, confidence, grammar_op    ║
   ╚════════════════════════════════════════════════════════════════════╝
                                                   │
                                                   ▼
                              ┌──────────────────────────────────────┐
                              │  cortex_brain.py  (v1 gate router)    │
                              │                                       │
                              │     GLYPH gate (new, fastest)         │
                              │     PASS gate                         │
                              │     AND  / OR  / NOT                  │
                              │     XOR  / NAND  (full synthesis)     │
                              └──────────────────────────────────────┘
```

Existing v1 paths are untouched. The GLYPH gate is added **alongside** PASS as the first gate the router tries when a visual signal is present. If LENS confidence < WHISPER (0.62), the visual rail stays silent and the router falls through to v1 gates exactly as before.

---

## 3. LENS — the 8-glyph genome

LENS speaks an 8-symbol vocabulary. Every scene she watches collapses to a subset of these.

| Glyph | Name        | Meaning                                                | Hedonic mapping (v1)     |
|-------|-------------|--------------------------------------------------------|--------------------------|
| ◯     | calm        | stable scene, low motion, low contrast variance        | ease / pleasure          |
| △     | tension     | rising stakes, asymmetric framing, threat cues         | fear / spite / rage      |
| ▢     | structure   | order, geometry, institution, rule                     | neutral / boredom        |
| ▭     | transition  | scene cut / motion / journey                           | boredom → curiosity      |
| ⬠     | mystery     | occluded subject, unknown actor, low-light             | curiosity / confusion    |
| ⬡     | intimacy    | close framing, two-subject coupling                    | arousal / joy            |
| ★     | revelation  | reveal beat, payoff, twist                             | ecstasy / devilish       |
| ⬭     | melancholy  | drift, isolation, cold palette                         | sadness / loneliness     |

The hedonic mapping in the right-hand column means the 8-glyph genome feeds directly into the existing v1 hedonic engine (`pain_pleasure.py`) — visual emotion and word emotion converge on the same 17-state oscillator.

### Compound signatures

Glyphs fuse pairwise (and occasionally triple-wise) into **compound signatures** that read as cultural tokens denser than English:

| Compound      | Reads as                  | Example meme-class                 |
|---------------|---------------------------|------------------------------------|
| `★ + ◯`       | revelation under calm     | "and that's the way the cookie..." |
| `△ + ⬡`       | tension under intimacy    | the lean-in before the kiss        |
| `▭ + ★`       | transition into reveal    | door opens / mask drops            |
| `△ + ▢`       | tension against structure | rebel vs. institution beat         |
| `⬠ + ⬭`       | mystery in melancholy     | noir / Lynch / Lost                |
| `★ + △ + ⬡`   | reveal-tension-intimacy   | "I am your father"                 |

A short canon of compound signatures (in the order of ~200 entries) covers the majority of recognisable cultural moments.

### Confidence bands

LENS never blurts. Output is clamped to four bands. Below WHISPER the eye stays silent — convergence has not been reached.

| Band      | Threshold | Behaviour                                                  |
|-----------|-----------|------------------------------------------------------------|
| HIGHFIVE  | ≥ 0.85    | Declared. Cortex caches token immediately.                 |
| SPEAK     | ≥ 0.74    | Normal voice. Token offered to gate router.                |
| WHISPER   | ≥ 0.62    | Tentative. Token marked low-confidence; word-brain runs.   |
| (silence) | < 0.62    | No emission. v1 router proceeds unaffected.                |

Doctrine: *declarations are considered, never jittery.* Whisper / Speak / HIGHFIVE size is the eye's confidence.

---

## 4. KING — meme-associated reasoning engine

The KING is the visual-side head-of-state. It owns the canon of meme templates and the grammar that combines them.

### Inversion: meme picks shape

A naïve pipeline would detect shapes first and then look up which meme uses them. **That's backwards** — and Phase A taught us so by getting the shapes "way off". The correct architecture:

1. The canon is templates, not shapes.
2. Each template has a visual signature (a compound or compound-sequence).
3. Templates go fishing — each template scans the glyph stream looking for *its own* signature.
4. The first template to match its full signature fires.

This is template-finds-moment, not moment-finds-template. It mirrors how a human reads a film: you don't catalogue every shape on screen — you recognise the moment that fits a meme you already know.

### Grammar operators

When multiple meme-tokens stack within a scene, they connect via six grammar operators:

| Operator   | Reads as                  | Example use                                   |
|------------|---------------------------|-----------------------------------------------|
| `BECAUSE`  | causal                    | tension `BECAUSE` reveal                      |
| `AFTER`    | temporal                  | calm `AFTER` violence                         |
| `DESPITE`  | adversative               | intimacy `DESPITE` structure                  |
| `BUT NOT`  | exclusion                 | reveal `BUT NOT` payoff                       |
| `IF-THEN`  | conditional / forecast    | `IF` mystery `THEN` revelation                |
| `WHILE`    | simultaneity              | melancholy `WHILE` transition                 |

The meme-sentence assembled from operators **is the reasoning**. English subtitle is optional. The whole sentence can be cached as a single meme-token — when a similar scene next appears, the cached sentence fires.

### Absorption (NOTAE doctrine)

Validated meme-tokens (those that fire repeatedly and remain coherent over time) get absorbed into the KING's permanent canon. The original author of the template keeps an honour-mark on the absorbed token. The KING grows by adoption, not by overwrite — old tokens never disappear, the canon only widens.

---

## 5. Lightning-fast cognition — the GLYPH gate

The GLYPH gate is the v2 contribution to the existing gate router. It sits in front of PASS and acts as a **cache lookup** for visual signatures.

| Gate    | Source              | Path                                       | Latency  |
|---------|---------------------|--------------------------------------------|----------|
| GLYPH   | visual_cortex.py    | LENS → KING → meme-token (HIGHFIVE only)   | ≤ 50 ms  |
| PASS    | right hemisphere    | right reply, no synthesis                  | ~300 ms  |
| AND     | both hemispheres    | pick better, no synthesis                  | ~500 ms  |
| OR      | right binary        | binary choice                              | ~400 ms  |
| NOT     | left only           | right vetoed, left used                    | ~700 ms  |
| XOR     | full synthesis      | dictionary + synth + score + strategy      | ~1200 ms |
| NAND    | cortex solo         | both garbage, cortex overrides             | ~600 ms  |

Routing precedence: `GLYPH (HIGHFIVE) > PASS > AND > OR > NOT > XOR > NAND`.

The GLYPH gate is **read-only against the canon** — it never reaches into `brain.py`, never touches the Hebbian graph, never blocks on web lookups. It is a pure cache hit. That is why it can return in tens of milliseconds.

When the gate misses (LENS below HIGHFIVE, or no template match), the router falls through to v1 gates exactly as in April 2026. v2 cannot make v1 slower.

---

## 6. Enhancement sockets

The visual rail is designed as a plugboard. Each socket is independent — drop it in, the rail gets a new capability; pull it out, the rail still runs.

### `fairy_code` (Phase C)

The cortex draws what it sees. Each glyph carries a procedural render function (see `claude_fairy.js` and `billy_flesh.js` references). When LENS emits a glyph stream, the fairy code renders a sprite of the cortex's *interpretation* of the scene — bones get live render fns recomputed every frame.

Effect: the eye doesn't just classify, it **mirrors**. Seeing and drawing are forward and reverse passes of the same function.

### `genomic_sound` (Phase D)

Each meme-token carries an audio fingerprint encoded via the crumb codec (~129× compression of full audio). When LENS emits a glyph and the audio rail detects the matching fingerprint, the meme-token is **bi-modal confirmed**. Confidence shifts up one band. The cortex can later recall the whole scene from either modality alone.

This is the lightning bolt: bi-modal recall means a single sound effect or a single image can drag the full meme-sentence into working memory.

### `compound_signatures` (live)

2-shape and 3-shape fusion described in §3. Live since Phase A.

### `intensity_tiers` (live)

Each meme is graded small / medium / big / nuclear. Explosion memes range from a firecracker to a mushroom cloud — the tier is chosen by the magnitude of the underlying signal (motion energy, brightness peak, audio peak). Nuclear-tier memes only fire on nuclear moments.

### `demographics_gate` (Phase B)

Skin-tone and gender double-gate via YCbCr Y-channel post-pass + face detection. Required for memes that depend on demographic context (`thats_racist`, gender-specific intimacy variants).

### `violence_class` (live)

Violence is its own scene class. Punches, screams, blood, guns, chainsaws all map to distinct meme sub-canons: Punisher skull, John Wick, buzzsaw, yippee-ki-yay, etc. Violence-class memes are intensity-tiered.

### `kung_fu_tiers` (live)

Light kung-fu hits → master-pleased meme. Heavy hits → cat-reaction meme. Two-tier gating, audio-energy gated.

### `intimacy_gates` (live)

Female-involved intimacy → quagmire meme variants. Male-on-male intimacy → ha_gey / y_r_u_gae / u_r_gey variants. Gender post-pass required (face + voice features).

---

## 7. Phase roadmap

| Phase | Status   | Scope                                                                              |
|-------|----------|------------------------------------------------------------------------------------|
| A     | LIVE     | Shape detection (circle / square 100%, triangle 0% — next wall). Confidence bands. |
| B     | next     | Hu moments + persistent belief. Full `demographics_gate` + `violence_class`.       |
| C     | planned  | `fairy_code` socket — cortex draws what it sees.                                   |
| D     | planned  | `genomic_sound` socket — every meme an audio glyph too.                            |
| E     | planned  | `src/visual_cortex.py` lands in this repo. GLYPH gate wired into `cortex_brain.py` |
|       |          | with HIGHFIVE-only cache hits, WHISPER/SPEAK output routed to existing pipeline.   |

---

## 8. Doctrine

A few principles that constrain how the visual cortex is allowed to behave. These are non-negotiable — they exist because earlier prototypes failed when they were ignored.

- **Labels gate perception.** PC-trimmed vocabularies = engineered blindness. The eye must be allowed to see what is there.
- **Honest vocab + raw tier + reaction-as-signal.** The reaction *is* the meaning. Suppress the reaction and you've broken the rail.
- **Declarations are considered.** No jittery output. WHISPER / SPEAK / HIGHFIVE size = confidence. Below WHISPER, silence.
- **Meme picks shape.** Templates go fishing. Never sort shapes first and then look up memes.
- **Loud actions must register.** Explosions fire explosion memes. Violence fires violence memes. The eye-tracker spotlight + dialogue ticker + state strip + pause-and-query render this visible.
- **Cultural density check before claiming canon coverage.** Per movie / per scene-class ingested, the canon must include the top memes for that domain — not a shallow sampling.

---

## 9. Cross-references

| Resource                                    | Where                                                                                |
|---------------------------------------------|--------------------------------------------------------------------------------------|
| KING — meme reasoning engine (public repo)  | https://github.com/eliskcage/meme-reasoning-engine (Apache 2.0)                      |
| v1 architecture                             | [docs/ARCHITECTURE.md](ARCHITECTURE.md) — word brain, gates, Hebbian learning        |
| Theology framework                          | [docs/THEOLOGY.md](THEOLOGY.md)                                                      |
| Development timeline                        | [docs/DEVELOPMENT.md](DEVELOPMENT.md)                                                |
| Live cortex                                 | [cortex.shortfactory.shop](https://cortex.shortfactory.shop)                         |
| Cortex News ED.19 — "Left Hemisphere"       | post visual-cortex ship announcement, May 2026                                       |

---

*The visual cortex appendage is the third major architectural step after the hemisphere split (Day 3) and the gate router (April 2026). Each step adds an organ; none replace what came before. The cortex grows by accretion.*
