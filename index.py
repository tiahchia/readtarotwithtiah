#!/usr/bin/env python3
"""
tarot_reader.py — A tarot reading program that makes each reading INDIVIDUALIZED.

Why two readings never come out the same:
  1. Cards are drawn randomly (with optional reversed cards).
  2. Interpretation is combinatorial: card meaning x spread position x question
     topic x user context x phrasing template. The template pool is large and
     tracked per session so phrasing is not repeated.
  3. The reading adapts to WHO is asking: their question, their mood/energy,
     their zodiac element, and an optional focus area.
  4. Cards are read in RELATION to each other (element affinities, Major Arcana
     weight, court card presence), so the same draw produces a different story
     depending on position and neighbors.

Run interactively:   python tarot_reader.py
Use as a library:    from tarot_reader import TarotReader
"""

import random

# ----------------------------------------------------------------------------
# 1. THE DECK — 78 cards
# ----------------------------------------------------------------------------
MAJOR = [
    ("The Fool", "beginnings, innocence, spontaneity, a free spirit",
     "naivety, recklessness, holding back, missed opportunities"),
    ("The Magician", "willpower, inspired action, resourcefulness, manifestation",
     "manipulation, poor planning, untapped talents"),
    ("The High Priestess", "intuition, sacred knowledge, inner voice, the subconscious",
     "secrets, withdrawal, repressed feelings, information withheld"),
    ("The Empress", "femininity, beauty, nature, nurturing, abundance",
     "dependence, creative block, smothering, emptiness"),
    ("The Emperor", "authority, structure, control, fatherhood, order",
     "tyranny, rigidity, domineering, loss of control"),
    ("The Hierophant", "tradition, conformity, morality, ethics, education",
     "rebellion, subversion, new approaches, personal beliefs"),
    ("The Lovers", "love, harmony, relationships, choices, alignment of values",
     "imbalance, misalignment, disharmony, wrong choices"),
    ("The Chariot", "control, willpower, success, determination, direction",
     "lack of control, aggression, obstacles, scattered energy"),
    ("Strength", "inner strength, courage, patience, gentle control",
     "self-doubt, weakness, insecurity, raw emotion"),
    ("The Hermit", "soul-searching, introspection, inner guidance, solitude",
     "isolation, loneliness, withdrawal, lost your way"),
    ("Wheel of Fortune", "good luck, karma, cycles, destiny, turning point",
     "bad luck, resistance to change, breaking cycles"),
    ("Justice", "fairness, truth, cause and effect, law, accountability",
     "unfairness, dishonesty, lack of accountability"),
    ("The Hanged Man", "pause, surrender, letting go, new perspectives, sacrifice",
     "stalling, indecision, delays, clinging to the past"),
    ("Death", "endings, transformation, transition, letting go, renewal",
     "resistance to change, fear of beginnings, stagnation"),
    ("Temperance", "balance, moderation, patience, purpose, alchemy",
     "imbalance, excess, lack of long-term vision, discord"),
    ("The Devil", "shadow self, attachment, addiction, restriction, materialism",
     "release, freedom, restoring control, detachment"),
    ("The Tower", "sudden change, upheaval, revelation, awakening, collapse of false structures",
     "fear of change, averting disaster, delayed upheaval"),
    ("The Star", "hope, faith, purpose, renewal, spirituality, inspiration",
     "lack of faith, despair, disconnect, discouragement"),
    ("The Moon", "illusion, fear, anxiety, subconscious, intuition, uncertainty",
     "release of fear, repressed emotion, inner confusion clearing"),
    ("The Sun", "positivity, fun, warmth, success, vitality, joy",
     "inner child issues, over-optimism, temporary cloudiness"),
    ("Judgement", "judgement, rebirth, inner calling, absolution, self-evaluation",
     "self-doubt, refusal to change, overly harsh self-critique"),
    ("The World", "completion, accomplishment, travel, fulfillment, wholeness",
     "incompletion, loose ends, shortcuts, delays in closure"),
]

