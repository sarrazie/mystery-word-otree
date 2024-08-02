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
    NUM_ROUNDS = 2
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
    ACHIEVEMENTS= ['Bildende_Kunst', 'Musik', 'Tanz', 'Architektur', 'Literatur', 'Humor', 'Erfindungen', 'Wissenschaftliche_Entdeckungen', 'Theater_und_Film', 'Kochen']

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    quality = models.IntegerField(initial=0)
    quantity = models.IntegerField(initial=0)
    originality = models.FloatField(initial=0)

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
    player_role2 = models.StringField()
    incentive = models.IntegerField()
    comments = models.LongStringField(label="<b>4. </b> Welche Strategie haben sie als Hinweisgebende verfolgt?", initial='', max_length=500, blank=True)
    comments_2 = models.LongStringField(label="<b>5. </b> Welche Strategie haben sie als Ratender verfolgt?", initial='', max_length=500, blank=True)
    understand_1 = models.StringField(choices=[['false', 'Unbegrenzt viele Versuche'],['false', 'Zwei Versuche'],['false', 'Drei Versuche'],['true', 'Nur einen Versuch']], label='<b>Frage 1:</b> Wie viele Versuche hat der Ratende, um das geheime Wort zu erraten?', widget=widgets.RadioSelect)
    understand_2 = models.StringField(choices=[['false,','Zwei'],['false', 'Drei'],['true', 'Vier'],['false', 'Fünf']], label='<b>Frage 2:</b> Wie viele Spielerinnen und Spieler bilden zusammen eine Gruppe?', widget=widgets.RadioSelect)
    understand_3= models.StringField(choices=[['true', '10 Euro fix für die Teilnahme an allen Runden'],['false', '5 Euro fix plus 5 Euro Bonus für die meisten generierten Ideen'],['false', '5 Euro fix plus 5 Euro Bonus für die meisten erratenen geheimen Wörter'],['false','5 Euro fix plus 5 Euro Bonus für die originellsten Hinweispaare, die zur richtigen Erratung des Wortes führen']], label='<b>Frage 3:</b> Wie viel Geld können Sie maximal in diesem Experiment verdienen?', widget=widgets.RadioSelect)
    understand_4 = models.StringField(choices=[['false', 'Time'], ['false', 'Zeitpunkt'],['false', 'ist Geld'],['false', 'Zeeeit'],['true', 'keiner der oben genannten Hinweise']], label='<b>Frage 4:</b> Welcher der folgenden Hinweise wäre ein gültiger Hinweis in einem Hinweispaar für das geheime Wort "Zeit"?', widget=widgets.RadioSelect)
    strategy_5 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>10. </b>"Es fiel mir aufgrund der fünf Tabuwörter sehr schwer, gute Hinweise zu schreiben."', widget=widgets.RadioSelectHorizontal)
    group_individual = models.StringField(choices=[['Gruppe', 'Es war produktiv, in der Gruppe zu arbeiten'], ['Individuell', 'Ich hätte lieber alleine Hinweise gegeben']], label='<b>11. </b>Wie haben Sie die Zusammenarbeit in Ihrer Gruppe erlebt?', widget=widgets.RadioSelectHorizontal)
    motivation = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>14. </b>"Mir hat die Arbeit an der Aufgabe Spaß gemacht."', widget=widgets.RadioSelectHorizontal)
    Bildende_Kunst = models.BooleanField(blank=True, initial=False)
    Musik = models.BooleanField(blank=True, initial=False)
    Tanz = models.BooleanField(blank=True, initial=False)
    Architektur = models.BooleanField(blank=True, initial=False)
    Literatur = models.BooleanField(blank=True, initial=False)
    Humor = models.BooleanField(blank=True, initial=False)
    Erfindungen = models.BooleanField(blank=True, initial=False)
    Wissenschaftliche_Entdeckungen = models.BooleanField(blank=True, initial=False)
    Theater_und_Film = models.BooleanField(blank=True, initial=False)
    Kochen = models.BooleanField(blank=True, initial=False)
    Bildende_Kunst_2_1 = models.IntegerField(blank=True)
    Bildende_Kunst_2_2 = models.IntegerField(blank=True)
    Bildende_Kunst_2_3 = models.IntegerField(blank=True)
    Bildende_Kunst_2_4 = models.IntegerField(blank=True)
    Bildende_Kunst_2_5 = models.IntegerField(blank=True)
    Bildende_Kunst_2_6 = models.IntegerField(blank=True)
    Bildende_Kunst_2_7 = models.IntegerField(blank=True)
    Musik_2_1 = models.IntegerField(blank=True) 
    Musik_2_2 = models.IntegerField(blank=True)
    Musik_2_3 = models.IntegerField(blank=True)
    Musik_2_4 = models.IntegerField(blank=True)
    Musik_2_5 = models.IntegerField(blank=True)
    Musik_2_6 = models.IntegerField(blank=True)
    Musik_2_7 = models.IntegerField(blank=True) 
    Tanz_2_1 = models.IntegerField(blank=True)
    Tanz_2_2 = models.IntegerField(blank=True)
    Tanz_2_3 = models.IntegerField(blank=True)
    Tanz_2_4 = models.IntegerField(blank=True)
    Tanz_2_5 = models.IntegerField(blank=True)
    Tanz_2_6 = models.IntegerField(blank=True)
    Tanz_2_7 = models.IntegerField(blank=True)
    Architektur_2_1 = models.IntegerField(blank=True)
    Architektur_2_2 = models.IntegerField(blank=True)
    Architektur_2_3 = models.IntegerField(blank=True)
    Architektur_2_4 = models.IntegerField(blank=True)
    Architektur_2_5 = models.IntegerField(blank=True)
    Architektur_2_6 = models.IntegerField(blank=True)
    Architektur_2_7 = models.IntegerField(blank=True)
    Literatur_2_1 = models.IntegerField(blank=True)
    Literatur_2_2 = models.IntegerField(blank=True)
    Literatur_2_3 = models.IntegerField(blank=True)
    Literatur_2_4 = models.IntegerField(blank=True)
    Literatur_2_5 = models.IntegerField(blank=True)
    Literatur_2_6 = models.IntegerField(blank=True)
    Literatur_2_7 = models.IntegerField(blank=True)
    Humor_2_1 = models.IntegerField(blank=True)
    Humor_2_2 = models.IntegerField(blank=True)
    Humor_2_3 = models.IntegerField(blank=True)
    Humor_2_4 = models.IntegerField(blank=True)
    Humor_2_5 = models.IntegerField(blank=True)
    Humor_2_6 = models.IntegerField(blank=True)
    Humor_2_7 = models.IntegerField(blank=True)
    Erfindungen_2_1 = models.IntegerField(blank=True)
    Erfindungen_2_2 = models.IntegerField(blank=True)
    Erfindungen_2_3 = models.IntegerField(blank=True)
    Erfindungen_2_4 = models.IntegerField(blank=True)
    Erfindungen_2_5 = models.IntegerField(blank=True)
    Erfindungen_2_6 = models.IntegerField(blank=True)
    Erfindungen_2_7 = models.IntegerField(blank=True)
    Wissenschaftliche_Entdeckungen_2_1 = models.IntegerField(blank=True)
    Wissenschaftliche_Entdeckungen_2_2 = models.IntegerField(blank=True)
    Wissenschaftliche_Entdeckungen_2_3 = models.IntegerField(blank=True)
    Wissenschaftliche_Entdeckungen_2_4 = models.IntegerField(blank=True)
    Wissenschaftliche_Entdeckungen_2_5 = models.IntegerField(blank=True)
    Wissenschaftliche_Entdeckungen_2_6 = models.IntegerField(blank=True)
    Wissenschaftliche_Entdeckungen_2_7 = models.IntegerField(blank=True)
    Theater_und_Film_2_1 = models.IntegerField(blank=True)
    Theater_und_Film_2_2 = models.IntegerField(blank=True)
    Theater_und_Film_2_3 = models.IntegerField(blank=True)
    Theater_und_Film_2_4 = models.IntegerField(blank=True)
    Theater_und_Film_2_5 = models.IntegerField(blank=True)
    Theater_und_Film_2_6 = models.IntegerField(blank=True)
    Theater_und_Film_2_7 = models.IntegerField(blank=True)
    Kochen_2_1 = models.IntegerField(blank=True)
    Kochen_2_2 = models.IntegerField(blank=True)
    Kochen_2_3 = models.IntegerField(blank=True)
    Kochen_2_4 = models.IntegerField(blank=True)
    Kochen_2_5 = models.IntegerField(blank=True)
    Kochen_2_6 = models.IntegerField(blank=True)
    Kochen_2_7 = models.IntegerField(blank=True)
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
    gender = models.IntegerField(choices=[[1, 'Männlich'],[2, 'Weiblich'],[3, 'Divers'],], label='Geschlecht:', blank=False)
    age = models.IntegerField(min=18, max=100, label='Alter:', blank=False)
    study = models.StringField(choices=[['Geisteswissenschaften', 'Geisteswissenschaften'],['Sport', 'Sport'],['Rechts-, Wirtschafts- und Sozialwissenschaften', 'Rechts-, Wirtschafts- und Sozialwissenschaften'],['Mathematik, Naturwissenschaften', 'Mathematik, Naturwissenschaften'],['Humanmedizin, Gesundheitswissenschaften', 'Humanmedizin, Gesundheitswissenschaften'],['Agrar-, Forst- und Ernährungswissenschaften, Veterinärmedizin', 'Agrar-, Forst- und Ernährungswissenschaften, Veterinärmedizin'], ['Ingenieurwissenschaften', 'Ingenieurwissenschaften'],['Kunst, Kunstwissenschaft', 'Kunst, Kunstwissenschaft'],['Sonstiges', 'Sonstiges'],], label='Studienbereich:', widget=widgets.RadioSelect, blank=False)
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
    group_number_check = models.IntegerField()
    group_number_guess = models.IntegerField()
    group_number_rating = models.IntegerField()
    usefulness_1 = models.StringField(blank=True)
    usefulness_2 = models.StringField(blank=True)
    usefulness_3 = models.StringField(blank=True)
    usefulness_4 = models.StringField(blank=True)
    usefulness_5 = models.StringField(blank=True)
    usefulness_6 = models.StringField(blank=True)
    usefulness_7 = models.StringField(blank=True)
    usefulness_8 = models.StringField(blank=True)
    usefulness_9 = models.StringField(blank=True)
    usefulness_10 = models.StringField(blank=True)
    usefulness_11 = models.StringField(blank=True)
    usefulness_12 = models.StringField(blank=True)
    usefulness_13 = models.StringField(blank=True)
    usefulness_14 = models.StringField(blank=True)
    usefulness_15 = models.StringField(blank=True)
    originality_1 = models.StringField(blank=True)
    originality_2 = models.StringField(blank=True)
    originality_3 = models.StringField(blank=True)
    originality_4 = models.StringField(blank=True)
    originality_5 = models.StringField(blank=True)
    originality_6 = models.StringField(blank=True)
    originality_7 = models.StringField(blank=True)
    originality_8 = models.StringField(blank=True)
    originality_9 = models.StringField(blank=True)
    originality_10 = models.StringField(blank=True)
    originality_11 = models.StringField(blank=True)
    originality_12 = models.StringField(blank=True)
    originality_13 = models.StringField(blank=True)
    originality_14 = models.StringField(blank=True)
    originality_15 = models.StringField(blank=True)
    creativity_1 = models.StringField(blank=True)
    creativity_2 = models.StringField(blank=True)
    creativity_3 = models.StringField(blank=True)
    creativity_4 = models.StringField(blank=True)
    creativity_5 = models.StringField(blank=True)
    creativity_6 = models.StringField(blank=True)
    creativity_7 = models.StringField(blank=True)
    creativity_8 = models.StringField(blank=True)
    creativity_9 = models.StringField(blank=True)
    creativity_10 = models.StringField(blank=True)
    creativity_11 = models.StringField(blank=True)
    creativity_12 = models.StringField(blank=True)
    creativity_13 = models.StringField(blank=True)
    creativity_14 = models.StringField(blank=True)
    creativity_15 = models.StringField(blank=True)
    number_pairs_after = models.IntegerField()
    circle_overlap = models.FloatField(label="Overlap Percentage",blank=True)
    explanation = models.LongStringField(label='<b>6. </b>Bitte beschreiben Sie, warum sich Ihre Gruppe final für dieses Hinweispaar entschieden hat. (optional)', blank=True, max_length=500)
    subjective_originality = models.IntegerField(choices=[0, 1, 2, 3 ,4, 5, 6, 7, 8, 9, 10],label = '<b>4. </b>Bitte bewerten Sie ihr finales Hinweispaar auf einer Skala von 0 bis 10, wie <b>originell</b> Sie es finden. <br> (0 = überhaupt nicht originell, 10 = sehr originell)', widget=widgets.RadioSelectHorizontal, blank= False)
    subjective_quality = models.IntegerField(choices=[0, 1, 2, 3 ,4, 5, 6, 7, 8, 9, 10,],label = '<b>5. </b>Bitte bewerten Sie ihr finales Hinweispaar auf einer Skala von 0 bis 10, wie <b>nützlich</b> es zur Erratung des geheimen Wortes ist. <br> (0 = überhaupt nicht nützlich, 10 = sehr nützlich)', widget=widgets.RadioSelectHorizontal, blank= False)
    rat1 = models.StringField(label= '', initial='', blank=True, max_length=18)
    rat2 = models.StringField(label= '', initial='', blank=True, max_length=18)
    rat3 = models.StringField(label= '', initial='', blank=True, max_length=18)
    rat4 = models.StringField(label= '', initial='', blank=True, max_length=18)
    rat5 = models.StringField(label= '', initial='', blank=True, max_length=18)
    rat6 = models.StringField(label= '', initial='', blank=True, max_length=18)
    rat7 = models.StringField(label= '', initial='', blank=True, max_length=18)
    rat8 = models.StringField(label= '', initial='', blank=True, max_length=18)
    rat9 = models.StringField(label= '', initial='', blank=True, max_length=18)
    rat10 = models.StringField(label= '', initial='', blank=True, max_length=18) 
    creative_self1 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], widget=widgets.RadioSelectHorizontal, blank=False, label = '<b> 1. </b>Ich denke, dass ich eine kreative Person bin.')
    creative_self2 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], widget=widgets.RadioSelectHorizontal, blank=False, label = '<b> 2. </b>Meine Vorstellungskraft und mein Einfallsreichtum unterscheiden mich von meinen Freunden.')
    creative_self3 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], widget=widgets.RadioSelectHorizontal, blank=False, label = '<b> 3. </b>Es ist mir wichtig, eine kreative Person zu sein.')
    creative_self4 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], widget=widgets.RadioSelectHorizontal, blank=False, label = '<b> 4. </b>Ich weiß, dass ich auch komplizierte Probleme effizient lösen kann.')
    creative_self5 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], widget=widgets.RadioSelectHorizontal, blank=False, label = '<b> 5. </b>Kreativität ist ein wichtiger Teil meines Selbstbilds.')
    creative_self6 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], widget=widgets.RadioSelectHorizontal, blank=False, label = '<b> 6. </b>Ich bin gut darin, kreative Lösungen für Probleme zu finden.')
    trust_game = models.IntegerField(max=10, min=0, blank=False, label= '<b>Wie viel von den 10 EUR würden Sie senden?</b>')
    AUT = models.LongStringField(label='Geben Sie jeweils eine alternative Verwendungsmöglichkeit <b>pro Zeile</b> an.', blank=True, max_length=800)
    AUT2 = models.LongStringField(label='Geben Sie jeweils eine alternative Verwendungsmöglichkeit <b>pro Zeile</b> an.', blank=True, max_length=800)
    quality_score = models.IntegerField(initial=0)
    communication = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>1. </b>Die Kommunikation in meiner Gruppe war effektiv.', widget=widgets.RadioSelectHorizontal, blank=False)
    intensity_discussion = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>2. </b>Wir haben unsere Hinweispaare intensiv diskutiert.', widget=widgets.RadioSelectHorizontal, blank=False)
    decision = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>3. </b>Wir haben am Ende das beste Hinweispaar ausgewählt.', widget=widgets.RadioSelectHorizontal, blank=False)

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
    ingroup_count = 0
    outgroup_count = 0
    for player in players:
        participant = player.participant
        participant.vars['treatment'] = treatment
        player.incentive = treatment
        player.player_role = 'Hinweisgebende' if player in [p for group in hintgiver_groups for p in group] else 'Ratender'
        if player.player_role == 'Hinweisgebende':
            if ingroup_count < (num_players - (num_players // 4)) // 2:
                player.player_role2 = 'ingroup'
                ingroup_count += 1
            elif outgroup_count < (num_players - (num_players // 4)) // 2:
                player.player_role2 = 'outgroup'
                outgroup_count += 1
            else: 
                player.player_role2 = random.choice(['outgroup', 'ingroup'])
        else: 
            player.player_role2 = None

def validate_ideas(player, ideas):
    stem_words = C.STEM_WORDS[player.round_number - 1]     
    wordlist = set()
    with open("vocab_german.txt", 'r', encoding = 'utf-8') as file:
        for line in file:
            words = line.strip().split()
            wordlist.update(words)
    special_char_map = {ord('ä'):'ae', ord('ü'):'ue', ord('ö'):'oe', ord('ß'):'ss'}                    
    occurrences = {}
    if len(ideas) > 0:
        ideas_low = [idea.translate(special_char_map).lower() for idea in ideas]
        for i in range(len(ideas)): 
            if ideas[i] != '':
                if ' ' in ideas[i] and re.search(r'\b\w+\s+\w+\b', ideas[i]):
                    ideas[i] = 'false'
                if ' ' in ideas[i]:
                    ideas[i] = ideas[i].replace(' ', '')
                for j in range(len(stem_words)):
                    if stem_words[j] in ideas_low[i]:
                        ideas[i] = 'false'
                if re.search(r"[^a-zA-Z0-9\s]", ideas_low[i]):
                    ideas[i] = 'false'                 
                if bool(re.search(r'\d',ideas[i])):
                    ideas[i] = 'false'
                if ideas[i].lower() not in wordlist:
                    ideas[i] = 'false'
                if ideas[i] != 'false':
                    if ideas[i] in occurrences:
                        occurrences[ideas[i]] += 1
                        ideas[i] = 'false'
                    else:
                        occurrences[ideas[i]] = 1
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
    template_name = 'experiment/UnderstandPage.html'
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
        player.pairsafter = ', '.join(pairsafter)
        number_pairs = len(pairsafter)
        pairs_dict = {f'Pair{i+1}': pairsafter[i] if i < number_pairs else '' for i in range(15)}
        Pair1, Pair2, Pair3, Pair4, Pair5, Pair6, Pair7, Pair8, Pair9, Pair10, Pair11, Pair12, Pair13, Pair14, Pair15 = pairs_dict.values()
        return dict(mystery_word = mystery_word, taboo_words= taboo_words, number_pairs = number_pairs, Pair1 = Pair1, Pair2 = Pair2, Pair3 = Pair3, Pair4 = Pair4, Pair5 = Pair5, Pair6 = Pair6, Pair7 = Pair7, Pair8 = Pair8, Pair9 = Pair9, Pair10 = Pair10, Pair11 = Pair11, Pair12 = Pair12, Pair13 = Pair13, Pair14 = Pair14, Pair15 = Pair15, pairs = pairsafter)
  
class VotingResultPage(Page):
    timeout_seconds = 5000
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende'
    def vars_for_template(player):
        pairs = player.pairsafter.split(', ')
        votes = [player.vote] + [p.vote for p in player.get_others_in_group()]
        while '' in votes:
            votes.remove('')
        random.seed(42)
        duplicates = [v for v in set(votes) if votes.count(v) >= 2]
        number_duplicates = len(duplicates)
        votes = sorted(votes)
        empty_pairs = 1 if pairs == [''] else 0
        if len(duplicates) > 0:
            vote_group = duplicates[0]
        else:
            if len(votes) == 1:
                vote_group = votes[0]
            elif len(votes) > 1:
                i = random.randint(0, len(votes) - 1) 
                vote_group = votes[i]
            else:
                if pairs != ['']:
                    i = random.randint(0, len(pairs) - 1)
                    vote_group = pairs[i]  
                else:
                    vote_group = 'Kein gültiges Hinweispaar'
        player.vote_group = vote_group
        return dict(vote_group=vote_group, duplicates=number_duplicates, empty_pairs=empty_pairs)
    
class Guess_Page1(Page):
    timeout_seconds = 5000
    def is_displayed(player):
        return player.player_role == 'Ratender'
    
    def vars_for_template(player):  
        hint_groups = [g for g in player.subsession.get_groups() if g.get_players()[0].player_role == 'Hinweisgebende']
        index = (player.id_in_group - 1 + player.round_number - 1) % len(hint_groups)
        vote_group = hint_groups[index].get_players()[0].vote_group
        player.vote_group = vote_group
        player.group_number_guess = hint_groups[index].id_in_subsession
        return dict(vote_group=vote_group)
    
    form_model = 'player'
    form_fields = ['guess1'] 
    
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.guess1 = 'Kein Tipp gegeben'
            player.correct_guess1 = False
        else:
            special_char_map = {ord('ä'):'ae', ord('ü'):'ue', ord('ö'):'oe', ord('ß'):'ss'}
            if ' ' in player.guess1:
                player.guess1 = player.guess1.replace(' ', '')
            if player.guess1.lower().translate(special_char_map)  == C.MYSTERY_WORDS[player.round_number - 1].lower():
                player.correct_guess1 = True
            else:
                player.correct_guess1 = False
        
class Guess_Page2(Page):
    timeout_seconds = 5000
    def is_displayed(player):
        return player.player_role == 'Ratender' and player.correct_guess1 == False
    
    def vars_for_template(player):  
        vote_group = player.vote_group
        return dict(vote_group=vote_group)
    
    form_model = 'player'
    form_fields = ['guess2'] 
    
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.guess2 = 'Kein Tipp gegeben'
            player.correct_guess2 = False
        else:
            special_char_map = {ord('ä'):'ae', ord('ü'):'ue', ord('ö'):'oe', ord('ß'):'ss'}
            if ' ' in player.guess2:
                player.guess2 = player.guess2.replace(' ', '')
            if player.guess2.lower().translate(special_char_map)  == C.MYSTERY_WORDS[player.round_number - 1].lower():
                player.correct_guess2 = True
            else:
                player.correct_guess2 = False

class Guess_Page3(Page):
    timeout_seconds = 5000
    def is_displayed(player): 
        return player.player_role == 'Ratender' and player.field_maybe_none('correct_guess2') == False
    
    def vars_for_template(player):  
        vote_group = player.vote_group
        return dict(vote_group=vote_group)
    
    form_model = 'player'
    form_fields = ['guess3'] 
    
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.guess3 = 'Kein Tipp gegeben'
            player.correct_guess3 = False
        else:
            special_char_map = {ord('ä'):'ae', ord('ü'):'ue', ord('ö'):'oe', ord('ß'):'ss'}
            if ' ' in player.guess3:
                player.guess3 = player.guess3.replace(' ', '')
            if player.guess3.lower().translate(special_char_map)  == C.MYSTERY_WORDS[player.round_number - 1].lower():
                player.correct_guess3 = True
            else:
                player.correct_guess3 = False

class PairCheck(Page):
    timeout_seconds = 5000
    def is_displayed(player):
        return player.player_role == 'Ratender'
    
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        hint_groups = [g for g in player.subsession.get_groups() if g.get_players()[0].player_role == 'Hinweisgebende']
        index = (player.id_in_group -1 + player.round_number) % len(hint_groups)  
        pairs = hint_groups[index].get_players()[0].pairsafter.split(', ')
        player.group_number_check = hint_groups[index].id_in_subsession
        while '' in pairs:
            pairs.remove('')
        number_pairs = len(pairs)
        return dict(mystery_word=mystery_word, pairs=pairs, number_pairs = number_pairs)
    
    form_model = 'player'
    def get_form_fields(player:Player):
        hint_groups = [g for g in player.subsession.get_groups() if g.get_players()[0].player_role == 'Hinweisgebende']
        index = (player.id_in_group - 1 + player.round_number) % len(hint_groups)  
        pairs = hint_groups[index].get_players()[0].pairsafter.split(', ')
        form_fields = ['check_invalid_' + str(i+1) for i in range(len(pairs))]
        return form_fields
    
class Originality_Calculation(Page):
    timeout_seconds = 5000
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende' and player.participant.treatment == 4
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1].lower()
        if player.vote_group != 'Kein gültiges Hinweispaar':        
            vote_group = player.vote_group.lower()
            for p in player.get_others_in_group():
                if p.field_maybe_none('originality') is not None:
                    originality = p.originality
                else:
                    with Model() as model:
                        with ThreadPoolExecutor() as executor:
                            future = executor.submit(model.calculate_originality, vote_group, mystery_word)
                            originality = future.result()
                        if originality is None:
                            originality = 0
        else:
            originality = 0
        originality = round(originality, 2)
        player.originality = float(originality) 
        return dict(vote_group = player.vote_group, originality = originality)
    
class DecisionConfidence(Page):
    timeout_seconds = 5000
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende'
    form_model = 'player'
    form_fields = ['communication', 'intensity_discussion', 'decision', 'subjective_originality', 'subjective_quality', 'explanation']
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        taboo_words = C.TABOO_WORDS[player.round_number - 1]
        own_vote = player.vote
        group_vote = player.vote_group
        return dict(mystery_word = mystery_word, taboo_words = taboo_words, own_vote = own_vote, group_vote = group_vote)
    
class Results(Page):
    timeout_seconds = 5000
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        taboo_words = C.TABOO_WORDS[player.round_number - 1]
        guesser = next((p for p in player.subsession.get_players() if p.player_role == 'Ratender' and p.group_number_guess == player.group.id_in_subsession), None)
        rater = next((p for p in player.subsession.get_players() if p.player_role == 'Ratender' and p.group_number_check == player.group.id_in_subsession), None)

        def calculate_result(player, guesses, mystery_word):
            mystery_word_lower = mystery_word.lower()
            guesses_lower = [guess.lower() for guess in guesses]
            if mystery_word_lower == guesses_lower[0]:
                return 'richtig', 3
            elif mystery_word_lower == guesses_lower[1]:
                return 'richtig', 2
            elif mystery_word_lower == guesses_lower[2]:
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
            check_invalid = []
            if guesser is not None:
                guesses = [guesser.guess1, guesser.guess2, guesser.guess3]
            else:
                guesses = [None, None, None]
            if rater is not None:
                for i in range(len(pairs)):
                    attr_name = f"check_invalid_{i+1}"  
                    attr_value = getattr(rater, attr_name, None)  
                    if attr_value is not None:
                        check_invalid.append(attr_value)
            player.missing = False
            missing = ''
            while '' in check_invalid:
                check_invalid.remove('')
            while '' in pairs:
                pairs.remove('')
            player.quantity = len(pairs) - len(check_invalid)
            player.result, player.score = calculate_result(player, guesses, mystery_word)
            if player.quantity == 0:
                player.missing = True
                missing = 'Achtung! Sie haben kein gültiges Hinweispaar abgegeben.'  
            quality_scores = []
            originality_scores = []
            quantity_scores = []
            for i in range(player.round_number):
                quality_scores.append(player.in_round(player.round_number - i).score)
                player.group.quality =  sum(quality_scores)  
                quantity_scores.append(player.in_round(player.round_number - i).quantity)
                player.group.quantity = sum(quantity_scores)  
                if player.participant.treatment == 4: 
                    originality_scores.append(float(player.in_round(player.round_number - i).originality))
                    player.group.originality = sum(originality_scores) / player.round_number 
            return dict (mystery_word = mystery_word, taboo_words = taboo_words, vote_group = player.vote_group, guess1 = guesses[0], guess2 = guesses[1], guess3 = guesses[2], result = player.result, player_role = player.player_role, missing = missing, invalid = invalid, number_ideas = player.quantity)
        else:
            player.guess_missing = False
            guess_missing = ''
            guesses = [player.guess1, player.guess2, player.guess3]
            if player.guess1 == 'Kein Tipp gegeben':
                player.guess_missing = True
                guess_missing = 'Achtung! Sie haben keinen Tipp abgegeben.'
            player.result, player.score = calculate_result(player, guesses, mystery_word)
            guesser_scores = []
            for i in range(player.round_number):
                guesser_scores.append(player.in_round(player.round_number - i).score)
                player.quality_score= sum(guesser_scores)
            return dict (mystery_word = mystery_word, taboo_words = taboo_words, vote_group = player.vote_group, guess1 = guesses[0], guess2 = guesses[1], guess3 = guesses[2], result = player.result, player_role = player.player_role, guess_missing = guess_missing)

class Usefulness(Page):
    timeout_seconds = 5000
    def is_displayed(player):
        return player.player_role == 'Ratender'
    
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        hint_groups = [g for g in player.subsession.get_groups() if g.get_players()[0].player_role == 'Hinweisgebende']
        index = (player.id_in_group + player.round_number) % len(hint_groups)  
        pairs = hint_groups[index].get_players()[0].pairsafter.split(', ')
        player.group_number_rating = hint_groups[index].id_in_subsession
        while '' in pairs:
            pairs.remove('')
        player.number_pairs_after = len(pairs)
        choices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        return dict(mystery_word=mystery_word, pairs=pairs, choices = choices, number_pairs = player.number_pairs_after)
    
    form_model = 'player'
    form_fields = ['usefulness_1', 'usefulness_2', 'usefulness_3', 'usefulness_4', 'usefulness_5', 'usefulness_6', 'usefulness_7', 'usefulness_8', 'usefulness_9', 'usefulness_10', 'usefulness_11', 'usefulness_12', 'usefulness_13', 'usefulness_14', 'usefulness_15']

def dimension_error_message(player, value, threshold):
    if value == '' and player.number_pairs_after > threshold:
        return f'Bitte wählen Sie eine Antwort für Paar {threshold + 1} aus!'

def usefulness_1_error_message(player, value):
    return dimension_error_message(player, value, 0)

def usefulness_2_error_message(player, value):
    return dimension_error_message(player, value, 1)

def usefulness_3_error_message(player, value):
    return dimension_error_message(player, value, 2)

def usefulness_4_error_message(player, value):
    return dimension_error_message(player, value, 3)

def usefulness_5_error_message(player, value):
    return dimension_error_message(player, value, 4)

def usefulness_6_error_message(player, value):
    return dimension_error_message(player, value, 5)

def usefulness_7_error_message(player, value):
    return dimension_error_message(player, value, 6)

def usefulness_8_error_message(player, value):
    return dimension_error_message(player, value, 7)

def usefulness_9_error_message(player, value):
    return dimension_error_message(player, value, 8)

def usefulness_10_error_message(player, value):
    return dimension_error_message(player, value, 9)

def usefulness_11_error_message(player, value):
    return dimension_error_message(player, value, 10)

def usefulness_12_error_message(player, value):
    return dimension_error_message(player, value, 11)

def usefulness_13_error_message(player, value):
    return dimension_error_message(player, value, 12)

def usefulness_14_error_message(player, value):
    return dimension_error_message(player, value, 13)

def usefulness_15_error_message(player, value):
    return dimension_error_message(player, value, 14)
   
class Originality(Page):
    timeout_seconds = 5000
    def is_displayed(player):
        return player.player_role == 'Ratender'
    
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        hint_groups = [g for g in player.subsession.get_groups() if g.get_players()[0].player_role == 'Hinweisgebende']
        index = (player.id_in_group + player.round_number) % len(hint_groups)  
        pairs = hint_groups[index].get_players()[0].pairsafter.split(', ')
        while '' in pairs:
            pairs.remove('')
        player.number_pairs_after = len(pairs)
        choices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        return dict(mystery_word=mystery_word, pairs=pairs, choices = choices, number_pairs = player.number_pairs_after)
    
    form_model = 'player'
    form_fields = ['originality_1', 'originality_2', 'originality_3', 'originality_4', 'originality_5', 'originality_6', 'originality_7', 'originality_8', 'originality_9', 'originality_10', 'originality_11', 'originality_12', 'originality_13', 'originality_14', 'originality_15']

def originality_1_error_message(player, value):
    return dimension_error_message(player, value, 0)

def originality_2_error_message(player, value):
    return dimension_error_message(player, value, 1)

def originality_3_error_message(player, value):
    return dimension_error_message(player, value, 2)

def originality_4_error_message(player, value):
    return dimension_error_message(player, value, 3)

def originality_5_error_message(player, value):
    return dimension_error_message(player, value, 4)

def originality_6_error_message(player, value):
    return dimension_error_message(player, value, 5)

def originality_7_error_message(player, value):
    return dimension_error_message(player, value, 6)

def originality_8_error_message(player, value):
    return dimension_error_message(player, value, 7)

def originality_9_error_message(player, value):
    return dimension_error_message(player, value, 8)

def originality_10_error_message(player, value):
    return dimension_error_message(player, value, 9)

def originality_11_error_message(player, value):
    return dimension_error_message(player, value, 10)

def originality_12_error_message(player, value):
    return dimension_error_message(player, value, 11)

def originality_13_error_message(player, value):
    return dimension_error_message(player, value, 12)

def originality_14_error_message(player, value):
    return dimension_error_message(player, value, 13)

def originality_15_error_message(player, value):
    return dimension_error_message(player, value, 14)

class Overall_Creativity(Page):
    timeout_seconds = 5000
    def is_displayed(player):
        return player.player_role == 'Ratender'
    
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        hint_groups = [g for g in player.subsession.get_groups() if g.get_players()[0].player_role == 'Hinweisgebende']
        index = (player.id_in_group + player.round_number) % len(hint_groups)  
        pairs = hint_groups[index].get_players()[0].pairsafter.split(', ')
        while '' in pairs:
            pairs.remove('')
        player.number_pairs_after = len(pairs)
        choices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        return dict(mystery_word=mystery_word, pairs=pairs, choices = choices, number_pairs = player.number_pairs_after)
    
    form_model = 'player'
    form_fields = ['creativity_1', 'creativity_2', 'creativity_3', 'creativity_4', 'creativity_5', 'creativity_6', 'creativity_7', 'creativity_8', 'creativity_9', 'creativity_10', 'creativity_11', 'creativity_12', 'creativity_13', 'creativity_14', 'creativity_15']
    
def creativity_1_error_message(player, value):
    return dimension_error_message(player, value, 0)

def creativity_2_error_message(player, value):
    return dimension_error_message(player, value, 1)
    
def creativity_3_error_message(player, value):
    return dimension_error_message(player, value, 2)

def creativity_4_error_message(player, value):
    return dimension_error_message(player, value, 3)

def creativity_5_error_message(player, value):
    return dimension_error_message(player, value, 4)
    
def creativity_6_error_message(player, value):
    return dimension_error_message(player, value, 5)

def creativity_7_error_message(player, value):
    return dimension_error_message(player, value, 6)
    
def creativity_8_error_message(player, value):
    return dimension_error_message(player, value, 7)

def creativity_9_error_message(player, value):
    return dimension_error_message(player, value, 8)
    
def creativity_10_error_message(player, value):
    return dimension_error_message(player, value, 9)
    
def creativity_11_error_message(player, value):
    return dimension_error_message(player, value, 10)
    
def creativity_12_error_message(player, value):
    return dimension_error_message(player, value, 11)
    
def creativity_13_error_message(player, value):
    return dimension_error_message(player, value, 12)
    
def creativity_14_error_message(player, value):
    return dimension_error_message(player, value, 13)
    
def creativity_15_error_message(player, value):
    return dimension_error_message(player, value, 14)

def get_sorted_scores(groups, attribute):
    scores = [getattr(group, attribute) for group in groups]
    return sorted(scores, reverse=True)

def get_overall_scores(group, attribute):
    subsession = group.subsession
    groups = [g for g in subsession.get_groups() if g.get_players()[0].player_role == 'Hinweisgebende']
    return get_sorted_scores(groups, attribute)

def get_overall_scores2(player, attribute):
    players = [player] + player.get_others_in_group() 
    return get_sorted_scores2(players, attribute)

def get_sorted_scores2(players, attribute):
    scores = [getattr(player, attribute) for player in players]
    return sorted(scores, reverse=True)

def calculate_rank(score, sorted_scores):
    rank = 1
    ranks = []
    for i in range(len(sorted_scores)):
        if i > 0 and sorted_scores[i] != sorted_scores[i - 1]:
            rank = len(ranks) + 1
        ranks.append(rank)
    return ranks[sorted_scores.index(score)], ranks

def calculate_payoff(rank, ranks):
    payoffs = {1: 20, 2: 15, 3: 12, 4: 10}
    rank_count = ranks.count(rank)
    if rank_count > 1:
        total_payoff = 0
        for r in range(rank, rank + rank_count):
            total_payoff += payoffs.get(r, 8) 
        return total_payoff / rank_count
    else:
        return payoffs.get(rank, 8)

class Score(Page):
    timeout_seconds = 2000
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende' and player.participant.treatment == 3 and player.round_number	== C.NUM_ROUNDS
    def vars_for_template(player):
        overall_score = get_overall_scores(player.group, 'quality')
        rank, ranks = calculate_rank(player.group.quality, overall_score)
        player.payoff = round(calculate_payoff(rank, ranks), 0)
        number_groups = len(overall_score)
        return dict(overall_score = overall_score, score = player.group.quality, payoff = player.payoff, rank = rank, number_groups = number_groups)
    
class Score2(Page):
    timeout_seconds = 2000
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende' and player.participant.treatment == 2 and player.round_number	== C.NUM_ROUNDS
    def vars_for_template(player):
        overall_quantity = get_overall_scores(player.group, 'quantity')
        rank, ranks = calculate_rank(player.group.quantity, overall_quantity)
        player.payoff = round(calculate_payoff(rank, ranks), 0)
        number_groups = len(overall_quantity)
        return dict(overall_quantity = overall_quantity, quantity = player.group.quantity, payoff = player.payoff, rank = rank, number_groups = number_groups)
    
class Score3(Page): 
    timeout_seconds = 2000
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende' and player.participant.treatment == 4 and player.round_number	== C.NUM_ROUNDS
    def vars_for_template(player):
        originality = round(player.group.originality, 2)
        overall_originality = get_overall_scores(player.group, 'originality')
        rank, ranks = calculate_rank(player.group.originality, overall_originality)
        player.payoff = round(calculate_payoff(rank, ranks), 0)
        number_groups = len(overall_originality)
        overall_originality = [round(score, 2) for score in overall_originality]
        return dict(overall_originality = overall_originality, originality = originality, payoff = player.payoff, rank = rank, number_groups = number_groups)
    
class Score4(Page):
    timeout_seconds = 2000
    def is_displayed(player):
        return player.player_role == 'Ratender' and player.round_number	== C.NUM_ROUNDS
    def vars_for_template(player):
        overall_score = get_overall_scores2(player, 'quality_score')
        rank, ranks = calculate_rank(player.quality_score, overall_score)
        player.payoff = round(calculate_payoff(rank, ranks), 0)
        number_groups = len(overall_score)
        return dict(overall_score = overall_score, score = player.quality_score, payoff = player.payoff, rank = rank, number_groups = number_groups)

class TestQuestions(Page):
    template_name = 'experiment/TestQuestions.html'
    timeout_seconds = 270
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    form_model = 'player'
    form_fields = ['comments', 'comments_2', 'strategy_5', 'group_individual', 'motivation']

class IndividualismQuestions(Page):
    template_name = 'experiment/IndividualismQuestions.html'
    timeout_seconds = 120
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    form_model = 'player'
    form_fields = ['age', 'gender', 'study', 'Bildende_Kunst', 'Musik', 'Tanz', 'Architektur', 'Literatur', 'Humor', 'Erfindungen', 'Wissenschaftliche_Entdeckungen', 'Theater_und_Film', 'Kochen']

class CreativeActivities(Page):
    timeout_seconds = 1000
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    def vars_for_template(player):
        choices = [1, 2, 3, 4, 5, 6, 7]
        ratings = [player.Bildende_Kunst, player.Musik, player.Tanz, player.Architektur, player.Literatur, player.Humor, player.Erfindungen, player.Wissenschaftliche_Entdeckungen, player.Theater_und_Film, player.Kochen]
        return dict(ratings = ratings, choices = choices)
    form_model = 'player'
    form_fields = ['Bildende_Kunst_2_1', 'Bildende_Kunst_2_2', 'Bildende_Kunst_2_3', 'Bildende_Kunst_2_4', 'Bildende_Kunst_2_5', 'Bildende_Kunst_2_6', 'Bildende_Kunst_2_7', 'Musik_2_1', 'Musik_2_2', 'Musik_2_3', 'Musik_2_4', 'Musik_2_5', 'Musik_2_6', 'Musik_2_7', 'Tanz_2_1', 'Tanz_2_2', 'Tanz_2_3', 'Tanz_2_4', 'Tanz_2_5', 'Tanz_2_6', 'Tanz_2_7', 'Architektur_2_1', 'Architektur_2_2', 'Architektur_2_3', 'Architektur_2_4', 'Architektur_2_5', 'Architektur_2_6', 'Architektur_2_7', 'Literatur_2_1', 'Literatur_2_2', 'Literatur_2_3', 'Literatur_2_4', 'Literatur_2_5', 'Literatur_2_6', 'Literatur_2_7', 'Humor_2_1', 'Humor_2_2', 'Humor_2_3', 'Humor_2_4', 'Humor_2_5', 'Humor_2_6', 'Humor_2_7', 'Erfindungen_2_1', 'Erfindungen_2_2', 'Erfindungen_2_3', 'Erfindungen_2_4', 'Erfindungen_2_5', 'Erfindungen_2_6', 'Erfindungen_2_7', 'Wissenschaftliche_Entdeckungen_2_1', 'Wissenschaftliche_Entdeckungen_2_2', 'Wissenschaftliche_Entdeckungen_2_3', 'Wissenschaftliche_Entdeckungen_2_4', 'Wissenschaftliche_Entdeckungen_2_5', 'Wissenschaftliche_Entdeckungen_2_6', 'Wissenschaftliche_Entdeckungen_2_7', 'Theater_und_Film_2_1', 'Theater_und_Film_2_2', 'Theater_und_Film_2_3', 'Theater_und_Film_2_4', 'Theater_und_Film_2_5', 'Theater_und_Film_2_6', 'Theater_und_Film_2_7', 'Kochen_2_1', 'Kochen_2_2', 'Kochen_2_3', 'Kochen_2_4', 'Kochen_2_5', 'Kochen_2_6', 'Kochen_2_7']

class Personality(Page):
    timeout_seconds = 270
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    form_model = 'player'
    form_fields = ['creative_self1', 'creative_self2', 'creative_self3', 'creative_self4', 'creative_self5', 'creative_self6']

class Identification(Page):
    timeout_seconds = 270
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende' and player.round_number == C.NUM_ROUNDS
    form_model = 'player'
    form_fields = ['circle_overlap']
 
    def js_vars(player: Player):
        return {}
    
class AUT(Page):    
    timeout_seconds = 240
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS and player.player_role == 'Hinweisgebende' 
    form_model = 'player'
    form_fields = ['AUT', 'AUT2']

class DAT(Page):
    timeout_seconds = 270
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende' and player.round_number == C.NUM_ROUNDS
    form_model = 'player'
    form_fields = ['word1', 'word2', 'word3', 'word4', 'word5', 'word6', 'word7', 'word8', 'word9', 'word10']
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.invalid_DAT = True
            return player.invalid_DAT
        else:
            player.invalid_DAT = False
            return player.invalid_DAT

class RAT_Instructions(Page):
    timeout_seconds = 300
    def is_displayed(player):
        return player.player_role == 'Ratender' and player.round_number == C.NUM_ROUNDS

class RAT(Page):
    timeout_seconds = 600
    def is_displayed(player):
        return player.player_role == 'Ratender' and player.round_number == C.NUM_ROUNDS
    form_model = 'player'
    form_fields = ['rat1', 'rat2', 'rat3', 'rat4', 'rat5', 'rat6', 'rat7', 'rat8', 'rat9', 'rat10']
    
class TrustGame(Page):
    timeout_seconds = 60
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS and player.player_role == 'Hinweisgebende' 
    form_model = 'player'
    form_fields = ['trust_game']

class FinalPage(Page):
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    def vars_for_template(player):
        if player.player_role == 'Hinweisgebende' and player.participant.treatment == 1:
            player.payoff = 13

# WAIT PAGES

class GroupWaitPage(WaitPage):
    template_name = 'experiment/GroupWaitPage.html'
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
    title_text = "Vielen Dank für Ihre Abstimmung"
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
   
class ResultsWaitPage(WaitPage):
    title_text = "Ihre Gruppe ist fertig!"
    body_text = "Bitte warten Sie, bis alle Gruppen ihre Hinweispaare und Tipps abgegeben haben."
    wait_for_all_groups = True

page_sequence = [GroupWaitPage, Intro, Intro2, Rules, Instructions, UnderstandPage, Round, Generation_Page, Generation_WaitPage, Discussion, Clue_WaitPage, Clue_Page, VotingWaitPage, Voting_Page, VotingResultWaitPage, VotingResultPage, GuesserWaitPage, Guess_Page1, Guess_Page2, Guess_Page3, PairCheck, Originality_Calculation, DecisionConfidence, ResultsWaitPage, Results, Usefulness, Originality, Overall_Creativity, Score, Score2, Score3, Score4, TrustGame, Identification, TestQuestions, IndividualismQuestions, CreativeActivities, Personality, AUT, DAT, RAT_Instructions, RAT, FinalPage]