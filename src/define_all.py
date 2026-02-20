"""
DEFINE ALL — Look up every undefined word in the brain from the internet.
Gives the prediction engine real vocabulary to work with.
Run: python define_all.py
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brain import CortexBrain, STOP_WORDS

STUDIO_DIR = os.path.dirname(os.path.abspath(__file__))
PINATA_JWT = os.environ.get('PINATA_JWT', 'your-pinata-jwt-here')

brain = CortexBrain(STUDIO_DIR, pinata_jwt=PINATA_JWT)

# Words too basic to bother looking up
SKIP = STOP_WORDS | {
    'the','a','an','is','am','are','was','were','be','been',
    'has','have','had','do','does','did','will','would','could',
    'should','can','may','might','shall','must',
    'not','no','yes','yeah','yep','nah','nope','ok','okay',
    'im','ive','ill','id','youre','youve','youll','youd',
    'hes','shes','theyre','theyve','were','weve',
    'dont','doesnt','didnt','cant','wont','isnt','arent',
    'wasnt','werent','havent','hasnt','couldnt','wouldnt','shouldnt',
    'plus','per','vs','etc','v3','v31','hp','mp4',
    'dont','cant','wont','isnt',
}

def main():
    nodes = brain.data['nodes']
    undefined = [
        w for w, v in nodes.items()
        if not v.get('means')
        and w not in SKIP
        and len(w) > 2
        and not w.isdigit()
        and not w.startswith("'")
    ]

    print(f'\n=== DEFINE ALL WORDS ===')
    print(f'Total nodes: {len(nodes)}')
    print(f'Already defined: {sum(1 for v in nodes.values() if v.get("means"))}')
    print(f'Undefined to lookup: {len(undefined)}')
    print()

    found = 0
    failed = 0
    skipped = 0

    for i, word in enumerate(undefined):
        # Rate limit: don't hammer the APIs
        if i > 0 and i % 5 == 0:
            time.sleep(1)

        definition = brain.lookup_word(word)
        if definition:
            nodes[word]['means'] = definition
            nodes[word]['source'] = 'internet'
            brain.learn_sequence(f"{word} means {definition}")
            found += 1
            print(f'  [{i+1}/{len(undefined)}] {word} = {definition}')
        else:
            failed += 1
            print(f'  [{i+1}/{len(undefined)}] {word} = ???')

        # Save every 20 lookups
        if (found + failed) % 20 == 0:
            brain.save()

    brain.save()

    total_defined = sum(1 for v in nodes.values() if v.get('means'))
    print(f'\n=== DONE ===')
    print(f'  Found: {found}')
    print(f'  Not found: {failed}')
    print(f'  Total defined: {total_defined} / {len(nodes)}')

    # Save to IPFS
    print(f'\nSaving to IPFS...')
    cid = brain.save_to_ipfs()
    if cid:
        print(f'  IPFS CID: {cid}')
    print()

if __name__ == '__main__':
    main()