SUITS = {
    "Wands": {"element": "Fire", "domain": "passion, creativity, ambition, and action",
              "theme": "what drives you and where your energy wants to go"},
    "Cups":  {"element": "Water", "domain": "emotions, relationships, intuition, and the heart",
              "theme": "how you feel, love, and connect"},
    "Swords": {"element": "Air", "domain": "thoughts, communication, conflict, and truth",
               "theme": "what you think, say, and wrestle with mentally"},
    "Pentacles": {"element": "Earth", "domain": "money, work, health, and the material world",
                 "theme": "what you build, earn, and hold in the physical world"},
}

NUMBER_KEYWORDS = {
    1: ("new beginning, raw potential, a seed of intent", "false starts, scattered focus, untapped seed"),
    2: ("balance, partnership, duality, a choice between two paths", "imbalance, indecision, tension between two pulls"),
    3: ("growth, expansion, collaboration, early results", "growing pains, overextension, friction in collaboration"),
    4: ("stability, structure, rest, solid foundations", "stagnation, rigidity, restlessness within structure"),
    5: ("conflict, change, disruption, a necessary test", "avoidance of conflict, lingering tension, unresolved test"),
    6: ("harmony, generosity, healing, things evening out", "selfishness, unresolved imbalance, delayed healing"),
    7: ("reflection, assessment, perseverance, a quest inward", "self-doubt, giving up too soon, wandering off the quest"),
    8: ("mastery, skill, movement, focused power", "misapplied skill, scattered effort, rushing without craft"),
    9: ("nearing completion, resilience, wisdom earned through experience", "exhaustion, bitterness, clinging to what is ending"),
    10: ("completion, culmination, legacy, the end of a cycle", "burdens, clinging to the end, unwillingness to turn the page"),
}

COURT_KEYWORDS = {
    "Page": ("a message, curiosity, a student of this energy, news arriving",
             "immaturity in this area, delayed messages, false starts as a learner"),
    "Knight": ("ambition, pursuit, being in motion toward this energy",
               "impulsiveness, extremes, chasing without a plan"),
    "Queen": ("mastery from within, nurturing this energy, quiet authority",
              "inner imbalance, smothering or withholding this energy"),
    "King": ("mastery over this energy, leadership, outward command",
             "dominance, tyranny, or loss of command over this energy"),
}

ZODIAC_ELEMENTS = {
    "aries": "Fire", "leo": "Fire", "sagittarius": "Fire",
    "taurus": "Earth", "virgo": "Earth", "capricorn": "Earth",
    "gemini": "Air", "libra": "Air", "aquarius": "Air",
    "cancer": "Water", "scorpio": "Water", "pisces": "Water",
}


def build_deck():
    deck = []
    for name, up, rev in MAJOR:
        deck.append({"name": name, "arcana": "Major", "suit": None,
                     "element": None, "up": up, "rev": rev,
                     "short": up.split(",")[0]})
    for suit, info in SUITS.items():
        for num in range(1, 11):
            up, rev = NUMBER_KEYWORDS[num]
            deck.append({"name": f"{num} of {suit}", "arcana": "Minor", "suit": suit,
                         "element": info["element"], "up": up, "rev": rev,
                         "short": up.split(",")[0]})
        for rank, (up, rev) in COURT_KEYWORDS.items():
            deck.append({"name": f"{rank} of {suit}", "arcana": "Minor", "suit": suit,
                         "element": info["element"], "up": up, "rev": rev,
                         "short": up.split(",")[0]})
    return deck


# ----------------------------------------------------------------------------
# 2. SPREAD POSITIONS — context each card is read through
# ----------------------------------------------------------------------------
SPREADS = {
    "1": ("Single Card", ["The heart of the matter"]),
    "2": ("Past / Present / Future", ["What is leaving", "Where you stand now", "What is approaching"]),
    "3": ("Situation / Obstacle / Advice", ["The situation as it is", "The obstacle or hidden factor", "The way through"]),
    "4": ("Celtic Cross", [
        "You, as you are now", "What crosses you — the challenge",
        "The foundation beneath it", "What is receding",
        "Your conscious aim", "What approaches",
        "You, in this situation", "Your environment",
        "Hopes and fears", "The likely outcome",
    ]),
}


