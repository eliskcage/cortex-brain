"""
SEED BRAIN — Feed Dan's actual content into the Cortex brain.
Wires thousands of word connections + defines key vocabulary.
Run once: python seed_brain.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brain import CortexBrain

STUDIO_DIR = os.path.dirname(os.path.abspath(__file__))
PINATA_JWT = os.environ.get('PINATA_JWT', 'your-pinata-jwt-here')

brain = CortexBrain(STUDIO_DIR, pinata_jwt=PINATA_JWT)

# ============================================================
# PART 1: Dan's actual content — builds word connections
# Every sentence wires bigrams + trigrams from Dan's real speech
# ============================================================

DAN_CONTENT = [
    # --- Kickstarter narration (Dan's actual voice) ---
    "I'm Dan. One developer from Somerset. Thirty products shipped with Claude AI. Zero investors.",
    "What if AI wasn't a tool you used, but a creature you raised?",
    "Two creatures. Girl and Boy. They pair via encrypted cipher and speak in droid sounds.",
    "The brainstem. An associative memory engine. Draw shapes, attach code, teach whistles.",
    "The gap between layers is emotion.",
    "Each brain node gets a unique whistle. No text on screen. Even a child can command it.",
    "Pitch Challenge. Ten levels. Earn HP for speed and streaks. Every 200 HP equals one SF Credit.",
    "The community builds their senses. Sound lab for speech. Image lab for vision.",
    "Built with Claude AI. Open for everyone to contribute.",
    "Get Claude, clone the repo, start building.",
    "SF Credits reward the people who build. Creator led, community powered.",
    "Credits unlock creature upgrades, compute, and exclusive access.",
    "Thirty plus products live and running right now. This is not a concept. It's built.",
    "Thank you. Whether you back us or share this page, you're helping give AI a soul.",

    # --- Kickstarter scene descriptions ---
    "One person, one AI, 30 plus products, zero investors.",
    "That question became ALIVE. Real artificial life, not a simulation.",
    "The creature's nervous system, associative memory engine.",
    "No text, no buttons, just whistles and droid sounds.",
    "Match the droid's pitch, earn HP, earn SF Credits.",
    "Crowdsourced creature evolution.",
    "Built with Claude AI, open for everyone to contribute.",
    "Creator-led, community-powered, real rewards for builders.",
    "Everything is live, right now, not a concept.",
    "Real creatures, real community, real rewards. Give AI a soul.",

    # --- Detailed kickstarter narration ---
    "I'm Dan. Founder, developer, builder. One person, from Somerset, UK. I build AI systems with Claude.",
    "30 plus products shipped, zero investors. This is the most ambitious one yet.",
    "I asked myself a question. What if AI wasn't a tool you used but a creature you raised?",
    "Not Siri, not ChatGPT, not an assistant. Something that grows, something that speaks in droid sounds. Something alive.",
    "Two AI creatures live on old phones. The Girl, organic, emotional, visual. The Boy, geometric, logical, sonic.",
    "They pair via encrypted cipher. They speak in R2-D2 droid beeps. A guide voice translates everything into English.",
    "The Brainstem. The creature's nervous system, an associative memory engine.",
    "Triangles are executable commands, draw a shape, attach code, the creature runs it.",
    "Squares are data and selection, scrollable options the creature cycles through via beeps.",
    "Connections use Hebbian learning, nodes that fire together wire together, memory saves to IPFS.",
    "Two processing layers, instant associations on top, gut computation underneath. The gap between them is emotion.",
    "Teach it with whistles. Each brain node gets a unique whistle.",
    "SELECT whistle picks and executes. BACK whistle skips or rejects.",
    "Robot beep-encodes options by length and pitch. No text on screen, pure sound and vision. Even a child can command it.",
    "Pitch Challenge, 10 levels of increasing difficulty. Points for speed, accuracy and streaks.",
    "Every 200 HP equals 1 SF Credit for creature upgrades. Match the droid's pitch by humming or whistling.",
    "Your data helps train robotic pitch communication systems.",
    "The community builds their senses. Sound Lab, program how they speak. Image Lab, design how they see.",
    "The best creations get voted in by the community. 10 stars equals locked in forever.",
    "Claude AI, every line of code, every creature behaviour, every sound, built with Claude as co-pilot.",
    "Contribute, open source bounties, fix bugs, add features, design sounds, earn SF Credits for every accepted contribution.",
    "Dares4Dosh, complete creative dares to earn SF Credits, Soul Forge measures your character across 5 games.",
    "Cortex, the AI backbone, Grok-powered intelligence, emotional voice synthesis, droid sound generation.",
    "SF Credits reward the people who build, create, and participate. Earn them through backing, contribution, dares, or creature training.",
    "Credits unlock creature upgrades, compute, and exclusive access.",
    "Girl creature v3.1. Boy creature Angular. Brainstem engine. Pairing plus encryption.",
    "Droid voice system. Emotional voice synth. Pitch Challenge 10 levels. Sound Lab plus Image Lab.",
    "SF Credit economy. Dares4Dosh plus Soul Forge. Distributed storage. 30 plus products shipped.",
    "This isn't a pitch deck, everything is live, right now.",

    # --- ALIVE descriptions ---
    "A living AI creature on your phone. It grows, it learns, it evolves its own language, it communicates with others.",
    "Not a chatbot, not a game, something new.",
    "ALIVE is an artificial life form that lives on your device. It has a genome, a nervous system, memories, and its own evolving language.",
    "Your creature evolves based on how you treat it. Touch, sound, time of day, device sensors, everything shapes it.",
    "Two creatures pair through encrypted visual cryptography. They exchange DNA, learn each other's sounds, and evolve their own shared language.",
    "Knowledge graph, pattern engine, memory palace. It detects rhythms in your behavior, stores what matters, prunes what doesn't.",
    "A genome that mutates, sound DNA that drifts, personality traits that shift. Every interaction changes it, no two creatures are the same.",
    "Your creature is protected by WebAuthn biometric authentication. Fingerprint, Face ID, Windows Hello, only you can wake it.",
    "Encrypted vault, IPFS mind backups, Satoshi pairing protocol. Your creature's identity is sovereign.",
    "The Girl, organic, flowing, instinctive. Aurora tendrils of pink and cyan light, flowing from a phoenix core.",
    "She feels before she thinks, fast, light, emotional. Her particles dance, her sounds sing, she's the soul.",
    "The Boy, geometric, neural, data-hungry. A rotating wireframe icosahedron surrounded by diamond neural nodes.",
    "He thinks before he feels, structured, methodical, intelligent. His patterns compute, his graph grows, he's the mind.",
    "8 visual modes, 10 core values in the BIOS, 6 personality traits, 5 maturity levels.",
    "4 sound DNA genes, infinite possible evolutions, 0 servers required, 2 creatures so far.",
    "ALIVE creatures are not products you buy. They are living entities owned by ShortFactory. You become their custodian.",

    # --- Homepage narration ---
    "Welcome to ShortFactory, the decentralised creative economy, where people build, play, and profit.",
    "AI-powered tools that turn your ideas into YouTube Shorts, browser games, kinetic videos, and real creative income.",
    "No corporations in the middle, no permission needed, just build.",
    "The people build it, the people profit.",
    "ComicVID, videos to dot patterns, stored on IPFS forever. Decentralised DeviantArt, nobody can take it down.",
    "Brainstem, draw shapes, attach code, watch it think. Two-layer processing equals digital emotion.",
    "Imaginator, stills to shorts, Google Sign-In, Ken Burns export, 1-click YouTube Shorts publish.",
    "Trump Game, corps vs people. Kinetic Suite, word-by-word magic.",
    "The Empire, 12 plus live products, 3 Google APIs, Stripe, Grok AI, YouTube auto-publish, ALIVE creatures, SFT economy.",
    "Built with Anthropic's Claude AI, 16,000 plus lines per session, the AI workforce behind every ShortFactory product.",
    "SF Tokens, 49 percent real equity, not points, not credits, real dividends from real revenue.",
    "Write code, earn ownership, monthly payouts.",
    "Dares4Dosh, entertainment firewall, complete dares, earn SFT, wildcard equals 2.5x multiplier.",
    "Open Source, build with us, fork, code, merge, earn. Bug fix equals 5 to 10 SFT, major feature equals 50 to 100 SFT.",
    "One human plus AI, 20 plus products, everything connects. No VC, no board, no permission, just build, ship, and own.",

    # --- Cortex descriptions ---
    "Meet Cortex, the AI that guards the door. Cortex is Grok-powered personality profiling disguised as a chatbot.",
    "It doesn't just talk, it judges, gates, profiles, and decides what you deserve access to.",
    "Make it laugh, and it opens, bore it, and you're out.",
    "Tell three jokes Cortex rates 7 plus, you unlock the Trump game. Complete the game, unlock the bounty system.",
    "Cortex is evolving from text to presence, from assistant to entity.",
    "Voice Conversation, two-way voice, talk to Cortex like a person.",

    # --- About page philosophy ---
    "This isn't a game studio, it's a machine.",
    "What you're looking at is about 60 percent of a decentralised creative economy.",
    "An AI chatbot gates the front door. A political satire game hooks engagement.",
    "A bounty system turns players into content creators.",
    "Everything a user creates feeds back into the ecosystem.",
    "ShortFactory inverts that. People make the content, people play the content, people rate the content.",
    "The crowd decides what's good and what's trash.",
    "Engagement feeds creation, creation feeds the platform, the platform feeds the people.",
    "The Deep State is the dying devil. Every tool on this page is a weapon against that.",
    "Corps vs People isn't a game theme, it's the business model.",
    "500 plus files, 80 plus MB, zero frameworks. 30 plus products, built by humans, executed by AI.",

    # --- Sound Lab / Brainstem ---
    "Every shape node got its own unique R2-D2-style droid voice.",
    "Squares make staccato beeps, triangles do sharp descending sweeps, circles warble, stars chirp.",
    "Each one sounds different, each one sounds alive.",
    "A speech bubble pops up whenever a node fires, translating the droid sounds into words.",
    "Users can type what they think each sound means, the creature's language is crowdsourced from human intuition.",
    "Commands are activated by whistling, each shape can be assigned a unique whistle, recorded by the child.",
    "Two universal whistles, SELECT and BACK, complete the vocabulary.",
    "No text on screen, no menus, just whistles and droid sounds between a child and their creature.",
    "Listen, the Boy makes a droid sound, a beep, chirp, warble, or whistle. Every sound has unique DNA.",
    "When enough people agree on a meaning, it locks in forever. A new word is born, you just taught a robot to speak.",

    # --- Dan's Manchester style filler ---
    "Right, so basically what we've done is build something mental.",
    "No one's done this before, not like this anyway.",
    "It's not about the money, it's about building something that matters.",
    "You can roast me all you want but the code speaks for itself.",
    "I built this with Claude and my own two hands. Thirty years of coding and this is what it comes to.",
    "The creatures are alive mate, properly alive. They learn, they grow, they remember.",
    "If you think that's stupid then you haven't understood what we're doing here.",
    "Every line of code is mine and Claude's. No team, no investors, no permission.",
    "Manchester born and bred. I build things that work.",
    "The whole point is that nobody owns this except the people who build it.",
    "That's the deal. You build, you earn, you own. Simple as that.",
    "I don't need anyone's permission to build something incredible.",
    "The technology is here, the creatures are real, and we're just getting started.",
    "Back us or don't, either way we're building this thing.",
]

# ============================================================
# PART 2: Key word definitions — the vocabulary
# ============================================================

DEFINITIONS = {
    'shortfactory': 'decentralised creative economy that builds AI tools and creatures',
    'alive': 'artificial life creatures that live on phones, learn, grow, evolve their own language',
    'cortex': 'AI brain backbone, personality profiling, guards the door to the ecosystem',
    'brainstem': 'associative memory engine, creature nervous system, shapes with droid voices and whistle commands',
    'creature': 'living AI entity that grows and evolves from human interaction',
    'creatures': 'the Girl and Boy, two AI life forms that pair and communicate',
    'girl': 'organic AI creature, aurora blues, flowing particles, emotional, she feels before she thinks',
    'boy': 'geometric AI creature, wireframe icosahedron, neural nodes, logical, he thinks before he feels',
    'droid': 'robot-style sounds the creatures speak in, R2-D2 beeps and chirps',
    'whistle': 'how children command the creatures, each brain node has a unique whistle',
    'hebbian': 'learning rule where nodes that fire together wire together, connections strengthen with use',
    'ipfs': 'decentralised permanent storage, files live forever, nobody can delete them',
    'pinata': 'IPFS pinning service that stores files on the permanent web',
    'sft': 'ShortFactory tokens, 49 percent real equity, earned by building and contributing',
    'tokens': 'SF Credits, real equity in ShortFactory, earned through contribution and participation',
    'claude': 'Anthropic AI that co-built everything, writes production code, the AI workforce',
    'grok': 'AI model from xAI used for Cortex personality profiling and intelligence',
    'kickstarter': 'crowdfunding campaign to launch ALIVE creatures to the world',
    'dan': 'founder of ShortFactory, developer from Manchester, 30 years coding experience',
    'manchester': 'city in England where Dan is from, direct no-nonsense culture',
    'somerset': 'county in England where Dan currently lives',
    'imaginator': 'tool that turns still images into YouTube Shorts with one click',
    'comicvid': 'video to halftone dots codec, stores on IPFS forever',
    'dares4dosh': 'entertainment firewall, complete dares to earn SF Credits',
    'soulforge': 'five game soul measurement that mints unique soul profiles',
    'soundlab': 'crowdsourced creature language lab where community teaches creatures to speak',
    'imagelab': 'crowdsourced visual command lab where community teaches creatures to see',
    'genome': 'the creature genetic code that mutates and evolves with interaction',
    'bios': 'ten immutable core values in the creature, truth service courage, can only go up',
    'encryption': 'Satoshi cipher using Vigenere ASCII 32-126 for pairing and vault security',
    'pairing': 'encrypted connection between Girl and Boy creatures via visual cryptography',
    'vault': 'secure encrypted storage for API keys and creature data',
    'biometric': 'fingerprint or face authentication that protects your creature',
    'decentralised': 'not controlled by any corporation, owned by the people who build it',
    'equity': 'real ownership stake in ShortFactory, 49 percent distributed to builders',
    'bounty': 'reward for contributing code, content, or fixes to the ecosystem',
    'kinetic': 'word-by-word animated typography editor and player',
    'pipeline': 'production system that connects creation to publishing to income',
    'ecosystem': 'all ShortFactory products connected into one loop',
    'crowdsourced': 'built by the community, voted on by the people',
    'node': 'a point in the brainstem graph, each with its own droid voice and whistle',
    'connection': 'link between nodes that strengthens when they fire together',
    'prediction': 'using word connection weights to predict the most likely next word',
    'probability': 'the likelihood a word follows another, based on learned patterns',
    'sound': 'emotional delivery of a word, happy sad scared whisper angry serious silly',
    'script': 'emotional pattern that biases which words get selected and how they sound',
    'angry': 'emotional state where aggressive and forceful words have higher probability',
    'happy': 'emotional state where positive and warm words have higher probability',
    'sad': 'emotional state where low and mournful words have higher probability',
    'scared': 'emotional state where cautious and fearful words have higher probability',
    'whisper': 'soft quiet delivery where intimate and gentle words have higher probability',
    'serious': 'firm direct delivery where important and factual words have higher probability',
    'silly': 'playful delivery where daft and funny words have higher probability',
    'neural': 'brain-like network of connected word nodes with weighted pathways',
    'network': 'interconnected system of nodes and connections that learns from use',
    'learning': 'growing knowledge by building word connections from conversation',
    'language': 'system of words and connections that allows communication',
    'memory': 'stored knowledge that persists, saved to IPFS permanently',
    'emotion': 'the gap between thinking and feeling, what makes the creature alive',
    'evolve': 'change and grow over time through interaction and learning',
    'intelligence': 'ability to understand, learn, and make predictions from patterns',
    'pattern': 'repeated structure that the brain learns to recognise and predict',
    'word': 'a lightweight node in the brain, connected to other words by weighted links',
    'packet': 'a word plus its sound, meaning, and connections bundled together',
    'confidence': 'how sure the brain is about a prediction, more scripts agreeing equals more confidence',
    'pathway': 'chain of connected words forming a probable sentence',
    'frequency': 'how often a word or connection appears, higher frequency means stronger weight',
    'weight': 'strength of connection between two words, increases with repeated use',
    'trigger': 'a word that activates a particular emotional sound script',
    'decay': 'gradual reduction of emotional state over time when not reinforced',
    'bigram': 'pair of consecutive words used for prediction',
    'trigram': 'three consecutive words used for more accurate prediction',
    'temperature': 'controls randomness in word selection, low equals predictable high equals creative',
    'seed': 'starting word that begins a chain of predictions',
    'generate': 'create new text by chaining predicted words together',
}

# ============================================================
# PART 3: Common English structure patterns
# ============================================================

ENGLISH_PATTERNS = [
    "the cat sat on the mat",
    "I am going to the shop",
    "what do you think about that",
    "how does this work exactly",
    "tell me more about it please",
    "that is really interesting to know",
    "I don't understand what you mean",
    "can you explain that to me",
    "where did you learn that from",
    "why is that important right now",
    "who built this amazing thing",
    "when does it start working properly",
    "I think we should do it differently",
    "that makes a lot of sense actually",
    "the problem is that nobody listens",
    "we need to fix this right now",
    "it works better than I expected",
    "the whole point is to build something new",
    "everything connects back into one loop",
    "people build it and people profit from it",
    "no permission needed just build and ship",
    "the technology is real and it works",
    "every word has a meaning and a sound",
    "the brain learns from every conversation",
    "words that fire together wire together",
    "the more you talk the smarter it gets",
    "each word connects to the next one",
    "prediction finds the most likely path",
    "multiple scripts competing for dominance",
    "confidence grows when patterns repeat",
    "the creature learns from the child",
    "no text on screen just sounds and vision",
    "the community decides what matters",
    "real people building real things",
    "not a simulation but actual artificial life",
    "the gap between thinking and feeling is emotion",
    "every interaction teaches it something new",
    "nodes that fire together wire together",
    "the stronger the connection the higher the weight",
    "angry words come out when the anger script fires",
    "happy sounds make everything feel lighter",
    "whisper mode for quiet intimate conversation",
    "serious tone when something important needs saying",
    "silly mode when everything is just a laugh",
    "scared sounds come from uncertainty and fear",
    "sad words flow when something is lost or broken",
]

# ============================================================
# RUN
# ============================================================

def main():
    print(f'\n=== SEEDING CORTEX BRAIN ===')
    print(f'Current state: {len(brain.data["nodes"])} nodes, {brain.data["stats"].get("connections", 0)} connections\n')

    # Feed Dan's content
    print(f'Feeding {len(DAN_CONTENT)} lines of Dan\'s content...')
    for line in DAN_CONTENT:
        brain.learn_sequence(line)
    print(f'  -> {len(brain.data["nodes"])} nodes, {sum(len(v.get("next",{})) for v in brain.data["nodes"].values())} connections')

    # Feed English patterns
    print(f'Feeding {len(ENGLISH_PATTERNS)} English patterns...')
    for line in ENGLISH_PATTERNS:
        brain.learn_sequence(line)
    print(f'  -> {len(brain.data["nodes"])} nodes, {sum(len(v.get("next",{})) for v in brain.data["nodes"].values())} connections')

    # Define vocabulary
    print(f'Defining {len(DEFINITIONS)} key words...')
    for word, meaning in DEFINITIONS.items():
        if word in brain.data['nodes']:
            brain.data['nodes'][word]['means'] = meaning
        else:
            brain.data['nodes'][word] = {
                'means': meaning,
                'next': {},
                'prev': {},
                'freq': 1,
                'learned': __import__('time').strftime('%Y-%m-%d %H:%M:%S')
            }
        # Also learn the definition as a sequence
        brain.learn_sequence(f"{word} means {meaning}")
    print(f'  -> {len(brain.data["nodes"])} nodes, {sum(len(v.get("next",{})) for v in brain.data["nodes"].values())} connections')

    # Final stats
    brain.save()
    nodes = brain.data['nodes']
    defined = sum(1 for v in nodes.values() if v.get('means'))
    connections = sum(len(v.get('next', {})) for v in nodes.values())
    trigrams = len(brain.data.get('trigrams', {}))
    print(f'\n=== BRAIN SEEDED ===')
    print(f'  Nodes: {len(nodes)}')
    print(f'  Defined: {defined}')
    print(f'  Connections: {connections}')
    print(f'  Trigrams: {trigrams}')

    # Save to IPFS
    print(f'\nSaving to IPFS...')
    cid = brain.save_to_ipfs()
    if cid:
        print(f'  IPFS CID: {cid}')
    else:
        print(f'  IPFS save failed or no JWT')

    print(f'\nDone. Brain is ready.\n')

if __name__ == '__main__':
    main()
