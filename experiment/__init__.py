from otree.api import *
import re
import ast
import gzip
import random
import numpy as np
import scipy.spatial.distance
from concurrent.futures import ThreadPoolExecutor

from settings import PARTICIPANT_FIELDS

doc = """
Ihre App-Beschreibung
"""

class C(BaseConstants):
    NAME_IN_URL = 'mabella_experiment'
    NUM_ROUNDS = 6
    MYSTERY_WORDS = ['Raum','Taube', 'Golf', 'Elektrizitaet', 'Ende', 'Sombrero']
    LANGUAGE_CODE = 'de'
    PLAYERS_PER_GROUP = None
    TABOO_WORDS = [
        ['Hotel', 'Wohnen', 'Zimmer', 'Wand', 'Kueche'],
        ['Vogel', 'Gurren', 'Fliegen', 'Bote', 'Frieden'],
        ['Volkswagen', 'Schlaeger', 'Par', 'Birdie', 'Mini'],
        ['Strom', 'Tesla', 'Edison', 'Spannung', 'Statisch'],
        ['Finale', 'Schluss', 'Stopp', 'Tot', 'Anfang'],
        ['Hut', 'Mexiko', 'Kopfbedeckung', 'Mariachi', 'Krempe']
    ]
    STEM_WORDS = [
        ['raum', 'raeum', 'zimmer', 'hotel', 'wohn', 'wand', 'waend', 'kuech', 'koch'], 
        ['taub', 'taeub', 'gurr', 'flieg', 'flug', 'fluege', 'vogel', 'voegel', 'bot', 'fried'],
        ['golf', 'vw', 'wagen', 'volk', 'voelk', 'schlaeg', 'schlag', 'par', 'birdie', 'mini'],
        ['elektr', 'strom', 'tesla', 'edison', 'spann', 'stati'],  
        ['end', 'final', 'schluss', 'stopp', 'tot', 'tod', 'an', 'fang', 'schluess', 'faeng'],
        ['sombrero', 'hut', 'huet', 'mexik', 'mexic', 'kopf', 'koepf', 'bedeck', 'mariach', 'kremp']
    ]

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    payoff = models.IntegerField(initial=1000)
    quantity = models.IntegerField(initial=1000)
    originality = models.FloatField(initial=1000)

