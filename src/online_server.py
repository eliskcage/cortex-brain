"""
CORTEX — Split Brain Architecture
Left Hemisphere:  morality, ethics, Bible, beauty, goodness (angel)
Right Hemisphere: mathematics, darkness, ideology, ugliness, hard truths (demon)
Cortex Mind:      the third brain — synthesises both hemispheres, the actual mind

Each hemisphere is a separate CortexBrain instance with its own brain.json.
The CortexMind queries both, weighs their arguments, and produces the real output.
Ramble mode lets the Cortex talk to itself — angel vs demon, live.

Usage: python3 online_server.py
"""
import http.server
import json
import os
import sys
import time
import threading
from pathlib import Path
from collections import defaultdict

PORT = 8643
STUDIO_DIR = Path(__file__).parent
LEFT_DIR = STUDIO_DIR / 'left'
RIGHT_DIR = STUDIO_DIR / 'right'
CORTEX_DIR = STUDIO_DIR / 'cortex'

# Ensure dirs exist
for d in [LEFT_DIR, RIGHT_DIR, CORTEX_DIR]:
    d.mkdir(exist_ok=True)

# Rate limiting
RATE_LIMIT = 30
RATE_WINDOW = 60
rate_tracker = defaultdict(list)
rate_lock = threading.Lock()

# Analysis log
analysis_log = []
analysis_lock = threading.Lock()
MAX_ANALYSIS_LOG = 500

# --- Load both hemispheres + Cortex Mind ---
sys.path.insert(0, str(STUDIO_DIR))
from brain import CortexBrain
from cortex_brain import CortexMind

PINATA_JWT = os.environ.get('PINATA_JWT', 'your-pinata-jwt-here')

print('[CORTEX] Loading LEFT hemisphere (morality, ethics, Bible)...')
left_brain = CortexBrain(str(LEFT_DIR), pinata_jwt=PINATA_JWT, name='Left Hemisphere')
print('[CORTEX] Loading RIGHT hemisphere (logic, darkness, ideology)...')
right_brain = CortexBrain(str(RIGHT_DIR), pinata_jwt=PINATA_JWT, name='Right Hemisphere')
print('[CORTEX] Initialising Cortex Mind (the third brain)...')
cortex = CortexMind(left_brain, right_brain)

# Legacy: keep "brain" pointing to left for backwards compat with trainer
brain = left_brain


def auto_save_loop():
    while True:
        time.sleep(300)
        try:
            cid = left_brain.save_to_ipfs()
            if cid:
                print('[SAVE] Left hemisphere -> IPFS: %s' % cid[:20])
            cid2 = right_brain.save_to_ipfs()
            if cid2:
                print('[SAVE] Right hemisphere -> IPFS: %s' % cid2[:20])
        except Exception as e:
            print('[SAVE] Error: %s' % str(e))


def check_rate(ip):
    now = time.time()
    with rate_lock:
        rate_tracker[ip] = [t for t in rate_tracker[ip] if now - t < RATE_WINDOW]
        if len(rate_tracker[ip]) >= RATE_LIMIT:
            return False
        rate_tracker[ip].append(now)
        return True


def log_for_analysis(ip, user_msg, reply, stats):
    entry = {
        'time': time.strftime('%Y-%m-%d %H:%M:%S'),
        'ip': ip,
        'user': user_msg[:200],
        'reply': reply[:200],
        'nodes': stats.get('total_nodes', 0),
        'defined': stats.get('defined', 0),
        'connections': stats.get('connections', 0),
        'sound': stats.get('dominant_sound', []),
    }
    with analysis_lock:
        analysis_log.append(entry)
        if len(analysis_log) > MAX_ANALYSIS_LOG:
            analysis_log.pop(0)


