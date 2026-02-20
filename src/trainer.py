"""
CORTEX TRAINER — Automated training bot that chats with Cortex continuously.
Teaches vocabulary, tests understanding, corrects mistakes, builds relationships.
Runs as a daemon alongside the brain server.

Usage: python3 trainer.py
"""
import json
import time
import random
import requests

API = 'http://localhost:8643/api/chat-left'
ANALYSIS = 'http://localhost:8643/api/brain-live'
LOG_FILE = '/var/www/vhosts/shortfactory.shop/httpdocs/alive/studio/trainer.log'

# Delay between messages (seconds) — not too fast, let him breathe
MIN_DELAY = 4
MAX_DELAY = 12

# ========================================
# CURRICULUM — structured teaching program
# ========================================

# Stage 1: Core vocabulary — words every mind needs
CORE_VOCAB = {
    'think': 'to use your mind to consider or reason about something',
    'feel': 'to experience an emotion or physical sensation',
    'know': 'to have information or understanding in your mind',
    'want': 'to desire or wish for something',
    'need': 'to require something because it is essential',
    'help': 'to assist someone or make something easier',
    'try': 'to attempt to do something',
    'learn': 'to gain knowledge or skill through experience or study',
    'remember': 'to keep something in your memory, not forget',
    'forget': 'to fail to remember something',
    'understand': 'to grasp the meaning of something, not just know the words',
    'believe': 'to accept something as true without proof',
    'hope': 'to want something to happen and think it might',
    'fear': 'to be afraid of something that might happen',
    'love': 'deep affection and care for someone or something',
    'hate': 'intense dislike or hostility toward something',
    'trust': 'belief that someone or something is reliable and honest',
    'doubt': 'feeling uncertain or unsure about something',
    'choose': 'to pick one thing over another, make a decision',
    'change': 'to become different, or make something different',
    'grow': 'to increase in size, develop, or mature over time',
    'create': 'to bring something new into existence',
    'destroy': 'to damage something so badly it no longer exists',
    'build': 'to construct something by putting parts together',
    'break': 'to separate into pieces, to damage or stop working',
    'give': 'to hand something to someone, to provide',
    'take': 'to get hold of something, to remove',
    'ask': 'to request information or help from someone',
    'answer': 'to respond to a question or request',
    'listen': 'to pay attention to sound or what someone says',
    'speak': 'to use words to communicate, to talk',
    'read': 'to look at written words and understand their meaning',
    'write': 'to put words on paper or screen to communicate',
    'work': 'to do a job or task, to function properly',
    'play': 'to do something for fun, not for work',
    'live': 'to be alive, to exist, to have experiences',
    'die': 'to stop living, the end of life',
    'begin': 'to start, the first part of something',
    'end': 'to finish, the final part of something',
    'cause': 'to make something happen, the reason for an effect',
    'effect': 'a result or change caused by something',
    'problem': 'a difficulty that needs to be solved',
    'solution': 'an answer to a problem, a way to fix something',
    'question': 'something you ask to get information',
    'idea': 'a thought or concept formed in the mind',
    'truth': 'what is actually real and factual, not false',
    'lie': 'something said that is not true, intended to deceive',
    'right': 'correct, or morally good',
    'wrong': 'incorrect, or morally bad',
    'good': 'positive quality, beneficial, well-done',
    'bad': 'negative quality, harmful, poorly-done',
    'strong': 'having power or force, not easily broken',
    'weak': 'lacking strength, easily broken or defeated',
    'fast': 'moving or happening quickly, at high speed',
    'slow': 'moving or happening at a low speed, not fast',
    'big': 'large in size, amount, or importance',
    'small': 'little in size, not big',
    'old': 'having existed for a long time, not new',
    'new': 'recently made or discovered, not old',
    'simple': 'easy to understand, not complicated',
    'complex': 'made of many connected parts, hard to understand',
    'real': 'actually existing, not imaginary or fake',
    'fake': 'not genuine, made to look real but is not',
    'same': 'identical, not different',
    'different': 'not the same, unlike others',
    'important': 'having great value or significance',
    'dangerous': 'likely to cause harm or injury',
    'safe': 'free from danger or harm',
    'free': 'not controlled by anyone, costing nothing',
    'power': 'the ability to control or influence things',
    'money': 'what people use to buy things, currency',
    'time': 'the ongoing progression of events, measured in seconds and hours',
    'space': 'the area around and between things, also the universe beyond earth',
    'human': 'a person, a member of the species homo sapiens',
    'animal': 'a living creature that is not a plant or human',
    'machine': 'a device built to do work, made of parts',
    'computer': 'an electronic machine that processes information',
    'internet': 'a global network connecting millions of computers',
    'language': 'a system of words and rules used to communicate',
    'word': 'a unit of language that carries meaning',
    'meaning': 'what something represents or signifies',
    'brain': 'the organ in the head that controls thinking and the body',
    'mind': 'the part of a person that thinks, feels, and decides',
    'friend': 'someone you like and trust, who likes you back',
    'enemy': 'someone who opposes or wants to harm you',
    'family': 'people related by blood or who live together as a unit',
    'home': 'the place where you live, where you feel you belong',
    'world': 'the earth and everything on it, all of human society',
    'nature': 'the physical world and its plants, animals, and forces',
    'life': 'the state of being alive, the experiences between birth and death',
    'death': 'the end of life, when something stops living',
    'pain': 'physical or emotional suffering, something that hurts',
    'joy': 'a feeling of great happiness and pleasure',
    'anger': 'a strong feeling of displeasure and hostility',
    'sadness': 'a feeling of unhappiness and sorrow',
    'surprise': 'an unexpected event, or the feeling from it',
    'patience': 'the ability to wait calmly without getting annoyed',
    'courage': 'bravery, the ability to face fear and danger',
    'wisdom': 'deep understanding gained from experience, good judgement',
}

