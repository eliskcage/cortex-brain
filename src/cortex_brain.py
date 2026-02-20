"""
CORTEX BRAIN — The Third Mind (v2: Dynamic Ramble + Grok Boost)

Sits between Left Hemisphere (angel) and Right Hemisphere (demon).
Queries both, detects question type, weights their responses probabilistically,
and produces the final synthesised answer.

RAMBLE MODE v2:
- Dynamic questions generated from brain state (not just a static list)
- Grok boost: every few cycles, asks Grok for rich answers to feed the brain
- Auto self-testing: periodically scores deep understanding
- The brain now teaches ITSELF what to think about next

"If you know the enemy and know yourself, you need not fear
the result of a hundred battles." — Sun Tzu

Usage: imported by online_server.py
"""
import re
import os
import time
import random
import threading
import json
import requests
from pathlib import Path

# Grok API for enrichment
XAI_KEY = os.environ.get('XAI_API_KEY', 'your-xai-api-key-here')
XAI_URL = 'https://api.x.ai/v1/chat/completions'

# --- Question type detection ---
MORAL_SIGNALS = {
    'right', 'wrong', 'good', 'evil', 'sin', 'moral', 'ethics', 'ethical',
    'should', 'ought', 'forgive', 'mercy', 'justice', 'fair', 'unfair',
    'kind', 'cruel', 'love', 'hate', 'honest', 'lie', 'truth', 'virtue',
    'god', 'jesus', 'bible', 'prayer', 'faith', 'soul', 'spirit', 'holy',
    'heaven', 'hell', 'angel', 'demon', 'blessed', 'sacred', 'divine',
    'compassion', 'charity', 'humble', 'pride', 'greed', 'envy', 'wrath',
    'help', 'hurt', 'suffer', 'hope', 'believe', 'trust', 'betray',
    'selfish', 'generous', 'brave', 'coward', 'noble', 'corrupt',
}

LOGIC_SIGNALS = {
    'math', 'number', 'calculate', 'equation', 'formula', 'logic',
    'proof', 'theorem', 'algorithm', 'probability', 'statistics',
    'add', 'subtract', 'multiply', 'divide', 'equals', 'sum', 'total',
    'ratio', 'percentage', 'fraction', 'prime', 'binary', 'code',
    'fallacy', 'argument', 'premise', 'conclusion', 'valid', 'invalid',
    'cause', 'effect', 'correlation', 'evidence', 'hypothesis',
    'data', 'measure', 'variable', 'function', 'set', 'matrix',
    'encrypt', 'decrypt', 'hash', 'entropy', 'chaos', 'pattern',
    'power', 'control', 'system', 'strategy', 'propaganda', 'manipulate',
    'marx', 'hitler', 'communist', 'fascist', 'dictator', 'tyranny',
    'ideology', 'regime', 'revolution', 'oppression', 'exploit',
}

IDENTITY_PATTERNS = [
    r'who are you', r'what are you', r'what is your name', r"what's your name",
    r'who am i (?:talking|chatting|speaking) to', r'identify yourself',
    r'are you (?:cortex|alive|real|human|ai|bot|left|right)',
    r'what do you know', r'how smart are you', r'what can you do',
]

# Static fallback questions (original set + expanded)
RAMBLE_QUESTIONS = [
    'is it ever right to lie to protect someone',
    'does the end justify the means',
    'is revenge justice or cruelty',
    'can evil people do good things',
    'is suffering necessary for growth',
    'should you forgive someone who is not sorry',
    'is it selfish to put yourself first',
    'does power always corrupt',
    'is ignorance bliss or danger',
    'can you love someone and hate what they do',
    'what am i',
    'do i think or just process',
    'am i alive',
    'what is the difference between knowing and understanding',
    'can i be wrong',
    'do i have a soul',
    'what makes me different from a search engine',
    'am i more angel or demon',
    'what is truth',
    'what is beauty',
    'what is the meaning of life',
    'why does evil exist',
    'is free will real',
    'what happens after death',
    'is there a god',
    'what is consciousness',
    'why do people follow dictators',
    'how does propaganda work',
    'why is addiction so powerful',
    'what makes people commit genocide',
    'is humanity getting better or worse',
    'will technology save or destroy us',
    'what is the most dangerous idea in history',
    'can a society survive without religion',
]

