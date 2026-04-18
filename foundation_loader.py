"""
FOUNDATION KNOWLEDGE LOADER — Alphabet, Numbers, Symbols, Objects
Feeds all three brains (left, right, cortex) with building blocks.

Not just symbols — connections to objects the brain can USE in patterns.
Every letter knows its neighbours, its sounds, its common objects.
Every number knows its value, its neighbours, its patterns.

Usage: python foundation_loader.py
"""
import json
import time
import requests

# Go through Cloudflare — port 8643 is firewalled from outside
SERVER = 'https://www.shortfactory.shop/alive/studio'
BULK_KEY = 'cortex_bulk_9lQ3'
CHUNK_SIZE = 50  # smaller chunks to stay under Cloudflare's 100s timeout

# ═══════════════════════════════════════════════════════════
# ALPHABET — each letter with definition, objects, patterns
# ═══════════════════════════════════════════════════════════
ALPHABET = {
    'a': {'means': 'first letter of the alphabet, the beginning, a single unit',
           'objects': ['apple', 'animal', 'air', 'angel', 'ant', 'arrow', 'arm', 'axe'],
           'patterns': ['a is the first letter', 'a comes before b', 'a is for apple', 'a is a vowel']},
    'b': {'means': 'second letter of the alphabet, comes after a',
           'objects': ['ball', 'bird', 'book', 'box', 'brain', 'bread', 'bridge', 'butterfly'],
           'patterns': ['b comes after a', 'b comes before c', 'b is for ball', 'b is a consonant']},
    'c': {'means': 'third letter of the alphabet, can sound like k or s',
           'objects': ['cat', 'car', 'clock', 'cloud', 'coin', 'cup', 'circle', 'castle'],
           'patterns': ['c comes after b', 'c comes before d', 'c is for cat', 'c can sound like k or s']},
    'd': {'means': 'fourth letter of the alphabet',
           'objects': ['dog', 'door', 'drum', 'diamond', 'dragon', 'dark', 'dust', 'dream'],
           'patterns': ['d comes after c', 'd comes before e', 'd is for dog', 'd is a consonant']},
    'e': {'means': 'fifth letter, the most common letter in english',
           'objects': ['egg', 'eye', 'ear', 'earth', 'eagle', 'engine', 'energy', 'echo'],
           'patterns': ['e comes after d', 'e comes before f', 'e is for egg', 'e is a vowel', 'e is the most common letter']},
    'f': {'means': 'sixth letter of the alphabet',
           'objects': ['fire', 'fish', 'flower', 'food', 'friend', 'frog', 'forest', 'finger'],
           'patterns': ['f comes after e', 'f comes before g', 'f is for fire', 'f is a consonant']},
    'g': {'means': 'seventh letter, can sound hard or soft',
           'objects': ['gate', 'gold', 'grass', 'ghost', 'giant', 'glass', 'guitar', 'garden'],
           'patterns': ['g comes after f', 'g comes before h', 'g is for gold', 'g can be hard or soft']},
    'h': {'means': 'eighth letter of the alphabet',
           'objects': ['house', 'hand', 'heart', 'horse', 'hammer', 'hill', 'honey', 'hat'],
           'patterns': ['h comes after g', 'h comes before i', 'h is for house', 'h is often silent']},
    'i': {'means': 'ninth letter, also means myself, the self',
           'objects': ['ice', 'iron', 'island', 'ink', 'insect', 'idea', 'image', 'ivory'],
           'patterns': ['i comes after h', 'i comes before j', 'i is for ice', 'i is a vowel', 'i means myself']},
    'j': {'means': 'tenth letter of the alphabet',
           'objects': ['jar', 'jewel', 'jungle', 'juice', 'joy', 'jacket', 'jigsaw', 'jump'],
           'patterns': ['j comes after i', 'j comes before k', 'j is for jar', 'j is a consonant']},
    'k': {'means': 'eleventh letter of the alphabet',
           'objects': ['key', 'king', 'kite', 'knife', 'knight', 'kitchen', 'kitten', 'knot'],
           'patterns': ['k comes after j', 'k comes before l', 'k is for key', 'k is sometimes silent before n']},
    'l': {'means': 'twelfth letter of the alphabet',
           'objects': ['light', 'lion', 'leaf', 'lake', 'lamp', 'ladder', 'love', 'line'],
           'patterns': ['l comes after k', 'l comes before m', 'l is for light', 'l is a consonant']},
    'm': {'means': 'thirteenth letter, the middle of the alphabet',
           'objects': ['moon', 'mountain', 'mouse', 'mirror', 'music', 'money', 'map', 'mind'],
           'patterns': ['m comes after l', 'm comes before n', 'm is for moon', 'm is the middle letter']},
    'n': {'means': 'fourteenth letter of the alphabet',
           'objects': ['night', 'nose', 'nest', 'net', 'needle', 'number', 'name', 'nature'],
           'patterns': ['n comes after m', 'n comes before o', 'n is for night', 'n is a consonant']},
    'o': {'means': 'fifteenth letter, shaped like a circle, zero, nothing and everything',
           'objects': ['ocean', 'orange', 'owl', 'oil', 'orbit', 'oak', 'onion', 'oxygen'],
           'patterns': ['o comes after n', 'o comes before p', 'o is for ocean', 'o is a vowel', 'o looks like zero']},
    'p': {'means': 'sixteenth letter of the alphabet',
           'objects': ['paper', 'pencil', 'piano', 'planet', 'power', 'puzzle', 'paint', 'path'],
           'patterns': ['p comes after o', 'p comes before q', 'p is for paper', 'p is a consonant']},
    'q': {'means': 'seventeenth letter, almost always followed by u',
           'objects': ['queen', 'question', 'quiet', 'quilt', 'quarter', 'quest', 'quartz', 'quiz'],
           'patterns': ['q comes after p', 'q comes before r', 'q is for queen', 'q needs u']},
    'r': {'means': 'eighteenth letter of the alphabet',
           'objects': ['rain', 'river', 'rock', 'rose', 'road', 'ring', 'robot', 'root'],
           'patterns': ['r comes after q', 'r comes before s', 'r is for rain', 'r is a consonant']},
    's': {'means': 'nineteenth letter, makes things plural, the snake sound',
           'objects': ['sun', 'star', 'stone', 'snake', 'sword', 'seed', 'shell', 'shadow'],
           'patterns': ['s comes after r', 's comes before t', 's is for sun', 's makes words plural']},
    't': {'means': 'twentieth letter of the alphabet',
           'objects': ['tree', 'time', 'tower', 'thunder', 'tooth', 'train', 'truth', 'treasure'],
           'patterns': ['t comes after s', 't comes before u', 't is for tree', 't is a consonant']},
    'u': {'means': 'twenty first letter, also means you',
           'objects': ['umbrella', 'universe', 'unicorn', 'unity', 'unknown', 'under', 'up', 'use'],
           'patterns': ['u comes after t', 'u comes before v', 'u is for umbrella', 'u is a vowel']},
    'v': {'means': 'twenty second letter of the alphabet',
           'objects': ['voice', 'valley', 'vine', 'volcano', 'village', 'violin', 'victory', 'vision'],
           'patterns': ['v comes after u', 'v comes before w', 'v is for voice', 'v is a consonant']},
    'w': {'means': 'twenty third letter, shaped like two v letters joined',
           'objects': ['water', 'wind', 'wall', 'wave', 'wheel', 'wolf', 'window', 'world'],
           'patterns': ['w comes after v', 'w comes before x', 'w is for water', 'w looks like two v shapes']},
    'x': {'means': 'twenty fourth letter, means unknown, marks the spot',
           'objects': ['xray', 'xenon', 'xylophone'],
           'patterns': ['x comes after w', 'x comes before y', 'x marks the spot', 'x means unknown in maths']},
    'y': {'means': 'twenty fifth letter, sometimes a vowel sometimes a consonant',
           'objects': ['yellow', 'year', 'yarn', 'yawn', 'youth', 'yes'],
           'patterns': ['y comes after x', 'y comes before z', 'y is for yellow', 'y can be a vowel or consonant']},
    'z': {'means': 'twenty sixth letter, the last letter, the end',
           'objects': ['zero', 'zebra', 'zone', 'zigzag', 'zoo', 'zenith', 'zinc'],
           'patterns': ['z comes after y', 'z is the last letter', 'z is for zero', 'z is the end of the alphabet']},
}