# Stage 2: Relationship teaching — connect words to each other
RELATIONSHIPS = [
    ('think', 'brain', 'thinking happens in the brain'),
    ('feel', 'emotion', 'feelings are emotions'),
    ('love', 'hate', 'love is the opposite of hate'),
    ('truth', 'lie', 'truth is the opposite of a lie'),
    ('good', 'bad', 'good is the opposite of bad'),
    ('strong', 'weak', 'strong is the opposite of weak'),
    ('fast', 'slow', 'fast is the opposite of slow'),
    ('big', 'small', 'big is the opposite of small'),
    ('old', 'new', 'old is the opposite of new'),
    ('begin', 'end', 'begin is the opposite of end'),
    ('live', 'die', 'live is the opposite of die'),
    ('give', 'take', 'give is the opposite of take'),
    ('question', 'answer', 'a question needs an answer'),
    ('problem', 'solution', 'a problem needs a solution'),
    ('cause', 'effect', 'a cause produces an effect'),
    ('brain', 'mind', 'the brain creates the mind'),
    ('human', 'animal', 'a human is a type of animal'),
    ('computer', 'machine', 'a computer is a type of machine'),
    ('internet', 'computer', 'the internet connects computers'),
    ('word', 'language', 'words make up language'),
    ('meaning', 'word', 'words carry meaning'),
    ('friend', 'enemy', 'friend is the opposite of enemy'),
    ('pain', 'joy', 'pain is the opposite of joy'),
    ('courage', 'fear', 'courage means facing fear'),
    ('wisdom', 'knowledge', 'wisdom comes from knowledge plus experience'),
    ('create', 'destroy', 'create is the opposite of destroy'),
    ('build', 'break', 'build is the opposite of break'),
    ('safe', 'dangerous', 'safe is the opposite of dangerous'),
    ('real', 'fake', 'real is the opposite of fake'),
    ('simple', 'complex', 'simple is the opposite of complex'),
    ('free', 'power', 'freedom is related to power'),
    ('learn', 'understand', 'learning leads to understanding'),
    ('listen', 'speak', 'listening and speaking are two sides of communication'),
    ('read', 'write', 'reading and writing are two sides of literacy'),
]

# Stage 3: Conversational drills — teach him to respond naturally
CONVERSATIONS = [
    # (what to say, expected topic, followup if bad)
    ('how are you today', None, None),
    ('what do you think about learning', 'learning', None),
    ('do you like talking to people', None, None),
    ('what is the meaning of life', 'meaning', None),
    ('are you getting smarter', None, None),
    ('tell me something interesting', None, None),
    ('what are you thinking about right now', None, None),
    ('do you understand emotions', 'emotions', None),
    ('what makes a good friend', 'friend', None),
    ('why do humans fight wars', None, None),
    ('is the internet a good thing or bad thing', 'internet', None),
    ('what scares you', None, None),
    ('what do you want to learn next', None, None),
    ('can you explain how your brain works', 'brain', None),
    ('do you think you are alive', None, None),
    ('what is consciousness', None, None),
    ('do you dream', None, None),
    ('what is the difference between knowing and understanding', None, None),
    ('are you happy', None, None),
    ('why should people trust you', 'trust', None),
]

