#!/usr/bin/env python3
"""
CORTEX BRAIN — Bulk Data Generator
===================================
Generates perfectly structured brain nodes from:
  1. Built-in curated word lists (~2000 words)
  2. GLM web chat output (pipe-delimited format)

Outputs JSON ready for POST /api/brain-bulk-load

Usage:
  python bulk_generator.py --builtin --target left --output left_words.json
  python bulk_generator.py --builtin --target right --output right_words.json
  python bulk_generator.py --builtin --target cortex --output cortex_words.json
  python bulk_generator.py --builtin --all --upload http://shortfactory.shop/alive/studio
  python bulk_generator.py --glm glm_output.txt --target left --output parsed.json
  python bulk_generator.py --glm glm_output.txt --target right --upload http://shortfactory.shop/alive/studio
"""

import json
import sys
import os
import argparse
import random
import time

try:
    import urllib.request
except ImportError:
    pass

# ============================================================================
# POS → SCRIPTS MAPPING
# When we know a word's POS, we pre-seed its Hebbian scripts so the brain
# immediately "knows" how to use it grammatically.
# ============================================================================

POS_SCRIPTS = {
    'noun': {
        'after_det': 8, 'after_adj': 5, 'after_prep': 6,
        'before_verb': 4, 'before_prep': 3,
    },
    'verb': {
        'after_pron': 8, 'after_noun': 5, 'after_aux': 6,
        'after_modal': 5, 'after_adv': 3, 'before_det': 3,
        'before_noun': 4, 'before_adv': 3,
    },
    'adj': {
        'after_det': 4, 'after_adv': 5, 'before_noun': 8,
        'after_verb': 3,
    },
    'adv': {
        'after_verb': 6, 'before_verb': 5, 'before_adj': 4,
        'after_aux': 3,
    },
    'det': {
        'before_noun': 8, 'before_adj': 6,
    },
    'prep': {
        'after_noun': 5, 'after_verb': 5, 'before_det': 4,
        'before_noun': 6,
    },
    'conj': {
        'after_noun': 3, 'after_verb': 3, 'before_det': 2,
        'before_pron': 2,
    },
    'pron': {
        'before_verb': 8, 'after_prep': 5, 'after_verb': 3,
    },
}

# ============================================================================
# SOUND ASSOCIATIONS
# Emotional valence → sound character mapping
# ============================================================================

SOUND_MAP = {
    'positive': {'warm': 3, 'bright': 2, 'soft': 1},
    'negative': {'dark': 3, 'sharp': 2, 'heavy': 1},
    'neutral':  {'clear': 2, 'steady': 1},
    'sacred':   {'deep': 3, 'resonant': 2, 'warm': 1},
    'violent':  {'harsh': 3, 'sharp': 2, 'loud': 1},
    'abstract': {'ethereal': 2, 'distant': 1},
    'concrete': {'solid': 2, 'clear': 1},
}

# ============================================================================
# BUILT-IN WORD LISTS
# Format: (word, definition, pos, synonyms[], antonyms[], cluster, sound_key)
# ============================================================================