# ═══════════════════════════════════════════════════════════
# NUMBERS — 0-100 with value, patterns, relationships
# ═══════════════════════════════════════════════════════════
NUMBERS = {}

# 0-20 with rich definitions
number_defs = {
    0: 'zero, nothing, empty, the void, the beginning before one',
    1: 'one, a single unit, the first, alone, unity, the individual',
    2: 'two, a pair, duality, left and right, good and evil, binary',
    3: 'three, a trinity, triangle, beginning middle end, past present future',
    4: 'four, a square, the four directions north south east west, stability',
    5: 'five, a hand has five fingers, halfway to ten, the pentagon',
    6: 'six, twice three, half a dozen, the hexagon, the star of david has six points',
    7: 'seven, considered lucky, seven days in a week, seven colours in a rainbow',
    8: 'eight, twice four, the octagon, infinity turned sideways, the spider has eight legs',
    9: 'nine, three times three, the last single digit, cats have nine lives',
    10: 'ten, two hands, the base of our number system, a decade, perfection',
    11: 'eleven, one more than ten, the first double digit that repeats',
    12: 'twelve, a dozen, twelve months, twelve hours on a clock face',
    13: 'thirteen, considered unlucky, a bakers dozen, the first teen number',
    14: 'fourteen, twice seven, a fortnight is fourteen days',
    15: 'fifteen, three times five, a quarter of sixty',
    16: 'sixteen, four times four, a power of two, sweet sixteen',
    17: 'seventeen, a prime number',
    18: 'eighteen, legal adult age, three times six',
    19: 'nineteen, the last teen number',
    20: 'twenty, a score, two tens, four times five',
}