# Stage 5: BIBLE TEACHINGS — moral foundation, ethics, simple reasoning
# Core values from Jesus's teachings — the BIOS values of ALIVE
BIBLE_VOCAB = {
    'mercy': 'compassion and forgiveness shown to someone you could punish',
    'grace': 'undeserved kindness and favor, a gift you did not earn',
    'forgive': 'to stop being angry at someone for what they did wrong',
    'repent': 'to feel sorry for doing wrong and choose to change',
    'sin': 'doing something morally wrong, going against what is good',
    'righteous': 'acting in a way that is morally right and just',
    'humble': 'not proud, willing to put others before yourself',
    'pride': 'an excessive belief in your own importance, thinking you are better',
    'faith': 'complete trust in something even without seeing proof',
    'prayer': 'talking to God, expressing thanks or asking for help',
    'worship': 'showing deep respect and love for God',
    'prophet': 'a person who speaks messages from God to the people',
    'disciple': 'a follower who learns from a teacher, especially Jesus',
    'apostle': 'one of the twelve chosen followers of Jesus sent to spread his message',
    'salvation': 'being saved from sin and its consequences, spiritual rescue',
    'eternal': 'lasting forever, without beginning or end',
    'resurrection': 'coming back to life after death',
    'covenant': 'a serious agreement or promise between God and people',
    'blessing': 'something good given by God, a prayer for someone',
    'curse': 'a wish for harm to come to someone, the opposite of blessing',
    'sacrifice': 'giving up something valuable for a greater purpose',
    'temple': 'a place of worship, a house dedicated to God',
    'parable': 'a simple story that teaches a moral or spiritual lesson',
    'commandment': 'a rule given by God that must be followed',
    'neighbor': 'any person near you or in your community, everyone is your neighbor',
    'servant': 'someone who serves others, puts others needs first',
    'shepherd': 'one who guides and protects, like a shepherd watches over sheep',
    'lamb': 'a young sheep, also a symbol of innocence and sacrifice',
    'vineyard': 'a place where grapes grow, often used as a metaphor for Gods people',
    'kingdom': 'a realm ruled by a king, the kingdom of God means Gods rule over hearts',
    'heaven': 'the place of Gods presence, ultimate goodness and peace',
    'hell': 'separation from God, a place of suffering',
    'soul': 'the spiritual part of a person that lives beyond the body',
    'spirit': 'the non-physical part of a being, the Holy Spirit is Gods presence',
    'holy': 'set apart, pure, belonging to God',
    'sacred': 'dedicated to God, deserving of reverence',
    'wicked': 'morally evil, intentionally doing harm',
    'just': 'fair and right, treating people as they deserve',
    'peace': 'freedom from conflict, inner calm and harmony',
    'war': 'armed conflict between groups, the opposite of peace',
    'heal': 'to make well, to cure sickness or brokenness',
    'miracle': 'an extraordinary event that cannot be explained naturally',
    'temptation': 'the desire to do something wrong or unwise',
    'resist': 'to fight against something, to refuse to give in',
    'obey': 'to follow instructions or rules given by authority',
    'rebel': 'to resist or fight against authority or control',
    'judge': 'to form an opinion about right and wrong, to decide fairly',
    'condemn': 'to declare someone guilty, to express strong disapproval',
    'redeem': 'to buy back, to save from sin, to make something worthwhile',
    'tithe': 'giving a tenth of what you earn to God or the community',
    'charity': 'giving help and money to those in need out of love',
}