class OnlineHandler(http.server.SimpleHTTPRequestHandler):

    def do_POST(self):
        client_ip = self.client_address[0]

        # === CORTEX CHAT — the third mind, synthesis of both hemispheres ===
        if self.path == '/api/chat' or self.path == '/api/chat-cortex':
            if not check_rate(client_ip):
                self._json_response({'ok': False, 'error': 'Slow down mate. Too many messages.'}, 429)
                return
            length = int(self.headers.get('Content-Length', 0))
            if length > 4096:
                self._json_response({'ok': False, 'error': 'Message too long'}, 400)
                return
            body = json.loads(self.rfile.read(length))
            user_msg = body.get('text', '').strip()
            if not user_msg:
                self._json_response({'ok': False, 'error': 'No message'})
                return
            if len(user_msg) > 500:
                user_msg = user_msg[:500]

            # CORTEX MIND — queries both hemispheres, synthesises final answer
            reply, debate = cortex.process(user_msg)
            stats = left_brain.get_stats()
            print('[CORTEX] %s | "%s" -> "%s" [%s/%s]' % (
                client_ip, user_msg[:40], (reply or '')[:40],
                debate.get('mode', '?'), debate.get('type', '?')))
            log_for_analysis(client_ip, user_msg, reply or '', stats)
            self._json_response({
                'ok': True, 'reply': reply, 'stats': stats,
                'hemisphere': debate.get('mode', 'unknown'),
                'type': debate.get('type', 'unknown'),
                'agreement': debate.get('agreement', None),
                'winner': debate.get('winner', None),
                'left_weight': debate.get('left_weight', None),
                'right_weight': debate.get('right_weight', None),
            })

        # --- Direct hemisphere chat (for trainers) ---
        elif self.path == '/api/chat-left':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            user_msg = body.get('text', '').strip()
            if not user_msg:
                self._json_response({'ok': False, 'error': 'No message'})
                return
            reply = left_brain.process(user_msg)
            self._json_response({'ok': True, 'reply': reply, 'stats': left_brain.get_stats()})

        elif self.path == '/api/chat-right':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            user_msg = body.get('text', '').strip()
            if not user_msg:
                self._json_response({'ok': False, 'error': 'No message'})
                return
            reply = right_brain.process(user_msg)
            self._json_response({'ok': True, 'reply': reply, 'stats': right_brain.get_stats()})

        elif self.path == '/api/chat-reset':
            left_brain.state = None
            left_brain.teaching_word = None
            right_brain.state = None
            right_brain.teaching_word = None
            self._json_response({'ok': True, 'message': 'All brains reset'})

        # --- Ramble mode controls ---
        elif self.path == '/api/ramble-start':
            cortex.start_ramble()
            self._json_response({'ok': True, 'message': 'Ramble mode started — Cortex is thinking aloud'})

        elif self.path == '/api/ramble-stop':
            cortex.stop_ramble()
            self._json_response({'ok': True, 'message': 'Ramble mode stopped'})

        elif self.path == '/api/ramble-log':
            self._json_response({
                'active': cortex.ramble_running,
                'total': len(cortex.ramble_log),
                'log': cortex.get_ramble_log(30),
            })

        # --- Stats and diagnostics ---
        elif self.path == '/api/brain-stats':
            self._json_response(cortex.get_stats())

        elif self.path == '/api/brain-save':
            cid_l = left_brain.save_to_ipfs()
            cid_r = right_brain.save_to_ipfs()
            self._json_response({'ok': True, 'left_cid': cid_l, 'right_cid': cid_r})

        elif self.path == '/api/brain-knowledge':
            self._json_response(left_brain.dump_knowledge())

        elif self.path == '/api/brain-abilities':
            self._json_response({
                'left': left_brain.check_abilities(),
                'right': right_brain.check_abilities(),
            })

        elif self.path == '/api/brain-live':
            ls = left_brain.get_stats()
            rs = right_brain.get_stats()
            la = left_brain.check_abilities()
            recent_log = left_brain.get_conversation_log(5)
            clusters = left_brain.data.get('clusters', {})
            recycled = left_brain.get_recycled()
            nodes = left_brain.data['nodes']
            recent_words = sorted(
                [(w, v.get('means',''), v.get('source',''), v.get('learned',''))
                 for w, v in nodes.items() if v.get('means') and v.get('learned')],
                key=lambda x: x[3], reverse=True
            )[:10]
            # Right hemisphere recent words
            rnodes = right_brain.data['nodes']
            right_recent = sorted(
                [(w, v.get('means',''), v.get('source',''), v.get('learned',''))
                 for w, v in rnodes.items() if v.get('means') and v.get('learned')],
                key=lambda x: x[3], reverse=True
            )[:10]
            self._json_response({
                'stats': ls,
                'right_stats': rs,
                'cortex_stats': cortex.get_stats(),
                'abilities': {
                    'unlocked': list(la['unlocked'].keys()),
                    'unlocked_details': {k: v['name'] for k, v in la['unlocked'].items()},
                    'locked_progress': {k: {
                        'name': v['name'],
                        'pct': round(sum(p['current']/max(p['needed'],1) for p in v['progress'].values()) / max(len(v['progress']),1) * 100),
                        'reqs': {rk: '%s/%s' % (rv['current'], rv['needed']) for rk, rv in v['progress'].items()}
                    } for k, v in la['locked'].items()},
                },
                'recent_words': [{'word': w, 'means': m[:60], 'source': s, 'learned': l} for w, m, s, l in recent_words],
                'right_recent_words': [{'word': w, 'means': m[:60], 'source': s, 'learned': l} for w, m, s, l in right_recent],
                'recent_chat': [{'user': c.get('user','')[:60], 'response': c.get('response','')[:60], 'time': c.get('time','')} for c in recent_log],
                'clusters': {k: v[:8] for k, v in list(clusters.items())[:10]},
                'recycled': list(recycled.keys()),
                'debates': cortex.get_debate_log(5),
                'ramble': cortex.get_ramble_log(5),
                'ramble_active': cortex.ramble_running,
            })

        elif self.path == '/api/debates':
            self._json_response({
                'total': len(cortex.debate_log),
                'recent': cortex.get_debate_log(50),
            })

        elif self.path == '/api/analysis':
            with analysis_lock:
                self._json_response({
                    'total': len(analysis_log),
                    'log': analysis_log[-100:],
                    'unique_ips': len(set(e['ip'] for e in analysis_log)),
                    'rate_limited_ips': len([ip for ip, times in rate_tracker.items() if len(times) >= RATE_LIMIT]),
                })

        else:
            self.send_response(404)
            self.end_headers()

    def _json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        if '/api/' in str(args[0]) if args else False:
            super().log_message(format, *args)


def main():
    os.chdir(str(STUDIO_DIR))
    ll = sum(1 for v in left_brain.data['nodes'].values() if v.get('means'))
    rl = sum(1 for v in right_brain.data['nodes'].values() if v.get('means'))
    print('[CORTEX] Split Brain Architecture + Cortex Mind')
    print('[CORTEX] LEFT  (angel):   %d nodes, %d defined' % (len(left_brain.data['nodes']), ll))
    print('[CORTEX] RIGHT (demon):   %d nodes, %d defined' % (len(right_brain.data['nodes']), rl))
    print('[CORTEX] MIND:            synthesises both hemispheres')
    print('[CORTEX] Port: %d | Rate limit: %d/%ds' % (PORT, RATE_LIMIT, RATE_WINDOW))
    print()

    threading.Thread(target=auto_save_loop, daemon=True).start()

    # Auto-start ramble mode — the Cortex thinks from boot
    cortex.start_ramble()

    server = http.server.HTTPServer(('0.0.0.0', PORT), OnlineHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n[CORTEX] Shutting down — saving both hemispheres')
        cortex.stop_ramble()
        left_brain.save_to_ipfs()
        right_brain.save_to_ipfs()
        server.shutdown()

if __name__ == '__main__':
    main()