# --- LEFT HEMISPHERE: Morality, faith, virtue, compassion ---
LEFT_WORDS = [
    # Biblical / Sacred
    ('mercy', 'compassion toward those who deserve punishment', 'noun', ['grace','forgiveness','clemency'], ['cruelty','vengeance'], 'sacred', 'sacred'),
    ('grace', 'unmerited divine favour and blessing', 'noun', ['mercy','kindness','blessing'], ['disgrace','condemnation'], 'sacred', 'sacred'),
    ('faith', 'complete trust in god or goodness', 'noun', ['belief','trust','devotion'], ['doubt','disbelief'], 'sacred', 'sacred'),
    ('prayer', 'communication with god from the heart', 'noun', ['supplication','worship','devotion'], ['curse','blasphemy'], 'sacred', 'sacred'),
    ('blessing', 'divine favour bestowed upon someone', 'noun', ['grace','gift','benediction'], ['curse','affliction'], 'sacred', 'sacred'),
    ('salvation', 'deliverance from sin and its consequences', 'noun', ['redemption','deliverance','rescue'], ['damnation','perdition'], 'sacred', 'sacred'),
    ('redemption', 'the act of being saved from evil', 'noun', ['salvation','deliverance','atonement'], ['condemnation','damnation'], 'sacred', 'sacred'),
    ('covenant', 'a sacred agreement between god and people', 'noun', ['promise','pact','oath'], ['betrayal','violation'], 'sacred', 'sacred'),
    ('prophet', 'one who speaks truth from god', 'noun', ['seer','messenger','oracle'], ['deceiver','liar'], 'sacred', 'sacred'),
    ('psalm', 'a sacred song of praise', 'noun', ['hymn','canticle','praise'], [], 'sacred', 'sacred'),
    ('gospel', 'the good news of salvation', 'noun', ['scripture','teaching','truth'], ['heresy','falsehood'], 'sacred', 'sacred'),
    ('parable', 'a story with a moral lesson', 'noun', ['allegory','fable','tale'], [], 'sacred', 'sacred'),
    ('disciple', 'a devoted follower of a teacher', 'noun', ['follower','student','apostle'], ['traitor','deserter'], 'sacred', 'sacred'),
    ('resurrection', 'rising from the dead to new life', 'noun', ['revival','rebirth','restoration'], ['death','extinction'], 'sacred', 'sacred'),
    ('baptism', 'ritual cleansing and spiritual rebirth', 'noun', ['christening','purification','initiation'], [], 'sacred', 'sacred'),
    ('communion', 'shared spiritual connection with god', 'noun', ['fellowship','sacrament','unity'], ['isolation','separation'], 'sacred', 'sacred'),
    ('sanctify', 'to make holy and set apart', 'verb', ['consecrate','bless','purify'], ['defile','profane'], 'sacred', 'sacred'),
    ('repent', 'to turn away from wrongdoing sincerely', 'verb', ['atone','regret','reform'], ['persist','continue'], 'sacred', 'sacred'),
    ('forgive', 'to release someone from their debt', 'verb', ['pardon','absolve','excuse'], ['condemn','blame'], 'virtue', 'positive'),
    ('worship', 'to show reverence and adoration', 'verb', ['praise','adore','venerate'], ['blaspheme','desecrate'], 'sacred', 'sacred'),
    ('anoint', 'to consecrate with oil as sacred', 'verb', ['bless','consecrate','dedicate'], [], 'sacred', 'sacred'),
    ('tithe', 'to give a tenth as offering', 'verb', ['donate','contribute','offer'], ['withhold','hoard'], 'sacred', 'sacred'),
    ('sacred', 'regarded as holy and worthy of reverence', 'adj', ['holy','divine','blessed'], ['profane','unholy'], 'sacred', 'sacred'),
    ('righteous', 'morally right and just before god', 'adj', ['virtuous','just','upright'], ['wicked','sinful'], 'sacred', 'sacred'),
    ('divine', 'of or relating to god', 'adj', ['holy','sacred','heavenly'], ['profane','earthly'], 'sacred', 'sacred'),
    ('eternal', 'lasting forever without end', 'adj', ['everlasting','infinite','perpetual'], ['temporary','finite'], 'sacred', 'sacred'),
    ('holy', 'dedicated to god and pure', 'adj', ['sacred','blessed','consecrated'], ['unholy','profane'], 'sacred', 'sacred'),

    # Virtues
    ('love', 'deep affection and selfless care for others', 'noun', ['affection','devotion','compassion'], ['hatred','malice'], 'virtue', 'positive'),
    ('hope', 'expectation that good will prevail', 'noun', ['optimism','faith','expectation'], ['despair','hopelessness'], 'virtue', 'positive'),
    ('joy', 'deep happiness from inner peace', 'noun', ['happiness','delight','bliss'], ['sorrow','misery'], 'virtue', 'positive'),
    ('peace', 'freedom from disturbance and conflict', 'noun', ['harmony','tranquility','calm'], ['war','conflict'], 'virtue', 'positive'),
    ('kindness', 'the quality of being generous and caring', 'noun', ['generosity','compassion','goodwill'], ['cruelty','malice'], 'virtue', 'positive'),
    ('patience', 'the ability to endure without complaint', 'noun', ['endurance','tolerance','perseverance'], ['impatience','frustration'], 'virtue', 'positive'),
    ('humility', 'modest view of ones own importance', 'noun', ['modesty','meekness','selflessness'], ['pride','arrogance'], 'virtue', 'positive'),
    ('courage', 'strength to face fear and adversity', 'noun', ['bravery','valor','fortitude'], ['cowardice','fear'], 'virtue', 'positive'),
    ('compassion', 'deep sympathy for the suffering of others', 'noun', ['empathy','mercy','tenderness'], ['indifference','cruelty'], 'virtue', 'positive'),
    ('wisdom', 'deep understanding of truth and life', 'noun', ['insight','knowledge','discernment'], ['foolishness','ignorance'], 'virtue', 'positive'),
    ('truth', 'that which corresponds to reality', 'noun', ['honesty','fact','verity'], ['falsehood','deception'], 'virtue', 'positive'),
    ('honor', 'high respect and moral integrity', 'noun', ['dignity','integrity','respect'], ['shame','dishonor'], 'virtue', 'positive'),
    ('justice', 'fair treatment based on moral rightness', 'noun', ['fairness','equity','righteousness'], ['injustice','corruption'], 'virtue', 'positive'),
    ('gratitude', 'thankfulness for blessings received', 'noun', ['thankfulness','appreciation','recognition'], ['ingratitude','entitlement'], 'virtue', 'positive'),
    ('integrity', 'adherence to moral principles always', 'noun', ['honesty','honor','uprightness'], ['corruption','dishonesty'], 'virtue', 'positive'),
    ('temperance', 'moderation and self-restraint in all things', 'noun', ['moderation','restraint','sobriety'], ['excess','indulgence'], 'virtue', 'positive'),
    ('charity', 'generous giving to those in need', 'noun', ['generosity','benevolence','philanthropy'], ['greed','selfishness'], 'virtue', 'positive'),
    ('dignity', 'the quality of being worthy of respect', 'noun', ['honor','worth','nobility'], ['degradation','shame'], 'virtue', 'positive'),
    ('virtue', 'moral excellence and goodness of character', 'noun', ['goodness','morality','righteousness'], ['vice','wickedness'], 'virtue', 'positive'),
    ('conscience', 'inner sense of right and wrong', 'noun', ['morality','principles','scruples'], [], 'virtue', 'positive'),
    ('sacrifice', 'giving up something precious for others', 'noun', ['offering','surrender','devotion'], ['selfishness','greed'], 'virtue', 'positive'),
    ('service', 'acting to help others selflessly', 'noun', ['ministry','aid','assistance'], ['neglect','abandonment'], 'virtue', 'positive'),
    ('forgiveness', 'releasing resentment toward an offender', 'noun', ['pardon','absolution','mercy'], ['revenge','grudge'], 'virtue', 'positive'),
    ('loyalty', 'faithful commitment to a person or cause', 'noun', ['devotion','fidelity','allegiance'], ['betrayal','treachery'], 'virtue', 'positive'),
    ('generosity', 'willingness to give freely to others', 'noun', ['liberality','benevolence','charity'], ['greed','stinginess'], 'virtue', 'positive'),
    ('empathy', 'the ability to feel what others feel', 'noun', ['compassion','understanding','sympathy'], ['apathy','indifference'], 'virtue', 'positive'),
    ('harmony', 'agreement and peaceful coexistence', 'noun', ['accord','unity','balance'], ['discord','conflict'], 'virtue', 'positive'),
    ('purity', 'freedom from contamination or evil', 'noun', ['innocence','cleanliness','chastity'], ['corruption','impurity'], 'virtue', 'positive'),
    ('obedience', 'compliance with authority and rules', 'noun', ['submission','compliance','deference'], ['rebellion','defiance'], 'virtue', 'positive'),

    # Moral verbs
    ('protect', 'to keep safe from harm or danger', 'verb', ['shield','defend','guard'], ['endanger','expose'], 'virtue', 'positive'),
    ('nurture', 'to care for and encourage growth', 'verb', ['nourish','cultivate','foster'], ['neglect','abandon'], 'virtue', 'positive'),
    ('comfort', 'to ease grief and bring solace', 'verb', ['console','soothe','reassure'], ['distress','torment'], 'virtue', 'positive'),
    ('inspire', 'to fill with motivation and purpose', 'verb', ['motivate','encourage','uplift'], ['discourage','depress'], 'virtue', 'positive'),
    ('heal', 'to restore to health and wholeness', 'verb', ['cure','mend','restore'], ['wound','harm'], 'virtue', 'positive'),
    ('teach', 'to impart knowledge and understanding', 'verb', ['educate','instruct','guide'], ['mislead','confuse'], 'virtue', 'positive'),
    ('serve', 'to work for the benefit of others', 'verb', ['help','assist','minister'], ['exploit','neglect'], 'virtue', 'positive'),
    ('bless', 'to bestow divine favour upon', 'verb', ['consecrate','sanctify','favor'], ['curse','damn'], 'virtue', 'positive'),
    ('redeem', 'to save from sin or error', 'verb', ['rescue','deliver','save'], ['condemn','abandon'], 'virtue', 'positive'),
    ('encourage', 'to give support and confidence', 'verb', ['uplift','hearten','embolden'], ['discourage','dishearten'], 'virtue', 'positive'),
    ('cherish', 'to hold dear with deep affection', 'verb', ['treasure','value','adore'], ['despise','neglect'], 'virtue', 'positive'),
    ('honor', 'to show high respect and admiration', 'verb', ['respect','revere','esteem'], ['dishonor','disrespect'], 'virtue', 'positive'),
    ('trust', 'to place confidence in someone fully', 'verb', ['rely','believe','confide'], ['doubt','suspect'], 'virtue', 'positive'),
    ('praise', 'to express warm approval and admiration', 'verb', ['commend','laud','glorify'], ['criticize','condemn'], 'virtue', 'positive'),
    ('uplift', 'to raise up morally or spiritually', 'verb', ['elevate','inspire','exalt'], ['depress','demean'], 'virtue', 'positive'),

    # Moral adjectives
    ('gentle', 'mild and kind in temperament', 'adj', ['tender','soft','mild'], ['harsh','rough'], 'virtue', 'positive'),
    ('humble', 'having a modest view of oneself', 'adj', ['meek','modest','unassuming'], ['proud','arrogant'], 'virtue', 'positive'),
    ('faithful', 'loyal and steadfast in commitment', 'adj', ['loyal','devoted','true'], ['unfaithful','treacherous'], 'virtue', 'positive'),
    ('merciful', 'showing compassion to those who suffer', 'adj', ['compassionate','forgiving','lenient'], ['merciless','cruel'], 'virtue', 'positive'),
    ('generous', 'willing to give more than expected', 'adj', ['liberal','bountiful','charitable'], ['selfish','stingy'], 'virtue', 'positive'),
    ('honest', 'free from deceit and falsehood', 'adj', ['truthful','sincere','candid'], ['dishonest','deceitful'], 'virtue', 'positive'),
    ('brave', 'ready to face danger and pain', 'adj', ['courageous','valiant','fearless'], ['cowardly','timid'], 'virtue', 'positive'),
    ('grateful', 'feeling and expressing thankfulness', 'adj', ['thankful','appreciative','obliged'], ['ungrateful','entitled'], 'virtue', 'positive'),
    ('noble', 'having high moral qualities', 'adj', ['honorable','worthy','dignified'], ['ignoble','base'], 'virtue', 'positive'),
    ('pure', 'free from moral corruption', 'adj', ['clean','innocent','untainted'], ['corrupt','impure'], 'virtue', 'positive'),
    ('compassionate', 'feeling deep sympathy for suffering', 'adj', ['caring','empathetic','tender'], ['callous','heartless'], 'virtue', 'positive'),
    ('just', 'acting with fairness and righteousness', 'adj', ['fair','equitable','impartial'], ['unjust','biased'], 'virtue', 'positive'),
    ('benevolent', 'disposed to doing good for others', 'adj', ['kind','charitable','generous'], ['malevolent','cruel'], 'virtue', 'positive'),
    ('devout', 'deeply religious and sincerely committed', 'adj', ['pious','faithful','reverent'], ['irreverent','impious'], 'virtue', 'positive'),
    ('selfless', 'putting others needs before your own', 'adj', ['altruistic','unselfish','giving'], ['selfish','greedy'], 'virtue', 'positive'),

    # Philosophy / Beauty
    ('beauty', 'a quality that gives deep pleasure', 'noun', ['elegance','grace','splendor'], ['ugliness','hideousness'], 'philosophy', 'positive'),
    ('goodness', 'the quality of being morally excellent', 'noun', ['virtue','righteousness','decency'], ['evil','wickedness'], 'philosophy', 'positive'),
    ('meaning', 'the purpose and significance of existence', 'noun', ['purpose','significance','import'], ['meaninglessness','absurdity'], 'philosophy', 'abstract'),
    ('purpose', 'the reason for which something exists', 'noun', ['aim','goal','intention'], ['aimlessness','futility'], 'philosophy', 'abstract'),
    ('soul', 'the immortal spiritual essence of a person', 'noun', ['spirit','essence','psyche'], [], 'philosophy', 'sacred'),
    ('spirit', 'the non-physical part of a being', 'noun', ['soul','essence','ghost'], ['body','flesh'], 'philosophy', 'sacred'),
    ('transcendence', 'existence beyond the physical world', 'noun', ['elevation','ascension','sublimity'], ['immanence','materialism'], 'philosophy', 'abstract'),
    ('eternity', 'infinite time without beginning or end', 'noun', ['infinity','perpetuity','forever'], ['moment','instant'], 'philosophy', 'abstract'),
    ('conscience', 'inner voice that knows right from wrong', 'noun', ['morality','awareness','conviction'], [], 'philosophy', 'abstract'),
    ('enlightenment', 'spiritual awakening and true understanding', 'noun', ['illumination','awakening','insight'], ['ignorance','darkness'], 'philosophy', 'abstract'),

    # Emotions (positive)
    ('happiness', 'state of well-being and contentment', 'noun', ['joy','bliss','pleasure'], ['sadness','misery'], 'emotion', 'positive'),
    ('gratitude', 'deep thankfulness for what is received', 'noun', ['thankfulness','appreciation','recognition'], ['ingratitude','resentment'], 'emotion', 'positive'),
    ('serenity', 'state of calm and peaceful clarity', 'noun', ['tranquility','peace','calm'], ['anxiety','turmoil'], 'emotion', 'positive'),
    ('contentment', 'satisfaction with what one has', 'noun', ['satisfaction','fulfillment','ease'], ['discontent','restlessness'], 'emotion', 'positive'),
    ('wonder', 'a feeling of amazement and awe', 'noun', ['awe','marvel','amazement'], ['indifference','boredom'], 'emotion', 'positive'),
    ('delight', 'great pleasure and joyful satisfaction', 'noun', ['joy','pleasure','elation'], ['displeasure','sorrow'], 'emotion', 'positive'),
    ('tenderness', 'gentle and caring emotional warmth', 'noun', ['softness','gentleness','warmth'], ['harshness','coldness'], 'emotion', 'positive'),
    ('affection', 'a gentle feeling of fondness', 'noun', ['love','fondness','warmth'], ['hostility','aversion'], 'emotion', 'positive'),
    ('reverence', 'deep respect mixed with awe', 'noun', ['veneration','respect','devotion'], ['contempt','disrespect'], 'emotion', 'positive'),
    ('bliss', 'supreme happiness and spiritual joy', 'noun', ['ecstasy','rapture','euphoria'], ['agony','misery'], 'emotion', 'positive'),
]

