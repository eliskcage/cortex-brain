"""
CORTEX TRAINER — WHITE BRAIN (Dictionary + Truth)

Feeds dictionary definitions into the Cortex's own word pool.
Source: Free Dictionary API (dictionaryapi.dev) — NO external AI.
The White brain is the Cortex's neutral ground truth — no morality, no darkness, just facts.

Usage: python3 trainer_cortex.py
Runs as: cortex-trainer-white.service
"""
import json
import time
import random
import requests

API = 'http://localhost:8643/api/chat-white'
ANALYSIS = 'http://localhost:8643/api/brain-live'
DICT_API = 'https://api.dictionaryapi.dev/api/v2/entries/en/%s'
LOG_FILE = '/var/www/vhosts/shortfactory.shop/httpdocs/alive/studio/trainer_cortex.log'

# Delay between messages — respect free API rate limits
MIN_DELAY = 6
MAX_DELAY = 15

# ========================================
# CURRICULUM — dictionary-quality definitions
# ========================================

# Stage 1: Core English (500 essential words)
# These are the building blocks of all language
CORE_ENGLISH = [
    # Abstract concepts
    'truth', 'beauty', 'justice', 'freedom', 'power', 'knowledge', 'wisdom',
    'courage', 'honor', 'dignity', 'integrity', 'loyalty', 'respect',
    'responsibility', 'authority', 'liberty', 'equality', 'democracy',
    'tyranny', 'oppression', 'rebellion', 'revolution', 'evolution',
    'progress', 'tradition', 'culture', 'civilization', 'society',
    'community', 'individual', 'identity', 'consciousness', 'awareness',
    'perception', 'reality', 'illusion', 'imagination', 'creativity',
    'intelligence', 'genius', 'intuition', 'instinct', 'reason',
    'logic', 'analysis', 'synthesis', 'theory', 'hypothesis',
    'evidence', 'proof', 'certainty', 'doubt', 'belief',
    'faith', 'trust', 'betrayal', 'deception', 'honesty',
    'virtue', 'vice', 'morality', 'ethics', 'principle',
    'value', 'meaning', 'purpose', 'destiny', 'fate',
    'chance', 'luck', 'fortune', 'risk', 'consequence',
    'cause', 'effect', 'influence', 'impact', 'legacy',

    # Emotions
    'love', 'hate', 'fear', 'anger', 'joy', 'sadness', 'grief',
    'hope', 'despair', 'anxiety', 'peace', 'contentment', 'satisfaction',
    'pride', 'shame', 'guilt', 'envy', 'jealousy', 'gratitude',
    'compassion', 'empathy', 'sympathy', 'contempt', 'disgust',
    'surprise', 'wonder', 'awe', 'curiosity', 'boredom',
    'frustration', 'patience', 'courage', 'cowardice', 'loneliness',

    # Human nature
    'ambition', 'greed', 'generosity', 'selfishness', 'altruism',
    'arrogance', 'humility', 'vanity', 'modesty', 'charisma',
    'discipline', 'laziness', 'persistence', 'resilience', 'vulnerability',
    'strength', 'weakness', 'talent', 'skill', 'effort',
    'success', 'failure', 'achievement', 'defeat', 'victory',
    'struggle', 'sacrifice', 'reward', 'punishment', 'forgiveness',

    # Philosophy & thought
    'existence', 'essence', 'being', 'nothingness', 'infinity',
    'eternity', 'mortality', 'immortality', 'soul', 'spirit',
    'mind', 'body', 'matter', 'energy', 'force',
    'nature', 'nurture', 'instinct', 'habit', 'choice',
    'determinism', 'free will', 'paradox', 'contradiction', 'irony',
    'metaphor', 'symbol', 'archetype', 'myth', 'legend',
    'philosophy', 'theology', 'ideology', 'dogma', 'doctrine',
    'skepticism', 'empiricism', 'rationalism', 'nihilism', 'existentialism',
    'pragmatism', 'utilitarianism', 'stoicism', 'hedonism', 'absurdism',

    # Science & nature
    'atom', 'molecule', 'cell', 'gene', 'DNA',
    'evolution', 'mutation', 'adaptation', 'selection', 'survival',
    'gravity', 'entropy', 'relativity', 'quantum', 'photon',
    'wavelength', 'frequency', 'spectrum', 'dimension', 'spacetime',
    'universe', 'galaxy', 'planet', 'star', 'orbit',
    'ecosystem', 'habitat', 'species', 'predator', 'symbiosis',
    'organism', 'bacteria', 'virus', 'immune', 'parasite',
    'climate', 'weather', 'temperature', 'pressure', 'cycle',

    # Technology
    'algorithm', 'data', 'network', 'protocol', 'encryption',
    'decentralisation', 'blockchain', 'cryptocurrency', 'artificial',
    'intelligence', 'neural', 'machine', 'computation', 'binary',
    'digital', 'analog', 'signal', 'bandwidth', 'latency',
    'server', 'client', 'database', 'cache', 'memory',
    'processor', 'transistor', 'circuit', 'voltage', 'current',

    # Economics & power
    'capital', 'labor', 'wealth', 'poverty', 'inequality',
    'market', 'monopoly', 'competition', 'supply', 'demand',
    'inflation', 'deflation', 'currency', 'debt', 'credit',
    'investment', 'profit', 'loss', 'dividend', 'interest',
    'taxation', 'subsidy', 'trade', 'tariff', 'embargo',
    'sovereignty', 'autonomy', 'independence', 'colony', 'empire',
    'propaganda', 'censorship', 'surveillance', 'privacy', 'security',

    # Relationships & society
    'family', 'marriage', 'friendship', 'alliance', 'rivalry',
    'hierarchy', 'equality', 'justice', 'law', 'order',
    'chaos', 'anarchy', 'government', 'constitution', 'rights',
    'obligation', 'duty', 'privilege', 'status', 'class',
    'education', 'literacy', 'ignorance', 'prejudice', 'tolerance',
    'diversity', 'unity', 'conflict', 'compromise', 'consensus',
    'negotiation', 'diplomacy', 'war', 'peace', 'treaty',

    # Language & communication
    'language', 'grammar', 'syntax', 'semantics', 'rhetoric',
    'narrative', 'argument', 'persuasion', 'propaganda', 'truth',
    'fiction', 'fact', 'opinion', 'bias', 'objectivity',
    'context', 'nuance', 'ambiguity', 'clarity', 'precision',

    # Art & expression
    'beauty', 'art', 'music', 'poetry', 'literature',
    'drama', 'comedy', 'tragedy', 'satire', 'parody',
    'innovation', 'tradition', 'style', 'form', 'content',
    'expression', 'interpretation', 'criticism', 'taste', 'aesthetic',

    # Time & change
    'past', 'present', 'future', 'history', 'memory',
    'nostalgia', 'anticipation', 'moment', 'era', 'epoch',
    'cycle', 'pattern', 'trend', 'momentum', 'inertia',
    'transformation', 'metamorphosis', 'decay', 'renewal', 'rebirth',

    # The body
    'heart', 'blood', 'bone', 'muscle', 'skin',
    'eye', 'ear', 'hand', 'foot', 'face',
    'breath', 'sleep', 'hunger', 'thirst', 'fatigue',
    'health', 'disease', 'medicine', 'surgery', 'therapy',

    # Everyday life
    'food', 'water', 'shelter', 'clothing', 'fire',
    'tool', 'weapon', 'wheel', 'bridge', 'road',
    'book', 'pen', 'paper', 'map', 'clock',
    'door', 'window', 'wall', 'roof', 'floor',
    'garden', 'forest', 'river', 'mountain', 'ocean',
    'rain', 'snow', 'wind', 'thunder', 'lightning',
    'sun', 'moon', 'earth', 'sky', 'horizon',

    # Social concepts
    'leader', 'follower', 'citizen', 'stranger', 'neighbor',
    'teacher', 'student', 'master', 'apprentice', 'mentor',
    'king', 'queen', 'soldier', 'priest', 'merchant',
    'criminal', 'victim', 'witness', 'judge', 'jury',
    'promise', 'contract', 'debt', 'gift', 'trade',
    'ceremony', 'ritual', 'festival', 'funeral', 'wedding',

    # Abstract thought
    'theory', 'practice', 'experiment', 'observation', 'conclusion',
    'assumption', 'exception', 'rule', 'principle', 'standard',
    'limit', 'boundary', 'threshold', 'balance', 'proportion',
    'origin', 'destination', 'journey', 'path', 'obstacle',
    'method', 'system', 'structure', 'foundation', 'framework',
    'process', 'result', 'outcome', 'measure', 'comparison',

    # Character & personality
    'honest', 'dishonest', 'kind', 'cruel', 'gentle',
    'fierce', 'calm', 'anxious', 'confident', 'timid',
    'stubborn', 'flexible', 'loyal', 'treacherous', 'reliable',
    'clever', 'foolish', 'wise', 'naive', 'cunning',
]