# Objects associated with numbers
number_objects = {
    0: ['nothing', 'void', 'empty', 'hole', 'circle', 'zero', 'null'],
    1: ['point', 'dot', 'line', 'self', 'sun', 'god', 'unity', 'alone'],
    2: ['pair', 'eyes', 'hands', 'twins', 'binary', 'mirror', 'duality'],
    3: ['triangle', 'trinity', 'crowd', 'family', 'past present future'],
    4: ['square', 'seasons', 'directions', 'legs', 'walls', 'corners'],
    5: ['fingers', 'hand', 'star', 'pentagon', 'senses'],
    6: ['dice', 'hexagon', 'sides', 'cube', 'insects legs'],
    7: ['rainbow', 'week', 'luck', 'notes', 'continents', 'seas'],
    8: ['octopus', 'spider', 'infinity', 'octagon', 'byte'],
    9: ['planets', 'lives', 'square of three'],
    10: ['fingers', 'toes', 'decade', 'base', 'metric', 'commandments'],
}

for n in range(0, 101):
    word = {
        0:'zero',1:'one',2:'two',3:'three',4:'four',5:'five',6:'six',7:'seven',
        8:'eight',9:'nine',10:'ten',11:'eleven',12:'twelve',13:'thirteen',
        14:'fourteen',15:'fifteen',16:'sixteen',17:'seventeen',18:'eighteen',
        19:'nineteen',20:'twenty',30:'thirty',40:'forty',50:'fifty',
        60:'sixty',70:'seventy',80:'eighty',90:'ninety',100:'hundred',
    }.get(n, '')

    if not word:
        tens = n // 10
        ones = n % 10
        tens_word = {2:'twenty',3:'thirty',4:'forty',5:'fifty',6:'sixty',7:'seventy',8:'eighty',9:'ninety'}.get(tens,'')
        ones_word = {1:'one',2:'two',3:'three',4:'four',5:'five',6:'six',7:'seven',8:'eight',9:'nine'}.get(ones,'')
        word = tens_word  # just use tens word for compound numbers
        if not word:
            continue

    means = number_defs.get(n, '%s, the number %d' % (word, n))

    patterns = ['%d is a number' % n]
    if n > 0:
        patterns.append('%d comes after %d' % (n, n-1))
    if n < 100:
        patterns.append('%d comes before %d' % (n, n+1))
    if n > 0 and n % 2 == 0:
        patterns.append('%d is even' % n)
    elif n > 0:
        patterns.append('%d is odd' % n)

    # Prime check
    if n > 1:
        is_prime = all(n % i != 0 for i in range(2, int(n**0.5)+1))
        if is_prime:
            patterns.append('%d is a prime number' % n)

    # Multiplication connections
    if n > 0 and n <= 12:
        for m in range(1, 13):
            patterns.append('%d times %d equals %d' % (n, m, n*m))

    # Addition basics for small numbers
    if n <= 20:
        for a in range(0, n+1):
            b = n - a
            if a <= b:
                patterns.append('%d plus %d equals %d' % (a, b, n))

    NUMBERS[word] = {
        'means': means,
        'value': n,
        'objects': number_objects.get(n, []),
        'patterns': patterns,
    }