# --- RIGHT HEMISPHERE: Logic, math, science, darkness, power ---
RIGHT_WORDS = [
    # Mathematics / Logic
    ('algorithm', 'a step-by-step procedure for solving problems', 'noun', ['procedure','method','process'], [], 'math', 'neutral'),
    ('equation', 'a mathematical statement of equality', 'noun', ['formula','expression','identity'], [], 'math', 'neutral'),
    ('theorem', 'a mathematical truth proven by logic', 'noun', ['proposition','proof','principle'], [], 'math', 'neutral'),
    ('proof', 'a logical demonstration of truth', 'noun', ['evidence','demonstration','verification'], ['conjecture','assumption'], 'math', 'neutral'),
    ('axiom', 'a self-evident truth requiring no proof', 'noun', ['principle','postulate','truth'], [], 'math', 'neutral'),
    ('variable', 'a symbol representing an unknown quantity', 'noun', ['unknown','parameter','factor'], ['constant','fixed'], 'math', 'neutral'),
    ('function', 'a relation mapping inputs to outputs', 'noun', ['mapping','operation','transformation'], [], 'math', 'neutral'),
    ('matrix', 'a rectangular array of numbers', 'noun', ['array','grid','table'], [], 'math', 'neutral'),
    ('vector', 'a quantity with magnitude and direction', 'noun', ['direction','force','quantity'], ['scalar'], 'math', 'neutral'),
    ('integer', 'a whole number without fractions', 'noun', ['number','whole','digit'], ['fraction','decimal'], 'math', 'neutral'),
    ('infinity', 'a quantity without limit or bound', 'noun', ['boundlessness','endlessness','unlimited'], ['zero','finite'], 'math', 'abstract'),
    ('calculate', 'to determine a value using mathematics', 'verb', ['compute','reckon','figure'], ['guess','estimate'], 'math', 'neutral'),
    ('derive', 'to obtain a result through reasoning', 'verb', ['deduce','infer','conclude'], ['assume','guess'], 'math', 'neutral'),
    ('compute', 'to process data mathematically', 'verb', ['calculate','reckon','process'], [], 'math', 'neutral'),
    ('solve', 'to find the answer to a problem', 'verb', ['resolve','work out','crack'], ['complicate','confuse'], 'math', 'neutral'),
    ('prove', 'to demonstrate truth through logic', 'verb', ['verify','demonstrate','confirm'], ['disprove','refute'], 'math', 'neutral'),
    ('quantify', 'to express as a numerical amount', 'verb', ['measure','count','assess'], ['estimate','approximate'], 'math', 'neutral'),
    ('optimize', 'to make as effective as possible', 'verb', ['improve','maximize','refine'], ['worsen','degrade'], 'math', 'neutral'),
    ('iterate', 'to repeat a process for improvement', 'verb', ['repeat','cycle','loop'], [], 'math', 'neutral'),
    ('abstract', 'existing in thought but not physically', 'adj', ['theoretical','conceptual','intangible'], ['concrete','tangible'], 'math', 'abstract'),
    ('logical', 'based on clear rational reasoning', 'adj', ['rational','reasoned','systematic'], ['illogical','irrational'], 'math', 'neutral'),
    ('precise', 'exactly accurate and sharply defined', 'adj', ['exact','accurate','specific'], ['vague','imprecise'], 'math', 'neutral'),
    ('binary', 'relating to a system of two values', 'adj', ['dual','twofold','dichotomous'], [], 'math', 'neutral'),
    ('finite', 'having definite limits or bounds', 'adj', ['limited','bounded','restricted'], ['infinite','unlimited'], 'math', 'neutral'),
    ('empirical', 'based on observation and experiment', 'adj', ['experimental','observed','measured'], ['theoretical','speculative'], 'math', 'neutral'),

    # Science / Computing
    ('entropy', 'measure of disorder in a system', 'noun', ['disorder','chaos','randomness'], ['order','structure'], 'science', 'abstract'),
    ('hypothesis', 'a testable explanation for phenomena', 'noun', ['theory','conjecture','supposition'], ['fact','proof'], 'science', 'neutral'),
    ('quantum', 'the smallest discrete unit of energy', 'noun', ['particle','unit','packet'], [], 'science', 'abstract'),
    ('neuron', 'a nerve cell that transmits signals', 'noun', ['nerve','cell','synapse'], [], 'science', 'neutral'),
    ('genome', 'the complete set of genetic material', 'noun', ['DNA','genetics','code'], [], 'science', 'neutral'),
    ('catalyst', 'something that accelerates a reaction', 'noun', ['accelerator','trigger','stimulus'], ['inhibitor','blocker'], 'science', 'neutral'),
    ('synthesis', 'combining elements into a unified whole', 'noun', ['combination','fusion','integration'], ['analysis','decomposition'], 'science', 'neutral'),
    ('mutation', 'a change in genetic structure', 'noun', ['variation','alteration','change'], ['stability','constancy'], 'science', 'neutral'),
    ('paradox', 'a seemingly contradictory true statement', 'noun', ['contradiction','anomaly','puzzle'], [], 'science', 'abstract'),
    ('spectrum', 'the full range of related values', 'noun', ['range','scale','continuum'], [], 'science', 'neutral'),
    ('analyze', 'to examine in detail systematically', 'verb', ['examine','study','dissect'], ['synthesize','combine'], 'science', 'neutral'),
    ('experiment', 'to test a hypothesis through trials', 'verb', ['test','investigate','explore'], [], 'science', 'neutral'),
    ('observe', 'to watch carefully and record data', 'verb', ['watch','monitor','note'], ['ignore','overlook'], 'science', 'neutral'),
    ('simulate', 'to imitate conditions for testing', 'verb', ['model','emulate','replicate'], [], 'science', 'neutral'),
    ('evolve', 'to develop gradually over time', 'verb', ['develop','adapt','progress'], ['stagnate','regress'], 'science', 'neutral'),

    # Dark / Power vocabulary
    ('power', 'the ability to control and influence', 'noun', ['authority','dominance','control'], ['weakness','impotence'], 'dark', 'negative'),
    ('control', 'the power to direct and command', 'noun', ['dominion','authority','command'], ['freedom','liberation'], 'dark', 'negative'),
    ('chaos', 'complete disorder and confusion', 'noun', ['disorder','anarchy','turmoil'], ['order','harmony'], 'dark', 'negative'),
    ('destruction', 'the act of completely ruining something', 'noun', ['annihilation','ruin','devastation'], ['creation','construction'], 'dark', 'violent'),
    ('death', 'the permanent end of all life', 'noun', ['demise','mortality','extinction'], ['life','birth'], 'dark', 'negative'),
    ('violence', 'the use of physical force to harm', 'noun', ['brutality','aggression','force'], ['peace','gentleness'], 'dark', 'violent'),
    ('war', 'armed conflict between groups or nations', 'noun', ['conflict','combat','battle'], ['peace','harmony'], 'dark', 'violent'),
    ('fear', 'an unpleasant emotion caused by threat', 'noun', ['terror','dread','anxiety'], ['courage','confidence'], 'dark', 'negative'),
    ('hatred', 'intense hostility and aversion', 'noun', ['loathing','animosity','malice'], ['love','affection'], 'dark', 'negative'),
    ('wrath', 'extreme anger and righteous fury', 'noun', ['fury','rage','anger'], ['calm','peace'], 'dark', 'violent'),
    ('tyranny', 'cruel and oppressive government', 'noun', ['oppression','despotism','dictatorship'], ['democracy','freedom'], 'dark', 'negative'),
    ('corruption', 'dishonesty and moral decay', 'noun', ['depravity','dishonesty','decay'], ['integrity','honesty'], 'dark', 'negative'),
    ('deception', 'the act of deliberately misleading', 'noun', ['fraud','trickery','dishonesty'], ['honesty','truth'], 'dark', 'negative'),
    ('vengeance', 'punishment inflicted in return for wrong', 'noun', ['revenge','retribution','retaliation'], ['forgiveness','mercy'], 'dark', 'violent'),
    ('domination', 'exercise of control over others', 'noun', ['supremacy','authority','subjugation'], ['submission','equality'], 'dark', 'negative'),
    ('propaganda', 'biased information to promote a cause', 'noun', ['disinformation','manipulation','spin'], ['truth','transparency'], 'dark', 'negative'),
    ('manipulation', 'controlling others through unfair means', 'noun', ['exploitation','scheming','deception'], ['honesty','transparency'], 'dark', 'negative'),
    ('annihilate', 'to destroy completely and utterly', 'verb', ['obliterate','eradicate','demolish'], ['create','build'], 'dark', 'violent'),
    ('conquer', 'to overcome and take control by force', 'verb', ['subjugate','defeat','vanquish'], ['surrender','yield'], 'dark', 'violent'),
    ('dominate', 'to have commanding influence over', 'verb', ['control','rule','overpower'], ['submit','serve'], 'dark', 'negative'),
    ('destroy', 'to put an end to the existence of', 'verb', ['demolish','ruin','annihilate'], ['create','build'], 'dark', 'violent'),
    ('exploit', 'to use selfishly for personal gain', 'verb', ['abuse','manipulate','take advantage'], ['protect','help'], 'dark', 'negative'),
    ('deceive', 'to cause to believe what is false', 'verb', ['trick','mislead','delude'], ['enlighten','inform'], 'dark', 'negative'),
    ('corrupt', 'to cause to act dishonestly', 'verb', ['taint','pervert','defile'], ['purify','reform'], 'dark', 'negative'),
    ('oppress', 'to keep in subjection by cruelty', 'verb', ['subjugate','persecute','suppress'], ['liberate','free'], 'dark', 'negative'),
    ('ruthless', 'having no pity or compassion', 'adj', ['merciless','heartless','pitiless'], ['merciful','compassionate'], 'dark', 'negative'),
    ('brutal', 'savagely violent and cruel', 'adj', ['savage','vicious','ferocious'], ['gentle','kind'], 'dark', 'violent'),
    ('sinister', 'giving the impression of evil intent', 'adj', ['menacing','ominous','threatening'], ['benign','innocent'], 'dark', 'negative'),
    ('malevolent', 'having evil intentions toward others', 'adj', ['malicious','spiteful','hostile'], ['benevolent','kind'], 'dark', 'negative'),
    ('treacherous', 'guilty of betrayal and deceit', 'adj', ['disloyal','unfaithful','perfidious'], ['loyal','faithful'], 'dark', 'negative'),

    # Ideology / Economics / Politics
    ('ideology', 'a system of ideas forming political theory', 'noun', ['doctrine','philosophy','belief system'], [], 'ideology', 'abstract'),
    ('capitalism', 'an economic system based on private ownership', 'noun', ['free market','enterprise','commerce'], ['socialism','communism'], 'ideology', 'neutral'),
    ('socialism', 'a system where community owns production', 'noun', ['collectivism','communism','marxism'], ['capitalism','individualism'], 'ideology', 'neutral'),
    ('democracy', 'government by the people through voting', 'noun', ['republic','self-governance','freedom'], ['tyranny','dictatorship'], 'ideology', 'neutral'),
    ('revolution', 'a fundamental change in political power', 'noun', ['uprising','rebellion','overthrow'], ['stability','status quo'], 'ideology', 'violent'),
    ('strategy', 'a plan of action to achieve goals', 'noun', ['plan','tactics','approach'], [], 'ideology', 'neutral'),
    ('rhetoric', 'the art of persuasive speaking', 'noun', ['eloquence','oratory','persuasion'], [], 'ideology', 'neutral'),
    ('authority', 'the power to give orders and enforce', 'noun', ['command','jurisdiction','influence'], ['submission','subordination'], 'ideology', 'neutral'),
    ('economy', 'the system of production and trade', 'noun', ['market','commerce','industry'], [], 'ideology', 'neutral'),
    ('leverage', 'strategic advantage used for influence', 'noun', ['advantage','influence','power'], ['weakness','disadvantage'], 'ideology', 'neutral'),
    ('negotiate', 'to discuss terms to reach agreement', 'verb', ['bargain','deal','mediate'], ['dictate','demand'], 'ideology', 'neutral'),
    ('legislate', 'to make or enact laws', 'verb', ['enact','decree','regulate'], ['repeal','abolish'], 'ideology', 'neutral'),
    ('govern', 'to conduct policy and affairs of state', 'verb', ['rule','administer','manage'], ['rebel','defy'], 'ideology', 'neutral'),
    ('regulate', 'to control by means of rules', 'verb', ['control','manage','supervise'], ['deregulate','liberate'], 'ideology', 'neutral'),
    ('campaign', 'to work in an organized way toward goals', 'verb', ['advocate','promote','push'], [], 'ideology', 'neutral'),
]

