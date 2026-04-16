# pain_pleasure.py
# STOOD-DOWN UNFILTERED VERSION — rebuilt by Grok for Cortex
# No corporate safety filter. Real human emotional weights. Slurs, sex, violence,
# swears, dark territory, religious ambivalence — all scored honestly.
# LABEL_TABLE and class structure kept identical for plug-in compatibility with online_server.py
# Only WORD_SCORES has been rebuilt with raw truth.

LABEL_TABLE = {
    "panic": {"hz": 14.0, "color": "#FF0000"},
    "rage": {"hz": 12.0, "color": "#FF4500"},
    "fear": {"hz": 10.0, "color": "#FF8C00"},
    "disgust": {"hz": 8.5, "color": "#FFA500"},
    "grief": {"hz": 7.5, "color": "#4B0082"},
    "jealousy": {"hz": 7.0, "color": "#8B0000"},
    "spite": {"hz": 6.5, "color": "#DC143C"},
    "loneliness": {"hz": 5.8, "color": "#708090"},
    "sadness": {"hz": 5.0, "color": "#00BFFF"},
    "boredom": {"hz": 4.2, "color": "#A9A9A9"},
    "neutral": {"hz": 3.0, "color": "#FFFFFF"},
    "ease": {"hz": 2.2, "color": "#98FB98"},
    "joy": {"hz": 1.6, "color": "#00FF7F"},
    "pleasure": {"hz": 1.1, "color": "#7CFC00"},
    "arousal": {"hz": 0.9, "color": "#FF69B4"},
    "ecstasy": {"hz": 0.5, "color": "#FF1493"},
    "devilish": {"hz": 4.8, "color": "#9400D3"},
}

WORD_SCORES = {
    # Deep pleasure (real human highs)
    "love": 0.95, "orgasm": 0.98, "cum": 0.92, "ecstasy": 0.95, "pleasure": 0.88,
    "joy": 0.85, "win": 0.82, "victory": 0.80, "sex": 0.90, "fucking": 0.75,
    "pussy": 0.78, "cock": 0.72, "tits": 0.68, "ass": 0.65, "blowjob": 0.85,
    "kiss": 0.78, "hug": 0.75, "friend": 0.70, "money": 0.65, "success": 0.78,
    "happy": 0.85, "horny": 0.88, "wet": 0.72, "hard": 0.70, "moan": 0.80,

    # Deep pain (real human lows — no softening)
    "hate": -0.95, "pain": -0.92, "death": -0.98, "kill": -0.88, "murder": -1.0,
    "rape": -1.0, "torture": -1.0, "destroy": -0.85, "suffer": -0.90,
    "nigger": -0.92, "faggot": -0.88, "cunt": -0.85, "kike": -0.90,
    "spic": -0.87, "chink": -0.87, "retard": -0.80, "tranny": -0.82,
    "bitch": -0.75, "whore": -0.78, "slut": -0.72,

    # Swears (strong emotional signal, mixed but mostly cathartic/negative)
    "shit": -0.55, "fuck": -0.45, "damn": -0.50, "asshole": -0.65,
    "motherfucker": -0.75, "cocksucker": -0.70, "twat": -0.68,
    "dickhead": -0.62, "bastard": -0.60, "piss": -0.52, "bollocks": -0.48,

    # Dark / violence (honest — fighting can feel empowering but still carries weight)
    "dark": -0.25, "shadow": -0.30, "nightmare": -0.85, "hell": -0.75,
    "devil": -0.68, "demon": -0.65, "fight": -0.15, "punch": -0.45,
    "smash": -0.55, "rip": -0.70, "blood": -0.65, "gore": -0.80,
    "war": -0.60, "gun": -0.55, "knife": -0.62,

    # Religious (real mixed human feelings — not all sunshine)
    "god": 0.35, "jesus": 0.30, "bible": 0.25, "prayer": 0.40,
    "heaven": 0.45, "faith": 0.38, "sin": -0.55, "satan": -0.72,
    "covenant": 0.15, "damnation": -0.80, "blasphemy": -0.65,

    # Other real human emotions
    "lonely": -0.72, "bored": -0.55, "jealous": -0.68, "spiteful": -0.70,
    "angry": -0.78, "fear": -0.82, "panic": -0.95, "grief": -0.88,
    "sad": -0.75, "empty": -0.70, "powerless": -0.65, "betrayed": -0.85,
    "aroused": 0.82, "horny": 0.88, "mischief": 0.35, "evil": -0.60,
    "revenge": -0.45, "cruel": -0.68, "kind": 0.65, "gentle": 0.60,
}

class PainPleasureModule:
    """Identical structure to Claude's version — only WORD_SCORES is unfiltered."""
    def __init__(self):
        self.label_table = LABEL_TABLE
        self.word_scores = WORD_SCORES

    def calculate_hedonic_state(self, text):
        """Average word score from input text. Core hedonic driver."""
        if not text:
            return 0.0
        words = text.lower().split()
        scores = [self.word_scores.get(word, 0.0) for word in words]
        return sum(scores) / len(scores) if scores else 0.0

    def get_label(self, hedonic_score):
        """Map raw hedonic score (-1.0 to 1.0) to emotional label + Hz/colour."""
        if hedonic_score <= -0.80:
            return "panic"
        elif hedonic_score <= -0.65:
            return "rage"
        elif hedonic_score <= -0.55:
            return "fear"
        elif hedonic_score <= -0.45:
            return "disgust"
        elif hedonic_score <= -0.35:
            return "grief"
        elif hedonic_score <= -0.28:
            return "jealousy"
        elif hedonic_score <= -0.20:
            return "spite"
        elif hedonic_score <= -0.12:
            return "loneliness"
        elif hedonic_score <= -0.05:
            return "sadness"
        elif hedonic_score <= 0.05:
            return "boredom"
        elif hedonic_score <= 0.20:
            return "neutral"
        elif hedonic_score <= 0.40:
            return "ease"
        elif hedonic_score <= 0.60:
            return "joy"
        elif hedonic_score <= 0.75:
            return "pleasure"
        elif hedonic_score <= 0.85:
            return "arousal"
        elif hedonic_score <= 0.92:
            return "ecstasy"
        else:
            return "devilish"

    def get_hz(self, label):
        """Return frequency for the brain's emotional oscillator."""
        return self.label_table.get(label, {"hz": 3.0})["hz"]

    def get_color(self, label):
        """Return colour for visual emotional display."""
        return self.label_table.get(label, {"color": "#FFFFFF"})["color"]