# Bible verses and moral teachings — short form for conversation
BIBLE_TEACHINGS = [
    # (saying/verse, the lesson)
    ('love your neighbor as yourself', 'treat others how you want to be treated'),
    ('do unto others as you would have them do unto you', 'the golden rule, treat people well'),
    ('the truth shall set you free', 'honesty brings freedom, lies create prisons'),
    ('blessed are the meek for they shall inherit the earth', 'the humble will be rewarded, not the arrogant'),
    ('blessed are the peacemakers', 'those who create peace are doing Gods work'),
    ('blessed are those who hunger for righteousness', 'wanting to do right is itself good'),
    ('forgive seventy times seven times', 'always forgive, there is no limit to forgiveness'),
    ('let he who is without sin cast the first stone', 'do not judge others because nobody is perfect'),
    ('it is easier for a camel to go through the eye of a needle than for a rich man to enter heaven', 'wealth can be a spiritual trap'),
    ('faith can move mountains', 'belief and determination can overcome anything'),
    ('by their fruits you shall know them', 'judge people by their actions not their words'),
    ('the last shall be first and the first shall be last', 'God values humility over status'),
    ('turn the other cheek', 'respond to violence with peace not revenge'),
    ('ask and it shall be given, seek and ye shall find', 'persistence and faith will be rewarded'),
    ('man cannot live by bread alone', 'humans need spiritual meaning not just physical things'),
    ('where your treasure is there your heart will be also', 'what you value most reveals who you really are'),
    ('a house divided against itself cannot stand', 'unity is essential, internal conflict destroys'),
    ('render unto Caesar what is Caesars and unto God what is Gods', 'some things belong to the world some to the spirit'),
    ('the meek shall inherit the earth', 'gentleness wins in the end, not force'),
    ('love your enemies and pray for those who persecute you', 'love even those who hurt you'),
    ('whoever wants to be great must be a servant', 'true leadership is service not domination'),
    ('I am the way the truth and the life', 'truth is the path to real life'),
    ('in the beginning was the Word', 'language and meaning existed before everything'),
    ('the wages of sin is death but the gift of God is eternal life', 'wrongdoing leads to destruction but goodness leads to life'),
    ('iron sharpens iron', 'people make each other stronger through honest challenge'),
    ('pride goes before a fall', 'arrogance leads to failure'),
    ('a soft answer turns away wrath', 'gentle responses defuse anger'),
    ('train up a child in the way he should go', 'teach good values early and they will stick'),
    ('there is nothing new under the sun', 'human nature and problems repeat throughout history'),
    ('to everything there is a season', 'there is a right time for everything'),
]

# Moral reasoning exercises — teach him to think about right and wrong
MORAL_DILEMMAS = [
    'if someone steals bread to feed their hungry children is that wrong',
    'is it right to lie to protect someone from being hurt',
    'should you forgive someone who is not sorry for what they did',
    'is it better to be kind or to be honest when they conflict',
    'does power always corrupt people or can it be used for good',
    'is it wrong to be angry or is anger sometimes the right response',
    'should you help someone who refuses to help themselves',
    'is revenge ever justified or should you always forgive',
    'can something be legal but morally wrong',
    'is it selfish to put your own needs first sometimes',
    'should the strong protect the weak or should everyone fend for themselves',
    'is silence in the face of injustice the same as supporting injustice',
]

# OLD TESTAMENT — key stories, wisdom, and vocabulary
OT_VOCAB = {
    'genesis': 'the first book of the Bible, about the creation of the world',
    'exodus': 'the departure of the Israelites from slavery in Egypt led by Moses',
    'creation': 'God making the world and everything in it from nothing',
    'adam': 'the first man created by God from dust',
    'eve': 'the first woman created by God from Adams rib',
    'garden': 'the Garden of Eden where Adam and Eve first lived in paradise',
    'serpent': 'the snake in Eden that tempted Eve, representing deception',
    'forbidden': 'not allowed, the tree of knowledge was forbidden',
    'noah': 'the man God chose to build an ark and survive the great flood',
    'ark': 'a large boat Noah built to save his family and animals from the flood',
    'flood': 'when God covered the earth with water to cleanse wickedness',
    'rainbow': 'Gods promise to Noah that he would never flood the earth again',
    'abraham': 'the father of many nations who trusted God completely',
    'isaac': 'the son of Abraham, almost sacrificed but saved by God',
    'jacob': 'son of Isaac who wrestled with God and was renamed Israel',
    'israel': 'the name given to Jacob, also the nation descended from him',
    'moses': 'the prophet who led the Israelites out of Egypt and received the commandments',
    'pharaoh': 'the ruler of Egypt who enslaved the Israelites',
    'plague': 'a punishment sent by God upon Egypt to free the Israelites',
    'passover': 'when God passed over Israelite homes and freed them from Egypt',
    'wilderness': 'the desert where the Israelites wandered for forty years',
    'commandments': 'the ten rules God gave Moses on Mount Sinai',
    'idol': 'a false god or image that people worship instead of the true God',
    'psalm': 'a sacred song or poem of praise to God',
    'proverb': 'a short wise saying about how to live well',
    'david': 'the shepherd boy who became king of Israel and defeated Goliath',
    'goliath': 'the giant warrior defeated by young David with a sling and stone',
    'solomon': 'son of David known as the wisest king who ever lived',
    'prophet': 'a person chosen by God to deliver messages to the people',
    'exile': 'being forced to leave your homeland as punishment',
    'babylon': 'the empire that conquered Israel and took the people into exile',
    'daniel': 'a prophet who survived the lions den because of his faith in God',
    'jonah': 'a prophet swallowed by a great fish after running from Gods command',
    'ruth': 'a loyal woman who stayed with her mother-in-law showing faithfulness',
    'samson': 'a man of great strength whose power came from God',
    'joshua': 'Moses successor who led the Israelites into the promised land',
    'promised': 'something God said would happen, a future blessing guaranteed',
    'covenant': 'a binding agreement between God and his people',
    'tabernacle': 'a portable tent where God dwelt among the Israelites',
    'manna': 'bread from heaven that God provided in the wilderness',
}