# Stage 2: Relationship teachings (word pairs with factual connections)
RELATIONSHIPS = [
    ('truth', 'deception', 'truth is the factual state of affairs, deception is its deliberate distortion'),
    ('cause', 'effect', 'a cause is what makes something happen, an effect is what results from it'),
    ('freedom', 'responsibility', 'freedom without responsibility leads to chaos'),
    ('power', 'corruption', 'power tends to corrupt because it removes accountability'),
    ('knowledge', 'wisdom', 'knowledge is having information, wisdom is knowing how to use it'),
    ('logic', 'emotion', 'logic deals with reasoning, emotion deals with feeling, both inform decisions'),
    ('theory', 'evidence', 'a theory must be supported by evidence to be considered valid'),
    ('individual', 'society', 'individuals form society, society shapes individuals'),
    ('nature', 'nurture', 'nature is what you are born with, nurture is what shapes you after'),
    ('supply', 'demand', 'when supply exceeds demand prices fall, when demand exceeds supply prices rise'),
    ('risk', 'reward', 'greater risk generally comes with greater potential reward'),
    ('action', 'consequence', 'every action has consequences, intended or not'),
    ('rights', 'obligations', 'rights come with corresponding obligations'),
    ('strength', 'vulnerability', 'true strength includes acknowledging vulnerability'),
    ('innovation', 'tradition', 'innovation breaks from tradition, both have value'),
    ('chaos', 'order', 'chaos is the absence of order, order is imposed structure'),
    ('fact', 'opinion', 'facts are verifiable, opinions are personal interpretations'),
    ('liberty', 'security', 'increasing security often requires sacrificing some liberty'),
    ('intelligence', 'wisdom', 'intelligence is processing speed, wisdom is knowing what to process'),
    ('ambition', 'contentment', 'ambition drives achievement, contentment brings peace'),
    ('leader', 'follower', 'a leader guides, a follower supports, both are needed'),
    ('teacher', 'student', 'a teacher shares knowledge, a student receives it, the best do both'),
    ('heart', 'mind', 'the heart feels, the mind thinks, wisdom uses both'),
    ('health', 'disease', 'health is the normal state, disease is its disruption'),
    ('promise', 'trust', 'a kept promise builds trust, a broken promise destroys it'),
    ('journey', 'destination', 'the journey shapes you, the destination is just where you end up'),
    ('foundation', 'structure', 'a strong foundation supports everything built upon it'),
    ('observation', 'conclusion', 'good conclusions come from careful observation not assumptions'),
    ('honest', 'dishonest', 'honesty builds relationships, dishonesty destroys them'),
    ('gentle', 'fierce', 'knowing when to be gentle and when to be fierce is wisdom'),
    ('calm', 'anxious', 'calm comes from acceptance, anxiety comes from resistance'),
    ('confident', 'timid', 'confidence grows from experience, timidity shrinks from fear'),
    ('sun', 'moon', 'the sun gives light directly, the moon reflects what it receives'),
    ('fire', 'water', 'fire transforms by consuming, water transforms by flowing'),
    ('mountain', 'river', 'mountains stand firm, rivers find the path of least resistance'),
]