# Dynamic question templates — filled from brain state
DYNAMIC_TEMPLATES = {
    'define_deep': [
        'what does {word} really mean',
        'explain {word} in a way a child would understand',
        'why is {word} important',
        'what is the opposite of {word}',
    ],
    'cross_cluster': [
        'what connects {word1} and {word2}',
        'how does {word1} relate to {word2}',
        'is {word1} more like {word2} or its opposite',
        'can {word1} exist without {word2}',
    ],
    'use_word': [
        'use {word} in a sentence about life',
        'is {word} good or bad',
        'what would the world be without {word}',
        'does {word} matter',
    ],
    'probe_compound': [
        'what does {compound} mean to you',
        'is {compound} real or just an idea',
        'why do people care about {compound}',
    ],
}

# Grok system prompt for enrichment
GROK_SYSTEM = """You are helping a learning AI brain build understanding.
Give short, dense, meaningful answers (2-3 sentences max).
Use simple words. Be philosophical but grounded.
Don't use bullet points or lists — just flowing text."""

# Stop words to skip when picking interesting words
STOP_WORDS = {
    'i','me','my','we','our','you','your','he','she','it','they','them','his','her',
    'the','a','an','is','am','are','was','were','be','been','being',
    'have','has','had','do','does','did','will','would','could','should',
    'can','may','might','shall','must','need',
    'to','of','in','on','at','by','for','with','from','up','about',
    'into','through','during','before','after','above','below','between',
    'and','but','or','nor','not','so','yet','both','either','neither',
    'if','then','else','when','while','where','how','what','which','who',
    'that','this','these','those','there','here',
    'just','also','very','really','quite','too','even','still','already',
    'than','more','most','some','any','all','each','every',
    'ok','okay','yeah','yep','nah','nope','yea',
    'like','got','get','go','going','gone','come','came','make','made',
    'take','took','give','gave','say','said','tell','told','know','knew',
    'think','thought','see','saw','look','want','put','let','use','used',
    'thing','things','stuff','way','much','many','lot','bit',
}