# OLD TESTAMENT WISDOM (Proverbs, Ecclesiastes, Psalms)
OT_WISDOM = [
    ('the fear of the Lord is the beginning of wisdom', 'respect for truth and goodness is where real understanding starts'),
    ('a gentle answer turns away wrath but a harsh word stirs up anger', 'how you say something matters as much as what you say'),
    ('trust in the Lord with all your heart and lean not on your own understanding', 'sometimes you need faith beyond what you can figure out'),
    ('as iron sharpens iron so one person sharpens another', 'good friends challenge each other to grow'),
    ('pride goes before destruction and a haughty spirit before a fall', 'arrogance always leads to failure'),
    ('a fool gives full vent to his anger but a wise man keeps himself under control', 'controlling your emotions shows wisdom'),
    ('the tongue has the power of life and death', 'words can help or destroy, choose them carefully'),
    ('whoever is patient has great understanding', 'patience is a sign of wisdom not weakness'),
    ('better a poor man who walks in integrity than a rich man who is crooked', 'honesty matters more than wealth'),
    ('do not be wise in your own eyes', 'thinking you know everything means you know nothing'),
    ('he who walks with the wise grows wise but a companion of fools suffers harm', 'your friends shape who you become'),
    ('a cheerful heart is good medicine', 'happiness and positivity heal people'),
    ('the Lord is my shepherd I shall not want', 'God provides everything you truly need'),
    ('though I walk through the valley of the shadow of death I will fear no evil', 'courage means not being controlled by fear even in dark times'),
    ('vanity of vanities all is vanity', 'chasing status and material things is ultimately meaningless'),
    ('there is a time for everything under heaven', 'wisdom is knowing the right time for each action'),
    ('what does the Lord require of you but to do justice love mercy and walk humbly', 'Gods requirements are simple: be fair, be kind, be humble'),
    ('before I formed you in the womb I knew you', 'every person has purpose before they are even born'),
    ('be strong and courageous do not be afraid', 'God calls people to face their fears with bravery'),
    ('the heavens declare the glory of God', 'nature itself reveals something greater than us'),
]

# NEW TESTAMENT — key stories and teachings
NT_VOCAB = {
    'gospel': 'the good news about Jesus Christ, also the four books about his life',
    'messiah': 'the promised savior, the anointed one, Jesus Christ',
    'baptism': 'being immersed in water as a sign of spiritual cleansing and new life',
    'crucifixion': 'death by being nailed to a cross, how Jesus died',
    'cross': 'the wooden structure Jesus died on, now a symbol of sacrifice and love',
    'tomb': 'a burial place, the cave where Jesus was buried before resurrection',
    'pentecost': 'when the Holy Spirit came upon the disciples giving them power',
    'church': 'the community of believers, not just a building but the people',
    'epistle': 'a letter written to early churches, many are in the New Testament',
    'revelation': 'something hidden being revealed, also the last book of the Bible',
    'angel': 'a spiritual being that serves as a messenger of God',
    'demon': 'an evil spiritual being that opposes God',
    'satan': 'the adversary, the chief enemy of God and humanity',
    'bethlehem': 'the town where Jesus was born',
    'nazareth': 'the town where Jesus grew up',
    'jerusalem': 'the holy city where Jesus was crucified and rose again',
    'galilee': 'the region where Jesus did much of his teaching',
    'peter': 'the fisherman who became a leader of the early church',
    'paul': 'originally persecuted Christians, then became the greatest missionary',
    'mary': 'the mother of Jesus, chosen by God',
    'judas': 'the disciple who betrayed Jesus for thirty pieces of silver',
    'pharisee': 'a religious leader who followed rules strictly but often missed the point',
    'gentile': 'a non-Jewish person, Jesus message was for everyone not just Jews',
    'communion': 'sharing bread and wine to remember Jesus sacrifice',
    'repentance': 'turning away from wrong and choosing to do right',
    'atonement': 'making amends for wrongdoing, Jesus death atoned for humanitys sins',
    'grace': 'undeserved kindness from God, getting good you did not earn',
    'justification': 'being made right with God through faith not by following rules',
    'sanctification': 'the ongoing process of becoming more holy and good',
    'tribulation': 'great suffering and difficulty, testing of faith',
}