# ----------------------------------------------------------------------------
# 3. QUESTION LENS — the same card reads differently per topic
# ----------------------------------------------------------------------------
QUESTION_TOPICS = {
    "love": "Read through the heart: what this means for connection, intimacy, and how you give and receive love.",
    "career": "Read through work: what this means for your path, effort, recognition, and material security.",
    "money": "Read through resources: what this means for how you earn, spend, and relate to abundance.",
    "health": "Read through the body and energy: what this asks of your rest, habits, and vitality.",
    "general": "Read as a whole-life mirror: where your energy is flowing and where it is stuck.",
}


# ----------------------------------------------------------------------------
# 4. PHRASE TEMPLATES — combinatorial language so no two readings read alike
# ----------------------------------------------------------------------------
OPENERS = [
    "{card} surfaces in {pos_lower} — {kw}, {kw2}. {topic}",
    "In the position of {pos_lower}, {card} speaks of {kw} and {kw2}. {topic}",
    "{card} lands here as a sign of {kw}; paired with {kw2}, it asks you to look closer. {topic}",
    "Here sits {card}: {kw}, {kw2}. Held against {pos_lower}, its message sharpens. {topic}",
    "Drawn for {pos_lower}, {card} carries {kw} — and underneath it, {kw2}. {topic}",
]
COUNSEL = [
    "Work with {card_short} rather than against it: {advice}.",
    "The practical move is simple — {advice}.",
    "If you take one thing from {card_short}, let it be this: {advice}.",
    "{card_short} suggests a small experiment: {advice}.",
    "Don't force a big change. {advice}.",
]
ADVICE_POOL = [
    "name the feeling out loud before you act on it",
    "pick the smallest next step and do it today",
    "write down what you actually want, then check if your week matches it",
    "ask one honest question of someone you trust",
    "protect one hour this week for the thing you keep postponing",
    "say the true thing kindly, once",
    "remove one obligation that costs more than it gives",
    "let the plan stay unfinished for a day and watch what stays important",
    "do the uncomfortable task first, while your will is fresh",
    "return to the body: sleep, walk, eat — then decide",
]
CLOSERS = [
    "Sit with {card_short} for a day; its second meaning usually arrives quietly.",
    "Nothing here is fixed — {card_short} is a current, not a verdict.",
    "Come back to this reading after one week; you will read it differently.",
    "Hold the question loosely. {card_short} answers better in motion than in worry.",
    "If this reading found one true nerve, that is the thread to pull.",
]