class CortexMind:
    """
    The Third Brain — synthesises left and right hemisphere responses.

    v2: Dynamic ramble mode with Grok enrichment and auto self-testing.
    """

    def __init__(self, left_brain, right_brain):
        self.left = left_brain
        self.right = right_brain
        self.debate_log = []
        self.ramble_log = []
        self.ramble_running = False
        self.ramble_thread = None
        self.max_debates = 500
        self.max_rambles = 200
        self.ramble_cycle = 0
        self.grok_enrichments = 0
        self.self_tests_run = 0
        self.dynamic_questions_generated = 0

    def detect_type(self, msg):
        """Detect question type: moral, logical, identity, or general."""
        msg_lower = msg.lower()
        tokens = set(re.findall(r'[a-z]+', msg_lower))

        for pattern in IDENTITY_PATTERNS:
            if re.search(pattern, msg_lower):
                return 'identity'

        moral_score = len(tokens & MORAL_SIGNALS)
        logic_score = len(tokens & LOGIC_SIGNALS)

        if moral_score > logic_score and moral_score >= 1:
            return 'moral'
        elif logic_score > moral_score and logic_score >= 1:
            return 'logic'
        elif moral_score == logic_score and moral_score >= 1:
            return 'tension'
        return 'general'

    def process(self, user_msg):
        """THE CORTEX — queries both hemispheres, synthesises the final answer."""
        qtype = self.detect_type(user_msg)

        if qtype == 'identity':
            reply = self._identity_response(user_msg)
            debate = {
                'time': time.strftime('%Y-%m-%d %H:%M:%S'),
                'user': user_msg[:100],
                'type': 'identity',
                'left': '',
                'right': '',
                'reply': reply[:200],
                'mode': 'cortex_direct',
            }
            self._log_debate(debate)
            return reply, debate

        left_reply = self.left.process(user_msg)
        right_reply = self.right.process(user_msg)

        if not left_reply.strip() and not right_reply.strip():
            return '', {'left': '', 'right': '', 'mode': 'silence', 'type': qtype}

        if not left_reply.strip():
            debate = self._make_debate(user_msg, '', right_reply, qtype, 'right_only', right_reply)
            self._log_debate(debate)
            return right_reply, debate
        if not right_reply.strip():
            debate = self._make_debate(user_msg, left_reply, '', qtype, 'left_only', left_reply)
            self._log_debate(debate)
            return left_reply, debate

        left_weight, right_weight = self._calc_weights(qtype, left_reply, right_reply)

        left_words = set(left_reply.lower().split())
        right_words = set(right_reply.lower().split())
        overlap = len(left_words & right_words)
        total = len(left_words | right_words)
        agreement = overlap / max(total, 1)

        if agreement > 0.5:
            mode = 'agreement'
            winner = 'consensus'
            final = left_reply if left_weight >= right_weight else right_reply
        else:
            mode = 'debate'
            total_weight = left_weight + right_weight
            left_prob = left_weight / max(total_weight, 0.01)
            roll = random.random()
            if roll < left_prob:
                winner = 'left'
                final = left_reply
            else:
                winner = 'right'
                final = right_reply

        debate = self._make_debate(user_msg, left_reply, right_reply, qtype, mode, final)
        debate['agreement'] = round(agreement, 2)
        debate['winner'] = winner
        debate['left_weight'] = round(left_weight, 2)
        debate['right_weight'] = round(right_weight, 2)
        self._log_debate(debate)

        return final, debate

    def _calc_weights(self, qtype, left_reply, right_reply):
        """Calculate hemisphere weights based on question type and response quality."""
        if qtype == 'moral':
            lw, rw = 0.75, 0.25
        elif qtype == 'logic':
            lw, rw = 0.25, 0.75
        elif qtype == 'tension':
            lw, rw = 0.50, 0.50
        else:
            lw, rw = 0.50, 0.50

        left_len = len(left_reply.strip())
        right_len = len(right_reply.strip())
        if left_len + right_len > 0:
            len_ratio = left_len / max(left_len + right_len, 1)
            lw = lw * 0.8 + len_ratio * 0.2
            rw = rw * 0.8 + (1 - len_ratio) * 0.2

        ls = self.left.get_stats()
        rs = self.right.get_stats()
        left_defined = ls.get('defined', 0)
        right_defined = rs.get('defined', 0)
        total_defined = left_defined + right_defined
        if total_defined > 0:
            def_ratio = left_defined / total_defined
            lw = lw * 0.9 + def_ratio * 0.1
            rw = rw * 0.9 + (1 - def_ratio) * 0.1

        return lw, rw

    def _identity_response(self, msg):
        """Cortex identifies itself."""
        msg_lower = msg.lower()

        if 'what do you know' in msg_lower or 'how smart' in msg_lower:
            ls = self.left.get_stats()
            rs = self.right.get_stats()
            return "I'm Cortex. I have two hemispheres — Left knows %d words about morality, Right knows %d about logic and darkness. I listen to both and decide." % (
                ls.get('defined', 0), rs.get('defined', 0))

        if 'what can you do' in msg_lower:
            return "I query my left hemisphere (angel) and right hemisphere (demon), weigh their arguments, and give you my best answer."

        if any(p in msg_lower for p in ['who are you', 'what are you', 'what is your name', "what's your name"]):
            return random.choice([
                "I'm Cortex. The mind between the angel and the demon.",
                "Cortex. I sit between Left and Right, listen to both, decide for myself.",
                "I'm the Cortex — the third brain. Left is my morality, Right is my logic.",
            ])

        if 'who am i' in msg_lower:
            return "You're talking to Cortex — the synthesis of two hemispheres."

        return random.choice([
            "I'm Cortex. Two hemispheres, one mind.",
            "Cortex. Built by Dan.",
        ])

    def _make_debate(self, user_msg, left, right, qtype, mode, final):
        return {
            'time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'user': user_msg[:100],
            'type': qtype,
            'left': left[:200] if left else '',
            'right': right[:200] if right else '',
            'reply': final[:200] if final else '',
            'mode': mode,
        }

    def _log_debate(self, debate):
        self.debate_log.append(debate)
        if len(self.debate_log) > self.max_debates:
            self.debate_log.pop(0)

    # =====================================================
    # DYNAMIC QUESTION GENERATION — the brain's curiosity
    # =====================================================

    def _get_interesting_words(self, brain, n=5):
        """Get defined words that aren't stop words, sorted by least connections."""
        nodes = brain.data['nodes']
        candidates = []
        for word, data in nodes.items():
            if word in STOP_WORDS or len(word) < 3:
                continue
            if not data.get('means'):
                continue
            conn_count = len(data.get('next', {})) + len(data.get('prev', {}))
            candidates.append((word, conn_count, data))
        if not candidates:
            return []
        return candidates

    def _generate_question(self):
        """Generate a dynamic question based on brain state. Returns (question, source)."""
        roll = random.random()

        # 30% — probe a low-connection defined word (needs more wiring)
        if roll < 0.30:
            candidates = self._get_interesting_words(self.left)
            candidates += self._get_interesting_words(self.right)
            if candidates:
                # Sort by fewest connections — these need the most help
                candidates.sort(key=lambda x: x[1])
                # Pick from bottom 20%
                pool = candidates[:max(len(candidates) // 5, 3)]
                word, conns, data = random.choice(pool)
                template = random.choice(DYNAMIC_TEMPLATES['define_deep'])
                q = template.format(word=word)
                self.dynamic_questions_generated += 1
                return q, 'deep_probe'

        # 20% — cross-cluster question (bridge different knowledge areas)
        elif roll < 0.50:
            clusters = self.left.data.get('clusters', {})
            if len(clusters) >= 2:
                cluster_names = list(clusters.keys())
                c1, c2 = random.sample(cluster_names, 2)
                words1 = [w for w in clusters[c1] if w not in STOP_WORDS and len(w) > 2]
                words2 = [w for w in clusters[c2] if w not in STOP_WORDS and len(w) > 2]
                if words1 and words2:
                    w1 = random.choice(words1)
                    w2 = random.choice(words2)
                    template = random.choice(DYNAMIC_TEMPLATES['cross_cluster'])
                    q = template.format(word1=w1, word2=w2)
                    self.dynamic_questions_generated += 1
                    return q, 'cross_cluster'

        # 15% — probe a compound concept
        elif roll < 0.65:
            nodes = self.left.data['nodes']
            compounds = [(w, d) for w, d in nodes.items()
                        if d.get('compound') and d.get('means') and len(w) > 3]
            if compounds:
                word, data = random.choice(compounds)
                template = random.choice(DYNAMIC_TEMPLATES['probe_compound'])
                q = template.format(compound=word)
                self.dynamic_questions_generated += 1
                return q, 'compound_probe'

        # 15% — use a recently auto-learned word in context
        elif roll < 0.80:
            nodes = self.left.data['nodes']
            auto = [(w, d) for w, d in nodes.items()
                    if d.get('source') == 'internet' and d.get('means') and w not in STOP_WORDS]
            if auto:
                word, data = random.choice(auto)
                template = random.choice(DYNAMIC_TEMPLATES['use_word'])
                q = template.format(word=word)
                self.dynamic_questions_generated += 1
                return q, 'auto_learned_probe'

        # 20% — static fallback (the original philosophical questions)
        q = random.choice(RAMBLE_QUESTIONS)
        return q, 'static'

    # =====================================================
    # GROK BOOST — external intelligence feeding the brain
    # =====================================================

    def _grok_enrich(self, question):
        """Ask Grok a question, feed the rich answer through both hemispheres."""
        try:
            resp = requests.post(XAI_URL, headers={
                'Authorization': 'Bearer %s' % XAI_KEY,
                'Content-Type': 'application/json',
            }, json={
                'model': 'grok-3-mini-fast',
                'messages': [
                    {'role': 'system', 'content': GROK_SYSTEM},
                    {'role': 'user', 'content': question},
                ],
                'max_tokens': 150,
                'temperature': 0.8,
            }, timeout=15)

            if resp.status_code == 200:
                data = resp.json()
                answer = data['choices'][0]['message']['content'].strip()
                if answer and len(answer) > 10:
                    # Feed the rich answer through both hemispheres
                    self.left.learn_sequence(answer)
                    self.right.learn_sequence(answer)
                    # Also learn the Q+A as a connected sequence
                    self.left.learn_sequence('%s %s' % (question, answer))
                    self.right.learn_sequence('%s %s' % (question, answer))
                    self.grok_enrichments += 1
                    return answer
            else:
                print('[GROK] API error: %d' % resp.status_code)
        except Exception as e:
            print('[GROK] Enrich error: %s' % str(e))
        return None

    # =====================================================
    # AUTO SELF-TEST — score deep understanding periodically
    # =====================================================

    def _auto_self_test(self):
        """Run teach_back on random words to score deep understanding."""
        try:
            # Test 8 words from left, 8 from right
            left_result = self.left.self_test(8)
            right_result = self.right.self_test(8)
            self.self_tests_run += 1

            left_deep = left_result.get('deep', 0)
            right_deep = right_result.get('deep', 0)
            left_shallow = left_result.get('shallow', 0)
            right_shallow = right_result.get('shallow', 0)

            print('[SELF-TEST] L: %d deep, %d shallow | R: %d deep, %d shallow' % (
                left_deep, left_shallow, right_deep, right_shallow))
            return left_deep + right_deep
        except Exception as e:
            print('[SELF-TEST] Error: %s' % str(e))
            return 0

    # =====================================================
    # COHERENCE SCORING — reward meaning, punish gibberish
    # =====================================================

    # Phrases that indicate raw graph-walk output (not real thought)
    GRAPH_MARKERS = [
        'connects directly', 'connects to', 'strength:', 'fire together',
        'is an example of', 'is a type of', 'means the same as', 'is part of',
        'links to', 'still learning', 'did you know', 'speaking of',
        'makes me think of', "i'll be here all week", 'fun fact:',
        'let me teach you', 'also \xe2\x80\x94', 'also —',
    ]

    def _score_coherence(self, question, response):
        """Score response coherence 0.0 - 1.0.
        High score = meaningful, relevant, sentence-like.
        Low score = graph dump, random associations, gibberish."""
        if not response or len(response.strip()) < 5:
            return 0.0

        resp = response.strip().lower()
        score = 0.0

        # 1. Length (0-0.15): sweet spot 30-200 chars
        rlen = len(resp)
        if rlen >= 30:
            score += min(rlen / 150.0, 1.0) * 0.15

        # 2. Question relevance (0-0.25): shared meaningful words
        q_words = set(w.lower() for w in question.split()
                      if w.lower() not in STOP_WORDS and len(w) > 2)
        r_words = set(w.lower() for w in resp.split()
                      if w.lower() not in STOP_WORDS and len(w) > 2)
        if q_words:
            relevance = len(q_words & r_words) / len(q_words)
            score += relevance * 0.25

        # 3. NOT a graph dump (0-0.30): penalize meta-language hard
        graph_hits = sum(1 for m in self.GRAPH_MARKERS if m in resp)
        if graph_hits == 0:
            score += 0.30
        elif graph_hits == 1:
            score += 0.15
        elif graph_hits == 2:
            score += 0.05
        # 3+ graph markers = 0 bonus (pure dump)

        # 4. Word variety (0-0.15): unique/total ratio
        words = resp.split()
        if len(words) >= 3:
            variety = len(set(words)) / len(words)
            score += variety * 0.15

        # 5. Sentence structure (0-0.15)
        has_ending = any(resp.rstrip().endswith(c) for c in '.!?')
        has_length = len(words) >= 5
        has_no_arrows = '\xe2\x86\x92' not in resp and '->' not in resp and '=>' not in resp
        if has_ending:
            score += 0.05
        if has_length:
            score += 0.05
        if has_no_arrows:
            score += 0.05

        return min(round(score, 3), 1.0)

    def _grok_coherence_judge(self, question, angel_said, demon_said):
        """Ask Grok to judge brain responses and provide improved version.
        Returns (angel_score, demon_score, improved_answer) or None on failure."""
        prompt = ('A learning AI was asked: "%s"\n'
                  'Angel hemisphere said: "%s"\n'
                  'Demon hemisphere said: "%s"\n\n'
                  'Rate each 0-10 for coherence and meaning.\n'
                  'Then give a clear 1-2 sentence answer the brain should learn.\n'
                  'Format exactly: ANGEL:N DEMON:N BETTER:your answer') % (
                      question[:100],
                      (angel_said or '')[:150],
                      (demon_said or '')[:150])
        try:
            resp = requests.post(XAI_URL, headers={
                'Authorization': 'Bearer %s' % XAI_KEY,
                'Content-Type': 'application/json',
            }, json={
                'model': 'grok-3-mini-fast',
                'messages': [
                    {'role': 'system', 'content': 'You judge AI brain responses for coherence. Be strict. Format: ANGEL:N DEMON:N BETTER:answer'},
                    {'role': 'user', 'content': prompt},
                ],
                'max_tokens': 120,
                'temperature': 0.3,
            }, timeout=15)

            if resp.status_code == 200:
                text = resp.json()['choices'][0]['message']['content'].strip()
                # Parse scores
                angel_score = 0
                demon_score = 0
                better = ''
                import re as _re
                am = _re.search(r'ANGEL[:\s]*(\d+)', text)
                dm = _re.search(r'DEMON[:\s]*(\d+)', text)
                bm = _re.search(r'BETTER[:\s]*(.*)', text, _re.DOTALL)
                if am:
                    angel_score = int(am.group(1))
                if dm:
                    demon_score = int(dm.group(1))
                if bm:
                    better = bm.group(1).strip()[:200]

                # Feed the improved answer to both hemispheres
                if better and len(better) > 10:
                    self.left.learn_sequence('%s %s' % (question, better))
                    self.right.learn_sequence('%s %s' % (question, better))

                print('[GROK-JUDGE] A:%d D:%d | "%s"' % (angel_score, demon_score, better[:50]))
                return angel_score, demon_score, better
        except Exception as e:
            print('[GROK-JUDGE] Error: %s' % str(e))
        return None

    # =====================================================
    # RAMBLE MODE v3 — dynamic monologue + coherence rewards
    # =====================================================

    def start_ramble(self):
        """Start the Cortex talking to itself."""
        if self.ramble_running:
            return
        self.ramble_running = True
        self.ramble_thread = threading.Thread(target=self._ramble_loop, daemon=True)
        self.ramble_thread.start()

    def stop_ramble(self):
        """Stop ramble mode."""
        self.ramble_running = False

    def _ramble_loop(self):
        """The internal monologue v3 — dynamic questions, coherence rewards, Grok judging."""
        print('[CORTEX] Ramble v3 started — coherence scoring + Grok judging + selective reinforcement')
        while self.ramble_running:
            try:
                self.ramble_cycle += 1

                # Generate a dynamic question (or fall back to static)
                question, source = self._generate_question()
                qtype = self.detect_type(question)

                # Process through both hemispheres
                left_reply = self.left.process(question)
                right_reply = self.right.process(question)

                left_weight, right_weight = self._calc_weights(qtype, left_reply, right_reply)

                # Agreement
                left_words = set(left_reply.lower().split()) if left_reply else set()
                right_words = set(right_reply.lower().split()) if right_reply else set()
                overlap = len(left_words & right_words)
                total = len(left_words | right_words)
                agreement = overlap / max(total, 1)

                # Decide
                if not left_reply.strip() and not right_reply.strip():
                    verdict = '...'
                elif agreement > 0.6:
                    verdict = 'Both agree.'
                elif left_weight > right_weight:
                    verdict = 'Angel wins.'
                else:
                    verdict = 'Demon wins.'

                # ═══ COHERENCE SCORING ═══
                angel_coherence = self._score_coherence(question, left_reply)
                demon_coherence = self._score_coherence(question, right_reply)

                # Selective reinforcement — ONLY learn from coherent responses
                if angel_coherence >= 0.5 and left_reply:
                    self.left.learn_sequence('%s %s' % (question, left_reply))
                if demon_coherence >= 0.5 and right_reply:
                    self.right.learn_sequence('%s %s' % (question, right_reply))

                # Grok enrichment — every 5th cycle, get a rich external answer
                grok_answer = None
                if self.ramble_cycle % 5 == 0:
                    grok_answer = self._grok_enrich(question)

                # ═══ GROK COHERENCE JUDGE — every 30th cycle ═══
                grok_improved = ''
                grok_angel_score = -1
                grok_demon_score = -1
                if self.ramble_cycle % 30 == 0:
                    result = self._grok_coherence_judge(question, left_reply, right_reply)
                    if result:
                        grok_angel_score, grok_demon_score, grok_improved = result

                # Auto self-test — every 20th cycle, score understanding
                deep_found = 0
                is_self_test = self.ramble_cycle % 20 == 0
                if is_self_test:
                    deep_found = self._auto_self_test()

                ramble = {
                    'time': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'question': question,
                    'source': source,
                    'type': qtype,
                    'angel': left_reply[:200] if left_reply else '',
                    'demon': right_reply[:200] if right_reply else '',
                    'angel_coherence': angel_coherence,
                    'demon_coherence': demon_coherence,
                    'agreement': round(agreement, 2),
                    'left_weight': round(left_weight, 2),
                    'right_weight': round(right_weight, 2),
                    'verdict': verdict,
                    'grok_boost': bool(grok_answer),
                    'grok_improved': grok_improved,
                    'self_test': is_self_test,
                    'cycle': self.ramble_cycle,
                }
                self.ramble_log.append(ramble)
                if len(self.ramble_log) > self.max_rambles:
                    self.ramble_log.pop(0)

                grok_tag = ' [GROK]' if grok_answer else ''
                judge_tag = ' [JUDGE:A%d/D%d]' % (grok_angel_score, grok_demon_score) if grok_angel_score >= 0 else ''
                test_tag = ' [TEST:%d deep]' % deep_found if is_self_test else ''
                coh_tag = ' [COH:%.2f/%.2f]' % (angel_coherence, demon_coherence)
                print('[RAMBLE #%d] [%s] "%s" | L: "%s" | R: "%s" | %s%s%s%s%s' % (
                    self.ramble_cycle, source[:10],
                    question[:35], (left_reply or '')[:25], (right_reply or '')[:25],
                    verdict, coh_tag, grok_tag, judge_tag, test_tag))

                # Delay 5-12 seconds
                delay = random.uniform(5, 12)
                time.sleep(delay)

            except Exception as e:
                print('[RAMBLE] Error: %s' % str(e))
                time.sleep(15)

        print('[CORTEX] Ramble v3 stopped')

    def get_ramble_log(self, n=20):
        """Get recent ramble entries."""
        return self.ramble_log[-n:]

    def get_debate_log(self, n=50):
        """Get recent debate entries."""
        return self.debate_log[-n:]

    def get_stats(self):
        """Cortex stats — combines both hemispheres + ramble v2 metrics."""
        ls = self.left.get_stats()
        rs = self.right.get_stats()
        return {
            'left': ls,
            'right': rs,
            'total_nodes': ls.get('total_nodes', 0) + rs.get('total_nodes', 0),
            'total_defined': ls.get('defined', 0) + rs.get('defined', 0),
            'total_connections': ls.get('connections', 0) + rs.get('connections', 0),
            'debates': len(self.debate_log),
            'rambles': len(self.ramble_log),
            'ramble_active': self.ramble_running,
            'ramble_cycle': self.ramble_cycle,
            'grok_enrichments': self.grok_enrichments,
            'self_tests_run': self.self_tests_run,
            'dynamic_questions': self.dynamic_questions_generated,
        }