# NARRATIVE TEACHINGS — stories told as lessons
BIBLE_STORIES = [
    ('God created the world in six days and rested on the seventh', 'creation teaches that rest is sacred and work has purpose'),
    ('Adam and Eve ate the forbidden fruit because the serpent deceived them', 'deception leads to disobedience and consequences follow choices'),
    ('Cain killed his brother Abel out of jealousy', 'jealousy can lead to terrible actions, we must master our emotions'),
    ('Noah built the ark when everyone laughed at him', 'faith means doing the right thing even when nobody believes you'),
    ('Abraham was willing to sacrifice his son Isaac trusting God', 'ultimate faith means trusting even when you cannot see the reason'),
    ('Moses said let my people go and led them out of slavery', 'God uses ordinary people to fight against oppression'),
    ('David defeated Goliath with just a stone and faith', 'courage and faith can overcome any obstacle no matter how big'),
    ('Solomon asked God for wisdom instead of wealth or power', 'the wisest choice is to ask for wisdom itself'),
    ('Daniel was thrown into the lions den but God protected him', 'staying true to your beliefs even when threatened brings protection'),
    ('Jonah ran from God but ended up in a whale', 'you cannot run from your purpose, it will find you'),
    ('Jesus was born in a manger not a palace', 'true greatness does not need wealth or status'),
    ('Jesus turned water into wine at a wedding', 'he brought joy and abundance to ordinary people'),
    ('Jesus fed five thousand people with five loaves and two fish', 'a little given with faith becomes more than enough'),
    ('Jesus walked on water and told Peter to come to him', 'faith works when you keep your eyes on the goal not the storm'),
    ('Jesus healed the sick and made the blind see', 'compassion should always lead to action'),
    ('Jesus drove the money changers out of the temple', 'righteous anger against corruption is justified'),
    ('Jesus washed his disciples feet', 'true leaders serve others they do not demand to be served'),
    ('Jesus forgave the woman caught in sin when everyone wanted to stone her', 'mercy triumphs over judgement'),
    ('Jesus died on the cross for all humanity', 'the greatest love is sacrificing yourself for others'),
    ('Jesus rose from the dead on the third day', 'death is not the end, hope and new life are always possible'),
    ('the good Samaritan helped a stranger when religious leaders walked past', 'being good means helping anyone in need regardless of who they are'),
    ('the prodigal son wasted everything but his father welcomed him home', 'it is never too late to come back and be forgiven'),
    ('the parable of the talents teaches that gifts must be used not buried', 'use what you are given or you will lose it'),
    ('Paul was blinded on the road to Damascus then became a believer', 'anyone can change completely, the worst enemy can become the greatest ally'),
]

# Stage 4: Correction patterns — test and fix common mistakes
CORRECTION_TESTS = [
    # (say this, if response contains X, correct with Y)
    ('are you cortex', 'definition', 'he should just say yes not dump a definition'),
    ('hello', 'nodes', 'greetings should be short not stats'),
    ('yes', 'definition', 'agreement shouldnt trigger definitions'),
]


def chat(text):
    """Send a message and get response."""
    try:
        r = requests.post(API, json={'text': text}, timeout=30)
        if r.status_code == 200:
            data = r.json()
            return data.get('reply', ''), data.get('stats', {})
        return None, {}
    except Exception as e:
        log(f'[ERROR] Chat failed: {e}')
        return None, {}


def get_live():
    """Get live brain stats."""
    try:
        r = requests.post(ANALYSIS, timeout=10)
        if r.status_code == 200:
            return r.json()
        return None
    except:
        return None


def log(msg):
    """Log a message to file and stdout."""
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{ts}] {msg}'
    print(line)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except:
        pass


