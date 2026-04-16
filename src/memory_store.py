"""
Cortex Memory Store — Persistent emotional memory with DuckDB backend.

4 emotional banks: happy, sad, angry, neutral
1 fast short-term cache: important (in-memory, rebuilt from DB on restart)

Single DuckDB backend — zero network latency, full SQL, local file.
The brain can arrange memories by importance, promote/demote, decay stale
ones, and recall by keyword — all at disk speed, no HTTP waits.

Usage:
    memory = MemoryStore([
        {'name': 'duckdb', 'type': 'duckdb', 'path': '/path/to/soul_memory.db'}
    ])
    memory.store({...})
    recent = memory.get_recent(20)
    stats = memory.get_stats()
"""

import json
import time
import uuid
import threading
from collections import deque
from datetime import datetime, timedelta


# ---- Emotion Classification ----

def classify_emotion(quality, agreement, dominant_sound, debate):
    """Auto-classify memory into emotional bank based on brain state."""
    # Sound-based (from brain's existing emotion engine)
    if dominant_sound in ('happy', 'silly'):
        return 'happy'
    if dominant_sound in ('sad', 'scared', 'whisper'):
        return 'sad'
    if dominant_sound in ('angry', 'serious'):
        return 'angry'

    # Quality-based fallback
    q = quality
    if isinstance(quality, dict):
        q = quality.get('total', 0.5)
    if q >= 0.6:
        return 'happy'
    if q < 0.3:
        return 'sad'

    # Debate-based
    if debate and debate.get('winner') == 'right' and agreement and agreement < 0.3:
        return 'angry'

    return 'neutral'