class Player(BasePlayer):        
    guess1 = models.StringField(label="Ihre Vermutung:", initial='', max_length=18)
    guess2 = models.StringField(label="Ihre Vermutung:", initial='', max_length=18)
    guess3 = models.StringField(label="Ihre Vermutung:", initial='', max_length=18)
    correct_guess1 = models.BooleanField(field_maybe_empty=True)
    correct_guess2 = models.BooleanField(field_maybe_empty=True)
    correct_guess3 = models.BooleanField(field_maybe_empty=True)
    score = models.IntegerField()
    result = models.StringField()
    player_role = models.StringField()
    incentive = models.IntegerField()
    known = models.StringField(choices=[['Ja', 'Ja'], ['Nein', 'Nein']], label='<b>1. </b> Kennen Sie das Spiel "Just One"?', widget=widgets.RadioSelect)
    understanding = models.StringField(choices=[['stimme vollkommen zu', 'stimme vollkommen zu'], ['stimme zu', 'stimme zu'], ['neutral', 'neutral'], ['stimme nicht zu', 'stimme nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='<b>2. </b> "Ich habe die Verfahrensweise und die Regeln schnell verstanden."', widget=widgets.RadioSelectHorizontal)
    comments = models.LongStringField(label="<b>4. </b> Welche Strategie haben sie als Hinweisgebende verfolgt?", initial='', max_length=500, blank=True)
    comments_2 = models.LongStringField(label="<b>5. </b> Welche Strategie haben sie als Ratender verfolgt?", initial='', max_length=500, blank=True)
    understand_1 = models.StringField(choices=[['false', 'Unbegrenzt viele Versuche'],['false', 'Zwei Versuche'],['false', 'Drei Versuche'],['true', 'Nur einen Versuch']], label='<b>Frage 1:</b> Wie viele Versuche hat der Ratende, um das geheime Wort zu erraten?', widget=widgets.RadioSelect)
    understand_2 = models.StringField(choices=[['false,','Zwei'],['false', 'Drei'],['true', 'Vier'],['false', 'Fünf']], label='<b>Frage 2:</b> Wie viele Spielerinnen und Spieler bilden zusammen eine Gruppe?', widget=widgets.RadioSelect)
    understand_3= models.StringField(choices=[['true', '10 Euro fix für die Teilnahme an allen Runden'],['false', '5 Euro fix plus 5 Euro Bonus für die meisten generierten Ideen'],['false', '5 Euro fix plus 5 Euro Bonus für die meisten erratenen geheimen Wörter'],['false','5 Euro fix plus 5 Euro Bonus für die originellsten Hinweispaare, die zur richtigen Erratung des Wortes führen']], label='<b>Frage 3:</b> Wie viel Geld können Sie maximal in diesem Experiment verdienen?', widget=widgets.RadioSelect)
    understand_4 = models.StringField(choices=[['false', 'Time'], ['false', 'Zeitpunkt'],['false', 'ist Geld'],['false', 'Zeeeit'],['true', 'keiner der oben genannten Hinweise']], label='<b>Frage 4:</b> Welcher der folgenden Hinweise wäre ein gültiger Hinweis in einem Hinweispaar für das geheime Wort "Zeit"?', widget=widgets.RadioSelect)
    strategy = models.StringField(choices=[['stimme vollkommen zu', 'stimme vollkommen zu'], ['stimme zu', 'stimme zu'], ['neutral', 'neutral'], ['stimme nicht zu', 'stimme nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='<b>6. </b>"Ich habe ständig nur daran gedacht, welche Hinweise andere Teilnehmende abgeben."', widget=widgets.RadioSelectHorizontal)
    strategy_2 = models.StringField(choices=[['stimme vollkommen zu', 'stimme vollkommen zu'], ['stimme zu', 'stimme zu'], ['neutral', 'neutral'], ['stimme nicht zu', 'stimme nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='<b>7. </b>"Erst möglichst viele Ideen aufzuschreiben, hilft mir dabei, später bessere Hinweise zu geben."', widget=widgets.RadioSelectHorizontal)
    strategy_3 = models.StringField(choices=[['stimme vollkommen zu', 'stimme vollkommen zu'], ['stimme zu', 'stimme zu'], ['neutral', 'neutral'], ['stimme nicht zu', 'stimme nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='<b>8. </b>"Ich habe versucht, möglichst originelle und einzigartige Hinweise zu geben, damit ich keine identischen Hinweise wie andere Teilnehmende abgebe."', widget=widgets.RadioSelectHorizontal)
    strategy_4 = models.StringField(choices=[['stimme vollkommen zu', 'stimme vollkommen zu'], ['stimme zu', 'stimme zu'], ['neutral', 'neutral'], ['stimme nicht zu', 'stimme nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='<b>9. </b>"Ich habe versucht, eindeutige und naheliegende Hinweise zu geben, auch auf die Gefahr hin, dass andere Teilnehmende identische Hinweise abgeben."', widget=widgets.RadioSelectHorizontal)
    strategy_5 = models.StringField(choices=[['stimme vollkommen zu', 'stimme vollkommen zu'], ['stimme zu', 'stimme zu'], ['neutral', 'neutral'], ['stimme nicht zu', 'stimme nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='<b>10. </b>"Es fiel mir aufgrund der fünf Tabuwörter sehr schwer, gute Hinweise zu schreiben."', widget=widgets.RadioSelectHorizontal)
    group_individual = models.StringField(choices=[['Gruppe', 'Es war produktiv, in der Gruppe zu arbeiten'], ['Individuell', 'Ich hätte lieber alleine Hinweise gegeben']], label='<b>11. </b>Wie haben Sie die Zusammenarbeit in Ihrer Gruppe erlebt?', widget=widgets.RadioSelectHorizontal)
    strategy_6 = models.StringField(choices=[['stimme vollkommen zu', 'stimme vollkommen zu'], ['stimme zu', 'stimme zu'], ['neutral', 'neutral'], ['stimme nicht zu', 'stimme nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='<b>12. </b>"Ein Wettkampf mit anderen Gruppen würde mich motivieren, möglichst gute Hinweise zu geben und das geheime Wort zu erraten."', widget=widgets.RadioSelectHorizontal)
    strategy_7 = models.StringField(choices=[['stimme vollkommen zu', 'stimme vollkommen zu'], ['stimme zu', 'stimme zu'], ['neutral', 'neutral'], ['stimme nicht zu', 'stimme nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='<b>13. </b>"Eine Bonuszahlung geknüpft an unsere Gruppenperformance würde mich motivieren, möglichst gute Hinweise zu geben und das geheime Wort zu erraten."', widget=widgets.RadioSelectHorizontal)
    individualism_1 = models.IntegerField(choices=[-3, -2, -1, 0, 1, 2, 3], widget=widgets.RadioSelect)
    individualism_2 = models.IntegerField(choices=[-3, -2, -1, 0, 1, 2, 3], widget=widgets.RadioSelect)
    individualism_3 = models.IntegerField(choices=[-3, -2, -1, 0, 1, 2, 3], widget=widgets.RadioSelect)
    individualism_4 = models.IntegerField(choices=[-3, -2, -1, 0, 1, 2, 3], widget=widgets.RadioSelect)
    individualism_5 = models.IntegerField(choices=[-3, -2, -1, 0, 1, 2, 3], widget=widgets.RadioSelect)
    Idea1 = models.StringField(label= '', initial='', blank=True, max_length=18)
    Idea2 = models.StringField(label= '', initial='', blank=True, max_length=18)
    Idea3 = models.StringField(label= '', initial='', blank=True, max_length=18)
    Idea4 = models.StringField(label= '', initial='', blank=True, max_length=18)
    Idea5 = models.StringField(label= '', initial='', blank=True, max_length=18)
    Idea6 = models.StringField(label= '', initial='', blank=True, max_length=18)
    Idea7 = models.StringField(label= '', initial='', blank=True, max_length=18)
    Idea8 = models.StringField(label= '', initial='', blank=True, max_length=18)
    Idea9 = models.StringField(label= '', initial='', blank=True, max_length=18)
    Idea10 = models.StringField(label= '', initial='', blank=True, max_length=18)
    word1 = models.StringField(label= '', initial='', blank=False)
    word2 = models.StringField(label= '', initial='', blank=False)
    word3 = models.StringField(label= '', initial='', blank=False)
    word4 = models.StringField(label= '', initial='', blank=False)
    word5 = models.StringField(label= '', initial='', blank=False)
    word6 = models.StringField(label= '', initial='', blank=False)
    word7 = models.StringField(label= '', initial='', blank=False)
    word8 = models.StringField(label= '', initial='', blank=False)
    word9 = models.StringField(label= '', initial='', blank=False)
    word10 = models.StringField(label= '', initial='', blank=False)
    gender = models.IntegerField(choices=[[1, 'Männlich'],[2, 'Weiblich'],[3, 'Divers'],], label='Geschlecht:')
    age = models.IntegerField(min=18, max=100, label='Alter:')
    study = models.StringField(choices=[['Geisteswissenschaften', 'Geisteswissenschaften'],['Sport', 'Sport'],['Rechts-, Wirtschafts- und Sozialwissenschaften', 'Rechts-, Wirtschafts- und Sozialwissenschaften'],['Mathematik, Naturwissenschaften', 'Mathematik, Naturwissenschaften'],['Humanmedizin, Gesundheitswissenschaften', 'Humanmedizin, Gesundheitswissenschaften'],['Agrar-, Forst- und Ernährungswissenschaften, Veterinärmedizin', 'Agrar-, Forst- und Ernährungswissenschaften, Veterinärmedizin'], ['Ingenieurwissenschaften', 'Ingenieurwissenschaften'],['Kunst, Kunstwissenschaft', 'Kunst, Kunstwissenschaft'],['Sonstiges', 'Sonstiges'],], label='Studienbereich:', widget=widgets.RadioSelect)
    invalid = models.BooleanField()
    missing = models.BooleanField()
    guess_missing = models.BooleanField()
    quantity = models.IntegerField()
    originality = models.FloatField()
    invalid_DAT = models.BooleanField()
    pair1 = models.StringField(initial='')
    pair2 = models.StringField(initial='')
    pair3 = models.StringField(initial='')
    pair4 = models.StringField(initial='')
    pair5 = models.StringField(initial='')
    pair1after = models.StringField(initial='')
    pair2after = models.StringField(initial='')
    pair3after = models.StringField(initial='')
    pair4after = models.StringField(initial='')
    pair5after = models.StringField(initial='')
    rating_before1 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    rating_before2 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    rating_before3 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    rating_before4 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    rating_before5 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    rating_before6 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    rating_before7 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    rating_before8 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    rating_before9 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    rating_before10 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    discussion1 = models.StringField(label= '', initial='', blank=True, max_length=18)
    discussion2 = models.StringField(label= '', initial='', blank=True, max_length=18)
    discussion3 = models.StringField(label= '', initial='', blank=True, max_length=18)
    discussion4 = models.StringField(label= '', initial='', blank=True, max_length=18)
    discussion5 = models.StringField(label= '', initial='', blank=True, max_length=18)
    discussion6 = models.StringField(label= '', initial='', blank=True, max_length=18)
    discussion7 = models.StringField(label= '', initial='', blank=True, max_length=18)
    discussion8 = models.StringField(label= '', initial='', blank=True, max_length=18)
    discussion9 = models.StringField(label= '', initial='', blank=True, max_length=18)
    discussion10 = models.StringField(label= '', initial='', blank=True, max_length=18)
    other_pairs = models.StringField(label= '', initial='', blank=True)
    replace_word1 = models.StringField(widget = widgets.RadioSelectHorizontal, choices=[['erste', 'erste Wort durch:'],['zweite', 'zweite Wort durch:'],], label='Ersetze das', blank=True, initial='')
    replace_word2 = models.StringField(widget = widgets.RadioSelectHorizontal, choices=[['erste', 'erste Wort durch:'],['zweite', 'zweite Wort durch:'],], label='Ersetze das', blank=True, initial='')
    replace_word3 = models.StringField(widget = widgets.RadioSelectHorizontal, choices=[['erste', 'erste Wort durch:'],['zweite', 'zweite Wort durch:'],], label='Ersetze das', blank=True, initial='')
    replace_word4 = models.StringField(widget = widgets.RadioSelectHorizontal, choices=[['erste', 'erste Wort durch:'],['zweite', 'zweite Wort durch:'],], label='Ersetze das', blank=True, initial='')
    replace_word5 = models.StringField(widget = widgets.RadioSelectHorizontal, choices=[['erste', 'erste Wort durch:'],['zweite', 'zweite Wort durch:'],], label='Ersetze das', blank=True, initial='')
    replace_word6 = models.StringField(widget = widgets.RadioSelectHorizontal, choices=[['erste', 'erste Wort durch:'],['zweite', 'zweite Wort durch:'],], label='Ersetze das', blank=True, initial='')
    replace_word7 = models.StringField(widget = widgets.RadioSelectHorizontal, choices=[['erste', 'erste Wort durch:'],['zweite', 'zweite Wort durch:'],], label='Ersetze das', blank=True, initial='')
    replace_word8 = models.StringField(widget = widgets.RadioSelectHorizontal, choices=[['erste', 'erste Wort durch:'],['zweite', 'zweite Wort durch:'],], label='Ersetze das', blank=True, initial='')
    replace_word9 = models.StringField(widget = widgets.RadioSelectHorizontal, choices=[['erste', 'erste Wort durch:'],['zweite', 'zweite Wort durch:'],], label='Ersetze das', blank=True, initial='')
    replace_word10 = models.StringField(widget = widgets.RadioSelectHorizontal, choices=[['erste', 'erste Wort durch:'],['zweite', 'zweite Wort durch:'],], label='Ersetze das', blank=True, initial='')
    pair_feedback1 = models.StringField(label= '', initial='', blank=True)
    pair_feedback2 = models.StringField(label= '', initial='', blank=True)
    pair_feedback3 = models.StringField(label= '', initial='', blank=True)
    pair_feedback4 = models.StringField(label= '', initial='', blank=True)
    pair_feedback5 = models.StringField(label= '', initial='', blank=True)
    pair_feedback6 = models.StringField(label= '', initial='', blank=True)
    pair_feedback7 = models.StringField(label= '', initial='', blank=True)
    pair_feedback8 = models.StringField(label= '', initial='', blank=True)
    pair_feedback9 = models.StringField(label= '', initial='', blank=True)
    pair_feedback10 = models.StringField(label= '', initial='', blank=True)
    vote = models.StringField(initial='')
    vote_group = models.StringField(initial='')
    pairsafter = models.StringField(label= '', initial='', blank=True)
    number_pairs = models.IntegerField()
    before_quantity = models.IntegerField()
    before_missing = models.BooleanField()
    before_invalid = models.IntegerField()
    after_invalid = models.IntegerField()
    check_invalid_1 = models.StringField(blank=True)
    check_invalid_2 = models.StringField(blank=True)
    check_invalid_3 = models.StringField(blank=True)
    check_invalid_4 = models.StringField(blank=True)
    check_invalid_5 = models.StringField(blank=True)
    check_invalid_6 = models.StringField(blank=True)
    check_invalid_7 = models.StringField(blank=True)
    check_invalid_8 = models.StringField(blank=True)
    check_invalid_9 = models.StringField(blank=True)
    check_invalid_10 = models.StringField(blank=True)
    check_invalid_11 = models.StringField(blank=True)
    check_invalid_12 = models.StringField(blank=True)
    check_invalid_13 = models.StringField(blank=True)
    check_invalid_14 = models.StringField(blank=True)
    check_invalid_15 = models.StringField(blank=True)

class Model:
    def __init__(player, model="vectors_german.txt.gz", dictionary="vocab_german.txt", pattern="^[a-z][a-z-]*[a-z]$"):
        player.model_file = model
        player.dictionary_file = dictionary
        player.pattern = re.compile(pattern)
        player.words = set()

    def load_words(player):
        with open(player.dictionary_file, "r", encoding="utf-8") as f:
            player.words.update(line.strip() for line in f if player.pattern.match(line))

    def get_vector(player, word):
        with gzip.open(player.model_file, "rt", encoding="utf-8") as f:
            for line in f:
                tokens = line.split(" ")
                if tokens[0] == word:
                    return np.array(tokens[1:], dtype=np.float32)
        return None

    def distance(player, word1, word2):
        vector1 = player.get_vector(word1)
        vector2 = player.get_vector(word2)
        if vector1 is not None and vector2 is not None:
            return scipy.spatial.distance.cosine(vector1, vector2) * 100
        return None
    
    def calculate_originality(player, word_pair, mystery_word):
        dist_1 = player.distance(word_pair.split(" + ")[0], mystery_word)
        dist_2 = player.distance(word_pair.split(" + ")[1], mystery_word)
        if dist_1 is not None and dist_2 is not None:
            return (dist_1 + dist_2) / 2
        return None
    
    def __enter__(player):
        player.load_words()
        return player

    def __exit__(player, exc_type, exc_value, traceback):
        pass

def creating_session(subsession: Subsession):
    session = subsession.session
    players = subsession.get_players()
    num_players = len(players)
    num_hintgiver_groups = num_players // 4
    hintgiver_groups = []
    ratender_group = []

    for i in range(num_hintgiver_groups):
        start_index = i * 3
        end_index = start_index + 3
        hintgiver_groups.append(players[start_index:end_index])

    ratender_group = players[num_hintgiver_groups * 3:]

    matrix = hintgiver_groups + [ratender_group]
    subsession.set_group_matrix(matrix)

    treatment = session.config['treatment']
    for player in players:
        participant = player.participant
        participant.vars['treatment'] = treatment
        player.incentive = treatment
        player.player_role = 'Hinweisgebende' if player in [p for group in hintgiver_groups for p in group] else 'Ratender'

def validate_ideas(player, ideas):
    stem_words = C.STEM_WORDS[player.round_number - 1]     
    with open("wordlist-german.txt", 'r') as file:
        wordlist = set(file.read().split())
    special_char_map = {ord('ä'):'ae', ord('ü'):'ue', ord('ö'):'oe', ord('ß'):'ss'}    
    if len(ideas) > 0:
        for i in range(len(ideas)): 
            if ideas[i] != '':
                ideas[i] = ideas[i].translate(special_char_map).lower()
                if ' ' in ideas[i] and re.search(r'\b\w+\s+\w+\b', ideas[i]):
                    ideas[i] = 'false'
                if ' ' in ideas[i]:
                    ideas[i] = ideas[i].replace(' ', '')
                for j in range(len(stem_words)):
                    if stem_words[j] in ideas[i] or ideas[i] in stem_words[j]:
                        ideas[i] = 'false'
                if re.search("[^a-zA-Z0-9\s]", ideas[i]):
                    ideas[i] = 'false'  
                if ideas[i] not in wordlist:
                    ideas[i] = 'false'
                if bool(re.search(r'\d',ideas[i])):
                    ideas[i] = 'false'
        for i in range(0, len(ideas), 2):
            if ideas[i] != 'false' and ideas[i] != '':
                if ideas[i] == ideas[i + 1]:
                    ideas[i] = ideas[i + 1] = 'false'
        return ideas    

# PAGES

class Intro(Page):
    timeout_seconds = 120
    def is_displayed(player):
        return player.round_number == 1

class Intro2(Page):
    timeout_seconds = 120
    def is_displayed(player):
        return player.round_number == 1
    
class Rules(Page):
    timeout_seconds = 70
    def is_displayed(player):
        return player.round_number == 1 
   
class Instructions(Page):
    timeout_seconds = 120
    def is_displayed(player):
        return player.round_number == 1
    
class UnderstandPage(Page):
    template_name = 'new_justone_deutsch_oR/UnderstandPage.html'
    timeout_seconds = 100
    def is_displayed(player):
        return player.round_number == 1
    form_model = 'player'
    form_fields = ['understand_1', 'understand_2', 'understand_3', 'understand_4']
    def error_message(player, values):
        for i in range(1, 5):
             if values[f'understand_{i}'] == 'false':
                return f'Falsche Antwort bei Frage {i}! Versuchen Sie es noch einmal.'   
             
class Round(Page):
    timeout_seconds = 30
    def vars_for_template(player):
        round_number = player.round_number 
        remaining_rounds = C.NUM_ROUNDS - round_number 
        group = player.group
        # get payoff from last round
        if round_number > 1:
            last_round = group.in_round(round_number - 1)
            group.payoff = last_round.payoff
            group.quantity = last_round.quantity
            group.originality = last_round.originality
        return dict(round_number = round_number, remaining_rounds = remaining_rounds) 
    
class Generation_Page(Page):
    timeout_seconds = 160
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende'   
    form_model = 'player'
    form_fields = ['Idea1', 'Idea2', 'Idea3', 'Idea4', 'Idea5', 'Idea6', 'Idea7', 'Idea8', 'Idea9', 'Idea10']
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        taboo_words = C.TABOO_WORDS[player.round_number - 1]
        return dict(mystery_word = mystery_word, taboo_words = taboo_words)

    def before_next_page(player, timeout_happened):
        if timeout_happened:        
            ideas = [player.Idea1, player.Idea2, player.Idea3, player.Idea4, player.Idea5, player.Idea6, player.Idea7, player.Idea8, player.Idea9, player.Idea10]
            ideas = validate_ideas(player, ideas)
            player.before_missing = False
            player.before_invalid = 0
            for i in range(len(ideas)):
                if ideas[i] == 'false':
                    player.before_invalid = player.before_invalid + 1
            for i in range(0, len(ideas), 2):
                if (ideas[i] != '' and ideas[i] != 'false') and (ideas[i + 1] != '' and ideas[i + 1] != 'false'):
                    setattr(player, f'pair{(i // 2) + 1}', f"{ideas[i]} + {ideas[i + 1]}")
                else:
                    setattr(player, f'pair{(i // 2) + 1}', 'empty') 
            pairs = [player.pair1] + [player.pair2] + [player.pair3] + [player.pair4] + [player.pair5] 
            while 'empty' in pairs:
                pairs.remove('empty')
            player.before_quantity = len(pairs)        
            if player.before_quantity == 0:
                player.before_missing = True
        else:
            player.before_invalid = 0
            player.before_missing = False
            ideas = [player.Idea1, player.Idea2, player.Idea3, player.Idea4, player.Idea5, player.Idea6, player.Idea7, player.Idea8, player.Idea9, player.Idea10]
            ideas = validate_ideas(player, ideas)
            for i in range(len(ideas)):
                if ideas[i] == 'false':  
                    player.before_invalid = player.before_invalid + 1
            for i in range(0, len(ideas), 2):
                if (ideas[i] != '' and ideas[i] != 'false') and (ideas[i + 1] != '' and ideas[i + 1] != 'false'):
                    setattr(player, f'pair{(i // 2) + 1}', f"{ideas[i]} + {ideas[i + 1]}")
                else:
                    setattr(player, f'pair{(i // 2) + 1}', 'empty')
            pairs = [player.pair1] + [player.pair2] + [player.pair3] + [player.pair4] + [player.pair5] 
            while 'empty' in pairs:
                pairs.remove('empty')
            player.before_quantity = len(pairs)
            if player.before_quantity == 0:
                player.before_missing = True       

class Discussion(Page):
    timeout_seconds = 5000
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende'
    form_model = 'player'   
    form_fields = ['rating_before1', 'rating_before2', 'rating_before3', 'rating_before4', 'rating_before5', 'rating_before6', 'rating_before7', 'rating_before8', 'rating_before9', 'rating_before10', 'replace_word1', 'replace_word2', 'replace_word3', 'replace_word4', 'replace_word5', 'replace_word6', 'replace_word7', 'replace_word8', 'replace_word9', 'replace_word10', 'discussion1','discussion2', 'discussion3', 'discussion4', 'discussion5', 'discussion6', 'discussion7', 'discussion8', 'discussion9', 'discussion10']
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        taboo_words = C.TABOO_WORDS[player.round_number - 1]
        pairs = [player.pair1 for player in player.get_others_in_group()] + [player.pair2 for player in player.get_others_in_group()] + [player.pair3 for player in player.get_others_in_group()] + [player.pair4 for player in player.get_others_in_group()] + [player.pair5 for player in player.get_others_in_group()] 
        while 'empty' in pairs:
            pairs.remove('empty')
        while '' in pairs:
            pairs.remove('')
        player.other_pairs = ', '.join(pairs)
        player.number_pairs = len(pairs)
        pairs_output = [pairs[i] if i < player.number_pairs else 'empty'for i in range(10)]
        return dict(mystery_word = mystery_word, taboo_words = taboo_words, number_pairs = player.number_pairs, Pair1 = pairs_output[0], Pair2 = pairs_output[1], Pair3 = pairs_output[2], Pair4 = pairs_output[3], Pair5 = pairs_output[4], Pair6 = pairs_output[5], Pair7 = pairs_output[6], Pair8 = pairs_output[7], Pair9 = pairs_output[8], Pair10 = pairs_output[9])   
    
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            pairs = [player.pair1 for player in player.get_others_in_group()] + [player.pair2 for player in player.get_others_in_group()] + [player.pair3 for player in player.get_others_in_group()] + [player.pair4 for player in player.get_others_in_group()] + [player.pair5 for player in player.get_others_in_group()]  
            while 'empty' in pairs:
                pairs.remove('empty')
            while '' in pairs:
                pairs.remove('')
            for i in range(player.number_pairs):
                feedback = [player.other_pairs.split(', ')[i], getattr(player, f'rating_before{i + 1}'), getattr(player, f'replace_word{i + 1}'), getattr(player, f'discussion{i + 1}')]
                setattr(player, f'pair_feedback{i + 1}', str(feedback))
        else:
            pairs = [player.pair1 for player in player.get_others_in_group()] + [player.pair2 for player in player.get_others_in_group()] + [player.pair3 for player in player.get_others_in_group()] + [player.pair4 for player in player.get_others_in_group()] + [player.pair5 for player in player.get_others_in_group()]  
            while 'empty' in pairs:
                pairs.remove('empty')
            while '' in pairs:
                pairs.remove('')
            for i in range(player.number_pairs):
                feedback = [player.other_pairs.split(', ')[i], getattr(player, f'rating_before{i + 1}'), getattr(player, f'replace_word{i + 1}'), getattr(player, f'discussion{i + 1}')]
                setattr(player, f'pair_feedback{i + 1}', str(feedback))

def rating_before1_error_message(player, value):
    if value == '' and player.number_pairs > 0:
        return 'Bitte wählen Sie eine Antwort aus!'

def rating_before2_error_message(player, value):
    if value == '' and player.number_pairs > 1:
        return 'Bitte wählen Sie eine Antwort aus!'

def rating_before3_error_message(player, value):
    if value == '' and player.number_pairs > 2:
        return 'Bitte wählen Sie eine Antwort aus!'

def rating_before4_error_message(player, value):
    if value == '' and player.number_pairs > 3:
        return 'Bitte wählen Sie eine Antwort aus!'

def rating_before5_error_message(player, value):
    if value == '' and player.number_pairs > 4:
        return 'Bitte wählen Sie eine Antwort aus!'

def rating_before6_error_message(player, value):
    if value == '' and player.number_pairs > 5:
        return 'Bitte wählen Sie eine Antwort aus!'

def rating_before7_error_message(player, value):
    if value == '' and player.number_pairs > 6:
        return 'Bitte wählen Sie eine Antwort aus!'

def rating_before8_error_message(player, value):
    if value == '' and player.number_pairs > 7:
        return 'Bitte wählen Sie eine Antwort aus!'

def rating_before9_error_message(player, value):
    if value == '' and player.number_pairs > 8:
        return 'Bitte wählen Sie eine Antwort aus!'

def rating_before10_error_message(player, value):
    if value == '' and player.number_pairs > 9:
        return 'Bitte wählen Sie eine Antwort aus!'
    
class Clue_Page(Page):
    timeout_seconds = 130
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende'   
    form_model = 'player'
    form_fields = ['Idea1', 'Idea2', 'Idea3', 'Idea4', 'Idea5', 'Idea6', 'Idea7', 'Idea8', 'Idea9', 'Idea10']
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        taboo_words = C.TABOO_WORDS[player.round_number - 1]
        feedback_groups = [
            [p.pair_feedback1 for p in player.get_others_in_group()],
            [p.pair_feedback2 for p in player.get_others_in_group()],
            [p.pair_feedback3 for p in player.get_others_in_group()],
            [p.pair_feedback4 for p in player.get_others_in_group()],
            [p.pair_feedback5 for p in player.get_others_in_group()],
            [p.pair_feedback6 for p in player.get_others_in_group()],
            [p.pair_feedback7 for p in player.get_others_in_group()],
            [p.pair_feedback8 for p in player.get_others_in_group()],
            [p.pair_feedback9 for p in player.get_others_in_group()],
            [p.pair_feedback10 for p in player.get_others_in_group()],
            ]
        filtered_feedback_groups = [list(filter(bool, group)) for group in feedback_groups]
        feedback1_group, feedback2_group, feedback3_group, feedback4_group, feedback5_group, feedback6_group, feedback7_group, feedback8_group, feedback9_group, feedback10_group = filtered_feedback_groups
        all_feedback_groups = []
        for group in filtered_feedback_groups:
            if group:
                all_feedback_groups.extend(group)
        ratings = [[] for _ in range(5)]
        replaces = [[] for _ in range(5)]
        r_words = [[] for _ in range(5)]
        pairs = [player.pair1, player.pair2, player.pair3, player.pair4, player.pair5]
        for element in all_feedback_groups:
            element_list = ast.literal_eval(element)
            for i, pair in enumerate(pairs):
                if element_list[0] == pair:
                    ratings[i].append(element_list[1])
                    replaces[i].append(element_list[2])
                    r_words[i].append(element_list[3])
        rating_1, rating_2, rating_3, rating_4, rating_5 = ratings
        replace_1, replace_2, replace_3, replace_4, replace_5 = replaces
        r_word_1, r_word_2, r_word_3, r_word_4, r_word_5 = r_words
        return dict(mystery_word = mystery_word, taboo_words = taboo_words, Rating_1 = rating_1, Replace_1 = replace_1, R_word_1 = r_word_1, Rating_2 = rating_2, Replace_2 = replace_2, R_word_2 = r_word_2, Rating_3 = rating_3, Replace_3 = replace_3, R_word_3 = r_word_3, Rating_4 = rating_4, Replace_4 = replace_4, R_word_4 = r_word_4, Rating_5 = rating_5, Replace_5 = replace_5, R_word_5 = r_word_5, Feedback1 = feedback1_group, Feedback2 = feedback2_group, Feedback3 = feedback3_group, Feedback4 = feedback4_group, Feedback5 = feedback5_group, Feedback6 = feedback6_group, Feedback7 = feedback7_group, Feedback8 = feedback8_group, Feedback9 = feedback9_group, Feedback10 = feedback10_group)
    
    def before_next_page(player, timeout_happened):
        if timeout_happened:        
            player.after_invalid = 0
            ideas = [player.Idea1, player.Idea2, player.Idea3, player.Idea4, player.Idea5, player.Idea6, player.Idea7, player.Idea8, player.Idea9, player.Idea10]
            ideas = validate_ideas(player, ideas)
            for i in range(len(ideas)):
                if ideas[i] == 'false':
                    player.after_invalid = player.after_invalid + 1
            for i in range(0, len(ideas), 2):
                if (ideas[i] != '' and ideas[i] != 'false') and (ideas[i + 1] != '' and ideas[i + 1] != 'false'):
                    setattr(player, f'pair{(i // 2) + 1}after', f"{ideas[i]} + {ideas[i + 1]}")
                else:
                    setattr(player, f'pair{(i // 2) + 1}after', 'empty')
        else:
            player.after_invalid = 0
            ideas = [player.Idea1, player.Idea2, player.Idea3, player.Idea4, player.Idea5, player.Idea6, player.Idea7, player.Idea8, player.Idea9, player.Idea10]
            ideas = validate_ideas(player, ideas)
            for i in range(len(ideas)):
                if ideas[i] == 'false':  
                    player.after_invalid = player.after_invalid + 1
            for i in range(0, len(ideas), 2):
                if (ideas[i] != '' and ideas[i] != 'false') and (ideas[i + 1] != '' and ideas[i + 1] != 'false'):
                    setattr(player, f'pair{(i // 2) + 1}after', f"{ideas[i]} + {ideas[i + 1]}")
                else:
                    setattr(player, f'pair{(i // 2) + 1}after', 'empty')

class Voting_Page(Page):
    timeout_seconds = 90
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende' 
    form_model = 'player'
    form_fields = ['vote']
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        taboo_words = C.TABOO_WORDS[player.round_number - 1]
        pairs = [player.pair1after] + [player.pair1after for player in player.get_others_in_group()] + [player.pair2after] + [player.pair2after for player in player.get_others_in_group()] + [player.pair3after] + [player.pair3after for player in player.get_others_in_group()] + [player.pair4after] + [player.pair4after for player in player.get_others_in_group()] + [player.pair5after] + [player.pair5after for player in player.get_others_in_group()] 
        while 'empty' in pairs:
            pairs.remove('empty')
        while '' in pairs:
            pairs.remove('')
        pairsafter = []
        for item in pairs:
            if pairs.count(item) > 1 and item not in pairsafter:
                pairsafter.append(item)
            elif pairs.count(item) == 1:
                pairsafter.append(item)
        pairsafter = sorted(pairsafter)
        player.pairsafter = ','.join(pairsafter)
        number_pairs = len(pairsafter)
        pairs_dict = {f'Pair{i+1}': pairsafter[i] if i < number_pairs else '' for i in range(15)}
        Pair1, Pair2, Pair3, Pair4, Pair5, Pair6, Pair7, Pair8, Pair9, Pair10, Pair11, Pair12, Pair13, Pair14, Pair15 = pairs_dict.values()
        return dict(mystery_word = mystery_word, taboo_words= taboo_words, number_pairs = number_pairs, Pair1 = Pair1, Pair2 = Pair2, Pair3 = Pair3, Pair4 = Pair4, Pair5 = Pair5, Pair6 = Pair6, Pair7 = Pair7, Pair8 = Pair8, Pair9 = Pair9, Pair10 = Pair10, Pair11 = Pair11, Pair12 = Pair12, Pair13 = Pair13, Pair14 = Pair14, Pair15 = Pair15, pairs = pairsafter)
  
class VotingResultPage(Page):
    timeout_seconds = 5000
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende'
    def vars_for_template(player):
        votes = [player.vote] + [p.vote for p in player.get_others_in_group()]
        while '' in votes:
            votes.remove('')
        random.seed(42)
        duplicates = [v for v in set(votes) if votes.count(v) >= 2]
        number_duplicates = len(duplicates)
        votes = sorted(votes)
        number_votes = len(votes)
        if len(duplicates) > 0:
            vote_group = duplicates[0]
        else:
            if len(votes) == 1:
                vote_group = votes[0]
            elif len(votes) > 1:
                i = random.randint(0, len(votes) - 1) 
                vote_group = votes[i]
            else:
                vote_group = 'Kein gültiges Hinweispaar'   
        player.vote_group = vote_group
        return dict(vote_group=vote_group, duplicates=number_duplicates, number_votes=number_votes)
    
class Originality_Calculation(Page):
    timeout_seconds = 5000
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende' and player.participant.treatment == 4
    def vars_for_template(player):
        vote_group = player.vote_group
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1].lower()
        if vote_group != 'Kein gültiges Hinweispaar':
            with Model() as model:
                originality_measures = []
                with ThreadPoolExecutor() as executor:
                    future = executor.submit(model.calculate_originality, vote_group, mystery_word)
                    originality_measures.append(future)

                for idx, originality in enumerate(originality_measures, start=1):
                    originality = future.result()
                    if originality is not None:
                        originality = round(originality, 2)
                    else: 
                        originality = 0
        else:
            originality = 0
        player.group.originality = originality
        return dict(vote_group = vote_group, originality = originality)

class Guess_Page1(Page):
    timeout_seconds = 5000
    def is_displayed(player):
        return player.player_role == 'Ratender'
    
    def vars_for_template(player):  
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1].lower()
        hint_groups = [g for g in player.subsession.get_groups() if g.get_players()[0].player_role == 'Hinweisgebende']
        index = (player.id_in_group - 1 + player.round_number - 1) % len(hint_groups)
        vote_group = hint_groups[index].get_players()[0].vote_group
        player.vote_group = vote_group
        return dict(vote_group=vote_group, mystery_word = mystery_word)
    
    form_model = 'player'
    form_fields = ['guess1'] 
    
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.guess1 = 'Kein Tipp gegeben'
            player.correct_guess1 = False
        else:
            special_char_map = {ord('ä'):'ae', ord('ü'):'ue', ord('ö'):'oe', ord('ß'):'ss'}
            player.guess1 = player.guess1.lower().translate(special_char_map) 
            if player.guess1 == C.MYSTERY_WORDS[player.round_number - 1].lower():
                player.correct_guess1 = True
            else:
                player.correct_guess1 = False
        
class Guess_Page2(Page):
    timeout_seconds = 5000
    def is_displayed(player):
        return player.player_role == 'Ratender' and player.correct_guess1 == False
    
    def vars_for_template(player):  
        vote_group = player.vote_group
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        return dict(vote_group=vote_group, mystery_word = mystery_word)
    
    form_model = 'player'
    form_fields = ['guess2'] 
    
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.guess2 = 'Kein Tipp gegeben'
            player.correct_guess2 = False
        else:
            special_char_map = {ord('ä'):'ae', ord('ü'):'ue', ord('ö'):'oe', ord('ß'):'ss'}
            player.guess2 = player.guess2.lower().translate(special_char_map) 
            if player.guess2 == C.MYSTERY_WORDS[player.round_number - 1].lower():
                player.correct_guess2 = True
            else:
                player.correct_guess2 = False

class Guess_Page3(Page):
    timeout_seconds = 5000
    def is_displayed(player): 
        return player.player_role == 'Ratender' and player.field_maybe_none('correct_guess2') == False
    
    def vars_for_template(player):  
        vote_group = player.vote_group
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        return dict(vote_group=vote_group, mystery_word = mystery_word)
    
    form_model = 'player'
    form_fields = ['guess3'] 
    
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.guess3 = 'Kein Tipp gegeben'
            player.correct_guess3 = False
        else:
            special_char_map = {ord('ä'):'ae', ord('ü'):'ue', ord('ö'):'oe', ord('ß'):'ss'}
            player.guess3 = player.guess3.lower().translate(special_char_map) 
            if player.guess3 == C.MYSTERY_WORDS[player.round_number - 1].lower():
                player.correct_guess3 = True
            else:
                player.correct_guess3 = False

class PairCheck(Page):
    timeout_seconds = 5000
    def is_displayed(player):
        return player.player_role == 'Ratender'

    form_model = 'player'
    def get_form_fields(player: Player):
        hint_groups = [g for g in player.subsession.get_groups() if g.get_players()[0].player_role == 'Hinweisgebende']
        index = (player.id_in_group - 1 + player.round_number - 1) % len(hint_groups)
        pairs = hint_groups[index].get_players()[0].pairsafter.split(', ') 
        form_fields = ['check_invalid_' + str(i+1) for i in range(len(pairs))]
        return form_fields

    def vars_for_template(player):  
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        hint_groups = [g for g in player.subsession.get_groups() if g.get_players()[0].player_role == 'Hinweisgebende']
        index = (player.id_in_group - 1 + player.round_number - 1) % len(hint_groups)
        pairs = hint_groups[index].get_players()[0].pairsafter.split(', ')
        return dict(mystery_word = mystery_word, pairs = pairs)

class Results(Page):
    timeout_seconds = 5000
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        taboo_words = C.TABOO_WORDS[player.round_number - 1]

        def calculate_result(player, guesses, mystery_word):
            if mystery_word == guesses[0]:
                return 'richtig', 3
            elif mystery_word == guesses[1]:
                return 'richtig', 2
            elif mystery_word == guesses[2]:
                return 'richtig', 1
            else:
                return 'falsch', 0
        
        if player.player_role == 'Hinweisgebende':
            vote_group = [p.vote_group for p in player.get_others_in_group()]
            while '' in vote_group:
                vote_group.remove('')
            invalid = ''              
            player.invalid = False
            vote_group = vote_group[0]
            if vote_group == 'Kein gültiges Hinweispaar':
                player.invalid = True
                invalid = 'Achtung! Das Hinweispaar Ihrer Gruppe war ungültig.'
            pairs = player.pairsafter.split(', ')
            guesser = next((p for p in player.subsession.get_players() if p.vote_group == player.vote_group and p.player_role == 'Ratender' and p.group != player.group), None)
            check_invalid = []
            if guesser is not None:
                guesses = [guesser.guess1, guesser.guess2, guesser.guess3]
                for i in range(len(pairs)):
                    attr_name = f"check_invalid_{i+1}"  
                    attr_value = getattr(guesser, attr_name, None)  
                    if attr_value is not None:
                        check_invalid.append(attr_value)
            else:
                guesses = [None, None, None]
            player.missing = False
            missing = ''
            while '' in check_invalid:
                check_invalid.remove('')
            player.quantity = len(pairs) - len(check_invalid)
            player.result, player.payoff = calculate_result(player, guesses, mystery_word)
            if player.quantity == 0:
                player.missing = True
                missing = 'Achtung! Sie haben kein gültiges Hinweispaar abgegeben.'        
            player.score =  int(player.participant.payoff)
            player.group.payoff =  player.score 
            player.group.quantity = player.quantity        
            if player.participant.treatment == 1:
                player.group.quantity = 1000
                player.group.payoff = 1000
            return dict (mystery_word = mystery_word, taboo_words = taboo_words, vote_group = player.vote_group, payoff = player.payoff, guess1 = guesses[0], guess2 = guesses[1], guess3 = guesses[2], result = player.result, player_role = player.player_role, missing = missing, invalid = invalid, number_ideas = player.quantity)
        else:
            player.guess_missing = False
            guess_missing = ''
            guesses = [player.guess1, player.guess2, player.guess3]
            if player.guess1 == 'Kein Tipp gegeben':
                player.guess_missing = True
                guess_missing = 'Achtung! Sie haben keinen Tipp abgegeben.'
            player.result, player.payoff = calculate_result(player, guesses, mystery_word)
            player.score =  int(player.participant.payoff)
            player.group.payoff =  player.score 
            if player.participant.treatment == 1:
                player.group.payoff = 1000
            return dict (mystery_word = mystery_word, taboo_words = taboo_words, vote_group = player.vote_group, payoff = player.payoff, guess1 = guesses[0], guess2 = guesses[1], guess3 = guesses[2], result = player.result, player_role = player.player_role, guess_missing = guess_missing)

def get_sorted_scores(groups, attribute):
    scores = [getattr(group, attribute) for group in groups if getattr(group, attribute) != 1000]
    return sorted(scores, reverse=True)

def get_overall_scores(group, attribute):
    subsession = group.subsession
    groups = subsession.get_groups()
    return get_sorted_scores(groups, attribute)

def calculate_rank(score, sorted_scores):
    rank = 0
    if score == sorted_scores[0]:
        rank = 1
    elif score == sorted_scores[1] and score != sorted_scores[0]:
        rank = 2
    elif len(sorted_scores) > 2 and score == sorted_scores[2] and score not in sorted_scores[:2]:
        rank = 3
    elif len(sorted_scores) > 3 and score == sorted_scores[3] and score not in sorted_scores[:3]:
        rank = 4
    elif len(sorted_scores) > 4 and score == sorted_scores[4] and score not in sorted_scores[:4]:
        rank = 5
    return rank

class Score(Page):
    timeout_seconds = 30
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende' and player.participant.treatment == 3 and player.round_number	== C.NUM_ROUNDS
    def vars_for_template(player):
        player.score =  int(player.participant.payoff)
        overall_score = get_overall_scores(player.group, 'payoff')
        rank = calculate_rank(player.score, overall_score)
        number_groups = len(overall_score)
        return dict(overall_score = overall_score, score = player.score, rank = rank, number_groups = number_groups)
    
class Score2(Page):
    timeout_seconds = 30
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende' and player.participant.treatment == 2 and player.round_number	== C.NUM_ROUNDS
    def vars_for_template(player):
        player.quantity = player.group.quantity
        overall_quantity = get_overall_scores(player.group, 'quantity')
        rank = calculate_rank(player.quantity, overall_quantity)
        number_groups = len(overall_quantity)
        return dict(overall_quantity = overall_quantity, quantity = player.quantity, rank = rank, number_groups = number_groups)
    
class Score3(Page): 
    timeout_seconds = 30
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende' and player.participant.treatment == 4 and player.round_number	== C.NUM_ROUNDS
    def vars_for_template(player):
        player.originality = player.group.originality
        overall_originality = get_overall_scores(player.group, 'originality')
        rank = calculate_rank(player.originality, overall_originality)
        number_groups = len(overall_originality)
        return dict(overall_originality = overall_originality, originality = player.originality, rank = rank, number_groups = number_groups)

class TestQuestions(Page):
    template_name = 'new_justone_deutsch_oR/TestQuestions.html'
    timeout_seconds = 270
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    form_model = 'player'
    form_fields = ['known', 'understanding', 'comments', 'comments_2', 'strategy', 'strategy_2', 'strategy_3', 'strategy_4', 'strategy_5', 'group_individual', 'strategy_6', 'strategy_7']

class IndividualismQuestions(Page):
    template_name = 'justone_deutsch/IndividualismQuestions.html'
    timeout_seconds = 120
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    form_model = 'player'
    form_fields = ['individualism_1', 'individualism_2', 'individualism_3', 'individualism_4', 'individualism_5']

class DAT(Page):
    timeout_seconds = 270
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    form_model = 'player'
    form_fields = ['word1', 'word2', 'word3', 'word4', 'word5', 'word6', 'word7', 'word8', 'word9', 'word10', 'gender', 'age', 'study']
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.invalid_DAT = True
            return player.invalid_DAT
        else:
            player.invalid_DAT = False
            return player.invalid_DAT

class FinalPage(Page):
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    
# WAIT PAGES

class GroupWaitPage(WaitPage):
    template_name = 'new_justone_deutsch_oR/GroupWaitPage.html'
    def is_displayed(player):
        return player.round_number == 1
        
class Generation_WaitPage(WaitPage):
    title_text = "Vielen Dank für Ihre Hinweispaare!"
    body_text = "Bitte warten Sie, bis alle ihre Hinweispaare abgegeben haben."
    wait_for_all_players = True
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende'
    
class Clue_WaitPage(WaitPage):
    title_text = "Vielen Dank für Ihr Feedback!"
    body_text = "Bitte warten Sie, bis all Ihre Gruppenmitglieder ihr Feedback abgegeben haben."
    wait_for_all_players = True
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende'

class VotingWaitPage(WaitPage):
    title_text = "Vielen Dank für Ihre Hinweispaare"
    body_text = "Bitte warten Sie, bis alle ihre Hinweispaare abgegeben haben."
    wait_for_all_players = True
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende'   
    
class VotingResultWaitPage(WaitPage):
    title_text = "Vielen Dank für Ihre Abstimmung!"
    body_text = "Bitte warten Sie, bis alle ihre Stimmen abgegeben haben."
    wait_for_all_players = True
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende'
    
class GuesserWaitPage(WaitPage):
    title_text = "Sie können Ihren Tipp bald abgeben"
    body_text = "Bitte warten Sie, bis die anderen Spielenden ein Hinweispaar für Sie abgegeben haben. Dies kann ein paar Minuten dauern."
    def is_displayed(player): 
        return player.player_role == 'Ratender'
    wait_for_all_groups = True    

class CluegiverWaitPage(WaitPage):
    title_text = "Vielen Dank für Ihr Hinweispaar!"
    body_text = "Das Hinweispaar wird nun dem Ratenden gezeigt."
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende'
    wait_for_all_groups = True
   
class ResultsWaitPage(WaitPage):
    title_text = "Ihre Gruppe ist fertig!"
    body_text = "Bitte warten Sie, bis alle Gruppen ihre Hinweispaare und Tipps abgegeben haben."
    wait_for_all_groups = True

page_sequence = [GroupWaitPage, Intro, Intro2, Rules, Instructions, UnderstandPage, Round, Generation_Page, Generation_WaitPage, Discussion, Clue_WaitPage, Clue_Page, VotingWaitPage, Voting_Page, VotingResultWaitPage, VotingResultPage, Originality_Calculation, GuesserWaitPage, CluegiverWaitPage, Guess_Page1, Guess_Page2, Guess_Page3, PairCheck, ResultsWaitPage, Results, Score, Score2, Score3, TestQuestions, IndividualismQuestions, DAT, FinalPage]