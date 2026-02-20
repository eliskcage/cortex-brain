"""
CRAWL & LEARN — Continuous autonomous internet learning for Cortex.
Runs in background. Explores the web, learns new words, wires connections.
Each word it finds gets stored in its brain with definitions, role scripts,
emotional tags, and probabilistic connections.

The brain grows while you sleep.

Run: python crawl_learn.py
     python crawl_learn.py --topic "artificial intelligence"
     python crawl_learn.py --deep    (follows links between definitions)
"""
import sys, os, time, re, random, argparse, json
# Fix Windows cp1252 encoding issues
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brain import CortexBrain, ROLE_HINTS, SOUND_TRIGGERS

STUDIO_DIR = os.path.dirname(os.path.abspath(__file__))
PINATA_JWT = os.environ.get('PINATA_JWT', 'your-pinata-jwt-here')

brain = CortexBrain(STUDIO_DIR, pinata_jwt=PINATA_JWT)

import requests

# Words too basic to look up
SKIP = brain.tokenize(' '.join([
    'the a an is am are was were be been has have had do does did',
    'will would could should can may might shall must not no yes',
    'i me my we our you your he she it they them his her its their',
    'to of in on at by for with from up about into through during',
    'and but or nor so yet if then else when while where how what which who',
    'just also very really quite too even still already than more most',
    'ok okay yeah yep nah nope like got get go come make take give say',
    'thing things stuff way much many lot bit cos because right well now',
    'im ive ill id youre youve youll youd hes shes theyre were weve',
    'dont doesnt didnt cant wont isnt arent wasnt werent havent hasnt',
    'per vs etc v3 hp mp4 ok um uh er ah oh',
]))
SKIP = set(SKIP) | set(w for w in SKIP if len(w) <= 2)

# Topics to explore when we run out of undefined words
SEED_TOPICS = [
    'computer science', 'artificial intelligence', 'neural network',
    'machine learning', 'blockchain', 'cryptography', 'internet',
    'programming', 'algorithm', 'database', 'operating system',
    'web development', 'cybersecurity', 'cloud computing',
    'human brain', 'consciousness', 'psychology', 'philosophy',
    'mathematics', 'physics', 'biology', 'chemistry',
    'evolution', 'genetics', 'ecology', 'astronomy',
    'economics', 'democracy', 'history', 'sociology',
    'music theory', 'art history', 'literature', 'linguistics',
    'entrepreneurship', 'startup', 'marketing', 'product design',
    'ethics', 'morality', 'theology', 'spirituality',
    'creativity', 'innovation', 'leadership', 'teamwork',
    'communication', 'language', 'writing', 'storytelling',
    'health', 'nutrition', 'exercise', 'sleep',
    'emotional intelligence', 'resilience', 'mindfulness', 'meditation',
    'decentralization', 'open source', 'digital rights', 'privacy',
    'robotics', 'automation', 'internet of things', 'virtual reality',
]