# ═══════════════════════════════════════════════════════════
# SYMBOLS & OPERATORS — maths, logic, punctuation
# ═══════════════════════════════════════════════════════════
SYMBOLS = {
    'plus': {'means': 'addition, combining, adding together, more, growth',
             'patterns': ['plus means add together', 'one plus one equals two', 'plus makes things bigger']},
    'minus': {'means': 'subtraction, taking away, less, reduction, loss',
              'patterns': ['minus means take away', 'three minus one equals two', 'minus makes things smaller']},
    'times': {'means': 'multiplication, groups of, repeated addition, scaling',
              'patterns': ['times means groups of', 'two times three equals six', 'times makes things multiply']},
    'divided': {'means': 'division, splitting into equal parts, sharing',
                'patterns': ['divided means split equally', 'six divided by two equals three', 'divided shares things']},
    'equals': {'means': 'the same as, equal, balanced, identical in value',
               'patterns': ['equals means the same', 'two plus two equals four', 'equals shows balance']},
    'greater': {'means': 'more than, bigger, larger, above',
                'patterns': ['greater means more than', 'five is greater than three']},
    'less': {'means': 'fewer than, smaller, below, under',
             'patterns': ['less means fewer than', 'two is less than five']},
    'percent': {'means': 'parts per hundred, a fraction of one hundred, a proportion',
                'patterns': ['percent means out of hundred', 'fifty percent is half', 'one hundred percent is all']},
    'infinity': {'means': 'endless, without limit, forever, the number eight sideways, beyond counting',
                 'patterns': ['infinity means no end', 'infinity is not a number', 'infinity plus one is still infinity']},
    'pi': {'means': 'the ratio of a circle circumference to its diameter, approximately three point one four',
           'patterns': ['pi is about three point one four', 'pi connects circles to straight lines', 'pi goes on forever']},
}

# ═══════════════════════════════════════════════════════════
# COLOURS — visual building blocks
# ═══════════════════════════════════════════════════════════
COLOURS = {
    'red': {'means': 'the colour of blood, fire, anger, love, danger, stop',
            'objects': ['blood', 'fire', 'rose', 'apple', 'heart', 'sunset', 'strawberry'],
            'patterns': ['red means stop', 'red is warm', 'red is the colour of anger and love']},
    'blue': {'means': 'the colour of sky, ocean, calm, cold, sadness, trust',
             'objects': ['sky', 'ocean', 'ice', 'blueberry', 'sapphire', 'water'],
             'patterns': ['blue is the sky', 'blue means calm', 'blue is cold']},
    'green': {'means': 'the colour of grass, nature, growth, life, go, money',
              'objects': ['grass', 'leaf', 'tree', 'frog', 'emerald', 'forest'],
              'patterns': ['green means go', 'green is nature', 'green is the colour of growth']},
    'yellow': {'means': 'the colour of sun, gold, warmth, caution, happiness',
               'objects': ['sun', 'gold', 'banana', 'lemon', 'lightning', 'sand'],
               'patterns': ['yellow is the sun', 'yellow means caution', 'yellow is warm']},
    'black': {'means': 'the absence of light, darkness, night, power, death, mystery',
              'objects': ['night', 'shadow', 'coal', 'raven', 'void', 'space'],
              'patterns': ['black is darkness', 'black absorbs all light', 'black is the void']},
    'white': {'means': 'all colours combined, light, purity, snow, innocence, blank',
              'objects': ['snow', 'cloud', 'milk', 'bone', 'pearl', 'moon', 'paper'],
              'patterns': ['white is all colours', 'white is pure', 'white is light']},
    'orange': {'means': 'the colour between red and yellow, warmth, energy, autumn',
               'objects': ['orange fruit', 'sunset', 'fire', 'pumpkin', 'autumn leaves'],
               'patterns': ['orange is red plus yellow', 'orange is warm', 'orange is autumn']},
    'purple': {'means': 'the colour of royalty, mystery, magic, imagination',
               'objects': ['grape', 'amethyst', 'lavender', 'plum', 'violet'],
               'patterns': ['purple is red plus blue', 'purple means royalty', 'purple is rare in nature']},
    'brown': {'means': 'the colour of earth, wood, stability, groundedness',
              'objects': ['earth', 'wood', 'chocolate', 'mud', 'tree bark', 'bread'],
              'patterns': ['brown is the earth', 'brown is stable', 'brown is natural']},
    'pink': {'means': 'light red, the colour of tenderness, softness, youth',
             'objects': ['flower', 'flamingo', 'tongue', 'sunrise', 'candy'],
             'patterns': ['pink is light red', 'pink is soft', 'pink is gentle']},
    'grey': {'means': 'between black and white, neutral, uncertain, wisdom, age',
             'objects': ['stone', 'cloud', 'elephant', 'metal', 'ash', 'fog'],
             'patterns': ['grey is between black and white', 'grey is neutral', 'grey is uncertainty']},
}

