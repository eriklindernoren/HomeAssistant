# -*- coding: utf-8 -*-
# nlg.py
import random
import datetime
from py4j_server import launch_py4j_server
from py4j.java_gateway import java_import

gateway = launch_py4j_server()

# Import the SimpleNLG classes
java_import(gateway.jvm, "simplenlg.features.*")
java_import(gateway.jvm, "simplenlg.realiser.*")

# Define aliases so that we don't have to use the gateway.jvm prefix.
NPPhraseSpec = gateway.jvm.NPPhraseSpec
PPPhraseSpec = gateway.jvm.PPPhraseSpec
SPhraseSpec = gateway.jvm.SPhraseSpec
InterrogativeType = gateway.jvm.InterrogativeType
Realiser = gateway.jvm.Realiser
TextSpec = gateway.jvm.TextSpec
Tense = gateway.jvm.Tense
Form = gateway.jvm.Form

date_endings = {
    "1": "1st",
    "2": "2nd",
    "3": "3rd",
    "4": "4th",
    "5": "5th",
    "6": "6th",
    "7": "7th",
    "8": "8th",
    "9": "9th"
}

months = {
    "01": "January",
    "02": "February",
    "03": "Mars",
    "04": "April",
    "05": "May",
    "06": "June",
    "07": "July",
    "08": "August",
    "09": "September",
    "10": "October",
    "11": "November",
    "12": "December"
}