def safe_print(text):
    """Print with fallback for encoding issues."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'))


def get_base_forms(word):
    """Get possible base forms of a word (simple stemming)."""
    forms = [word]
    if word.endswith('ing') and len(word) > 5:
        forms.append(word[:-3])       # running -> runn (not great but tries)
        forms.append(word[:-3] + 'e') # making -> make
        if len(word) > 6 and word[-4] == word[-5]:
            forms.append(word[:-4])   # running -> run
    if word.endswith('ed') and len(word) > 4:
        forms.append(word[:-2])       # played -> play
        forms.append(word[:-1])       # created -> create (remove d only)
        if len(word) > 5 and word[-3] == word[-4]:
            forms.append(word[:-3])   # stopped -> stop
    if word.endswith('es') and len(word) > 4:
        forms.append(word[:-2])       # reaches -> reach
        forms.append(word[:-1])       # takes -> take (remove s only)
    elif word.endswith('s') and len(word) > 3:
        forms.append(word[:-1])       # builds -> build
    if word.endswith('ly') and len(word) > 4:
        forms.append(word[:-2])       # actively -> active
    if word.endswith('tion') and len(word) > 5:
        forms.append(word[:-4] + 'te')  # separation -> separate
        forms.append(word[:-3] + 'e')   # creation -> create-ish
    if word.endswith('ment') and len(word) > 5:
        forms.append(word[:-4])       # movement -> move
    if word.endswith('ness') and len(word) > 5:
        forms.append(word[:-4])       # darkness -> dark
    if word.endswith('ity') and len(word) > 5:
        forms.append(word[:-3])       # clarity -> clar (not great)
        forms.append(word[:-3] + 'e') # creativity -> creative
    if word.endswith('ies') and len(word) > 4:
        forms.append(word[:-3] + 'y') # similarities -> similarity
    if word.endswith('er') and len(word) > 4:
        forms.append(word[:-2])       # builder -> build
        forms.append(word[:-1])       # closer -> close
    return list(dict.fromkeys(forms))  # unique, preserve order


def fetch_wikipedia_extract(topic):
    """Get Wikipedia extract for a topic. Returns (extract, related_links)."""
    try:
        # Search for the topic first
        resp = requests.get(
            'https://en.wikipedia.org/api/rest_v1/page/summary/' + topic.replace(' ', '_'),
            headers={'User-Agent': 'CortexBrain/1.0'},
            timeout=8
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get('type') != 'disambiguation':
                extract = data.get('extract', '')
                return extract
    except Exception as e:
        print(f'  [WIKI] Error: {e}')
    return None


def fetch_wikipedia_related(topic):
    """Get related links from a Wikipedia page for deeper exploration."""
    try:
        resp = requests.get(
            f'https://en.wikipedia.org/api/rest_v1/page/related/{topic.replace(" ", "_")}',
            headers={'User-Agent': 'CortexBrain/1.0'},
            timeout=8
        )
        if resp.status_code == 200:
            data = resp.json()
            pages = data.get('pages', [])
            return [p.get('title', '').lower() for p in pages[:10] if p.get('title')]
    except:
        pass
    return []


def extract_content_words(text):
    """Pull meaningful words from text, filtering junk."""
    tokens = brain.tokenize(text)
    return [w for w in tokens
            if w not in SKIP
            and len(w) > 2
            and not w.isdigit()
            and not w.startswith("'")
            and w.isalpha()]


def auto_tag_role(word, definition):
    """Auto-detect grammatical role from definition text."""
    lower_def = definition.lower()
    # Simple heuristics
    if any(lower_def.startswith(p) for p in ['to ', 'act of ', 'process of ']):
        return 'verb'
    if any(lower_def.startswith(p) for p in ['having ', 'being ', 'not ', 'relating to', 'of or ']):
        return 'adj'
    if any(p in lower_def for p in ['person who', 'group of', 'place ', 'device ', 'system ', 'collection of', 'state of']):
        return 'noun'
    return 'noun'  # default


def auto_tag_emotion(word, definition):
    """Auto-detect emotional associations from definition text."""
    tags = {}
    text = (word + ' ' + definition).lower()
    for script, triggers in SOUND_TRIGGERS.items():
        hits = sum(1 for t in triggers if t in text)
        if hits > 0:
            tags[script] = hits
    return tags


def learn_from_extract(word, extract, depth=0):
    """Learn a word from its Wikipedia extract. Wire connections deeply."""
    if not extract or len(extract) < 20:
        return False

    # Get short definition
    definition = brain._trim_definition(extract)
    if not definition or len(definition) < 4:
        return False

    nodes = brain.data['nodes']

    # Store the definition
    if word not in nodes:
        nodes[word] = {
            'means': None, 'next': {}, 'prev': {},
            'freq': 1, 'learned': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    if not nodes[word].get('means'):
        nodes[word]['means'] = definition
        nodes[word]['source'] = 'internet'

    # Learn the full extract as a sequence (wires LOTS of connections)
    sentences = re.split(r'[.!?]+', extract)
    for sent in sentences[:5]:  # First 5 sentences max
        sent = sent.strip()
        if len(sent) > 10:
            brain.learn_sequence(sent)

    # Also wire "X means Y" explicitly
    brain.learn_sequence(f"{word} means {definition}")

    # Auto-tag role
    role = auto_tag_role(word, definition)
    brain.set_role(word, role)

    # Auto-tag emotions
    emotions = auto_tag_emotion(word, definition)
    for script, strength in emotions.items():
        brain._inc_script(word, f'emotion_{script}', strength)

    # Extract new words from the definition to learn next
    content_words = extract_content_words(extract)
    new_words = [w for w in content_words
                 if w not in nodes or not nodes.get(w, {}).get('means')]

    return new_words


def crawl_undefined():
    """Look up all undefined words in the brain."""
    nodes = brain.data['nodes']
    undefined = [
        w for w, v in nodes.items()
        if not v.get('means')
        and w not in SKIP
        and len(w) > 2
        and not w.isdigit()
        and not w.startswith("'")
        and w.isalpha()
    ]
    random.shuffle(undefined)
    return undefined


def crawl_topic(topic):
    """Explore a topic from Wikipedia, learn words, follow connections."""
    print(f'\n--- Exploring: {topic} ---')
    extract = fetch_wikipedia_extract(topic)
    if not extract:
        print(f'  Nothing found for "{topic}"')
        return []

    new_words = learn_from_extract(topic.replace(' ', '_') if ' ' in topic else topic, extract)
    if new_words:
        print(f'  Learned "{topic}" + found {len(new_words)} new words to explore')
    return new_words or []


def main():
    parser = argparse.ArgumentParser(description='Cortex continuous learner')
    parser.add_argument('--topic', help='Specific topic to explore')
    parser.add_argument('--deep', action='store_true', help='Follow links between definitions')
    parser.add_argument('--rounds', type=int, default=5, help='Number of learning rounds')
    parser.add_argument('--max-per-round', type=int, default=30, help='Max words per round')
    args = parser.parse_args()

    nodes = brain.data['nodes']
    defined_start = sum(1 for v in nodes.values() if v.get('means'))
    print(f'\n=== CORTEX CONTINUOUS LEARNER ===')
    print(f'Starting: {len(nodes)} nodes, {defined_start} defined')
    print(f'Mode: {"Deep exploration" if args.deep else "Standard"}, {args.rounds} rounds')
    print()

    total_learned = 0
    total_connections_start = sum(len(v.get('next', {})) for v in nodes.values())
    explore_queue = []

    # If specific topic, start there
    if args.topic:
        new = crawl_topic(args.topic)
        explore_queue.extend(new)

    for round_num in range(args.rounds):
        print(f'\n=== ROUND {round_num + 1}/{args.rounds} ===')

        # Get undefined words to look up
        undefined = crawl_undefined()
        if not undefined and not explore_queue:
            # Nothing undefined — explore a new topic
            topic = random.choice(SEED_TOPICS)
            print(f'All words defined! Exploring new topic: {topic}')
            new = crawl_topic(topic)
            explore_queue.extend(new)
            undefined = crawl_undefined()

        # Mix undefined words with explore queue
        words_to_learn = undefined[:args.max_per_round]
        if args.deep and explore_queue:
            # Add some exploration words
            extra = explore_queue[:10]
            explore_queue = explore_queue[10:]
            words_to_learn = list(set(words_to_learn + extra))[:args.max_per_round]

        if not words_to_learn:
            print('Nothing to learn this round. Exploring...')
            topic = random.choice(SEED_TOPICS)
            crawl_topic(topic)
            continue

        print(f'Learning {len(words_to_learn)} words...')
        round_learned = 0

        for i, word in enumerate(words_to_learn):
            # Rate limit
            if i > 0 and i % 5 == 0:
                time.sleep(1)

            # Skip if already defined
            if word in nodes and nodes[word].get('means'):
                continue

            # Try the word itself, then base forms
            found = False
            forms = get_base_forms(word)
            for form in forms:
                extract = fetch_wikipedia_extract(form)
                if extract:
                    new_words = learn_from_extract(word, extract)
                    if new_words and args.deep:
                        explore_queue.extend(new_words[:5])
                    definition = brain._trim_definition(extract)
                    round_learned += 1
                    total_learned += 1
                    safe_print(f'  [{i+1}/{len(words_to_learn)}] {word} = {definition[:60]}')
                    found = True
                    break

            if not found:
                # Try DuckDuckGo with base forms
                for form in forms:
                    definition = brain.lookup_word(form)
                    if definition:
                        nodes.setdefault(word, {
                            'means': None, 'next': {}, 'prev': {},
                            'freq': 1, 'learned': time.strftime('%Y-%m-%d %H:%M:%S')
                        })
                        nodes[word]['means'] = definition
                        nodes[word]['source'] = 'internet'
                        brain.learn_sequence(f"{word} means {definition}")
                        role = auto_tag_role(word, definition)
                        brain.set_role(word, role)
                        round_learned += 1
                        total_learned += 1
                        safe_print(f'  [{i+1}/{len(words_to_learn)}] {word} = {definition[:60]}')
                        found = True
                        break

                if not found:
                    safe_print(f'  [{i+1}/{len(words_to_learn)}] {word} = ???')

            # Save every 20 words
            if (i + 1) % 20 == 0:
                brain.save()
                print(f'  [saved]')

        brain.save()
        print(f'Round {round_num + 1}: learned {round_learned} words')

        # If deep mode, also explore related topics
        if args.deep and total_learned > 0:
            defined_words = [w for w, v in nodes.items() if v.get('means')]
            if defined_words:
                random_known = random.choice(defined_words)
                related = fetch_wikipedia_related(random_known)
                if related:
                    explore_queue.extend(related[:5])
                    print(f'  Deep explore: found {len(related)} related topics from "{random_known}"')

    # Final stats
    brain.save()
    defined_end = sum(1 for v in nodes.values() if v.get('means'))
    connections_end = sum(len(v.get('next', {})) for v in nodes.values())
    trigrams = len(brain.data.get('trigrams', {}))
    scripted = sum(1 for v in nodes.values() if v.get('scripts'))

    print(f'\n=== LEARNING COMPLETE ===')
    print(f'  Words learned:    {total_learned}')
    print(f'  Nodes:            {len(nodes)} (was {len(nodes) - total_learned}+)')
    print(f'  Defined:          {defined_end} (was {defined_start})')
    print(f'  Connections:      {connections_end} (was {total_connections_start})')
    print(f'  Trigrams:         {trigrams}')
    print(f'  With scripts:     {scripted}')

    # Save to IPFS
    print(f'\nSaving to IPFS...')
    cid = brain.save_to_ipfs()
    if cid:
        print(f'  IPFS CID: {cid}')
    print()


if __name__ == '__main__':
    main()