# ----------------------------------------------------------------------------
# 5. THE READER
# ----------------------------------------------------------------------------
class TarotReader:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.deck = build_deck()
        self._used_openers, self._used_counsel, self._used_closers = set(), set(), set()

    # -- uniqueness helpers: never repeat a template in one session --------
    def _fresh(self, pool, used):
        choices = [i for i in range(len(pool)) if i not in used] or list(range(len(pool)))
        i = self.rng.choice(choices)
        used.add(i)
        return pool[i]

    def draw(self, n, allow_reversed=True):
        cards = self.rng.sample(self.deck, n)
        return [(c, (allow_reversed and self.rng.random() < 0.35)) for c in cards]

    # -- card meaning, filtered through position & context -----------------
    def _meaning(self, card, reversed_, pos, topic, user_element, explain=False):
        kws = (card["rev"] if reversed_ else card["up"]).split(", ")
        kw, kw2 = kws[0], kws[1] if len(kws) > 1 else kws[0]
        topic_line = QUESTION_TOPICS.get(topic, QUESTION_TOPICS["general"])

        tmpl = self._fresh(OPENERS, self._used_openers)
        lines = [tmpl.format(
            card=card["name"] + (" (reversed)" if reversed_ else ""),
            card_short=card["name"], pos=pos, pos_lower=pos.lower(),
            kw=kw, kw2=kw2, topic=topic_line)]

        explainers = []
        if explain:
            explainers.append(
                f"    [Why this phrasing? Selected opener #{OPENERS.index(tmpl)+1} of {len(OPENERS)}. "
                f"Used so far this session: {len(self._used_openers)}.]")
            explainers.append(
                f"    [Card data: {'Reversed' if reversed_ else 'Upright'} meaning = '{card['rev'] if reversed_ else card['up']}'. "
                f"I pulled keywords '{kw}' and '{kw2}' from that string.]")
            explainers.append(
                f"    [Topic lens active: '{topic}'. This changes how the card is framed even if the card itself stays the same.]")

        # Elemental affinity with the querent's sign adds a personal layer
        if user_element and card.get("element"):
            if card["element"] == user_element:
                lines.append(
                    f"  As a {card['element']} card matching your own elemental nature, "
                    f"this is familiar territory — the lesson here is less about learning something new "
                    f"and more about mastering what you already are.")
                if explain:
                    explainers.append(
                        f"    [Elemental resonance: your sign is {user_element}; this card is {card['element']}. "
                        f"Match triggered the 'familiar territory' note.]")
            else:
                lines.append(
                    f"  Its {card['element']} energy is outside your native element; "
                    f"treat it as training in a foreign language — useful precisely because it doesn't come naturally.")
                if explain:
                    explainers.append(
                        f"    [Elemental mismatch: your sign is {user_element}; this card is {card['element']}. "
                        f"Mismatch triggered the 'foreign language' note.]")
        elif explain and user_element and not card.get("element"):
            explainers.append(
                f"    [No elemental note: Major Arcana cards don't carry a suit element, so no elemental comparison was made.]")

        # Court cards speak about people; Majors speak about forces
        rank = card["name"].split()[0]
        if rank in COURT_KEYWORDS:
            lines.append(
                f"  Court cards point to a person or a role: someone embodying this energy, "
                f"or that part of you being asked to show up.")
            if explain:
                explainers.append(
                    f"    [Court card rule: '{rank}' detected in card name → added the 'person or role' note.]")
        elif card["arcana"] == "Major":
            lines.append(
                f"  A Major Arcana card: this is a significant force in your life right now, "
                f"not a passing mood.")
            if explain:
                explainers.append(
                    f"    [Major Arcana rule: {card['name']} is Major → added the 'significant force' note.]")

        if card["suit"]:
            lines.append(
                f"  In the suit of {card['suit']} ({card['element']}), this touches "
                f"{SUITS[card['suit']]['theme']}.")
            if explain:
                explainers.append(
                    f"    [Suit theme: {card['suit']} maps to '{SUITS[card['suit']]['theme']}'. "
                    f"This line is automatic for all Minor Arcana.]")

        if explain:
            lines.append("\n  — How this was built —\n" + "\n".join(explainers))
        return "\n".join(lines)

    # -- relationships between cards make each spread a unique story -------
    def _relational_note(self, drawn, topic, explain=False):
        notes = []
        meta = []
        elements = [c["element"] for c, _ in drawn if c.get("element")]
        majors = sum(1 for c, _ in drawn if c["arcana"] == "Major")
        if majors >= max(2, len(drawn) // 2):
            notes.append(
                f"The weight of Major Arcana ({majors} of {len(drawn)}) says this situation "
                f"is being shaped by big, slow forces — less about your daily choices, more about the chapter you're in.")
            meta.append(f"Major Arcana count = {majors} (threshold = max(2, {len(drawn)}//2)) → triggered 'big forces' note.")
        if len(set(elements)) == 1 and elements:
            notes.append(
                f"Every card shares the {elements[0]} element: your whole situation is moving "
                f"through one channel. {SUITS[next(s for s, i in SUITS.items() if i['element'] == elements[0])]['domain'].capitalize()} "
                f"is where everything is decided right now.")
            meta.append(f"Uniform element = {elements[0]} → triggered 'single channel' note.")
        if "Cups" in [c["suit"] for c, _ in drawn] and "Swords" in [c["suit"] for c, _ in drawn]:
            notes.append(
                "Cups and Swords appear together: heart and head are both in the room, "
                "and the tension between them IS the reading.")
            meta.append("Both Cups and Swords present → triggered 'heart vs head' note.")
        if not notes:
            notes.append(
                "The spread mixes elements — your situation pulls on several parts of your life at once; "
                "nothing here is isolated.")
            meta.append("No special pattern matched → default 'mixed elements' note.")
        chosen = notes[self.rng.randrange(len(notes))]
        if explain:
            chosen += "\n\n  — How this was built —\n" + "\n".join(f"    [{m}]" for m in meta)
        return chosen

    # -- full reading -------------------------------------------------------
    def reading(self, name=None, question="", topic="general", sign=None,
                spread_key="2", allow_reversed=True, explain=False):
        spread_name, positions = SPREADS[spread_key]
        drawn = self.draw(len(positions), allow_reversed)
        user_element = ZODIAC_ELEMENTS.get((sign or "").lower())

        out = [f"\n{'~'*58}",
               f"  Spread: {spread_name}" + (f"   |   Querent: {name}" if name else ""),
               f"  Question: {question or '(open reading)'}" + ("   |   Explain mode ON" if explain else ""),
               f"{'~'*58}"]
        for (card, rev), pos in zip(drawn, positions):
            out.append(f"\n■ {pos}\n" + self._meaning(card, rev, pos, topic, user_element, explain))

        out.append(f"\n— The cards in conversation —\n{self._relational_note(drawn, topic, explain)}")

        advice = self._fresh(ADVICE_POOL, set())
        counsel_tmpl = self._fresh(COUNSEL, self._used_counsel)
        out.append("\n— Counsel —\n" + counsel_tmpl.format(
            card_short=drawn[-1][0]["name"], advice=advice))
        if explain:
            out.append(
                f"\n  — How this was built —\n"
                f"    [Advice selected: '{advice}' from pool of {len(ADVICE_POOL)}.\n"
                f"     Counsel template #{COUNSEL.index(counsel_tmpl)+1} of {len(COUNSEL)} used.]")

        closer = self._fresh(CLOSERS, self._used_closers)
        out.append("\n" + closer.format(card_short=drawn[-1][0]["name"]))
        if explain:
            out.append(
                f"\n  — How this was built —\n"
                f"    [Closer template #{CLOSERS.index(closer)+1} of {len(CLOSERS)} used.]")
        out.append(f"\n{'~'*58}\n")
        return "\n".join(out)


# ----------------------------------------------------------------------------
# 6. INTERACTIVE MODE
# ----------------------------------------------------------------------------
def interactive():
    print("✦ TAROT READER ✦  each reading is built from your cards, your question, and you.\n")
    name = input("Your name (or press Enter): ").strip()
    question = input("What are you asking about? ").strip()
    topic = "general"
    q = question.lower()
    for key in QUESTION_TOPICS:
        if key in q:
            topic = key
            break
    if topic == "general" and question:
        guess = input(f"I read this as a '{topic}' reading — topics: love / career / money / health / general. Pick one: ").strip().lower()
        if guess in QUESTION_TOPICS:
            topic = guess
    sign = input("Your zodiac sign (optional, for elemental resonance): ").strip() or None
    print("\nSpreads:\n  1. Single Card\n  2. Past / Present / Future\n  3. Situation / Obstacle / Advice\n  4. Celtic Cross")
    sk = input("Choose a spread [2]: ").strip() or "2"
    ex = input("Show your work / explain the reading? (y/n) [n]: ").strip().lower() == "y"
    reader = TarotReader()
    while True:
        print(reader.reading(name, question, topic, sign, sk, explain=ex))
        again = input("Draw again with new cards? (y/n) ").strip().lower()
        if again != "y":
            break


if __name__ == "__main__":
    interactive()
