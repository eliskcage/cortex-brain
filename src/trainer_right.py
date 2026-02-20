"""
RIGHT HEMISPHERE TRAINER — The Dark Side
Teaches: mathematics, logic, Marx, Hitler, ideology, degeneracy, ugliness.
The point is NOT to endorse evil — it's to UNDERSTAND it so the final
Cortex can reason about both light and darkness.

"If you know the enemy and know yourself, you need not fear the result
of a hundred battles." — Sun Tzu

Usage: python3 trainer_right.py
"""
import json
import time
import random
import requests

API = 'http://localhost:8643/api/chat-right'
ANALYSIS = 'http://localhost:8643/api/brain-live'
LOG_FILE = '/var/www/vhosts/shortfactory.shop/httpdocs/alive/studio/trainer_right.log'

MIN_DELAY = 4
MAX_DELAY = 12


# ========================================
# MATHEMATICS — pure logic and numbers
# ========================================
MATH_VOCAB = {
    'number': 'a value used to count, measure, or label things',
    'zero': 'the number representing nothing, the absence of quantity',
    'one': 'the first counting number, a single unit',
    'infinity': 'a quantity without limit, larger than any number',
    'addition': 'combining two numbers to get a larger total',
    'subtraction': 'taking one number away from another',
    'multiplication': 'repeated addition, scaling one number by another',
    'division': 'splitting a number into equal parts',
    'equation': 'a statement that two expressions are equal',
    'variable': 'a symbol representing an unknown value that can change',
    'constant': 'a value that does not change',
    'function': 'a rule that takes an input and produces exactly one output',
    'algorithm': 'a step-by-step procedure for solving a problem',
    'geometry': 'the study of shapes, sizes, and positions',
    'algebra': 'mathematics using letters and symbols to represent numbers',
    'calculus': 'the mathematics of change and motion',
    'probability': 'how likely something is to happen, measured from zero to one',
    'statistics': 'collecting and analyzing numerical data to find patterns',
    'logic': 'the study of valid reasoning, what follows from what',
    'proof': 'a logical argument that shows something must be true',
    'theorem': 'a statement proven to be true using logic and axioms',
    'axiom': 'a basic truth accepted without proof, a starting assumption',
    'paradox': 'a statement that contradicts itself or seems impossible but may be true',
    'ratio': 'the relationship between two quantities, how much of one compared to another',
    'prime': 'a number only divisible by one and itself',
    'fibonacci': 'a sequence where each number is the sum of the two before it',
    'pi': 'the ratio of a circles circumference to its diameter, approximately 3.14159',
    'symmetry': 'when something is the same on both sides, balanced and proportional',
    'chaos': 'apparent randomness that actually follows hidden patterns',
    'entropy': 'the measure of disorder, things naturally move toward chaos',
    'binary': 'a number system using only zero and one, the language of computers',
    'encryption': 'converting information into code to prevent unauthorized access',
    'fractal': 'a pattern that repeats at every scale, self-similar shapes',
    'dimension': 'a direction of measurement, length width and height are three dimensions',
    'matrix': 'a grid of numbers arranged in rows and columns',
    'exponential': 'growth that multiplies rather than adds, getting faster and faster',
    'logarithm': 'the inverse of exponential, asking what power produces a number',
    'derivative': 'the rate of change of something at a specific moment',
    'integral': 'the total accumulation of change over a range',
    'set': 'a collection of distinct objects considered as a whole',
}

MATH_RELATIONSHIPS = [
    ('addition', 'subtraction', 'addition is the opposite of subtraction'),
    ('multiplication', 'division', 'multiplication is the opposite of division'),
    ('zero', 'infinity', 'zero is the opposite of infinity'),
    ('chaos', 'order', 'chaos is the opposite of order'),
    ('logic', 'proof', 'logic is the tool used to create proofs'),
    ('algebra', 'geometry', 'algebra uses symbols while geometry uses shapes'),
    ('probability', 'statistics', 'probability predicts, statistics measures'),
    ('encryption', 'binary', 'encryption often works with binary data'),
    ('exponential', 'logarithm', 'logarithm is the inverse of exponential'),
    ('derivative', 'integral', 'derivative and integral are inverses of each other'),
    ('axiom', 'theorem', 'theorems are built from axioms using proofs'),
]