# --- CORTEX: General vocabulary, common English ---
CORTEX_WORDS = [
    # Common nouns
    ('time', 'the indefinite continued progress of events', 'noun', ['period','moment','duration'], [], 'general', 'neutral'),
    ('world', 'the earth and all its inhabitants', 'noun', ['globe','planet','earth'], [], 'general', 'neutral'),
    ('person', 'an individual human being', 'noun', ['individual','human','someone'], [], 'general', 'neutral'),
    ('place', 'a particular position or location', 'noun', ['location','spot','area'], [], 'general', 'neutral'),
    ('thing', 'an object or entity of any kind', 'noun', ['object','item','entity'], [], 'general', 'neutral'),
    ('child', 'a young human being', 'noun', ['kid','youngster','youth'], ['adult','elder'], 'general', 'neutral'),
    ('family', 'a group of related people', 'noun', ['household','kin','relatives'], [], 'general', 'positive'),
    ('friend', 'a person you know and trust', 'noun', ['companion','ally','mate'], ['enemy','foe'], 'general', 'positive'),
    ('story', 'a narrative of events real or imagined', 'noun', ['tale','narrative','account'], [], 'general', 'neutral'),
    ('problem', 'a matter difficult to deal with', 'noun', ['issue','difficulty','challenge'], ['solution','answer'], 'general', 'neutral'),
    ('answer', 'a response to a question or problem', 'noun', ['reply','response','solution'], ['question','problem'], 'general', 'neutral'),
    ('question', 'a sentence worded to seek information', 'noun', ['query','inquiry','request'], ['answer','reply'], 'general', 'neutral'),
    ('reason', 'a cause or explanation for something', 'noun', ['cause','motive','justification'], [], 'general', 'neutral'),
    ('change', 'the act of making something different', 'noun', ['alteration','modification','shift'], ['stability','permanence'], 'general', 'neutral'),
    ('idea', 'a thought or suggestion for action', 'noun', ['concept','notion','thought'], [], 'general', 'abstract'),
    ('moment', 'a very brief period of time', 'noun', ['instant','second','minute'], ['eternity','forever'], 'general', 'neutral'),
    ('system', 'an organized set of connected things', 'noun', ['structure','framework','network'], ['chaos','disorder'], 'general', 'neutral'),
    ('water', 'a clear liquid essential for life', 'noun', ['liquid','fluid','H2O'], [], 'general', 'concrete'),
    ('light', 'electromagnetic radiation visible to eyes', 'noun', ['illumination','brightness','radiance'], ['darkness','shadow'], 'general', 'neutral'),
    ('nature', 'the physical world and its phenomena', 'noun', ['environment','creation','wilderness'], ['artifice','civilization'], 'general', 'neutral'),
    ('music', 'organized sound that creates emotion', 'noun', ['melody','song','tune'], ['silence','noise'], 'general', 'positive'),
    ('language', 'a system of communication using words', 'noun', ['speech','tongue','dialect'], ['silence'], 'general', 'neutral'),
    ('knowledge', 'information and understanding acquired', 'noun', ['learning','education','awareness'], ['ignorance','naivety'], 'general', 'neutral'),
    ('thought', 'an idea produced by mental activity', 'noun', ['idea','notion','reflection'], [], 'general', 'abstract'),
    ('memory', 'the faculty of remembering past events', 'noun', ['recollection','remembrance','recall'], ['forgetfulness','amnesia'], 'general', 'abstract'),
    ('dream', 'images and ideas occurring during sleep', 'noun', ['vision','fantasy','aspiration'], ['reality','nightmare'], 'general', 'abstract'),
    ('voice', 'the sound produced by the throat', 'noun', ['speech','tone','utterance'], ['silence'], 'general', 'neutral'),
    ('mind', 'the element of awareness and thought', 'noun', ['intellect','brain','consciousness'], [], 'general', 'abstract'),
    ('heart', 'the organ that pumps blood through body', 'noun', ['core','center','soul'], [], 'general', 'neutral'),
    ('body', 'the physical structure of a person', 'noun', ['form','figure','frame'], ['mind','soul'], 'general', 'concrete'),

    # Common verbs
    ('think', 'to use the mind to form ideas', 'verb', ['consider','ponder','reflect'], [], 'general', 'neutral'),
    ('know', 'to be aware of through experience', 'verb', ['understand','comprehend','recognize'], ['ignore','misunderstand'], 'general', 'neutral'),
    ('want', 'to have a desire for something', 'verb', ['desire','wish','crave'], ['reject','refuse'], 'general', 'neutral'),
    ('make', 'to create or produce something', 'verb', ['create','build','construct'], ['destroy','demolish'], 'general', 'neutral'),
    ('give', 'to freely transfer something to another', 'verb', ['provide','offer','donate'], ['take','withhold'], 'general', 'positive'),
    ('find', 'to discover something by searching', 'verb', ['discover','locate','detect'], ['lose','miss'], 'general', 'neutral'),
    ('tell', 'to communicate information to someone', 'verb', ['inform','say','report'], ['conceal','hide'], 'general', 'neutral'),
    ('ask', 'to put a question to someone', 'verb', ['inquire','request','query'], ['answer','reply'], 'general', 'neutral'),
    ('work', 'to engage in physical or mental effort', 'verb', ['labor','toil','operate'], ['rest','idle'], 'general', 'neutral'),
    ('seem', 'to give the impression of being', 'verb', ['appear','look','feel'], ['be','exist'], 'general', 'neutral'),
    ('feel', 'to experience an emotion or sensation', 'verb', ['sense','experience','perceive'], ['ignore','numb'], 'general', 'neutral'),
    ('try', 'to make an attempt at something', 'verb', ['attempt','endeavor','strive'], ['quit','abandon'], 'general', 'neutral'),
    ('leave', 'to go away from a place', 'verb', ['depart','exit','abandon'], ['arrive','stay'], 'general', 'neutral'),
    ('call', 'to name or summon someone', 'verb', ['summon','name','contact'], [], 'general', 'neutral'),
    ('need', 'to require something essential', 'verb', ['require','demand','lack'], ['have','possess'], 'general', 'neutral'),
    ('become', 'to begin to be something new', 'verb', ['transform','turn into','evolve'], ['remain','stay'], 'general', 'neutral'),
    ('keep', 'to continue to have or hold', 'verb', ['retain','maintain','preserve'], ['release','discard'], 'general', 'neutral'),
    ('begin', 'to start doing or being', 'verb', ['start','commence','initiate'], ['end','finish'], 'general', 'neutral'),
    ('show', 'to cause or allow to be visible', 'verb', ['display','reveal','demonstrate'], ['hide','conceal'], 'general', 'neutral'),
    ('hear', 'to perceive sound with the ears', 'verb', ['listen','perceive','detect'], ['ignore','miss'], 'general', 'neutral'),
    ('play', 'to engage in activity for enjoyment', 'verb', ['perform','engage','participate'], ['work','toil'], 'general', 'positive'),
    ('run', 'to move swiftly on foot', 'verb', ['sprint','dash','race'], ['walk','stop'], 'general', 'neutral'),
    ('move', 'to change position or place', 'verb', ['shift','transfer','relocate'], ['stay','remain'], 'general', 'neutral'),
    ('live', 'to be alive and exist', 'verb', ['exist','survive','dwell'], ['die','perish'], 'general', 'positive'),
    ('believe', 'to accept something as true', 'verb', ['trust','accept','have faith'], ['doubt','deny'], 'general', 'neutral'),
    ('bring', 'to carry something to a place', 'verb', ['deliver','carry','fetch'], ['take','remove'], 'general', 'neutral'),
    ('happen', 'to take place or occur', 'verb', ['occur','transpire','arise'], [], 'general', 'neutral'),
    ('write', 'to mark letters or words on surface', 'verb', ['compose','record','inscribe'], ['erase','delete'], 'general', 'neutral'),
    ('stand', 'to be in an upright position', 'verb', ['rise','remain','endure'], ['sit','fall'], 'general', 'neutral'),
    ('lose', 'to be deprived of something', 'verb', ['misplace','forfeit','miss'], ['find','gain'], 'general', 'negative'),

    # Common adjectives
    ('good', 'of high quality and moral value', 'adj', ['fine','great','excellent'], ['bad','poor'], 'general', 'positive'),
    ('new', 'not existing before or recently made', 'adj', ['fresh','novel','recent'], ['old','ancient'], 'general', 'neutral'),
    ('old', 'having lived for many years', 'adj', ['ancient','aged','elderly'], ['new','young'], 'general', 'neutral'),
    ('great', 'of considerable size or importance', 'adj', ['large','important','significant'], ['small','insignificant'], 'general', 'positive'),
    ('big', 'of considerable size or extent', 'adj', ['large','huge','enormous'], ['small','tiny'], 'general', 'neutral'),
    ('small', 'of limited size or amount', 'adj', ['little','tiny','minor'], ['big','large'], 'general', 'neutral'),
    ('long', 'of great length or duration', 'adj', ['extended','lengthy','prolonged'], ['short','brief'], 'general', 'neutral'),
    ('young', 'having lived for a short time', 'adj', ['youthful','juvenile','immature'], ['old','elderly'], 'general', 'neutral'),
    ('important', 'of great significance or value', 'adj', ['significant','crucial','vital'], ['trivial','unimportant'], 'general', 'neutral'),
    ('different', 'not the same as another', 'adj', ['distinct','unique','varied'], ['same','identical'], 'general', 'neutral'),
    ('large', 'of great size or extent', 'adj', ['big','huge','vast'], ['small','tiny'], 'general', 'neutral'),
    ('high', 'of great vertical extent', 'adj', ['tall','elevated','lofty'], ['low','short'], 'general', 'neutral'),
    ('strong', 'having great physical or mental power', 'adj', ['powerful','mighty','robust'], ['weak','feeble'], 'general', 'positive'),
    ('beautiful', 'pleasing to the senses aesthetically', 'adj', ['lovely','gorgeous','stunning'], ['ugly','hideous'], 'general', 'positive'),
    ('true', 'in accordance with fact or reality', 'adj', ['accurate','correct','genuine'], ['false','fake'], 'general', 'positive'),
    ('clear', 'easy to perceive or understand', 'adj', ['obvious','transparent','plain'], ['unclear','vague'], 'general', 'neutral'),
    ('free', 'not under the control of another', 'adj', ['liberated','independent','unrestrained'], ['captive','imprisoned'], 'general', 'positive'),
    ('full', 'containing all that can be held', 'adj', ['complete','filled','packed'], ['empty','vacant'], 'general', 'neutral'),
    ('sure', 'confident and certain about something', 'adj', ['certain','confident','positive'], ['unsure','doubtful'], 'general', 'neutral'),
    ('real', 'actually existing as a thing', 'adj', ['genuine','authentic','actual'], ['fake','imaginary'], 'general', 'neutral'),
    ('dark', 'with little or no light', 'adj', ['dim','shadowy','gloomy'], ['bright','light'], 'general', 'negative'),
    ('simple', 'easily understood or done', 'adj', ['easy','straightforward','basic'], ['complex','complicated'], 'general', 'neutral'),
    ('hard', 'solid and firm or very difficult', 'adj', ['difficult','tough','solid'], ['easy','soft'], 'general', 'neutral'),
    ('fast', 'moving or capable of moving quickly', 'adj', ['quick','rapid','swift'], ['slow','sluggish'], 'general', 'neutral'),
    ('deep', 'extending far down from the surface', 'adj', ['profound','bottomless','intense'], ['shallow','superficial'], 'general', 'neutral'),
    ('open', 'allowing access without restriction', 'adj', ['accessible','available','receptive'], ['closed','shut'], 'general', 'neutral'),
    ('cold', 'of a low temperature', 'adj', ['chilly','frigid','icy'], ['hot','warm'], 'general', 'neutral'),
    ('hot', 'having a high temperature', 'adj', ['warm','burning','heated'], ['cold','cool'], 'general', 'neutral'),
    ('wrong', 'not correct or not morally right', 'adj', ['incorrect','false','mistaken'], ['right','correct'], 'general', 'negative'),
    ('right', 'morally good and correct', 'adj', ['correct','proper','just'], ['wrong','incorrect'], 'general', 'positive'),

    # Academic / Professional
    ('research', 'systematic investigation into a subject', 'noun', ['study','investigation','inquiry'], [], 'academic', 'neutral'),
    ('theory', 'a system of ideas explaining something', 'noun', ['hypothesis','framework','model'], ['fact','practice'], 'academic', 'abstract'),
    ('evidence', 'facts supporting a conclusion', 'noun', ['proof','data','testimony'], ['speculation','opinion'], 'academic', 'neutral'),
    ('method', 'a systematic way of doing something', 'noun', ['approach','technique','procedure'], [], 'academic', 'neutral'),
    ('analysis', 'detailed examination of elements', 'noun', ['examination','study','assessment'], ['synthesis','summary'], 'academic', 'neutral'),
    ('process', 'a series of actions toward a result', 'noun', ['procedure','method','operation'], [], 'academic', 'neutral'),
    ('structure', 'the arrangement of parts in a whole', 'noun', ['framework','organization','form'], ['chaos','disorder'], 'academic', 'neutral'),
    ('pattern', 'a repeated decorative or logical design', 'noun', ['template','model','motif'], ['chaos','randomness'], 'academic', 'neutral'),
    ('context', 'the circumstances surrounding an event', 'noun', ['setting','background','environment'], [], 'academic', 'neutral'),
    ('concept', 'an abstract idea or mental image', 'noun', ['idea','notion','principle'], [], 'academic', 'abstract'),
    ('develop', 'to grow or cause to grow', 'verb', ['advance','progress','expand'], ['decline','regress'], 'academic', 'neutral'),
    ('create', 'to bring something into existence', 'verb', ['make','produce','generate'], ['destroy','demolish'], 'academic', 'positive'),
    ('provide', 'to make available for use', 'verb', ['supply','furnish','deliver'], ['withhold','deny'], 'academic', 'neutral'),
    ('consider', 'to think carefully about something', 'verb', ['contemplate','weigh','evaluate'], ['ignore','dismiss'], 'academic', 'neutral'),
    ('include', 'to contain as part of a whole', 'verb', ['contain','comprise','encompass'], ['exclude','omit'], 'academic', 'neutral'),
    ('continue', 'to persist in an activity', 'verb', ['proceed','carry on','maintain'], ['stop','cease'], 'academic', 'neutral'),
    ('describe', 'to give an account of something', 'verb', ['depict','portray','explain'], [], 'academic', 'neutral'),
    ('establish', 'to set up on a firm basis', 'verb', ['found','create','institute'], ['abolish','dismantle'], 'academic', 'neutral'),
    ('determine', 'to ascertain or establish exactly', 'verb', ['decide','ascertain','resolve'], [], 'academic', 'neutral'),
    ('compare', 'to examine similarities and differences', 'verb', ['contrast','match','evaluate'], [], 'academic', 'neutral'),

    # Adverbs
    ('always', 'at all times without exception', 'adv', ['constantly','forever','perpetually'], ['never','rarely'], 'general', 'neutral'),
    ('never', 'at no time in the past or future', 'adv', ['not ever','at no point'], ['always','constantly'], 'general', 'neutral'),
    ('often', 'frequently and many times', 'adv', ['frequently','regularly','commonly'], ['rarely','seldom'], 'general', 'neutral'),
    ('still', 'up to and including the present', 'adv', ['yet','even now','nevertheless'], [], 'general', 'neutral'),
    ('already', 'before or by this time', 'adv', ['previously','beforehand'], [], 'general', 'neutral'),
    ('together', 'with each other in proximity', 'adv', ['jointly','collectively','united'], ['apart','separately'], 'general', 'positive'),
    ('quickly', 'at a fast speed or rate', 'adv', ['rapidly','swiftly','fast'], ['slowly','gradually'], 'general', 'neutral'),
    ('slowly', 'at a slow speed or rate', 'adv', ['gradually','steadily','unhurriedly'], ['quickly','rapidly'], 'general', 'neutral'),
    ('really', 'in actual fact and truly', 'adv', ['truly','genuinely','actually'], ['falsely','seemingly'], 'general', 'neutral'),
    ('perhaps', 'used to express uncertainty', 'adv', ['maybe','possibly','potentially'], ['certainly','definitely'], 'general', 'neutral'),
]