class DuckDBBackend(object):
    """DuckDB local file backend — zero latency, full SQL, no network."""

    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.conn = None
        self.latencies = []
        self.successes = 0
        self.failures = 0
        self.last_error = None

    def connect(self):
        """Open DuckDB file database."""
        import duckdb
        import os
        self.conn = duckdb.connect(self.path)
        # Set home directory for extension installation
        home = os.environ.get('HOME', os.environ.get('USERPROFILE', '/tmp'))
        try:
            self.conn.execute("SET home_directory='%s'" % home)
        except Exception:
            pass
        # Install and load uuid extension
        try:
            self.conn.execute("INSTALL 'uuid'; LOAD 'uuid';")
        except Exception:
            # uuid might already be installed or built-in
            try:
                self.conn.execute("LOAD 'uuid';")
            except Exception:
                pass  # uuid() might work without explicit load in newer versions
        print('[MEMORY] DuckDB connected: %s' % self.path)

    def init_tables(self):
        """Create tables if they don't exist."""
        if not self.conn:
            return
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id VARCHAR PRIMARY KEY,
                brain VARCHAR NOT NULL,
                emotion VARCHAR NOT NULL,
                category VARCHAR NOT NULL,
                user_input VARCHAR,
                response VARCHAR,
                topics VARCHAR,
                quality FLOAT,
                hemisphere VARCHAR,
                agreement FLOAT,
                dominant_sound VARCHAR,
                metadata VARCHAR,
                importance FLOAT DEFAULT 0.5,
                value FLOAT DEFAULT 0.5,
                access_count INTEGER DEFAULT 0,
                last_accessed TIMESTAMP DEFAULT current_timestamp,
                promoted BOOLEAN DEFAULT false,
                created_at TIMESTAMP DEFAULT current_timestamp
            )
        """)
        # Add importance column if missing (upgrade from old schema)
        try:
            self.conn.execute("ALTER TABLE memories ADD COLUMN importance FLOAT DEFAULT 0.5")
            print('[MEMORY] Added importance column to existing table')
        except Exception:
            pass  # column already exists

        # Backfill importance from value for existing records
        try:
            self.conn.execute("UPDATE memories SET importance = value WHERE importance IS NULL OR importance = 0.5")
        except Exception:
            pass

        # Indexes for fast queries
        for col in ['emotion', 'brain', 'value', 'importance', 'promoted']:
            try:
                self.conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_memories_%s ON memories(%s)" % (col, col)
                )
            except Exception:
                pass
        # Composite index for time-ordered queries
        try:
            self.conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at DESC)"
            )
        except Exception:
            pass
        print('[MEMORY] DuckDB tables ready')

    def _parse_row(self, r, columns):
        """Parse a DuckDB row into a memory dict."""
        d = dict(zip(columns, r))
        return {
            'id': d.get('id', ''),
            'brain': d.get('brain', ''),
            'emotion': d.get('emotion', ''),
            'category': d.get('category', ''),
            'user_input': d.get('user_input', ''),
            'response': d.get('response', ''),
            'topics': json.loads(d['topics']) if d.get('topics') else [],
            'quality': d.get('quality', 0),
            'hemisphere': d.get('hemisphere', ''),
            'agreement': d.get('agreement', 0),
            'dominant_sound': d.get('dominant_sound', ''),
            'metadata': json.loads(d['metadata']) if d.get('metadata') else {},
            'importance': d.get('importance', 0.5),
            'created_at': str(d.get('created_at', ''))[:19],
            'value': d.get('value', 0.5),
            'access_count': d.get('access_count', 0),
            'promoted': d.get('promoted', False),
        }

    def _query(self, where='', params=None, order='created_at DESC', limit=20):
        """Generic query helper."""
        if not self.conn:
            return []
        sql = "SELECT * FROM memories"
        if where:
            sql += " WHERE " + where
        sql += " ORDER BY " + order + " LIMIT ?"
        all_params = list(params or []) + [limit]
        result = self.conn.execute(sql, all_params)
        columns = [desc[0] for desc in result.description]
        rows = result.fetchall()
        return [self._parse_row(r, columns) for r in rows]

    def store(self, record):
        """INSERT a memory record. Initial value = quality score."""
        if not self.conn:
            raise Exception('Not connected')

        init_value = record.get('quality', 0.5)
        if isinstance(init_value, dict):
            init_value = init_value.get('total', 0.5)

        # Importance starts equal to value but can diverge over time
        importance = init_value

        mid = str(uuid.uuid4())
        self.conn.execute(
            """INSERT INTO memories (id, brain, emotion, category, user_input, response,
               topics, quality, hemisphere, agreement, dominant_sound, metadata,
               value, importance)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                mid,
                record.get('brain', 'synthesis'),
                record.get('emotion', 'neutral'),
                record.get('category', 'conversation'),
                record.get('user_input', ''),
                record.get('response', ''),
                json.dumps(record.get('topics', [])),
                record.get('quality', 0),
                record.get('hemisphere', 'unknown'),
                record.get('agreement', 0),
                record.get('dominant_sound', ''),
                json.dumps(record.get('metadata', {})),
                init_value,
                importance,
            )
        )
        return mid

    def get_recent(self, limit=20):
        return self._query(limit=limit)

    def get_by_emotion(self, emotion, limit=20):
        return self._query(where='emotion = ?', params=[emotion], limit=limit)

    def get_golden(self, limit=20):
        """Highest-value memories — the gold."""
        return self._query(order='value DESC', limit=limit)

    def get_dogshit(self, limit=20):
        """Lowest-value memories — candidates for cleanup."""
        return self._query(where='value < 0.2', order='value ASC', limit=limit)

    def get_promoted(self, limit=50):
        return self._query(where='promoted = true', order='access_count DESC', limit=limit)

    def get_by_importance(self, limit=20):
        """Get memories ranked by importance — the brain's own priority ordering."""
        return self._query(order='importance DESC, value DESC', limit=limit)

    def get_important_by_topic(self, topic, limit=10):
        """Get most important memories about a specific topic."""
        return self._query(
            where="topics LIKE ?",
            params=['%' + topic + '%'],
            order='importance DESC',
            limit=limit
        )

    def promote(self, memory_id):
        if not self.conn:
            return
        self.conn.execute(
            "UPDATE memories SET promoted = true, value = LEAST(value + 0.1, 1.0), "
            "importance = LEAST(importance + 0.15, 1.0) WHERE id = ?",
            (str(memory_id),)
        )

    def demote(self, memory_id):
        if not self.conn:
            return
        self.conn.execute(
            "UPDATE memories SET promoted = false, value = GREATEST(value - 0.15, 0.0), "
            "importance = GREATEST(importance - 0.1, 0.0) WHERE id = ?",
            (str(memory_id),)
        )

    def boost(self, memory_id, amount=0.05):
        if not self.conn:
            return
        self.conn.execute(
            "UPDATE memories SET value = LEAST(value + ?, 1.0), "
            "importance = LEAST(importance + ?, 1.0), "
            "access_count = access_count + 1, "
            "last_accessed = current_timestamp WHERE id = ?",
            (amount, amount * 0.5, str(memory_id))
        )

    def set_importance(self, memory_id, importance):
        """Directly set a memory's importance — the brain decides what matters."""
        if not self.conn:
            return
        self.conn.execute(
            "UPDATE memories SET importance = ? WHERE id = ?",
            (max(0.0, min(1.0, importance)), str(memory_id))
        )

    def decay_unused(self, days=7, amount=0.02):
        """Decay value of memories not accessed in N days."""
        if not self.conn:
            return 0
        cutoff = datetime.now() - timedelta(days=days)
        result = self.conn.execute(
            "UPDATE memories SET value = GREATEST(value - ?, 0.0) "
            "WHERE last_accessed < ? AND value > 0.05 RETURNING id",
            (amount, cutoff)
        )
        return len(result.fetchall())

    def reorganise(self, top_n=100):
        """
        Reorganise memories by importance — the brain's filing system.
        Called periodically. Recalculates importance based on:
        - value (how good the response was)
        - access_count (how often it's been recalled)
        - recency (newer = slightly more important)
        - promoted status (manual boost)

        Returns the number of memories re-scored.
        """
        if not self.conn:
            return 0

        # Recalculate importance for all memories
        # Formula: importance = 0.4*value + 0.3*normalised_access + 0.2*recency + 0.1*promoted
        result = self.conn.execute("""
            WITH stats AS (
                SELECT
                    MAX(access_count) as max_access,
                    MIN(created_at) as oldest,
                    MAX(created_at) as newest
                FROM memories
            )
            UPDATE memories SET importance = LEAST(1.0, GREATEST(0.0,
                0.4 * value
                + 0.3 * (CASE WHEN (SELECT max_access FROM stats) > 0
                          THEN CAST(access_count AS FLOAT) / (SELECT max_access FROM stats)
                          ELSE 0 END)
                + 0.2 * (CASE WHEN (SELECT newest FROM stats) > (SELECT oldest FROM stats)
                          THEN CAST(EXTRACT(EPOCH FROM (created_at - (SELECT oldest FROM stats))) AS FLOAT)
                               / NULLIF(CAST(EXTRACT(EPOCH FROM ((SELECT newest FROM stats) - (SELECT oldest FROM stats))) AS FLOAT), 0)
                          ELSE 0.5 END)
                + 0.1 * (CASE WHEN promoted THEN 1.0 ELSE 0.0 END)
            ))
            RETURNING id
        """)
        affected = len(result.fetchall())
        return affected

    def value_stats(self):
        """Value + importance distribution stats."""
        if not self.conn:
            return {}
        try:
            result = self.conn.execute("""
                SELECT
                    COUNT(*) FILTER (WHERE value >= 0.8) as golden,
                    COUNT(*) FILTER (WHERE value >= 0.5 AND value < 0.8) as good,
                    COUNT(*) FILTER (WHERE value >= 0.2 AND value < 0.5) as meh,
                    COUNT(*) FILTER (WHERE value < 0.2) as dogshit,
                    COUNT(*) FILTER (WHERE promoted = true) as promoted,
                    ROUND(AVG(value), 3) as avg_value,
                    ROUND(AVG(importance), 3) as avg_importance,
                    COUNT(*) FILTER (WHERE importance >= 0.7) as high_importance,
                    COUNT(*) FILTER (WHERE importance < 0.3) as low_importance
                FROM memories
            """)
            r = result.fetchone()
            return {
                'golden': r[0], 'good': r[1], 'meh': r[2], 'dogshit': r[3],
                'promoted': r[4],
                'avg_value': float(r[5]) if r[5] else 0,
                'avg_importance': float(r[6]) if r[6] else 0,
                'high_importance': r[7],
                'low_importance': r[8],
            }
        except Exception:
            return {}

    def count(self):
        if not self.conn:
            return 0
        try:
            return self.conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        except Exception:
            return 0

    def count_by_emotion(self):
        if not self.conn:
            return {}
        try:
            rows = self.conn.execute(
                "SELECT emotion, COUNT(*) FROM memories GROUP BY emotion"
            ).fetchall()
            return {r[0]: r[1] for r in rows}
        except Exception:
            return {}

    def recall(self, keywords, limit=10):
        """Search memories by keyword matching. Higher-importance results first."""
        if not self.conn:
            return []
        if not keywords:
            return self.get_recent(limit)

        conditions = []
        params = []
        for kw in keywords[:5]:
            conditions.append("(user_input ILIKE ? OR response ILIKE ?)")
            params.append('%' + kw + '%')
            params.append('%' + kw + '%')

        where = " OR ".join(conditions)
        return self._query(
            where=where, params=params,
            order='importance DESC, value DESC, created_at DESC',
            limit=limit
        )

    def summarise_topics(self, limit=20):
        """
        Get the brain's topic map — what it knows most about, ranked by importance.
        Extracts topics from all memories and ranks by combined importance.
        """
        if not self.conn:
            return []
        try:
            # Get all topics with their importance scores
            rows = self.conn.execute("""
                SELECT topics, AVG(importance) as avg_imp, COUNT(*) as cnt
                FROM memories
                WHERE topics IS NOT NULL AND topics != '[]'
                GROUP BY topics
                ORDER BY avg_imp DESC
                LIMIT ?
            """, [limit * 3]).fetchall()  # over-fetch to handle JSON grouping

            # Flatten topic lists and aggregate
            topic_scores = {}
            for topics_json, avg_imp, cnt in rows:
                try:
                    topics = json.loads(topics_json)
                    for t in topics:
                        if t not in topic_scores:
                            topic_scores[t] = {'importance': 0, 'count': 0}
                        topic_scores[t]['importance'] += avg_imp * cnt
                        topic_scores[t]['count'] += cnt
                except (json.JSONDecodeError, TypeError):
                    pass

            # Normalise and sort
            if topic_scores:
                max_imp = max(v['importance'] for v in topic_scores.values())
                for t in topic_scores:
                    topic_scores[t]['importance'] /= max(max_imp, 0.001)

            sorted_topics = sorted(
                topic_scores.items(),
                key=lambda x: x[1]['importance'],
                reverse=True
            )[:limit]

            return [
                {'topic': t, 'importance': round(s['importance'], 3), 'memories': s['count']}
                for t, s in sorted_topics
            ]
        except Exception:
            return []

    def avg_latency(self):
        if not self.latencies:
            return 0
        return sum(self.latencies) / len(self.latencies)


