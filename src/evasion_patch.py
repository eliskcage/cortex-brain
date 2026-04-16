# EVASION MODE — persistent flag lives here, imported by online_server
evasion_mode = False

def apply_evasion(reply, quality_total):
    """Post-process reply into minimal evasive form."""
    if not reply or not reply.strip():
        return '...'
    r = reply.strip()
    low = r.lower()
    # Low confidence → dunno
    if quality_total < 0.35:
        return random.choice(['dunno', 'no idea', '...', 'not sure', 'beats me'])
    # Yes signals
    if low.startswith(('yes', 'yeah', 'correct', 'true', 'right', 'absolutely', 'definitely')):
        return random.choice(['yeah', 'yep', 'yes'])
    # No signals
    if low.startswith(('no', 'nope', 'not', 'never', 'incorrect', 'false', 'wrong')):
        return random.choice(['nope', 'no', 'nah'])
    # Busy deflection (20% chance)
    if random.random() < 0.20:
        return random.choice(['busy', '...busy', 'later', 'not now', 'hold on'])
    # Truncate to first 5-8 words
    words = r.split()
    if len(words) > 8:
        cut = random.randint(4, 7)
        return ' '.join(words[:cut]) + '.'
    # Short enough already — return first sentence
    first = re.split(r'[.!?]', r)[0].strip()
    return first if first else r