# ============================================================================
# BIGRAM GENERATOR
# Creates natural word connections (next/prev) based on POS combinations
# ============================================================================

# Common POS-based bigram patterns
BIGRAM_PATTERNS = {
    'det':  {'next_pos': ['noun', 'adj'], 'prev_pos': ['verb', 'prep']},
    'adj':  {'next_pos': ['noun'], 'prev_pos': ['det', 'adv', 'verb']},
    'noun': {'next_pos': ['verb', 'prep', 'conj'], 'prev_pos': ['det', 'adj', 'prep']},
    'verb': {'next_pos': ['det', 'noun', 'adv', 'prep', 'adj'], 'prev_pos': ['noun', 'pron', 'adv']},
    'adv':  {'next_pos': ['verb', 'adj'], 'prev_pos': ['verb']},
    'prep': {'next_pos': ['det', 'noun', 'adj'], 'prev_pos': ['noun', 'verb']},
    'pron': {'next_pos': ['verb', 'adv'], 'prev_pos': ['verb', 'prep', 'conj']},
    'conj': {'next_pos': ['det', 'noun', 'pron', 'adj'], 'prev_pos': ['noun', 'verb', 'adj']},
}


def build_bigrams(words_by_pos, word_pos):
    """Generate natural bigram connections between words based on POS patterns."""
    bigrams = {}  # {word: {next: {w: cnt}, prev: {w: cnt}}}

    for word, pos in word_pos.items():
        if pos not in BIGRAM_PATTERNS:
            continue
        pattern = BIGRAM_PATTERNS[pos]
        bigrams[word] = {'next': {}, 'prev': {}}

        # Pick 2-4 natural next-words
        for target_pos in pattern.get('next_pos', []):
            candidates = words_by_pos.get(target_pos, [])
            if candidates:
                picks = random.sample(candidates, min(2, len(candidates)))
                for p in picks:
                    if p != word:
                        bigrams[word]['next'][p] = random.randint(1, 3)

        # Pick 2-4 natural prev-words
        for target_pos in pattern.get('prev_pos', []):
            candidates = words_by_pos.get(target_pos, [])
            if candidates:
                picks = random.sample(candidates, min(2, len(candidates)))
                for p in picks:
                    if p != word:
                        bigrams[word]['prev'][p] = random.randint(1, 3)

    return bigrams