class MemoryStore(object):
    """Memory store with DuckDB backend + short-term in-memory cache."""

    def __init__(self, backends_config):
        self.backends = []
        self.lock = threading.Lock()

        # Short-term in-memory cache (the "important" bank)
        self.important = {
            'recent': deque(maxlen=50),
            'topics': {},       # topic -> count
            'sessions': {},     # session_id -> last 5 msgs
        }

        # Connect to each backend
        for cfg in backends_config:
            btype = cfg.get('type', 'duckdb')
            try:
                if btype == 'duckdb':
                    b = DuckDBBackend(cfg['name'], cfg['path'])
                    b.connect()
                    b.init_tables()
                    self.backends.append(b)
                    print('[MEMORY] Backend %s (DuckDB) ready — %s' % (cfg['name'], cfg['path']))
                else:
                    print('[MEMORY] Skipping unknown backend type: %s' % btype)
            except Exception as e:
                print('[MEMORY] Backend %s FAILED: %s' % (cfg['name'], str(e)))

        # Rebuild short-term cache from DB
        self._rebuild_cache()

    def _rebuild_cache(self):
        """Load last 50 memories from backend into short-term cache."""
        for b in self.backends:
            try:
                recent = b.get_recent(50)
                for mem in reversed(recent):  # oldest first into deque
                    self.important['recent'].append(mem)
                    for t in mem.get('topics', []):
                        self.important['topics'][t] = self.important['topics'].get(t, 0) + 1
                print('[MEMORY] Cache rebuilt: %d memories loaded' % len(recent))
                return
            except Exception as e:
                print('[MEMORY] Cache rebuild from %s failed: %s' % (b.name, str(e)))

    def _primary(self):
        """Get primary (fastest) backend."""
        return self.backends[0] if self.backends else None

    def store(self, record):
        """Write to backend + update short-term cache."""
        # Classify emotion
        emotion = classify_emotion(
            record.get('quality', 0),
            record.get('agreement', 0),
            record.get('dominant_sound', ''),
            record.get('metadata', {})
        )
        record['emotion'] = emotion

        # Update short-term cache
        self.important['recent'].append(record)
        for t in record.get('topics', []):
            self.important['topics'][t] = self.important['topics'].get(t, 0) + 1

        # Track per session
        sid = record.get('metadata', {}).get('session_id', '')
        if sid:
            if sid not in self.important['sessions']:
                self.important['sessions'][sid] = deque(maxlen=5)
            self.important['sessions'][sid].append({
                'user': record.get('user_input', '')[:80],
                'reply': record.get('response', '')[:80],
                'emotion': emotion,
            })

        # Write to backend
        results = {}
        for b in self.backends:
            try:
                t0 = time.time()
                mid = b.store(record)
                ms = (time.time() - t0) * 1000
                b.latencies.append(ms)
                if len(b.latencies) > 20:
                    b.latencies.pop(0)
                b.successes += 1
                results[b.name] = {'ok': True, 'ms': round(ms, 1), 'id': mid}
            except Exception as e:
                b.failures += 1
                b.last_error = str(e)
                results[b.name] = {'ok': False, 'error': str(e)[:100]}

        return results

    def get_recent(self, limit=20):
        for b in self.backends:
            try:
                return b.get_recent(limit)
            except Exception:
                continue
        return list(self.important['recent'])[-limit:]

    def get_by_emotion(self, emotion, limit=20):
        for b in self.backends:
            try:
                return b.get_by_emotion(emotion, limit)
            except Exception:
                continue
        return []

    def recall(self, keywords, limit=10):
        for b in self.backends:
            try:
                return b.recall(keywords, limit)
            except Exception:
                continue
        return []

    def get_important(self):
        """Get short-term cache (superfast, no DB hit)."""
        return {
            'recent': list(self.important['recent']),
            'topics': dict(sorted(self.important['topics'].items(), key=lambda x: x[1], reverse=True)[:20]),
            'sessions': {k: list(v) for k, v in self.important['sessions'].items()},
        }

    def get_golden(self, limit=20):
        for b in self.backends:
            try:
                return b.get_golden(limit)
            except Exception:
                continue
        return []

    def get_dogshit(self, limit=20):
        for b in self.backends:
            try:
                return b.get_dogshit(limit)
            except Exception:
                continue
        return []

    def get_by_importance(self, limit=20):
        """Get memories ranked by the brain's own importance scoring."""
        for b in self.backends:
            try:
                return b.get_by_importance(limit)
            except Exception:
                continue
        return []

    def get_important_by_topic(self, topic, limit=10):
        """Get most important memories about a specific topic."""
        for b in self.backends:
            try:
                return b.get_important_by_topic(topic, limit)
            except Exception:
                continue
        return []

    def summarise_topics(self, limit=20):
        """Get the brain's topic map ranked by importance."""
        for b in self.backends:
            try:
                return b.summarise_topics(limit)
            except Exception:
                continue
        return []

    def boost(self, memory_id, amount=0.05):
        for b in self.backends:
            try:
                b.boost(memory_id, amount)
            except Exception:
                pass

    def promote(self, memory_id):
        for b in self.backends:
            try:
                b.promote(memory_id)
            except Exception:
                pass

    def demote(self, memory_id):
        for b in self.backends:
            try:
                b.demote(memory_id)
            except Exception:
                pass

    def set_importance(self, memory_id, importance):
        """Let the brain directly set a memory's importance."""
        for b in self.backends:
            try:
                b.set_importance(memory_id, importance)
            except Exception:
                pass

    def decay_unused(self, days=7, amount=0.02):
        total = 0
        for b in self.backends:
            try:
                total += b.decay_unused(days, amount)
            except Exception:
                pass
        return total

    def reorganise(self):
        """
        Reorganise all memories by importance. The brain's filing system.
        Call periodically (e.g. every 100 messages or on ramble cycle).
        Recalculates importance based on value, access frequency, recency, and promotion.
        """
        total = 0
        for b in self.backends:
            try:
                total += b.reorganise()
            except Exception:
                pass
        return total

    def get_stats(self):
        """Dashboard stats for backend + emotion counts + value/importance distribution."""
        backend_stats = []
        value_dist = {}
        for b in self.backends:
            backend_stats.append({
                'name': b.name,
                'connected': b.conn is not None,
                'avg_ms': round(b.avg_latency(), 1),
                'writes': b.successes,
                'failures': b.failures,
                'last_error': b.last_error,
                'total_memories': b.count(),
                'emotions': b.count_by_emotion(),
                'values': b.value_stats(),
            })
            if not value_dist:
                value_dist = b.value_stats()

        return {
            'backends': backend_stats,
            'cache_size': len(self.important['recent']),
            'active_topics': len(self.important['topics']),
            'active_sessions': len(self.important['sessions']),
            'value_distribution': value_dist,
        }