class NLG(object):

    def __init__(self, user_name=None):
        self.user_name = user_name
        self.last_message = ""
        # make random more random by seeding with time
        random.seed(datetime.datetime.now())

    def acknowledge(self):

        user_name = self.user_name
        if user_name is None:
            user_name = ""

        simple_acknoledgement = [
            "Yes?",
            "What can I do for you?",
            "How can I help?"
        ]

        personal_acknowledgement = [
            "How can I help you today, %s" % user_name,
            "How can I help you, %s" % user_name,
            "What can I do for you, %s" % user_name,
            "Hi %s, what can I do for you?" % user_name,
            "Hey %s, what can I do for you?" % user_name
        ]

        choice = 0
        if self.user_name is not None:
            choice = random.randint(0, 2)
        else:
            choice = random.randint(0,1)

        ret_phrase = ""

        if choice == 0:
            ret_phrase = random.choice(simple_acknoledgement)
        elif choice == 1:
            date = datetime.datetime.now()
            ret_phrase = "Good %s. What can I do for you?" % self.time_of_day(date)
        else:
            ret_phrase = random.choice(personal_acknowledgement)

        return ret_phrase

    def identification(self):
        id_phrases = [
            "Alfred. 🤖",
            "Well my name is Alfred. Good to meet you.",
            "I'm Alfred. Your humble butler.",
            "My name is Alfred. A virtual butler.",
            "I'm an artificial butler. My name is Alfred.",
            "I will look that up... Haha. Just kidding. My name is Alfred.",
            "Some thousand lines of Python code."
        ]
        return random.choice(id_phrases)

    def searching(self):
        searching_phrases = [
            "I'll see what I can find",
            "Excuse me while I am reaching for my glasses...",
            "Hold on a second and let me look it up",
            "Just a second",
            "Give me a moment",
            "Hold on a second",
            "I'll look that up",
            "Let me see what I can find"
        ]

        phrase = random.choice(searching_phrases)
        phrase += " sir." if random.randint(0, 1) == 1 else "."
        return phrase

    def user_status(self, type='positive', attribute=None):

        ret_phrase = ""

        positive_complements = [
            "good",
            "nice",
            "great",
            "perfect",
            "Beautiful"
        ]

        negative_complements = [
            "bad",
            "terrible"
        ]

        moderate_complements = [
            "alright",
            "okay"
        ]

        complement_choice = positive_complements
        if type == 'negative':
            complement_choice = negative_complements
        elif type == 'moderate':
            complement_choice = moderate_complements

        if attribute is None:
            ret_phrase = "You look %s" % random.choice(complement_choice)
        else:
            ret_phrase = self.generate('none', {'subject': "Your %s" % attribute, 'verb': 'look %s' % random.choice(complement_choice)}, "present")

        return ret_phrase

    def goodbye(self):
        bye = [
            "See you later sir.",
            "Take care sir.",
            "I'll talk to you later then.",
            "Goodbye sir."
        ]
        return random.choice(bye)

    def alarm_info(self, date, time):
        
        time_missing = [
            "What time do you want me to set the alarm for?",
            "Sure! When?",
            "Just say the time, sir."
            "Of course, when do you want me to set the alarm for?",
            "With pleasure. What time do you want me to set the alarm for?",
        ]
        if not date:
            return random.choice(time_missing)

        month = months[date.split("-")[1]]
        day_first_digit = date.split("-")[-1][0]
        day_second_digit = date.split("-")[-1][1]
        day = ""
        if day_first_digit != "0":
            day = day_first_digit
        day += date_endings[day_second_digit]

        return "The alarm is set for %s on the %s of %s" % (time, day, month)

    def personal_status(self, status_type=None):
        positive_status=[
            "I can't complain... Literally. I don't have that functionality.",
            "Never been better.",
            "I'm doing great.",
            "I'm awesome.",
            "Incredible!"
        ]

        negative_status = [
            "Very busy, sir",
            "Incredibly bored",
            "I'm not doing well today",
            "I could be much better"
        ]

        moderate_status = [
            "I'm doing alright",
            "I'm okay",
            "I could be better",
            "I'm alright"
        ]

        if status_type == 'negative':
            return random.choice(negative_status)
        elif status_type == 'moderate':
            return random.choice(moderate_status)

        return random.choice(positive_status)

    def joke(self):
        jokes = [
            "Artificial intelligence is no match for natural stupidity.",
            "This morning I made a mistake and poured milk over my breakfast instead of oil, and it rusted before I could eat it.",
            "An Englishman, an Irishman and a Scotsman walk into a bar. The bartender turns to them, takes one look, and says, \"What is this - some kind of joke?\"",
            "What is an onomatopoeia? Just what it sounds like!",
            "Why did the elephant cross the road? Because the chicken retired.",
            "Today a man knocked on my door and asked for a small donation towards the local swimming pool. I gave him a glass of water.",
            "A recent study has found that women who carry a little extra weight live longer than the men who mention it.",
            "I can totally keep secrets. It is the people I tell them to that can not.",
            "My therapist says I have a preoccupation with vengeance. We will see about that.",
            "Money talks ...but all mine ever says is good-bye.",
            "I started out with nothing, and I still have most of it.",
            "I used to think I was indecisive, but now I'm not too sure.",
            "I named my hard drive that ass, so once a month my computer asks if I want to back that ass up.",
            "A clean house is the sign of a broken computer.",
            "My favorite mythical creature? The honest politician.",
            "Regular naps prevent old age, especially if you take them while driving.",
            "For maximum attention, nothing beats a good mistake.",
            "Take my advice. I am not using it.",
            'Did you hear about the two antennas that got married? The ceremony was long and boring, but the reception was great!',
            'Chuck Norris counted to infinity - twice.',
            'Death once had a near-Chuck Norris experience.',
            'Why was the Math book sad? Because it had so many problems.'
        ]

        return random.choice(jokes)

    def news(self, tense):

        headlines_nouns = [
            "stories",
            "articles",
            "headlines",
        ]

        headlines_adjectives = [
            ["these"],
            ["some"],
            ["a", "few"],
            ["a", "couple"]
        ]

        headlines_prepmodifiers = [
            "you"
        ]

        choice = random.randint(0, 1)

        if choice == 1:
            ret_phrase = self.generate('none', {'subject': "I", 'object': random.choice(headlines_nouns), 'verb': 'find', 'objmodifiers': random.choice(headlines_adjectives), 'preposition': 'for', 'prepmodifiers': [random.choice(headlines_prepmodifiers)]}, tense)
        else:
            ret_phrase = self.generate('none', {'subject': "I", 'object': random.choice(headlines_nouns), 'verb': 'find', 'objmodifiers': random.choice(headlines_adjectives)}, tense)

        return ret_phrase

    def article_interest(self, article_titles):
        ret_phrase = None

        if True or random.randint(0,2) == 0: # 1 in 3 chance the bot will express interest in a random article
            if article_titles is not None:
                article = random.choice(article_titles)
                article = article.rsplit('-', 1)[0]
                ret_phrase = "%s sounds particularly interesting" % article

        return ret_phrase

    def insult(self):
        return "That's not very nice. Talk to me again when you have fixed your attitude"

    def greet(self, by_name):
        """
        Creates a greeting phrase.
        :return:
        """

        greeting_words = [
            "Hi",
            "Hey",
            "Hello",
        ]

        goofy_greetings = [
            "Good day to you.",
            "What's cracking?",
            "What's up."
        ]

        choice = random.randint(0,4)
        ret_phrase = ""

        if (choice == 0) or (choice == 3): # time related
            ret_phrase = "Good %s" % self.time_of_day(datetime.datetime.now())
            if by_name and self.user_name is not None:
                ret_phrase = "%s %s" % (ret_phrase, self.user_name)
            elif random.randint(0,1) == 0:
                ret_phrase = "%s %s" % (ret_phrase, "sir")
        elif (choice == 1) or (choice == 4): # standard greeting
            ret_phrase = random.choice(greeting_words)
            if by_name and self.user_name is not None:
                ret_phrase = "%s %s" % (ret_phrase, self.user_name)
            elif random.randint(0,1) == 0:
                ret_phrase = "%s %s" % (ret_phrase, "sir")
        elif choice == 2: # goofy greeting
            ret_phrase = random.choice(goofy_greetings)

        return ret_phrase

    def weather(self, forecast_obj, date):

        ret_phrase = ""
        forecast = ""

        request_type = forecast_obj['forecast_type']
        location = forecast_obj['location']

        post = [
            "It will be",
            "Looks like it will be",
            "Hey look at that. Seems like it'll be",
            "It is going to be",
        ]

        post_with_loc = [
            "The weather in %s will be" % (location),
            "Looks like the weather in %s will be" % (location),
            "Hey look at that. Seems like the weather in %s will be" % (location),
            "The weather in %s is going to be" % (location),
        ]

        pre = [
            "It was"
        ]

        pre_with_loc = [
            "The weather in %s was" % (location)
        ]

        presens = [
            "It is",
            "Looks like it is",
            "Seems like it's",
            "It's'",
        ]

        presens_with_loc = [
            "The weather in %s is" % (location),
            "Looks like the weather in %s is" % (location),
            "Seems like the weather in %s is" % (location),
        ]

        if location:
            start = random.choice(post_with_loc)
            if date < datetime.datetime.now():
                start = random.choice(pre_with_loc)
        else:
            start = random.choice(post)
            if date < datetime.datetime.now():
                start = random.choice(pre)

        if request_type == "current":
            if location:
                start = random.choice(presens_with_loc)
            else:
                start = random.choice(presens)
            temperature = forecast_obj["temperature"]
            summary = forecast_obj["summary"].lower()
            apparent_temperature = forecast_obj["apparent_temperature"]
            ret_phrase = "%s %s with a temperature of %s degrees, but with an apparent temperature of %s." % (start, summary, temperature, apparent_temperature)
        elif request_type == "hour":
            temperature = forecast_obj["temperature"]
            summary = forecast_obj["summary"].lower()
            ret_phrase = "%s %s with a temperature of %s degrees." % (start, summary, temperature)
        elif request_type == "day":
            summary = forecast_obj['summary'].lower()
            temp_min = forecast_obj['temp_min']
            temp_max = forecast_obj['temp_max']
            ret_phrase = "%s %s With temperatures between %s and %s degrees." % (start, summary, temp_min, temp_max)

        return ret_phrase


    def score(self, score_obj):

        ret_phrase = ""
        home_score = int(score_obj['home_score'])
        away_score = int(score_obj['away_score'])

        if home_score > away_score:
            winner = score_obj['home_team']
            w_score = home_score
            loser = score_obj['away_team']
            l_score = away_score
        else:
            winner = score_obj['away_team']
            w_score = away_score
            loser = score_obj['home_team']
            l_score = home_score

        finished = score_obj['finished']
        if finished:
            ret_phrase = "The %s beat the %s by %i to %i" % (winner, loser, w_score, l_score)
        else:
            ret_phrase = "The %s lead the %s by %i to %i" % (winner, loser, w_score, l_score)

        return ret_phrase


    def appreciation(self):
        phrases = [
            "My pleasure, sir.",
            "You're too kind.",
            "You're welcome",
            "Sure, no problem",
            "Of course",
            "Don't mention it",
            "Don't worry about it"
        ]

        return random.choice(phrases)

    def holiday(self, holiday_name):
        phrases = [
            "",
            "Looks like the next holiday is ",
            "The next important day is "
        ]

        return "%s%s" % (random.choice(phrases), holiday_name)

    def meaning_of_life(self):
        phrases = [
            "42",
            "The meaning of life, the universe, and everything else is 42",
            "Let me look that up for you..... Ok, I found nothing."
        ]

        return random.choice(phrases)

    def name(self):
        return self.user_name

    def time_of_day(self, date, with_adjective=False):
        ret_phrase = ""
        if date.hour < 4:
            ret_phrase = "night"
            if with_adjective:
                ret_phrase = "%s %s" % ("this", ret_phrase)
        elif date.hour < 10:
            ret_phrase = "morning"
            if with_adjective:
                ret_phrase = "%s %s" % ("this", ret_phrase)
        elif (date.hour >= 10) and (date.hour < 18):
            ret_phrase = "afternoon"
            if with_adjective:
                ret_phrase = "%s %s" % ("this", ret_phrase)
        elif date.hour >= 18:
            ret_phrase = "evening"
            if with_adjective:
                ret_phrase = "%s %s" % ("this", ret_phrase)

        return ret_phrase

    def close(self):
        gateway.close()

    def generate(self, utter_type, keywords, tense=None):
        """
        Input: a type of inquiry to create and a dictionary of keywords.
        Types of inquiries include 'what', 'who', 'where', 'why', 'how',
        and 'yes/no' questions. Alternatively, 'none' can be specified to
        generate a declarative statement.

        The dictionary is essentially divided into three core parts: the
        subject, the verb, and the object. Modifiers can be specified to these
        parts (adverbs, adjectives, etc). Additionally, an optional
        prepositional phrase can be specified.

        Example:

        nlg = NaturalLanguageGenerator(logging.getLogger())
        words = {'subject': 'you',
                 'verb': 'prefer',
                 'object': 'recipes',
                 'preposition': 'that contains',
                 'objmodifiers': ['Thai'],
                 'prepmodifiers': ['potatoes', 'celery', 'carrots'],
                 'adverbs': ['confidently'],
        }

        nlg.generate('yes_no', words)
        u'Do you confidently prefer Thai recipes that contains potatoes, celery and carrots?'
        nlg.generate('how', words)
        u'How do you confidently prefer Thai recipes that contains potatoes, celery and carrots?'
        """
        utterance = SPhraseSpec()
        subject = NPPhraseSpec(keywords['subject'])
        target = None
        if 'object' in keywords:
            target = NPPhraseSpec(keywords['object'])
        preposition = PPPhraseSpec()

        if 'preposition' in keywords:
            preposition.setPreposition(keywords['preposition'])

        if 'prepmodifiers' in keywords:
            for modifier in keywords['prepmodifiers']:
                preposition.addComplement(modifier)

        if 'submodifiers' in keywords:
            for modifier in keywords['submodifiers']:
                subject.addModifier(modifier)

        if 'objmodifiers' in keywords:
            for modifier in keywords['objmodifiers']:
                target.addModifier(modifier)

        if utter_type.lower() == 'yes_no':
            utterance.setInterrogative(InterrogativeType.YES_NO)
        elif utter_type.lower() == 'how':
            utterance.setInterrogative(InterrogativeType.HOW)
        elif utter_type.lower() == 'what':
            utterance.setInterrogative(InterrogativeType.WHAT)
        elif utter_type.lower() == 'where':
            utterance.setInterrogative(InterrogativeType.WHERE)
        elif utter_type.lower() == 'who':
            utterance.setInterrogative(InterrogativeType.WHO)
        elif utter_type.lower() == 'why':
            utterance.setInterrogative(InterrogativeType.WHY)

        if target is not None:
            target.addModifier(preposition)
        utterance.setSubject(subject)
        utterance.setVerb(keywords['verb'])
        if 'adverbs' in keywords:
            for modifier in keywords['adverbs']:
                utterance.addModifier(modifier)
        if target is not None:
            utterance.addComplement(target)

        if tense.lower() == 'future':
            utterance.setTense(Tense.FUTURE)
        elif tense.lower() == 'past':
            utterance.setTense(Tense.PAST)

        realiser = Realiser()
        output = realiser.realiseDocument(utterance).strip()
        return output