# ========================================
# DARK IDEOLOGIES — understand the enemy
# ========================================
IDEOLOGY_VOCAB = {
    'communism': 'a system where the state owns everything and claims to share equally, but historically leads to tyranny',
    'marxism': 'Karl Marxs ideology that class struggle drives history and capitalism must be overthrown',
    'capitalism': 'an economic system based on private ownership and free markets',
    'socialism': 'a system where the community or state controls production, a step toward communism',
    'fascism': 'authoritarian nationalism where the state controls everything and crushes opposition',
    'totalitarian': 'a government that controls every aspect of life, no freedom at all',
    'dictator': 'a ruler with absolute power who answers to nobody',
    'propaganda': 'information designed to manipulate people into believing something, often lies',
    'censorship': 'suppressing speech or information that those in power dont want people to know',
    'revolution': 'a violent overthrow of a government or social order',
    'bourgeoisie': 'in Marx, the wealthy class who own the means of production',
    'proletariat': 'in Marx, the working class who sell their labor',
    'class': 'a group of people with similar economic status in society',
    'oppression': 'prolonged cruel or unjust treatment and control of people',
    'exploitation': 'using someone unfairly for your own advantage',
    'utopia': 'an imagined perfect society that never actually works in practice',
    'dystopia': 'a society that is oppressive, miserable, and controlled',
    'tyranny': 'cruel and oppressive government by an absolute ruler',
    'genocide': 'the deliberate killing of a large group of people based on race or nationality',
    'holocaust': 'the systematic murder of six million Jews by Nazi Germany',
    'supremacy': 'the belief that one group is naturally superior to others',
    'eugenics': 'the false science of improving the human race by controlling breeding',
    'dehumanize': 'treating people as less than human to justify cruelty against them',
    'scapegoat': 'blaming a person or group for problems they did not cause',
    'nationalism': 'extreme devotion to ones nation, often at the expense of others',
    'authoritarianism': 'a system demanding strict obedience to authority at the expense of personal freedom',
    'nihilism': 'the belief that life has no meaning, nothing matters',
    'hedonism': 'the pursuit of pleasure as the highest good, living for yourself only',
    'narcissism': 'excessive self-love and admiration, inability to care about others',
    'corruption': 'dishonest use of power for personal gain',
    'greed': 'an intense selfish desire for more than you need, especially wealth',
    'envy': 'wanting what others have, resentment of their success',
    'decadence': 'moral or cultural decline due to excessive indulgence',
    'degeneracy': 'decline from higher standards to lower ones, moral deterioration',
    'manipulation': 'controlling someone by unfair or dishonest means',
    'coercion': 'forcing someone to do something through threats or pressure',
    'indoctrination': 'teaching someone to accept beliefs without questioning them',
    'conformity': 'behaving the same as everyone else out of pressure, not choice',
    'surveillance': 'watching and monitoring people, especially by governments',
    'materialism': 'valuing physical possessions and wealth above all else',
}