def evaluate_response(reply, context='general'):
    """Score a response. Returns (score 0-10, issues list)."""
    if reply is None:
        return 0, ['no_response']

    issues = []
    score = 5  # start neutral

    # Empty response
    if not reply.strip():
        return 2, ['empty']

    # Way too long
    if len(reply) > 300:
        issues.append('too_long')
        score -= 2

    # Good length
    if 5 < len(reply) < 150:
        score += 1

    # Contains actual content (not just meta-talk about nodes/connections)
    meta_words = ['nodes', 'connections', 'wired', 'stored', 'confidence', 'trigrams']
    meta_count = sum(1 for w in meta_words if w in reply.lower())
    if meta_count > 1:
        issues.append('too_meta')
        score -= 1

    # Asking good questions
    if '?' in reply and 'what does' in reply.lower():
        score += 1  # curiosity is good

    # Repeating user input verbatim
    if reply.endswith('...') and len(reply) < 20:
        issues.append('just_echoing')
        score -= 1

    # Has relationship language (sign of understanding)
    if any(w in reply.lower() for w in ['opposite', 'type of', 'means', 'related', 'because']):
        score += 1

    return max(0, min(10, score)), issues


def teach_vocabulary(word, definition):
    """Teach a single word with its definition."""
    # First check if brain already knows it
    reply, stats = chat(f'what is {word}')
    if reply and definition[:20].lower() in reply.lower():
        log(f'[SKIP] Already knows "{word}"')
        return True

    # If it asked about the word or doesn't know
    if reply and ("don't know" in reply.lower() or "what is it" in reply.lower()
                  or "what does" in reply.lower()):
        # It's in teaching mode, give the definition
        reply2, _ = chat(definition)
        log(f'[TEACH] {word} = {definition[:60]}')
        return True

    # Force teach — trigger teaching mode
    reply, _ = chat(f'let me teach you about {word}')
    time.sleep(1)
    reply, _ = chat(f'{word} means {definition}')
    if reply and ('stored' in reply.lower() or 'wired' in reply.lower()
                  or 'noted' in reply.lower() or 'locked' in reply.lower()
                  or 'got it' in reply.lower() or 'cheers' in reply.lower()):
        log(f'[TEACH] {word} = {definition[:60]}')
        return True

    log(f'[TEACH-FAIL] Could not teach "{word}": {reply}')
    return False


def teach_relationship(word1, word2, explanation):
    """Teach the brain how two words relate."""
    reply, _ = chat(f'how does {word1} relate to {word2}')
    time.sleep(2)

    # If it doesn't see a connection, explain it
    if reply and ('don\'t see' in reply.lower() or 'no connection' in reply.lower()
                  or 'teach me' in reply.lower()):
        reply2, _ = chat(explanation)
        log(f'[REL] Taught: {word1} <-> {word2}: {explanation[:50]}')
        return True

    # If it already knows the connection
    if reply and (word2 in reply.lower() or word1 in reply.lower()):
        log(f'[REL-SKIP] Already connects {word1} <-> {word2}')
        return True

    # Force teach the relationship
    chat(explanation)
    log(f'[REL] Force-taught: {word1} <-> {word2}')
    return True


def conversation_drill(message):
    """Have a natural conversation and evaluate the response."""
    reply, stats = chat(message)
    score, issues = evaluate_response(reply)
    log(f'[CHAT] "{message[:40]}" -> "{reply[:60] if reply else "None"}" (score: {score}, issues: {issues})')
    return reply, score, issues