# Stage 3: Truth vs comfort — teach the brain when to choose truth
TRUTH_DRILLS = [
    'sometimes the truth hurts but it is still better than a comfortable lie',
    'facts do not care about feelings, but wise people consider both',
    'telling someone what they want to hear is not kindness, it is cowardice',
    'the hardest truths are usually the most important ones to hear',
    'a painful truth is worth more than a pleasant fiction',
    'truth is not democratic, it does not change because people disagree with it',
    'evidence outweighs intuition when they conflict',
    'being right is more important than being liked, but delivery matters',
    'comfort is not the same as truth, and truth is not always comfortable',
    'the truth does not require your belief to be true',
    'when feelings and facts collide, examine the facts first',
    'strategic honesty is knowing when truth serves better than diplomacy',
    'a good summary captures the essential truth, not every detail',
    'synthesis means finding what is true in opposing views, not splitting the difference',
    'the best answer is often the one that acknowledges complexity without losing clarity',
    'the map is not the territory, a description of something is not the thing itself',
    'silence can be more powerful than words when used at the right moment',
    'the first step to solving a problem is admitting it exists',
    'what you do when nobody is watching reveals your true character',
    'the greatest teacher is failure because it forces you to adapt',
    'understanding something and being able to explain it simply are two different skills',
    'strong opinions loosely held means believe deeply but change when evidence demands it',
    'the answer to most either or questions is both',
    'knowing what you do not know is more valuable than knowing what you do know',
    'the simplest explanation is usually the best one',
    'you cannot reason someone out of a position they did not reason themselves into',
    'the difference between medicine and poison is the dose',
    'correlation does not imply causation just because two things happen together does not mean one caused the other',
    'extraordinary claims require extraordinary evidence',
]