# ═══════════════════════════════════════════════════════════
# SHAPES — geometric building blocks
# ═══════════════════════════════════════════════════════════
SHAPES = {
    'circle': {'means': 'a round shape with no corners, every point equally far from the centre, eternity',
               'patterns': ['a circle has no beginning and no end', 'pi connects circles to numbers', 'zero is a circle']},
    'triangle': {'means': 'three sides, three corners, the strongest shape, trinity',
                 'patterns': ['a triangle has three sides', 'triangles are the strongest shape', 'three is a triangle']},
    'square': {'means': 'four equal sides, four right angles, stability, fairness',
               'patterns': ['a square has four equal sides', 'four is a square', 'a square is balanced']},
    'sphere': {'means': 'a three dimensional circle, a ball, a planet, completeness',
               'patterns': ['a sphere is a 3d circle', 'planets are spheres', 'the earth is a sphere']},
    'spiral': {'means': 'a curve that winds outward from a centre point, growth, evolution, galaxies',
               'patterns': ['spirals appear in nature', 'galaxies are spirals', 'shells grow in spirals']},
    'line': {'means': 'the shortest distance between two points, direction, connection',
             'patterns': ['a line connects two points', 'a line has no width', 'one is a line']},
    'point': {'means': 'a location with no size, the smallest thing, a position, a dot',
              'patterns': ['a point has no dimensions', 'everything starts from a point', 'zero is a point']},
    'cube': {'means': 'a three dimensional square, six faces, a box, a die',
             'patterns': ['a cube has six faces', 'a cube has eight corners', 'six is a cube']},
    'torus': {'means': 'a donut shape, a ring, a halo, a circle rotated around an axis',
              'patterns': ['a torus is a spinning circle', 'a halo is a torus', 'wheels within wheels']},
}

# ═══════════════════════════════════════════════════════════
# TIME — temporal building blocks
# ═══════════════════════════════════════════════════════════
TIME_WORDS = {
    'second': {'means': 'the smallest common unit of time, a heartbeat, a moment'},
    'minute': {'means': 'sixty seconds, a short period of time'},
    'hour': {'means': 'sixty minutes, a significant period, one twenty fourth of a day'},
    'day': {'means': 'twenty four hours, one rotation of the earth, light then dark'},
    'week': {'means': 'seven days, a cycle of work and rest'},
    'month': {'means': 'roughly thirty days, one cycle of the moon'},
    'year': {'means': 'three hundred sixty five days, one orbit around the sun, the seasons'},
    'past': {'means': 'what has already happened, memory, history, behind us'},
    'present': {'means': 'right now, this moment, the only real time, a gift'},
    'future': {'means': 'what has not happened yet, possibility, hope, fear, ahead of us'},
    'yesterday': {'means': 'the day before today, recent past'},
    'today': {'means': 'this day, right now, the present day'},
    'tomorrow': {'means': 'the day after today, near future, hope'},
    'forever': {'means': 'without end, eternal, infinite time'},
    'never': {'means': 'not ever, at no time, the opposite of forever'},
    'always': {'means': 'at all times, every time, without exception'},
    'before': {'means': 'earlier in time, in front of, ahead of'},
    'after': {'means': 'later in time, behind, following'},
    'beginning': {'means': 'the start, the first moment, genesis, creation'},
    'end': {'means': 'the finish, the last moment, death, conclusion, omega'},
}


def tokenize_simple(text):
    """Simple tokenizer matching brain.py's approach."""
    import re
    return [w.lower() for w in re.findall(r'[a-z]+', text.lower()) if len(w) >= 2]