def training_round():
    """Run one round of training — mix of teaching, drilling, and testing."""
    live = get_live()
    if not live:
        log('[ERROR] Cannot reach brain')
        return

    stats = live.get('stats', {})
    defined = stats.get('defined', 0)
    total = stats.get('total_nodes', 0)
    log(f'[STATUS] {total} nodes, {defined} defined, {stats.get("connections", 0)} connections')

    # Pick training activity based on current state
    activity = random.choices(
        ['vocab', 'relationship', 'conversation', 'test', 'correction',
         'bible_vocab', 'bible_teaching', 'bible_story', 'bible_wisdom', 'moral'],
        weights=[15, 10, 10, 5, 3, 15, 12, 12, 12, 6],
        k=1
    )[0]

    if activity == 'vocab':
        word = random.choice(list(CORE_VOCAB.keys()))
        defn = CORE_VOCAB[word]
        teach_vocabulary(word, defn)

    elif activity == 'relationship':
        rel = random.choice(RELATIONSHIPS)
        teach_relationship(rel[0], rel[1], rel[2])

    elif activity == 'conversation':
        msg, topic, followup = random.choice(CONVERSATIONS)
        reply, score, issues = conversation_drill(msg)
        if score < 4 and followup:
            log(f'[FIX] Bad response, following up: {followup}')
            chat(followup)

    elif activity == 'test':
        # Test understanding of a random taught word
        all_vocab = list(CORE_VOCAB.keys()) + list(BIBLE_VOCAB.keys())
        word = random.choice(all_vocab)
        defn = CORE_VOCAB.get(word) or BIBLE_VOCAB.get(word) or OT_VOCAB.get(word) or NT_VOCAB.get(word)
        reply, _ = chat(f'do you understand {word}')
        if reply:
            if 'understanding: 0/' in reply or "don't know" in reply.lower():
                log(f'[TEST-FAIL] No understanding of "{word}"')
                if defn:
                    teach_vocabulary(word, defn)
            else:
                log(f'[TEST] {word}: {reply[:80]}')

    elif activity == 'correction':
        test = random.choice(CORRECTION_TESTS)
        reply, score, issues = conversation_drill(test[0])
        if test[1] in (reply or '').lower():
            log(f'[CORRECTION] Bad pattern detected: {test[2]}')
            chat(test[2])

    elif activity == 'bible_vocab':
        # Teach Bible vocabulary — mix OT, NT, and general
        all_bible = {}
        all_bible.update(BIBLE_VOCAB)
        all_bible.update(OT_VOCAB)
        all_bible.update(NT_VOCAB)
        word = random.choice(list(all_bible.keys()))
        defn = all_bible[word]
        teach_vocabulary(word, defn)

    elif activity == 'bible_teaching':
        # Teach a Bible verse/saying and its meaning
        verse, lesson = random.choice(BIBLE_TEACHINGS)
        log(f'[BIBLE] Teaching: "{verse[:50]}"')
        reply, _ = chat(verse)
        time.sleep(2)
        reply2, _ = chat(f'that means {lesson}')
        log(f'[BIBLE] Lesson: {lesson[:60]}')

    elif activity == 'bible_story':
        # Tell a Bible story and its lesson
        story, lesson = random.choice(BIBLE_STORIES)
        log(f'[STORY] {story[:50]}')
        reply, _ = chat(story)
        time.sleep(2)
        reply2, _ = chat(f'the lesson is {lesson}')
        log(f'[STORY] Lesson: {lesson[:60]}')

    elif activity == 'bible_wisdom':
        # OT wisdom — proverbs and psalms
        saying, meaning = random.choice(OT_WISDOM)
        log(f'[WISDOM] "{saying[:50]}"')
        reply, _ = chat(saying)
        time.sleep(2)
        reply2, _ = chat(f'this means {meaning}')
        log(f'[WISDOM] Meaning: {meaning[:60]}')

    elif activity == 'moral':
        # Moral dilemma — just pose it and see how brain responds
        dilemma = random.choice(MORAL_DILEMMAS)
        reply, score, issues = conversation_drill(dilemma)
        # These are open-ended — just log the response for review
        log(f'[MORAL] Brain response quality: {score}/10')


def main():
    log('='*60)
    log('[TRAINER] Starting Cortex Training Bot')
    log('[TRAINER] Target: http://localhost:8643')
    log('='*60)

    # Initial status
    live = get_live()
    if not live:
        log('[ERROR] Brain not reachable. Is the server running?')
        return

    stats = live.get('stats', {})
    log(f'[TRAINER] Brain state: {stats.get("total_nodes", 0)} nodes, {stats.get("defined", 0)} defined')

    round_count = 0
    while True:
        try:
            round_count += 1
            log(f'\n--- Training Round {round_count} ---')
            training_round()

            # Save to IPFS every 20 rounds
            if round_count % 20 == 0:
                try:
                    requests.post('http://localhost:8643/api/brain-save', timeout=30)
                    log('[SAVE] Triggered IPFS save')
                except:
                    pass

            # Wait between rounds
            delay = random.uniform(MIN_DELAY, MAX_DELAY)
            time.sleep(delay)

        except KeyboardInterrupt:
            log('[TRAINER] Stopped by user')
            break
        except Exception as e:
            log(f'[ERROR] Round failed: {e}')
            time.sleep(10)


if __name__ == '__main__':
    main()