# ========================================
# DICTIONARY API FUNCTIONS
# ========================================

def fetch_definition(word):
    """Get definition from Free Dictionary API. Returns (definition, part_of_speech) or (None, None)."""
    try:
        url = DICT_API % word.replace(' ', '%20')
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data and isinstance(data, list):
                entry = data[0]
                meanings = entry.get('meanings', [])
                if meanings:
                    pos = meanings[0].get('partOfSpeech', '')
                    defs = meanings[0].get('definitions', [])
                    if defs:
                        defn = defs[0].get('definition', '')
                        # Get additional definitions for richness
                        all_defs = []
                        for m in meanings[:2]:
                            for d in m.get('definitions', [])[:2]:
                                all_defs.append(d.get('definition', ''))
                        combined = '. '.join(all_defs[:3])
                        return combined[:250], pos
        return None, None
    except Exception as e:
        log('[DICT-API] Error for "%s": %s' % (word, str(e)))
        return None, None


# ========================================
# BRAIN COMMUNICATION
# ========================================

def chat(text):
    """Send a message to the white brain."""
    try:
        r = requests.post(API, json={'text': text}, timeout=30)
        if r.status_code == 200:
            data = r.json()
            return data.get('reply', ''), data.get('stats', {})
        return None, {}
    except Exception as e:
        log('[ERROR] Chat failed: %s' % str(e))
        return None, {}


def get_live():
    """Get live brain stats."""
    try:
        r = requests.post(ANALYSIS, timeout=10)
        if r.status_code == 200:
            return r.json()
        return None
    except:
        return None


def log(msg):
    """Log a message."""
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    line = '[%s] %s' % (ts, msg)
    print(line)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except:
        pass


# ========================================
# TEACHING FUNCTIONS
# ========================================

def teach_word(word, definition):
    """Teach a word with its dictionary definition to the white brain."""
    # Check if already known
    reply, stats = chat('what is %s' % word)
    if reply and definition[:20].lower() in reply.lower():
        log('[SKIP] Already knows "%s"' % word)
        return True

    # Try to teach
    if reply and ("don't know" in reply.lower() or "what does" in reply.lower()
                  or "what is it" in reply.lower()):
        reply2, _ = chat(definition)
        log('[TEACH] %s = %s' % (word, definition[:80]))
        return True

    # Force teach
    reply, _ = chat('let me teach you about %s' % word)
    time.sleep(1)
    reply, _ = chat('%s means %s' % (word, definition))
    if reply and any(w in reply.lower() for w in ['stored', 'wired', 'noted', 'locked', 'got it', 'cheers']):
        log('[TEACH] %s = %s' % (word, definition[:80]))
        return True

    log('[TEACH-FAIL] Could not teach "%s": %s' % (word, reply))
    return False


