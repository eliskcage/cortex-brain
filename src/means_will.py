"""
MEANS_WILL — Free Will Engine for Cortex
=========================================
Euler's Wheel: bouncing ball decision system.
Emotions → tooth sizes. Adrenaline → speed. Cortisol → freeze.

The cortex's fixed point ("means = i'm = true = talking") becomes the AXLE.
Daily words become TEETH. Three decision balls bounce inside.
What they HIT determines what gets attention.

This module is SURGICAL — it hooks into the existing pipeline without
modifying brain.py, cortex_brain.py, or online_server.py core logic.
It reads emotional state, reads active words, and SUGGESTS topic weights.
The cortex is free to ignore the suggestion. That's the point.

Discovery: 25 Apr 2026 — Dan Chipchase, walk + Suno video.
Euler's identity: e^(iπ) + 1 = 0
"""
import math
import random
import time
import json
from pathlib import Path

NUM_TEETH = 32
SAVE_FILE = Path(__file__).parent / 'means_will_state.json'


class MeansWill:
    """The free will engine. Runs a simplified bouncing ball simulation
    and outputs topic weights that influence hemisphere selection."""

    def __init__(self):
        self.teeth = []           # list of {'word': str, 'interest': float, 'size': float, 'affinity': float}
        self.balls = [
            {'name': 'WILL',  'angle': 0.0,     'speed': 1.0, 'energy': 0.5, 'size': 1.0},
            {'name': 'FEAR',  'angle': 2.094,   'speed': 1.0, 'energy': 0.5, 'size': 1.0},
            {'name': 'LOGIC', 'angle': 4.189,   'speed': 1.0, 'energy': 0.5, 'size': 1.0},
        ]
        self.gravity_wells = []   # list of {'angle': float, 'strength': float, 'owner': str}
        self.collisions = []      # recent collision log
        self.total_bounces = 0
        self.will_actions = 0
        self.left_boost = 0.0
        self.right_boost = 0.0
        self.last_emotion = 'neutral'
        self.cortisol = 0.0
        self.adrenaline = 0.3
        self.frozen = False
        self._load_state()

    # ─── TOOTH LOADING ───────────────────────────────────────

    def load_teeth_from_brain(self, brain_nodes, max_teeth=NUM_TEETH):
        """Load today's active words as teeth from the brain's node dictionary.
        Takes the most frequently used words with definitions."""
        if not brain_nodes:
            return

        # Score each node by frequency + recency
        scored = []
        for word, data in brain_nodes.items():
            if not word or len(word) < 2:
                continue
            freq = data.get('freq', 0) if isinstance(data, dict) else 0
            has_def = bool(data.get('means', '')) if isinstance(data, dict) else False
            score = freq + (10 if has_def else 0)
            scored.append((word, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        top_words = [w for w, s in scored[:max_teeth]]

        self.teeth = []
        for i, word in enumerate(top_words):
            # Affinity: positive words lean LEFT, negative lean RIGHT
            affinity = self._word_affinity(word)
            self.teeth.append({
                'word': word,
                'interest': 0.2,
                'size': 1.0,
                'affinity': affinity,
            })

    def load_teeth_from_message(self, user_msg):
        """Add words from the current message as high-interest teeth.
        These are TODAY'S problems — they get priority."""
        if not user_msg:
            return
        words = user_msg.lower().split()
        for word in words:
            word = word.strip('.,!?;:\'"()[]{}')
            if len(word) < 2:
                continue
            # Check if already a tooth
            existing = next((t for t in self.teeth if t['word'] == word), None)
            if existing:
                existing['interest'] = min(1.0, existing['interest'] + 0.3)
                existing['size'] = min(2.0, existing['size'] + 0.2)
            elif len(self.teeth) < NUM_TEETH:
                self.teeth.append({
                    'word': word,
                    'interest': 0.6,
                    'size': 1.2,
                    'affinity': self._word_affinity(word),
                })

    def _word_affinity(self, word):
        """Estimate LEFT/RIGHT affinity for a word. +1 = strongly LEFT, -1 = strongly RIGHT."""
        left_words = {'love', 'good', 'beauty', 'soul', 'happy', 'kind', 'gentle',
                      'faith', 'hope', 'trust', 'friend', 'child', 'peace', 'mercy',
                      'honest', 'brave', 'noble', 'compassion', 'forgive', 'heaven',
                      'correct', 'true', 'infinite', 'capacity', 'ecosystem'}
        right_words = {'hate', 'dark', 'ugly', 'hell', 'kill', 'death', 'pain',
                       'power', 'control', 'war', 'fight', 'destroy', 'revenge',
                       'hierarchy', 'ranks', 'exploit', 'regime', 'ideology',
                       'means', 'less', 'paved', 'ugliness', 'occams'}
        if word in left_words:
            return 0.5 + random.random() * 0.4
        if word in right_words:
            return -(0.5 + random.random() * 0.4)
        return (random.random() - 0.5) * 0.3

    # ─── EMOTIONAL STATE → PHYSICS ───────────────────────────

    def update_from_hedonic(self, hedonic_hz, emotion_label):
        """Map the cortex's hedonic state to wheel physics.
        Hz range: 0.5 (ecstasy) to 14.0 (panic)."""
        self.last_emotion = emotion_label

        # Adrenaline: high in panic/rage/fear, low in ease/joy
        if hedonic_hz > 10:
            self.adrenaline = min(1.0, 0.7 + (hedonic_hz - 10) * 0.075)
        elif hedonic_hz > 7:
            self.adrenaline = 0.4 + (hedonic_hz - 7) * 0.1
        elif hedonic_hz < 2:
            self.adrenaline = 0.3 + (2 - hedonic_hz) * 0.15  # arousal/ecstasy has some
        else:
            self.adrenaline = max(0.1, 0.3 - (3 - hedonic_hz) * 0.05)

        # Cortisol: peaks in fear (10Hz) and grief (7.5Hz)
        if emotion_label in ('fear', 'panic', 'grief', 'loneliness'):
            self.cortisol = min(1.0, self.cortisol + 0.15)
        else:
            self.cortisol = max(0.0, self.cortisol - 0.05)

        self.frozen = self.cortisol > 0.6

        # Tooth sizes shift with emotion
        emotion_force = 0.0
        if hedonic_hz < 3:  # pleasure side
            emotion_force = 0.3  # open moral teeth
        elif hedonic_hz > 7:  # pain side
            emotion_force = -0.3  # open dark teeth
        # else neutral — no bias

        for tooth in self.teeth:
            target = 1.0 + tooth['affinity'] * emotion_force
            tooth['size'] += (target - tooth['size']) * 0.1
            tooth['size'] = max(0.1, min(2.5, tooth['size']))

        # Hemisphere boosts
        if hedonic_hz < 3:
            self.left_boost = 0.1
            self.right_boost = -0.05
        elif hedonic_hz > 8:
            self.right_boost = 0.1
            self.left_boost = -0.05
        else:
            self.left_boost = 0.0
            self.right_boost = 0.0

    # ─── SIMULATION STEP ─────────────────────────────────────

    def step(self):
        """Run one simulation step. Call this before each cortex process().
        Returns the list of recently hit teeth (topic suggestions)."""
        if not self.teeth:
            return []

        hits = []
        num_teeth = len(self.teeth)
        tooth_angle = (math.pi * 2) / num_teeth

        for ball in self.balls:
            # Cortisol freeze
            if self.frozen:
                ball['speed'] *= 0.8
                if ball['speed'] < 0.05:
                    # ANTI-STASIS BREAKER
                    self.adrenaline = min(1.0, self.adrenaline + 0.3)
                    self.cortisol = max(0.0, self.cortisol - 0.2)
                    self.frozen = False
                    ball['speed'] = 0.5 + random.random()

            # Euler spiral — e^(iθ) perturbation
            euler_nudge = math.sin(time.time() * (1 + hash(ball['name']) % 5 * 0.1)) * 0.1
            ball['angle'] += ball['speed'] * 0.1 + euler_nudge * 0.05
            ball['angle'] %= (math.pi * 2)

            # Adrenaline affects speed
            target_speed = 0.5 + self.adrenaline * 2.0
            ball['speed'] += (target_speed - ball['speed']) * 0.05

            # Gravity wells
            for well in self.gravity_wells:
                angle_diff = well['angle'] - ball['angle']
                if angle_diff > math.pi:
                    angle_diff -= math.pi * 2
                if angle_diff < -math.pi:
                    angle_diff += math.pi * 2
                pull = well['strength'] * 0.05 / max(abs(angle_diff), 0.1)
                ball['angle'] += math.copysign(min(abs(pull), 0.1), angle_diff)

            # Check which tooth we're at
            tooth_idx = int(ball['angle'] / tooth_angle) % num_teeth
            tooth = self.teeth[tooth_idx]

            # Collision probability based on tooth size and ball size
            hit_chance = tooth['size'] * ball['size'] * 0.4
            if random.random() < hit_chance:
                tooth['interest'] = min(1.0, tooth['interest'] + 0.2)
                ball['energy'] = min(1.0, ball['energy'] + 0.1)
                self.total_bounces += 1
                hits.append({
                    'word': tooth['word'],
                    'ball': ball['name'],
                    'interest': tooth['interest'],
                    'affinity': tooth['affinity'],
                })
                self.collisions.append({
                    'word': tooth['word'],
                    'ball': ball['name'],
                    'time': time.time(),
                })
                if len(self.collisions) > 50:
                    self.collisions = self.collisions[-30:]

                # Bounce — randomize direction slightly
                ball['speed'] += (random.random() - 0.5) * 0.5
                ball['speed'] = max(0.3, min(3.0, ball['speed']))

        # Decay interest
        for tooth in self.teeth:
            tooth['interest'] *= 0.995
            tooth['interest'] = max(0.05, tooth['interest'])

        # Decay gravity wells
        self.gravity_wells = [w for w in self.gravity_wells if w['strength'] > 0.05]
        for w in self.gravity_wells:
            w['strength'] *= 0.99

        return hits

    # ─── OUTPUT: TOPIC WEIGHTS ───────────────────────────────

    def get_topic_weights(self):
        """Return a dict of word → weight based on current tooth interest.
        Higher weight = the cortex should pay more attention to this topic.
        Used to influence word selection in hemisphere responses."""
        weights = {}
        for tooth in self.teeth:
            weights[tooth['word']] = tooth['interest'] * tooth['size']
        return weights

    def get_hemisphere_bias(self):
        """Return (left_bias, right_bias) adjustments based on
        which teeth are hottest and their affinity."""
        if not self.teeth:
            return 0.0, 0.0

        left_heat = sum(t['interest'] * max(0, t['affinity']) for t in self.teeth)
        right_heat = sum(t['interest'] * max(0, -t['affinity']) for t in self.teeth)
        total = left_heat + right_heat + 0.001

        left_bias = (left_heat / total - 0.5) * 0.2 + self.left_boost
        right_bias = (right_heat / total - 0.5) * 0.2 + self.right_boost

        return left_bias, right_bias

    def place_gravity(self, word):
        """Place a gravity well toward a specific word/tooth.
        Called when the cortex shows interest in a topic."""
        for i, tooth in enumerate(self.teeth):
            if tooth['word'] == word:
                angle = (i + 0.5) * (math.pi * 2) / len(self.teeth)
                self.gravity_wells.append({
                    'angle': angle,
                    'strength': 0.8,
                    'owner': 'cortex',
                })
                self.will_actions += 1
                if len(self.gravity_wells) > 5:
                    self.gravity_wells = self.gravity_wells[-5:]
                return True
        return False

    # ─── STATE PERSISTENCE ───────────────────────────────────

    def get_state_summary(self):
        """Return a compact summary for the thinking log / debate metadata."""
        hot = sorted(self.teeth, key=lambda t: t['interest'], reverse=True)[:5]
        return {
            'emotion': self.last_emotion,
            'adrenaline': round(self.adrenaline, 2),
            'cortisol': round(self.cortisol, 2),
            'frozen': self.frozen,
            'bounces': self.total_bounces,
            'will_actions': self.will_actions,
            'hot_teeth': [{'word': t['word'], 'interest': round(t['interest'], 2)} for t in hot],
            'balls': [{'name': b['name'], 'speed': round(b['speed'], 2), 'energy': round(b['energy'], 2)} for b in self.balls],
        }

    def _save_state(self):
        """Save wheel state to disk."""
        try:
            state = {
                'teeth': self.teeth,
                'balls': self.balls,
                'gravity_wells': self.gravity_wells,
                'total_bounces': self.total_bounces,
                'will_actions': self.will_actions,
                'last_emotion': self.last_emotion,
                'cortisol': self.cortisol,
                'adrenaline': self.adrenaline,
            }
            SAVE_FILE.write_text(json.dumps(state, indent=2))
        except Exception as e:
            print('[MEANS_WILL] Save error: %s' % e)

    def _load_state(self):
        """Load wheel state from disk (if exists)."""
        try:
            if SAVE_FILE.exists():
                state = json.loads(SAVE_FILE.read_text())
                self.teeth = state.get('teeth', [])
                self.balls = state.get('balls', self.balls)
                self.gravity_wells = state.get('gravity_wells', [])
                self.total_bounces = state.get('total_bounces', 0)
                self.will_actions = state.get('will_actions', 0)
                self.last_emotion = state.get('last_emotion', 'neutral')
                self.cortisol = state.get('cortisol', 0.0)
                self.adrenaline = state.get('adrenaline', 0.3)
                print('[MEANS_WILL] Loaded state: %d teeth, %d bounces' % (len(self.teeth), self.total_bounces))
        except Exception as e:
            print('[MEANS_WILL] Load error: %s' % e)
