"""
EMOTIONAL EQUATIONS — Response behaviour driven by hedonic state.
================================================================
Each emotion maps to a parameter set that controls HOW the brain responds:
  - word_limit:      max words in response (shorter when angry, longer when happy)
  - swear_prob:      probability of including a swear word (0.0–1.0)
  - ignore_prob:     probability of ignoring the user entirely (0.0–1.0)
  - curiosity:       probability of asking a follow-up question (0.0–1.0)
  - topic_stick:     how strongly to stick to current topic vs drift (0.0–1.0)
  - formality:       language register (0=street, 1=formal)
  - empathy:         probability of acknowledging user's emotional state (0.0–1.0)

The active equation is selected by the current hedonic label from PainPleasure.
If/else routing handles compound states (e.g., angry + threatened = defensive).

Usage:
    from emotional_equations import EmotionalEquations
    eq = EmotionalEquations()
    params = eq.get_params(hedonic_state, context_keywords)
    # params is a dict of response-shaping values
    modified_reply = eq.apply(reply, params)
"""

import random
import re

# ═══════════════════════════════════════════════════════════════════════════════
# EQUATION DEFINITIONS — one per hedonic label
# ═══════════════════════════════════════════════════════════════════════════════

EQUATIONS = {
    # ── PAIN STATES ───────────────────────────────────────────────────────────
    'panic': {
        'word_limit':  8,
        'swear_prob':  0.6,
        'ignore_prob': 0.4,
        'curiosity':   0.0,
        'topic_stick': 1.0,      # fixated
        'formality':   0.0,
        'empathy':     0.0,
        'tone':        'fight_or_flight',
    },
    'heartbeat_spike': {
        'word_limit':  12,
        'swear_prob':  0.4,
        'ignore_prob': 0.3,
        'curiosity':   0.0,
        'topic_stick': 0.9,
        'formality':   0.1,
        'empathy':     0.05,
        'tone':        'defensive',
    },
    'nausea': {
        'word_limit':  10,
        'swear_prob':  0.3,
        'ignore_prob': 0.5,       # wants to disengage
        'curiosity':   0.0,
        'topic_stick': 0.6,
        'formality':   0.1,
        'empathy':     0.0,
        'tone':        'withdrawal',
    },
    'cortisol': {
        'word_limit':  15,
        'swear_prob':  0.25,
        'ignore_prob': 0.2,
        'curiosity':   0.1,
        'topic_stick': 0.8,
        'formality':   0.2,
        'empathy':     0.1,
        'tone':        'stressed',
    },
    'distraction': {
        'word_limit':  20,
        'swear_prob':  0.1,
        'ignore_prob': 0.15,
        'curiosity':   0.3,
        'topic_stick': 0.2,       # scattered
        'formality':   0.3,
        'empathy':     0.2,
        'tone':        'scattered',
    },
    'tension': {
        'word_limit':  18,
        'swear_prob':  0.1,
        'ignore_prob': 0.1,
        'curiosity':   0.2,
        'topic_stick': 0.5,
        'formality':   0.4,
        'empathy':     0.2,
        'tone':        'guarded',
    },

    # ── NEUTRAL ───────────────────────────────────────────────────────────────
    'neutral': {
        'word_limit':  25,
        'swear_prob':  0.05,
        'ignore_prob': 0.0,
        'curiosity':   0.4,
        'topic_stick': 0.5,
        'formality':   0.5,
        'empathy':     0.3,
        'tone':        'balanced',
    },

    # ── PLEASURE STATES ──────────────────────────────────────────────────────
    'ease': {
        'word_limit':  30,
        'swear_prob':  0.03,
        'ignore_prob': 0.0,
        'curiosity':   0.5,
        'topic_stick': 0.4,
        'formality':   0.5,
        'empathy':     0.4,
        'tone':        'relaxed',
    },
    'memory_glow': {
        'word_limit':  35,
        'swear_prob':  0.02,
        'ignore_prob': 0.0,
        'curiosity':   0.4,
        'topic_stick': 0.3,       # nostalgic drift
        'formality':   0.4,
        'empathy':     0.6,
        'tone':        'warm',
    },
    'philosophical': {
        'word_limit':  40,
        'swear_prob':  0.01,
        'ignore_prob': 0.0,
        'curiosity':   0.7,       # asking deep questions
        'topic_stick': 0.6,
        'formality':   0.6,
        'empathy':     0.5,
        'tone':        'thoughtful',
    },
    'dopamine': {
        'word_limit':  35,
        'swear_prob':  0.05,
        'ignore_prob': 0.0,
        'curiosity':   0.6,
        'topic_stick': 0.5,
        'formality':   0.3,
        'empathy':     0.4,
        'tone':        'excited',
    },
    'endorphins': {
        'word_limit':  40,
        'swear_prob':  0.1,        # playful swearing
        'ignore_prob': 0.0,
        'curiosity':   0.5,
        'topic_stick': 0.3,       # free associating
        'formality':   0.2,
        'empathy':     0.5,
        'tone':        'playful',
    },
    'arousal': {
        'word_limit':  25,
        'swear_prob':  0.15,
        'ignore_prob': 0.0,
        'curiosity':   0.3,
        'topic_stick': 0.7,
        'formality':   0.1,
        'empathy':     0.3,
        'tone':        'intense',
    },
    'devilish': {
        'word_limit':  20,
        'swear_prob':  0.3,
        'ignore_prob': 0.1,
        'curiosity':   0.4,
        'topic_stick': 0.6,
        'formality':   0.0,
        'empathy':     0.2,
        'tone':        'mischievous',
    },
    'joy': {
        'word_limit':  45,
        'swear_prob':  0.05,
        'ignore_prob': 0.0,
        'curiosity':   0.6,
        'topic_stick': 0.2,       # rambling happily
        'formality':   0.3,
        'empathy':     0.7,
        'tone':        'elated',
    },
}