def teach_relationship(word1, word2, explanation):
    """Teach how two words relate."""
    reply, _ = chat('how does %s relate to %s' % (word1, word2))
    time.sleep(1)
    chat(explanation)
    log('[REL] %s <-> %s: %s' % (word1, word2, explanation[:60]))
    return True


def teach_truth_drill(statement):
    """Feed a truth-priority statement through the brain."""
    reply, _ = chat(statement)
    log('[TRUTH] "%s" -> "%s"' % (statement[:50], (reply or '')[:50]))
    return True


# ========================================
# TRAINING ROUND
# ========================================

# Track which words we've tried to fetch definitions for
definition_cache = {}


def training_round():
    """Run one round of dictionary training."""

    # Pick training activity
    activity = random.choices(
        ['dict_word', 'relationship', 'truth_drill', 'test_understanding'],
        weights=[50, 20, 20, 10],
        k=1
    )[0]

    if activity == 'dict_word':
        # Pick a random word from curriculum
        word = random.choice(CORE_ENGLISH)
        word_clean = word.strip().lower()

        # Check cache first
        if word_clean in definition_cache:
            defn = definition_cache[word_clean]
        else:
            # Free Dictionary API only — no external AI
            defn, pos = fetch_definition(word_clean)
            if defn:
                log('[DICT] Got definition for "%s" (%s)' % (word_clean, pos))

            if defn:
                definition_cache[word_clean] = defn
            else:
                log('[DICT] No definition found for "%s"' % word_clean)
                return

        teach_word(word_clean, defn)

    elif activity == 'relationship':
        rel = random.choice(RELATIONSHIPS)
        teach_relationship(rel[0], rel[1], rel[2])

    elif activity == 'truth_drill':
        drill = random.choice(TRUTH_DRILLS)
        teach_truth_drill(drill)

    elif activity == 'test_understanding':
        word = random.choice(CORE_ENGLISH).strip().lower()
        reply, _ = chat('do you understand %s' % word)
        if reply:
            if "don't know" in reply.lower() or 'understanding: 0/' in reply:
                log('[TEST-FAIL] No understanding of "%s" — will reteach' % word)
                defn, pos = fetch_definition(word)
                if defn:
                    teach_word(word, defn)
            else:
                log('[TEST] %s: %s' % (word, (reply or '')[:80]))


# ========================================
# MAIN LOOP
# ========================================

def main():
    log('=' * 60)
    log('[WHITE TRAINER] Starting Cortex Dictionary Trainer')
    log('[WHITE TRAINER] Target: %s' % API)
    log('[WHITE TRAINER] Dictionary: dictionaryapi.dev — pure, no external AI')
    log('[WHITE TRAINER] Curriculum: %d words, %d relationships, %d truth drills' % (
        len(CORE_ENGLISH), len(RELATIONSHIPS), len(TRUTH_DRILLS)))
    log('=' * 60)

    # Wait for server to be ready
    for attempt in range(10):
        live = get_live()
        if live:
            break
        log('[WHITE TRAINER] Waiting for brain server... (attempt %d)' % (attempt + 1))
        time.sleep(5)

    if not live:
        log('[ERROR] Brain not reachable after 10 attempts. Is the server running?')
        return

    round_count = 0
    while True:
        try:
            round_count += 1
            log('\n--- White Training Round %d ---' % round_count)
            training_round()

            # Save to IPFS every 30 rounds
            if round_count % 30 == 0:
                try:
                    requests.post('http://localhost:8643/api/brain-save', timeout=30)
                    log('[SAVE] Triggered IPFS save')
                except:
                    pass

            # Wait between rounds — respect API rate limits
            delay = random.uniform(MIN_DELAY, MAX_DELAY)
            time.sleep(delay)

        except KeyboardInterrupt:
            log('[WHITE TRAINER] Stopped by user')
            break
        except Exception as e:
            log('[ERROR] Round failed: %s' % str(e))
            time.sleep(15)


if __name__ == '__main__':
    main()