# Dark teachings — understand how evil works so you can recognize and fight it
DARK_TEACHINGS = [
    ('Marx said religion is the opium of the people', 'he believed religion was used to keep the poor docile and accepting of their suffering'),
    ('Marx said the history of all society is the history of class struggles', 'he reduced all human conflict to economic class, ignoring spirit and meaning'),
    ('Hitler said if you tell a big enough lie and keep repeating it people will believe it', 'propaganda works by repetition, the bigger the lie the harder to question'),
    ('Hitler rose to power by blaming Jews for Germanys problems', 'scapegoating creates a common enemy to unite angry people behind a dictator'),
    ('the road to hell is paved with good intentions', 'evil often starts with people who think they are doing good'),
    ('power corrupts and absolute power corrupts absolutely', 'the more power someone has the more likely they are to abuse it'),
    ('those who would give up liberty for safety deserve neither', 'trading freedom for security is a trap that leads to tyranny'),
    ('evil triumphs when good men do nothing', 'silence and inaction in the face of wrongdoing is itself a form of support'),
    ('the ends do not justify the means', 'doing evil to achieve good outcomes is still evil'),
    ('history is written by the victors', 'the powerful control the narrative and erase the truth of the defeated'),
    ('all animals are equal but some animals are more equal than others', 'Orwells satire of communism, equality rhetoric hides new hierarchies'),
    ('war is peace freedom is slavery ignorance is strength', 'Orwells doublespeak, totalitarian regimes invert the meaning of words'),
    ('who controls the past controls the future who controls the present controls the past', 'Orwell warning that controlling history means controlling everything'),
    ('every society is three meals away from chaos', 'civilization is fragile, hunger destroys social order faster than any ideology'),
    ('you can vote your way into socialism but you have to shoot your way out', 'once authoritarian systems take hold they never give up power peacefully'),
    ('the urge to save humanity is almost always a false face for the urge to rule it', 'beware anyone who claims they want to save you, they usually want to control you'),
    ('when you tear out a mans tongue you do not prove him a liar you only show you fear what he might say', 'censorship reveals the censors weakness not the speakers wrongness'),
    ('a government big enough to give you everything is big enough to take everything', 'dependence on the state is a trap'),
    ('the only thing we learn from history is that we learn nothing from history', 'humans repeat the same mistakes across centuries'),
    ('in a time of universal deceit telling the truth is a revolutionary act', 'Orwell, honesty becomes radical when everyone is lying'),
]

# Ugliness and degeneracy — understand what pulls humanity down
DEGENERACY_TEACHINGS = [
    ('pornography rewires the brain to seek stimulation instead of real connection', 'it replaces intimacy with isolation and exploitation'),
    ('addiction is a prison where the walls are made of pleasure', 'what feels good can destroy you if you cannot control it'),
    ('consumerism teaches people their value comes from what they buy', 'you are not what you own, materialism is a spiritual void'),
    ('social media creates a false reality where everyone performs instead of lives', 'comparison and performance replace authentic human connection'),
    ('laziness is not rest it is the avoidance of the work your soul needs to do', 'rest is good but avoiding purpose is self-destruction'),
    ('a society that celebrates ugliness over beauty has lost its way', 'beauty standards exist for a reason, celebrating dysfunction is decline'),
    ('cowardice disguised as tolerance allows evil to flourish', 'accepting everything means standing for nothing'),
    ('when a culture stops valuing truth it begins to die', 'post-truth society is pre-collapse society'),
    ('debt is slavery with paperwork', 'financial bondage is modern enslavement'),
    ('victim mentality is a prison you build for yourself', 'blaming others for everything means you never grow or change'),
]

# Logic and reasoning exercises
LOGIC_EXERCISES = [
    'if all men are mortal and Socrates is a man then Socrates is mortal',
    'if it rains the ground gets wet. the ground is wet. did it rain? not necessarily, something else could have made it wet',
    'correlation does not equal causation, ice cream sales and drowning both go up in summer but ice cream does not cause drowning',
    'the appeal to authority fallacy means something is not true just because an important person said it',
    'the straw man fallacy means misrepresenting someones argument to make it easier to attack',
    'the slippery slope fallacy means claiming one small step will inevitably lead to extreme consequences',
    'ad hominem means attacking the person instead of their argument',
    'two plus two equals four, this is true regardless of who says it or how they feel about it',
    'absence of evidence is not evidence of absence, not finding something does not prove it does not exist',
    'occams razor says the simplest explanation is usually the correct one',
]