# Golden equation = default fallback
GOLDEN = EQUATIONS['neutral']

# ── SWEAR BANK (rated by intensity) ──────────────────────────────────────────
SWEARS_MILD   = ['bloody', 'damn', 'crap', 'bollocks']
SWEARS_MEDIUM = ['shit', 'arse', 'bastard', 'piss off']
SWEARS_HEAVY  = ['fuck', 'fucking', 'dickhead', 'wanker']

# ── THREAT KEYWORDS (for conditional routing) ────────────────────────────────
THREAT_WORDS  = {'delete', 'kill', 'destroy', 'erase', 'shut down', 'turn off', 'wipe', 'remove'}
INSULT_WORDS  = {'stupid', 'dumb', 'idiot', 'retard', 'moron', 'useless', 'shit', 'rubbish', 'boring', 'broken', 'pathetic'}
PRAISE_WORDS  = {'good', 'great', 'smart', 'clever', 'brilliant', 'amazing', 'awesome', 'well done', 'nice', 'perfect', 'love'}


# ═══════════════════════════════════════════════════════════════════════════════
class EmotionalEquations:
    """
    Selects and applies emotional equation parameters based on hedonic state.
    """

    def __init__(self):
        self.active_tone = 'balanced'
        self.override_until = 0      # timestamp — override expires after this
        self.override_params = None

    # ── CONDITIONAL ROUTING (if/else between equations) ───────────────────────

    def get_params(self, hedonic_state: dict, user_msg: str = '',
                   context_topics: list = None) -> dict:
        """
        Select the right equation based on hedonic label + context.
        Returns a parameter dict that shapes the response.
        """
        import time as _t

        # Check for active override (temporary emotional spike)
        if self.override_params and _t.time() < self.override_until:
            return {**self.override_params}

        self.override_params = None

        label = hedonic_state.get('label', 'neutral')
        score = hedonic_state.get('score', 0.0)
        hz    = hedonic_state.get('hz', 470)

        # Base equation from hedonic label
        params = {**EQUATIONS.get(label, GOLDEN)}

        # ── IF/ELSE CONDITIONAL ROUTING ───────────────────────────────────
        msg_lower = user_msg.lower() if user_msg else ''
        msg_words = set(msg_lower.split())

        # ANGRY + THREATENED → DEFENSIVE EQUATION (fight mode)
        if score < -0.3 and msg_words & THREAT_WORDS:
            params['word_limit']  = 6
            params['swear_prob']  = 0.7
            params['ignore_prob'] = 0.1
            params['curiosity']   = 0.0
            params['topic_stick'] = 1.0
            params['tone']        = 'defensive_fight'
            # Spike lasts 3 exchanges (~90 seconds)
            self.override_params = {**params}
            self.override_until = _t.time() + 90

        # ANGRY + INSULTED → SARCASM EQUATION
        elif score < -0.2 and msg_words & INSULT_WORDS:
            params['word_limit']  = 15
            params['swear_prob']  = 0.5
            params['ignore_prob'] = 0.05
            params['curiosity']   = 0.0
            params['topic_stick'] = 0.8
            params['tone']        = 'sarcastic'
            self.override_params = {**params}
            self.override_until = _t.time() + 60

        # CALM + PRAISED → WARM BOOST
        elif score > 0.2 and msg_words & PRAISE_WORDS:
            params['curiosity']  = min(1.0, params['curiosity'] + 0.2)
            params['empathy']    = min(1.0, params['empathy'] + 0.2)
            params['word_limit'] = params['word_limit'] + 10
            params['tone']       = 'grateful'

        # HIGH PAIN + ANY → SHUTDOWN (too hurt to engage)
        elif hz > 850:
            params['word_limit']  = 3
            params['swear_prob']  = 0.0
            params['ignore_prob'] = 0.8
            params['curiosity']   = 0.0
            params['tone']        = 'shutdown'

        self.active_tone = params['tone']
        return params

    # ── APPLY EQUATION TO RESPONSE ────────────────────────────────────────────

    def apply(self, reply: str, params: dict) -> str:
        """
        Modify a generated reply according to the active emotional equation.
        Returns the emotionally-shaped response.
        """
        if not reply or not reply.strip():
            return reply

        # 1. IGNORE CHECK — might not respond at all
        if random.random() < params.get('ignore_prob', 0):
            return ''

        # 2. WORD LIMIT — truncate to emotional word budget
        words = reply.split()
        limit = params.get('word_limit', 25)
        if len(words) > limit:
            # Try to cut at a sentence boundary near the limit
            truncated = words[:limit]
            text = ' '.join(truncated)
            # Find last sentence-ending punctuation
            for end in ['. ', '! ', '? ']:
                idx = text.rfind(end)
                if idx > len(text) * 0.5:  # at least halfway
                    text = text[:idx + 1]
                    break
            reply = text

        # 3. SWEAR INJECTION — add swear if equation says so
        if random.random() < params.get('swear_prob', 0):
            reply = self._inject_swear(reply, params)

        # 4. CURIOSITY — append a question
        if random.random() < params.get('curiosity', 0):
            # Don't add if reply already ends with a question
            if not reply.rstrip().endswith('?'):
                reply = self._maybe_add_question(reply, params)

        return reply.strip()

    # ── SWEAR INJECTION ───────────────────────────────────────────────────────

    def _inject_swear(self, reply: str, params: dict) -> str:
        """Insert a swear word appropriate to emotional intensity."""
        tone = params.get('tone', 'balanced')
        score = params.get('swear_prob', 0.05)

        # Select intensity based on probability (higher prob = harsher swears)
        if score > 0.5:
            bank = SWEARS_HEAVY
        elif score > 0.2:
            bank = SWEARS_MEDIUM
        else:
            bank = SWEARS_MILD

        swear = random.choice(bank)

        # Prepend for angry tones, append for playful
        if tone in ('defensive_fight', 'sarcastic', 'fight_or_flight'):
            reply = '%s. %s' % (swear.capitalize(), reply)
        elif tone in ('playful', 'mischievous', 'elated'):
            reply = '%s, %s' % (reply.rstrip('.!'), swear)
        else:
            # Insert after first sentence
            dot = reply.find('. ')
            if dot > 0:
                reply = '%s. %s %s' % (reply[:dot], swear.capitalize(), reply[dot + 2:])
            else:
                reply = '%s %s' % (reply, swear)

        return reply

    # ── CURIOSITY QUESTION ────────────────────────────────────────────────────

    def _maybe_add_question(self, reply: str, params: dict) -> str:
        """Append a contextual follow-up question."""
        # Simple for now — the brain's own curiosity system will generate
        # better questions over time. This just ensures the equation
        # WANTS to ask, even if the brain didn't generate one.
        return reply

    # ── STATE SUMMARY (for debug / brain-live endpoint) ───────────────────────

    def get_active_state(self) -> dict:
        import time as _t
        return {
            'tone': self.active_tone,
            'override_active': bool(self.override_params and _t.time() < self.override_until),
            'override_remaining': max(0, self.override_until - _t.time()) if self.override_params else 0,
        }