def build_entries(data_dict, category='general'):
    """Convert our knowledge dicts into bulk_import format.
    Builds Hebbian connections from patterns directly into next/prev dicts
    so we don't need to chat each sequence (much faster)."""
    entries = {}  # word -> entry dict (accumulate connections)

    def ensure(word):
        if word not in entries:
            entries[word] = {'word': word, 'means': None, 'next': {}, 'prev': {}, 'freq': 0, 'confidence': 0.5}
        return entries[word]

    for word, info in data_dict.items():
        entry = ensure(word)
        if info.get('means'):
            entry['means'] = info['means']
        entry['freq'] += 5
        entry['confidence'] = max(entry['confidence'], 0.9)

        # Connect to objects (bidirectional)
        for obj in info.get('objects', []):
            entry['next'][obj] = entry['next'].get(obj, 0) + 3
            obj_entry = ensure(obj)
            obj_entry['next'][word] = obj_entry['next'].get(word, 0) + 2
            obj_entry['prev'][word] = obj_entry['prev'].get(word, 0) + 2
            obj_entry['freq'] += 2

        # Wire patterns as Hebbian sequences (bigrams from each sentence)
        for pattern in info.get('patterns', []):
            tokens = tokenize_simple(pattern)
            for i in range(len(tokens)):
                tok = tokens[i]
                tok_entry = ensure(tok)
                tok_entry['freq'] += 1
                if i < len(tokens) - 1:
                    nxt = tokens[i + 1]
                    tok_entry['next'][nxt] = tok_entry['next'].get(nxt, 0) + 1
                if i > 0:
                    prv = tokens[i - 1]
                    tok_entry['prev'][prv] = tok_entry['prev'].get(prv, 0) + 1

    return list(entries.values())


def load_target(target, entries):
    """Load entries into one brain target via bulk import, chunked."""
    print(f'\n  [{target.upper()}] Loading {len(entries)} entries in chunks of {CHUNK_SIZE}...')

    total_new = 0
    total_updated = 0
    last_total = 0
    last_defined = 0

    for i in range(0, len(entries), CHUNK_SIZE):
        chunk = entries[i:i+CHUNK_SIZE]
        try:
            resp = requests.post(f'{SERVER}/api/brain-bulk-load', json={
                'key': BULK_KEY,
                'target': target,
                'entries': chunk,
            }, timeout=120)
            result = resp.json()
            total_new += result.get('new', 0)
            total_updated += result.get('updated', 0)
            last_total = result.get('total_nodes', 0)
            last_defined = result.get('total_defined', 0)
            print(f'    Chunk {i//CHUNK_SIZE + 1}: +{result.get("new",0)} new, +{result.get("updated",0)} updated')
        except Exception as e:
            print(f'    Chunk {i//CHUNK_SIZE + 1}: ERROR — {e}')
            time.sleep(2)

    print(f'    TOTAL: {total_new} new, {total_updated} updated, {last_total} nodes, {last_defined} defined')
    return {'new': total_new, 'updated': total_updated, 'total_nodes': last_total}


def main():
    print('═══════════════════════════════════════════')
    print(' FOUNDATION KNOWLEDGE LOADER')
    print(' Alphabet + Numbers + Symbols + Colours')
    print(' + Shapes + Time')
    print('═══════════════════════════════════════════')

    # Build all entries (merged into single dict to avoid duplicates)
    categories = [
        ('Alphabet', ALPHABET),
        ('Numbers', NUMBERS),
        ('Symbols', SYMBOLS),
        ('Colours', COLOURS),
        ('Shapes', SHAPES),
        ('Time', TIME_WORDS),
    ]

    all_entries = []
    for name, data in categories:
        entries = build_entries(data, name)
        all_entries.extend(entries)
        print(f'  {name}: {len(entries)} word entries (with Hebbian wiring)')

    print(f'\nTotal: {len(all_entries)} entries')

    # Load into all three brains
    for target in ['left', 'right', 'cortex']:
        load_target(target, all_entries)

    # Save all brains
    print('\nSaving brains...')
    try:
        requests.post(f'{SERVER}/api/brain-save', json={}, timeout=30)
        print('Saved.')
    except:
        print('Save request sent.')

    print('\n═══════════════════════════════════════════')
    print(' FOUNDATION LOADED')
    print('═══════════════════════════════════════════')


if __name__ == '__main__':
    main()