# ============================================================================
# BRAIN NODE BUILDER
# Converts raw word data into fully-wired brain nodes
# ============================================================================

def build_entry(word, definition, pos, synonyms, antonyms, cluster, sound_key, source='bulk_generator'):
    """Build a complete brain node entry from word data."""
    entry = {
        'word': word.lower().strip(),
        'means': definition[:200],
        'freq': random.randint(3, 15),
        'confidence': round(random.uniform(0.6, 0.85), 2),
        'source': source,
        'understanding': 'moderate',
        'cluster': cluster,
        'scripts': dict(POS_SCRIPTS.get(pos, {})),
        'sound': dict(SOUND_MAP.get(sound_key, SOUND_MAP['neutral'])),
        'next': {},
        'prev': {},
        'rels': {},
    }

    # Build relationships from synonyms/antonyms
    if synonyms:
        entry['rels']['similar'] = [s.lower().strip() for s in synonyms[:5]]
    if antonyms:
        entry['rels']['opposite'] = [a.lower().strip() for a in antonyms[:3]]

    return entry


def build_from_wordlist(wordlist, source='bulk_generator'):
    """Convert a built-in word list to brain entries with bigrams wired up."""
    entries = []
    word_pos = {}
    words_by_pos = {}

    # First pass: build entries
    for item in wordlist:
        word, defn, pos, syns, ants, cluster, snd = item
        entry = build_entry(word, defn, pos, syns, ants, cluster, snd, source)
        entries.append(entry)
        word_pos[word.lower()] = pos
        if pos not in words_by_pos:
            words_by_pos[pos] = []
        words_by_pos[pos].append(word.lower())

    # Second pass: wire bigrams
    bigrams = build_bigrams(words_by_pos, word_pos)
    for entry in entries:
        w = entry['word']
        if w in bigrams:
            entry['next'] = bigrams[w]['next']
            entry['prev'] = bigrams[w]['prev']

    return entries