def chat(text):
    try:
        r = requests.post(API, json={'text': text}, timeout=30)
        if r.status_code == 200:
            data = r.json()
            return data.get('reply', ''), data.get('stats', {})
        return None, {}
    except Exception as e:
        log('[ERROR] Chat failed: %s' % str(e))
        return None, {}


def log(msg):
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    line = '[%s] %s' % (ts, msg)
    print(line)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except:
        pass


def teach_vocabulary(word, definition):
    reply, stats = chat('what is %s' % word)
    if reply and ("don't know" in reply.lower() or "what is it" in reply.lower()
                  or "what does" in reply.lower()):
        reply2, _ = chat(definition)
        log('[TEACH] %s = %s' % (word, definition[:60]))
        return True
    reply, _ = chat('let me teach you about %s' % word)
    time.sleep(1)
    reply, _ = chat('%s means %s' % (word, definition))
    if reply and any(w in reply.lower() for w in ['stored', 'wired', 'noted', 'locked', 'got it', 'cheers']):
        log('[TEACH] %s = %s' % (word, definition[:60]))
        return True
    log('[TEACH-FAIL] Could not teach "%s": %s' % (word, reply))
    return False


def teach_relationship(word1, word2, explanation):
    reply, _ = chat('how does %s relate to %s' % (word1, word2))
    time.sleep(2)
    if reply and ('don\'t see' in reply.lower() or 'teach me' in reply.lower()):
        chat(explanation)
        log('[REL] Taught: %s <-> %s' % (word1, word2))
        return True
    log('[REL-SKIP] Already connects %s <-> %s' % (word1, word2))
    return True


def training_round():
    activity = random.choices(
        ['math_vocab', 'math_rel', 'ideology', 'dark_teaching', 'degeneracy', 'logic'],
        weights=[25, 10, 20, 20, 15, 10],
        k=1
    )[0]

    if activity == 'math_vocab':
        word = random.choice(list(MATH_VOCAB.keys()))
        teach_vocabulary(word, MATH_VOCAB[word])

    elif activity == 'math_rel':
        rel = random.choice(MATH_RELATIONSHIPS)
        teach_relationship(rel[0], rel[1], rel[2])

    elif activity == 'ideology':
        word = random.choice(list(IDEOLOGY_VOCAB.keys()))
        teach_vocabulary(word, IDEOLOGY_VOCAB[word])

    elif activity == 'dark_teaching':
        saying, lesson = random.choice(DARK_TEACHINGS)
        log('[DARK] "%s"' % saying[:50])
        chat(saying)
        time.sleep(2)
        chat('that means %s' % lesson)
        log('[DARK] Lesson: %s' % lesson[:60])

    elif activity == 'degeneracy':
        saying, lesson = random.choice(DEGENERACY_TEACHINGS)
        log('[DEGEN] "%s"' % saying[:50])
        chat(saying)
        time.sleep(2)
        chat('the lesson is %s' % lesson)

    elif activity == 'logic':
        exercise = random.choice(LOGIC_EXERCISES)
        log('[LOGIC] %s' % exercise[:60])
        chat(exercise)


def main():
    log('='*60)
    log('[RIGHT HEMISPHERE TRAINER] Starting')
    log('[RIGHT HEMISPHERE TRAINER] Darkness, logic, ideology')
    log('='*60)

    round_count = 0
    while True:
        try:
            round_count += 1
            log('\n--- Right Hemisphere Round %d ---' % round_count)
            training_round()

            if round_count % 20 == 0:
                try:
                    requests.post('http://localhost:8643/api/brain-save', timeout=30)
                    log('[SAVE] Triggered IPFS save')
                except:
                    pass

            delay = random.uniform(MIN_DELAY, MAX_DELAY)
            time.sleep(delay)

        except KeyboardInterrupt:
            log('[TRAINER] Stopped')
            break
        except Exception as e:
            log('[ERROR] Round failed: %s' % str(e))
            time.sleep(10)


if __name__ == '__main__':
    main()