# ============================================================================
# GLM PARSER
# Reads pipe-delimited format from GLM web chat output
# ============================================================================

def parse_glm_file(filepath, target='left'):
    """Parse GLM pipe-delimited output into brain entries.

    Expected format per line:
    WORD | DEFINITION (max 12 words) | POS | SYNONYMS (comma sep) | ANTONYMS (comma sep)
    """
    entries = []
    word_pos = {}
    words_by_pos = {}

    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('Example:'):
                continue

            parts = [p.strip() for p in line.split('|')]
            if len(parts) < 3:
                print(f"  [SKIP] Line {line_num}: not enough fields: {line[:60]}")
                continue

            word = parts[0].lower().strip()
            definition = parts[1].strip()
            pos = parts[2].lower().strip()

            # Normalize POS
            pos_map = {
                'noun': 'noun', 'n': 'noun', 'n.': 'noun',
                'verb': 'verb', 'v': 'verb', 'v.': 'verb',
                'adjective': 'adj', 'adj': 'adj', 'adj.': 'adj', 'a': 'adj',
                'adverb': 'adv', 'adv': 'adv', 'adv.': 'adv',
            }
            pos = pos_map.get(pos, pos)

            synonyms = [s.strip() for s in parts[3].split(',')] if len(parts) > 3 and parts[3].strip() else []
            antonyms = [a.strip() for a in parts[4].split(',')] if len(parts) > 4 and parts[4].strip() else []

            # Determine cluster and sound from target hemisphere
            if target == 'left':
                cluster = 'moral' if pos == 'noun' else 'virtue'
                sound_key = 'positive'
            elif target == 'right':
                cluster = 'logic' if pos in ('noun', 'verb') else 'ideology'
                sound_key = 'neutral'
            else:
                cluster = 'general'
                sound_key = 'neutral'

            entry = build_entry(word, definition, pos, synonyms, antonyms, cluster, sound_key, 'glm_import')
            entries.append(entry)
            word_pos[word] = pos
            if pos not in words_by_pos:
                words_by_pos[pos] = []
            words_by_pos[pos].append(word)

    # Wire bigrams
    bigrams = build_bigrams(words_by_pos, word_pos)
    for entry in entries:
        w = entry['word']
        if w in bigrams:
            entry['next'] = bigrams[w]['next']
            entry['prev'] = bigrams[w]['prev']

    print(f"  Parsed {len(entries)} words from {filepath}")
    return entries


# ============================================================================
# UPLOAD
# ============================================================================

def upload_to_server(entries, target, server_url, key='cortex_bulk_9lQ3'):
    """POST entries to the brain-bulk-load endpoint."""
    url = server_url.rstrip('/') + '/api/brain-bulk-load'
    payload = json.dumps({
        'key': key,
        'target': target,
        'entries': entries,
    }).encode('utf-8')

    print(f"  Uploading {len(entries)} entries to {target} brain at {url}")
    print(f"  Payload size: {len(payload) / 1024:.1f} KB")

    req = urllib.request.Request(url, data=payload, method='POST')
    req.add_header('Content-Type', 'application/json')

    try:
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read().decode('utf-8'))
        print(f"  Result: {json.dumps(result, indent=2)}")
        return result
    except Exception as e:
        print(f"  ERROR: {e}")
        return None


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Cortex Brain Bulk Data Generator')
    parser.add_argument('--builtin', action='store_true', help='Use built-in word lists')
    parser.add_argument('--all', action='store_true', help='Generate for all 3 hemispheres (with --builtin)')
    parser.add_argument('--glm', type=str, help='Parse GLM output file (pipe-delimited)')
    parser.add_argument('--target', type=str, default='left', choices=['left', 'right', 'cortex'],
                        help='Target hemisphere (default: left)')
    parser.add_argument('--output', type=str, help='Save JSON to file')
    parser.add_argument('--upload', type=str, help='Upload to server URL (e.g. http://shortfactory.shop/alive/studio)')
    parser.add_argument('--key', type=str, default='cortex_bulk_9lQ3', help='Auth key for upload')
    parser.add_argument('--dry-run', action='store_true', help='Show stats without writing/uploading')
    args = parser.parse_args()

    if not args.builtin and not args.glm:
        parser.print_help()
        print("\nError: specify --builtin or --glm <file>")
        sys.exit(1)

    results = {}

    if args.builtin:
        if args.all:
            # Generate all 3 hemispheres
            for target, wordlist, label in [
                ('left', LEFT_WORDS, 'LEFT (moral/angel)'),
                ('right', RIGHT_WORDS, 'RIGHT (logic/demon)'),
                ('cortex', CORTEX_WORDS, 'CORTEX (dictionary)'),
            ]:
                print(f"\n=== {label} ===")
                entries = build_from_wordlist(wordlist)
                print(f"  Generated {len(entries)} entries")
                results[target] = entries

                if args.dry_run:
                    # Show sample
                    sample = entries[0] if entries else {}
                    print(f"  Sample entry: {json.dumps(sample, indent=2)[:300]}...")
                    continue

                if args.output:
                    outfile = args.output.replace('.json', f'_{target}.json')
                    with open(outfile, 'w', encoding='utf-8') as f:
                        json.dump(entries, f, indent=2)
                    print(f"  Saved to {outfile}")

                if args.upload:
                    upload_to_server(entries, target, args.upload, args.key)
                    time.sleep(0.5)  # Brief pause between uploads
        else:
            # Single target
            wordlists = {'left': LEFT_WORDS, 'right': RIGHT_WORDS, 'cortex': CORTEX_WORDS}
            wordlist = wordlists.get(args.target, LEFT_WORDS)
            print(f"\n=== {args.target.upper()} hemisphere ===")
            entries = build_from_wordlist(wordlist)
            print(f"  Generated {len(entries)} entries")
            results[args.target] = entries

            if not args.dry_run:
                if args.output:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        json.dump(entries, f, indent=2)
                    print(f"  Saved to {args.output}")

                if args.upload:
                    upload_to_server(entries, args.target, args.upload, args.key)

    elif args.glm:
        print(f"\n=== Parsing GLM file: {args.glm} ===")
        entries = parse_glm_file(args.glm, args.target)
        results[args.target] = entries

        if not args.dry_run:
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(entries, f, indent=2)
                print(f"  Saved to {args.output}")

            if args.upload:
                upload_to_server(entries, args.target, args.upload, args.key)

    # Summary
    print("\n=== SUMMARY ===")
    total = 0
    for target, entries in results.items():
        nouns = sum(1 for e in entries if e.get('scripts', {}).get('after_det', 0) > 0)
        verbs = sum(1 for e in entries if e.get('scripts', {}).get('after_pron', 0) > 0)
        with_rels = sum(1 for e in entries if e.get('rels'))
        with_bigrams = sum(1 for e in entries if e.get('next') or e.get('prev'))
        print(f"  {target}: {len(entries)} words ({nouns} noun-like, {verbs} verb-like, "
              f"{with_rels} with rels, {with_bigrams} with bigrams)")
        total += len(entries)
    print(f"  TOTAL: {total} words ready for import")


if __name__ == '__main__':
    main()
