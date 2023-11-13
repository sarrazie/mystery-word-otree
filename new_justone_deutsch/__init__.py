from otree.api import *

from settings import PARTICIPANT_FIELDS

doc = """
Ihre App-Beschreibung
"""

class C(BaseConstants):
    NAME_IN_URL = 'New_Mystery_Word_deutsch'
    NUM_ROUNDS = 2
    PLAYERS_PER_GROUP = 4
    MYSTERY_WORDS = ['Treppe', 'Haare']
    LANGUAGE_CODE = 'de'

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    payoff = models.IntegerField(initial=1000)
    
class Player(BasePlayer): 
    def role(player):
        if player.round_number % 4 == 1:
            return {1: 'Ratender', 2: 'Hinweisgeber', 3: 'Hinweisgeber', 4: 'Hinweisgeber'}[player.id_in_group]
        if player.round_number % 4 == 2:
            return {1: 'Hinweisgeber', 2: 'Ratender', 3: 'Hinweisgeber', 4: 'Hinweisgeber'}[player.id_in_group]
        if player.round_number % 4 == 3:
            return {1: 'Hinweisgeber', 2: 'Hinweisgeber', 3: 'Ratender', 4: 'Hinweisgeber'}[player.id_in_group]
        if player.round_number % 4 == 0:
            return {1: 'Hinweisgeber', 2: 'Hinweisgeber', 3: 'Hinweisgeber', 4: 'Ratender'}[player.id_in_group]
        
    guess = models.StringField(label="Ihre Vermutung:", initial='')
    clues = models.StringField(label="Ihr finaler Hinweis:", initial='')
    score = models.IntegerField()
    result = models.StringField()
    incentive = models.IntegerField()
    known = models.StringField(choices=[['Ja', 'Ja'], ['Nein', 'Nein']], label='Kennen Sie das Spiel "Just One"?', widget=widgets.RadioSelect)
    role_question = models.StringField(choices=[['Hinweisgeber', 'Hinweisgeber'], ['Ratender', 'Ratender']], label='In welcher Rolle haben sie sich wohler gefühlt?', widget=widgets.RadioSelect)
    understanding = models.StringField(choices=[['stimme vollkommen zu', 'stimme vollkommen zu'], ['stimme zu', 'stimme zu'], ['neutral', 'neutral'], ['stimme nicht zu', 'stimme nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='"Ich habe die Verfahrensweise und die Regeln schnell verstanden."', widget=widgets.RadioSelectHorizontal)
    comments = models.LongStringField(label="Welche Strategie haben sie als Hinweisgeber verfolgt?", initial='', max_length=500, blank=True)
    comments_2 = models.LongStringField(label="Welche Strategie haben sie als Ratender verfolgt?", initial='', max_length=500, blank=True)
    freda_1 = models.StringField(choices=[['stimme voll zu', 'stimme voll zu'], ['stimme eher zu', 'stimme eher zu'], ['weder noch', 'weder noch'], ['stimme eher nicht zu', 'stimme eher nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='"In meiner Familie werden Werte und Familienrituale über Generationen weitergegeben."', widget=widgets.RadioSelectHorizontal)
    freda_2 = models.StringField(choices=[['stimme voll zu', 'stimme voll zu'], ['stimme eher zu', 'stimme eher zu'], ['weder noch', 'weder noch'], ['stimme eher nicht zu', 'stimme eher nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='"Die Zuneigung und Unterstützung meiner Eltern hängen davon ab, inwiefern ich ihre Erwartungen erfülle."', widget=widgets.RadioSelectHorizontal)
    freda_3 = models.StringField(choices=[['stimme voll zu', 'stimme voll zu'], ['stimme eher zu', 'stimme eher zu'], ['weder noch', 'weder noch'], ['stimme eher nicht zu', 'stimme eher nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='"Ich weiß besser, was gut für mein (künftiges) Kind ist, als mein (künftiges) Kind selbst."', widget=widgets.RadioSelectHorizontal)
    freda_4 = models.StringField(choices=[['stimme voll zu', 'stimme voll zu'], ['stimme eher zu', 'stimme eher zu'], ['weder noch', 'weder noch'], ['stimme eher nicht zu', 'stimme eher nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='"Ich möchte, dass mein (künftiges) Kind wie ich ist, wenn es erwachsen ist."', widget=widgets.RadioSelectHorizontal)
    freda_5 = models.StringField(choices=[['stimme voll zu', 'stimme voll zu'], ['stimme eher zu', 'stimme eher zu'], ['weder noch', 'weder noch'], ['stimme eher nicht zu', 'stimme eher nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='"Es gibt eine gute Übereinstimmung zwischen dem, was mein Job mir bietet, und dem, was ich von einem Job erwarte."', widget=widgets.RadioSelectHorizontal)
    freda_6 = models.StringField(choices=[['stimme voll zu', 'stimme voll zu'], ['stimme eher zu', 'stimme eher zu'], ['weder noch', 'weder noch'], ['stimme eher nicht zu', 'stimme eher nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='"In meinem Job lerne ich häufig dazu, indem ich mich zum Beispiel auf den neuesten Stand bringe oder neue Aufgaben praktisch durchführe (“learning by doing”)."', widget=widgets.RadioSelectHorizontal)
    freda_7 = models.StringField(choices=[['stimme voll zu', 'stimme voll zu'], ['stimme eher zu', 'stimme eher zu'], ['weder noch', 'weder noch'], ['stimme eher nicht zu', 'stimme eher nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='"Meine Eltern gaben mir immer alle Freiheiten."', widget=widgets.RadioSelectHorizontal)
    freda_8 = models.StringField(choices=[['stimme voll zu', 'stimme voll zu'], ['stimme eher zu', 'stimme eher zu'], ['weder noch', 'weder noch'], ['stimme eher nicht zu', 'stimme eher nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='"Ich versuche, meinem (künftigen) Kind so viele Freiheiten zu geben, wie ich von meinen Eltern erhalten habe."', widget=widgets.RadioSelectHorizontal)
    understand_1 = models.StringField(choices=[['false', 'Die Hinweispaare werden den Ratenden gezeigt'], ['true', 'Die Hinweispaare werden entfernt, bevor die Ratenden sie sehen.'], ['false', 'Die Hinweispaare zählen doppelt'],['false', 'Der Gewinn der Gruppen wird verdoppelt']], label='Was passiert, wenn Gruppen identische Hinweispaare abgeben?', widget=widgets.RadioSelect)
    understand_2 = models.StringField(choices=[['false', 'Unbegrenzt viele Versuche'],['false', 'Zwei Versuche'],['false', 'Drei Versuche'],['true', 'Nur einen Versuch']], label='Wie viele Versuche hat der Ratende, um das geheime Wort zu erraten?', widget=widgets.RadioSelect)
    understand_3 = models.StringField(choices=[['false,','Zwei'],['false', 'Drei'],['true', 'Vier'],['false', 'Fünf']], label='Wie viele Spieler bilden zusammen eine Gruppe?', widget=widgets.RadioSelect)
    understand_4 = models.StringField(choices=[['false', 'Die meisten Hinweispaare aller Gruppen generieren'],['true', 'Die meisten geheimen Wörter erraten von allen Gruppen'],['false', 'Die meisten identischen Hinweispaare aller Gruppen geben'],['false','Die wenigsten geheimen Wörter aller Gruppen erraten']], label='Was ist das Ziel deiner Gruppe?', widget=widgets.RadioSelect)
    understand_5 = models.StringField(choices=[['true', '12 Euro für die Teilnahme an allen Runden'],['false', '3 Euro fix plus 9 Euro Bonus für die meisten generierten Ideen'],['false', '3 Euro fix plus 9 Euro Bonus für die meisten erratenen geheimen Wörter'],['false','3 Euro fix plus 9 Euro Bonus für die originellsten Hinweispaare, die zur richtigen Erratung des Wortes führen']], label='Wie viel Geld kannst du maximal in diesem Experiment verdienen?', widget=widgets.RadioSelect)
    understand_6 = models.StringField(choices=[['false', 'Time'], ['false', 'Zeitpunkt'],['false', 'ist Geld'],['false', 'Zeeeit'],['true', 'keiner der oben genannten Hinweise']], label='Beispiel: Welcher der folgenden Hinweise wäre ein gültiger Hinweis in einem Hinweispaar für das geheime Wort "Zeit"?', widget=widgets.RadioSelect)
    strategy = models.StringField(choices=[['stimme vollkommen zu', 'stimme vollkommen zu'], ['stimme zu', 'stimme zu'], ['neutral', 'neutral'], ['stimme nicht zu', 'stimme nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='"Ich habe ständig nur daran gedacht, welche Hinweise meine Mitspieler abgeben."', widget=widgets.RadioSelectHorizontal)
    strategy_2 = models.StringField(choices=[['stimme vollkommen zu', 'stimme vollkommen zu'], ['stimme zu', 'stimme zu'], ['neutral', 'neutral'], ['stimme nicht zu', 'stimme nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='"Erst möglichst viele Ideen aufzuschreiben, hilft mir dabei, später bessere Hinweise zu geben."', widget=widgets.RadioSelectHorizontal)
    strategy_3 = models.StringField(choices=[['stimme vollkommen zu', 'stimme vollkommen zu'], ['stimme zu', 'stimme zu'], ['neutral', 'neutral'], ['stimme nicht zu', 'stimme nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='"Ich habe versucht, möglichst originelle und einzigartige Hinweise zu geben, damit ich keine identischen Hinweise wie meine Mitspieler abgebe."', widget=widgets.RadioSelectHorizontal)
    strategy_4 = models.StringField(choices=[['stimme vollkommen zu', 'stimme vollkommen zu'], ['stimme zu', 'stimme zu'], ['neutral', 'neutral'], ['stimme nicht zu', 'stimme nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='"Ich habe versucht, eindeutige und naheliegende Hinweise zu geben, auch auf die Gefahr hin, dass meine Mitspieler identische Hinweise abgegen."', widget=widgets.RadioSelectHorizontal)
    strategy_5 = models.StringField(choices=[['stimme vollkommen zu', 'stimme vollkommen zu'], ['stimme zu', 'stimme zu'], ['neutral', 'neutral'], ['stimme nicht zu', 'stimme nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='"Der Wettkampf mit den anderen Gruppen hat mich motiviert, möglichst gute Hinweise zu geben und das geheime Wort zu erraten."', widget=widgets.RadioSelectHorizontal)
    Idea1 = models.StringField(label= '', initial='', blank=True)
    Idea2 = models.StringField(label= '', initial='', blank=True)
    Idea3 = models.StringField(label= '', initial='', blank=True)
    Idea4 = models.StringField(label= '', initial='', blank=True)
    Idea5 = models.StringField(label= '', initial='', blank=True)
    Idea6 = models.StringField(label= '', initial='', blank=True)
    Idea7 = models.StringField(label= '', initial='', blank=True)
    Idea8 = models.StringField(label= '', initial='', blank=True)
    Idea9 = models.StringField(label= '', initial='', blank=True)
    Idea10 = models.StringField(label= '', initial='', blank=True)
    Idea11 = models.StringField(label= '', initial='', blank=True)
    Idea12 = models.StringField(label= '', initial='', blank=True)
    word1 = models.StringField(label= '', initial='', blank=True)
    word2 = models.StringField(label= '', initial='', blank=True)
    word3 = models.StringField(label= '', initial='', blank=True)
    word4 = models.StringField(label= '', initial='', blank=True)
    word5 = models.StringField(label= '', initial='', blank=True)
    word6 = models.StringField(label= '', initial='', blank=True)
    word7 = models.StringField(label= '', initial='', blank=True)
    word8 = models.StringField(label= '', initial='', blank=True)
    word9 = models.StringField(label= '', initial='', blank=True)
    word10 = models.StringField(label= '', initial='', blank=True)
    gender = models.IntegerField(choices=[[1, 'Männlich'],[2, 'Weiblich'],[3, 'Diverse'],], label='Geschlecht:')
    age = models.IntegerField(min=18, max=100, label='Alter:')
    identical = models.BooleanField()
    invalid = models.BooleanField()
    missing = models.BooleanField()
    guess_missing = models.BooleanField()
    quantity = models.IntegerField()
    invalid_DAT = models.BooleanField()
    pair1 = models.StringField(initial='')
    pair2 = models.StringField(initial='')
    pair3 = models.StringField(initial='')
    pair4 = models.StringField(initial='')
    pair5 = models.StringField(initial='')
    pair6 = models.StringField(initial='')
    pair1after = models.StringField(initial='')
    pair2after = models.StringField(initial='')
    pair3after = models.StringField(initial='')
    pair4after = models.StringField(initial='')
    pair5after = models.StringField(initial='')
    pair6after = models.StringField(initial='')
    rating_before1 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='empty')
    rating_before2 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='empty')
    rating_before3 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='empty')
    rating_before4 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='empty')
    rating_before5 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='empty')
    rating_before6 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='empty')
    rating_before7 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='empty')
    rating_before8 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='empty')
    rating_before9 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='empty')
    rating_before10 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='empty')
    rating_before11 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='empty')
    rating_before12 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='empty')
    discussion1 = models.StringField(label= '', initial='', blank=True)
    discussion2 = models.StringField(label= '', initial='', blank=True)
    discussion3 = models.StringField(label= '', initial='', blank=True)
    discussion4 = models.StringField(label= '', initial='', blank=True)
    discussion5 = models.StringField(label= '', initial='', blank=True)
    discussion6 = models.StringField(label= '', initial='', blank=True)
    discussion7 = models.StringField(label= '', initial='', blank=True)
    discussion8 = models.StringField(label= '', initial='', blank=True)
    discussion9 = models.StringField(label= '', initial='', blank=True)
    discussion10 = models.StringField(label= '', initial='', blank=True)
    discussion11 = models.StringField(label= '', initial='', blank=True)
    discussion12 = models.StringField(label= '', initial='', blank=True)
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
    replace_word10 = models.StringField(widget = widgets.RadioSelectHorizontal, choices=[['erste', 'erste Wort durch:'],['zweite', 'zweite Wort durch:'],['dritte', 'dritte Wort durch:'],], label='Ersetze das', blank=True, initial='')
    replace_word11 = models.StringField(widget = widgets.RadioSelectHorizontal, choices=[['erste', 'erste Wort durch:'],['zweite', 'zweite Wort durch:'],['dritte', 'dritte Wort durch:'],], label='Ersetze das', blank=True, initial='')
    replace_word12 = models.StringField(widget = widgets.RadioSelectHorizontal, choices=[['erste', 'erste Wort durch:'],['zweite', 'zweite Wort durch:'],['dritte', 'dritte Wort durch:'],], label='Ersetze das', blank=True, initial='')
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
    pair_feedback11 = models.StringField(label= '', initial='', blank=True)
    pair_feedback12 = models.StringField(label= '', initial='', blank=True)
    vote = models.StringField(initial='')
    vote_group = models.StringField(initial='')
    corrected_votes = models.StringField()
    pairsafter = models.StringField(label= '', initial='', blank=True)

def creating_session(subsession: Subsession):
    session = subsession.session
    for player in subsession.get_players():
        participant = player.participant
        participant.vars['treatment'] = session.config['treatment']
        player.incentive = participant.vars['treatment']

# PAGES
class GroupWaitPage(WaitPage):
    template_name = 'justone_deutsch/GroupWaitPage.html'
    group_by_arrival_time = True
    def is_displayed(player):
        return player.round_number == 1
        
class Introduction(Page):
    def is_displayed(player):
        return player.round_number == 1
    
class Intro(Page):
    timeout_seconds = 150
    def is_displayed(player):
        return player.round_number == 1
    
class DAT(Page):
    timeout_seconds = 360
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    form_model = 'player'
    form_fields = ['word1', 'word2', 'word3', 'word4', 'word5', 'word6', 'word7', 'word8', 'word9', 'word10', 'gender', 'age']
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.invalid_DAT = True
            return player.invalid_DAT
        else:
            player.invalid_DAT = False
            return player.invalid_DAT
   
class Instructions(Page):
    timeout_seconds = 120
    def is_displayed(player):
        return player.round_number == 1
  
class Round(Page):
    timeout_seconds = 30
    def vars_for_template(player):
        round_number = player.round_number 
        remaining_rounds = C.NUM_ROUNDS - round_number 
        group = player.group
        # get payoff from last round
        if round_number > 1:
            group.payoff = group.in_round(round_number - 1).payoff
        return dict(round_number = round_number, remaining_rounds = remaining_rounds)

class Clue_Page(Page):
    timeout_seconds = 10000
    def is_displayed(player):
        return player.role() == 'Hinweisgeber'   
    form_model = 'player'
    form_fields = ['Idea1', 'Idea2', 'Idea3', 'Idea4', 'Idea5', 'Idea6', 'Idea7', 'Idea8', 'Idea9', 'Idea10', 'Idea11', 'Idea12']
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        feedback1_group = [p.pair_feedback1 for p in player.get_others_in_group()]
        feedback1_group = list(filter(bool, feedback1_group))
        feedback2_group = [p.pair_feedback2 for p in player.get_others_in_group()]
        feedback2_group = list(filter(bool, feedback2_group))
        feedback3_group = [p.pair_feedback3 for p in player.get_others_in_group()]
        feedback3_group = list(filter(bool, feedback3_group))
        feedback4_group = [p.pair_feedback4 for p in player.get_others_in_group()]
        feedback4_group = list(filter(bool, feedback4_group))
        feedback5_group = [p.pair_feedback5 for p in player.get_others_in_group()]
        feedback5_group = list(filter(bool, feedback5_group))
        feedback6_group = [p.pair_feedback6 for p in player.get_others_in_group()]
        feedback6_group = list(filter(bool, feedback6_group))
        feedback7_group = [p.pair_feedback7 for p in player.get_others_in_group()]
        feedback7_group = list(filter(bool, feedback7_group))
        feedback8_group = [p.pair_feedback8 for p in player.get_others_in_group()]
        feedback8_group = list(filter(bool, feedback8_group))
        feedback9_group = [p.pair_feedback9 for p in player.get_others_in_group()]
        feedback9_group = list(filter(bool, feedback9_group))
        feedback10_group = [p.pair_feedback10 for p in player.get_others_in_group()]
        feedback10_group = list(filter(bool, feedback10_group))
        feedback11_group = [p.pair_feedback11 for p in player.get_others_in_group()]
        feedback11_group = list(filter(bool, feedback11_group))
        feedback12_group = [p.pair_feedback12 for p in player.get_others_in_group()]
        feedback12_group = list(filter(bool, feedback12_group))
        rating_1 = []
        replace_1 = []
        r_word_1 = []
        rating_2 = []
        replace_2 = []
        r_word_2 = []
        rating_3 = []
        replace_3 = []
        r_word_3 = []
        rating_4 = []
        replace_4 = []
        r_word_4 = []
        rating_5 = []
        replace_5 = []
        r_word_5 = []
        rating_6 = []
        replace_6 = []
        r_word_6 = []
        all_feedback_groups = []
        if feedback1_group != ['', '']:
            all_feedback_groups = feedback1_group
        if feedback1_group != ['', ''] and feedback2_group != ['', '']:
            all_feedback_groups = feedback1_group + feedback2_group
        if feedback1_group != ['', ''] and feedback2_group != ['', ''] and feedback3_group != ['', '']:
            all_feedback_groups = feedback1_group + feedback2_group + feedback3_group
        if feedback1_group != ['', ''] and feedback2_group != ['', ''] and feedback3_group != ['', ''] and feedback4_group != ['', '']: 
            all_feedback_groups = feedback1_group + feedback2_group + feedback3_group + feedback4_group
        if feedback1_group != ['', ''] and feedback2_group != ['', ''] and feedback3_group != ['', ''] and feedback4_group != ['', ''] and feedback5_group != ['', '']:
            all_feedback_groups = feedback1_group + feedback2_group + feedback3_group + feedback4_group + feedback5_group
        if feedback1_group != ['', ''] and feedback2_group != ['', ''] and feedback3_group != ['', ''] and feedback4_group != ['', ''] and feedback5_group != ['', ''] and feedback6_group != ['', '']:
            all_feedback_groups = feedback1_group + feedback2_group + feedback3_group + feedback4_group + feedback5_group + feedback6_group
        if feedback1_group != ['', ''] and feedback2_group != ['', ''] and feedback3_group != ['', ''] and feedback4_group != ['', ''] and feedback5_group != ['', ''] and feedback6_group != ['', ''] and feedback7_group != ['', '']:
            all_feedback_groups = feedback1_group + feedback2_group + feedback3_group + feedback4_group + feedback5_group + feedback6_group + feedback7_group
        if feedback1_group != ['', ''] and feedback2_group != ['', ''] and feedback3_group != ['', ''] and feedback4_group != ['', ''] and feedback5_group != ['', ''] and feedback6_group != ['', ''] and feedback7_group != ['', ''] and feedback8_group != ['', '']:
            all_feedback_groups = feedback1_group + feedback2_group + feedback3_group + feedback4_group + feedback5_group + feedback6_group + feedback7_group + feedback8_group
        if feedback1_group != ['', ''] and feedback2_group != ['', ''] and feedback3_group != ['', ''] and feedback4_group != ['', ''] and feedback5_group != ['', ''] and feedback6_group != ['', ''] and feedback7_group != ['', ''] and feedback8_group != ['', ''] and feedback9_group != ['', '']:
            all_feedback_groups = feedback1_group + feedback2_group + feedback3_group + feedback4_group + feedback5_group + feedback6_group + feedback7_group + feedback8_group + feedback9_group
        if feedback1_group != ['', ''] and feedback2_group != ['', ''] and feedback3_group != ['', ''] and feedback4_group != ['', ''] and feedback5_group != ['', ''] and feedback6_group != ['', ''] and feedback7_group != ['', ''] and feedback8_group != ['', ''] and feedback9_group != ['', ''] and feedback10_group != ['', '']:
            all_feedback_groups = feedback1_group + feedback2_group + feedback3_group + feedback4_group + feedback5_group + feedback6_group + feedback7_group + feedback8_group + feedback9_group + feedback10_group
        if feedback1_group != ['', ''] and feedback2_group != ['', ''] and feedback3_group != ['', ''] and feedback4_group != ['', ''] and feedback5_group != ['', ''] and feedback6_group != ['', ''] and feedback7_group != ['', ''] and feedback8_group != ['', ''] and feedback9_group != ['', ''] and feedback10_group != ['', ''] and feedback11_group != ['', '']:
            all_feedback_groups = feedback1_group + feedback2_group + feedback3_group + feedback4_group + feedback5_group + feedback6_group + feedback7_group + feedback8_group + feedback9_group + feedback10_group + feedback11_group
        if feedback1_group != ['', ''] and feedback2_group != ['', ''] and feedback3_group != ['', ''] and feedback4_group != ['', ''] and feedback5_group != ['', ''] and feedback6_group != ['', ''] and feedback7_group != ['', ''] and feedback8_group != ['', ''] and feedback9_group != ['', ''] and feedback10_group != ['', ''] and feedback11_group != ['', ''] and feedback12_group != ['', '']:
            all_feedback_groups = feedback1_group + feedback2_group + feedback3_group + feedback4_group + feedback5_group + feedback6_group + feedback7_group + feedback8_group + feedback9_group + feedback10_group + feedback11_group + feedback12_group
        import ast
        for element in all_feedback_groups:
            element_list = ast.literal_eval(element)
            if element_list[0] == player.pair1:
                rating_1.append(element_list[1])
                replace_1.append(element_list[2])
                r_word_1.append(element_list[3])
            if element_list[0] == player.pair2:
                rating_2.append(element_list[1])
                replace_2.append(element_list[2])
                r_word_2.append(element_list[3])
            if element_list[0] == player.pair3:
                rating_3.append(element_list[1])
                replace_3.append(element_list[2])
                r_word_3.append(element_list[3])
            if element_list[0] == player.pair4:
                rating_4.append(element_list[1])
                replace_4.append(element_list[2])
                r_word_4.append(element_list[3])
            if element_list[0] == player.pair5:
                rating_5.append(element_list[1])
                replace_5.append(element_list[2])
                r_word_5.append(element_list[3])
            if element_list[0] == player.pair6:
                rating_6.append(element_list[1])
                replace_6.append(element_list[2])
                r_word_6.append(element_list[3])
        return dict(mystery_word = mystery_word, Rating_1 = rating_1, Replace_1 = replace_1, R_word_1 = r_word_1, Rating_2 = rating_2, Replace_2 = replace_2, R_word_2 = r_word_2, Rating_3 = rating_3, Replace_3 = replace_3, R_word_3 = r_word_3, Rating_4 = rating_4, Replace_4 = replace_4, R_word_4 = r_word_4, Rating_5 = rating_5, Replace_5 = replace_5, R_word_5 = r_word_5, Rating_6 = rating_6, Replace_6 = replace_6, R_word_6 = r_word_6, Feedback1 = feedback1_group, Feedback2 = feedback2_group, Feedback3 = feedback3_group, Feedback4 = feedback4_group, Feedback5 = feedback5_group, Feedback6 = feedback6_group, Feedback7 = feedback7_group, Feedback8 = feedback8_group, Feedback9 = feedback9_group, Feedback10 = feedback10_group, Feedback11 = feedback11_group, Feedback12 = feedback12_group)
    
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.pair1after = 'empty'
            player.pair2after = 'empty'
            player.pair3after = 'empty'
            player.pair4after = 'empty'
            player.pair5after = 'empty'
            player.pair6after = 'empty'
        else:
            mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
            mystery_word = mystery_word.lower()   
            ideas = [player.Idea1, player.Idea2, player.Idea3, player.Idea4, player.Idea5, player.Idea6, player.Idea7, player.Idea8, player.Idea9, player.Idea10, player.Idea11, player.Idea12]
            import re            
            import translators as ts            
            def has_numbers(s):
                return bool(re.search(r'\d',s))
            with open('C:/Users/sarrazie/Desktop/otree/testproject/justone_deutsch/wordlist-german.txt', 'r') as file:
                text = file.read()
                wordlist= text.split()
            if len(ideas) > 0:
                for i in range(len(ideas)): 
                    special_char_map = {ord('ä'):'ae', ord('ü'):'ue', ord('ö'):'oe', ord('ß'):'ss'}
                    ideas[i] = ideas[i].translate(special_char_map) 
                    ideas[i] = ideas[i].lower()
                    if ' ' in ideas[i]:
                        more = ideas[i].split() 
                        if len(more)>1: 
                            ideas[i] = 'false'
                    if ideas[i] in mystery_word or mystery_word in ideas[i]:
                        ideas[i] = 'false'
                    if ideas[i] not in wordlist:
                        ideas[i] = 'false' 
                    if re.search("[^a-zA-Z0-9s]", ideas[i]):
                        ideas[i] = 'false'          
                    if has_numbers(ideas[i]) == False:
                        idea_trans = ts.translate_text(query_text=ideas[i], translator='google', from_language='auto', to_language='de')
                        idea_trans = idea_trans.lower()
                        if mystery_word in idea_trans or idea_trans in mystery_word:  
                            ideas[i] = 'false'
                
            if ((ideas[0] != '' and ideas[0] != 'false') and (ideas[1] != '' and ideas[1] != 'false')):
                player.pair1after = ideas[0] + ' + ' + ideas[1]
            else:
                player.pair1after = 'empty'
            if ((ideas[2] != '' and ideas[2] != 'false') and (ideas[3] != '' and ideas[3] != 'false')):
                player.pair2after = ideas[2] + ' + ' + ideas[3]
            else:
                player.pair2after = 'empty'
            if ((ideas[4] != '' and ideas[4] != 'false') and (ideas[5] != '' and ideas[5] != 'false')):
                player.pair3after = ideas[4] + ' + ' + ideas[5]
            else:
                player.pair3after = 'empty'
            if ((ideas[6] != '' and ideas[6] != 'false') and (ideas[7] != '' and ideas[7] != 'false')):
                player.pair4after = ideas[6] + ' + ' + ideas[7]
            else:
                player.pair4after = 'empty'
            if ((ideas[8] != '' and ideas[8] != 'false') and (ideas[9] != '' and ideas[9] != 'false')):
                player.pair5after = ideas[8] + ' + ' + ideas[9]
            else:
                player.pair5after = 'empty'
            if ((ideas[10] != '' and ideas[10] != 'false') and (ideas[11] != '' and ideas[11] != 'false')):
                player.pair6after = ideas[10] + ' + ' + ideas[11]
            else:
                player.pair6after = 'empty'
            
def wordlength(player, value):
    value = value.lower()
    if len(value) > 18:
        return True

def Idea1_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Deine Idee darf nicht länger als 18 Zeichen sein!'

def Idea2_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Deine Idee darf nicht länger als 18 Zeichen sein!'

def Idea3_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Deine Idee darf nicht länger als 18 Zeichen sein!'

def Idea4_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Deine Idee darf nicht länger als 18 Zeichen sein!'

def Idea5_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Deine Idee darf nicht länger als 18 Zeichen sein!'

def Idea6_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Deine Idee darf nicht länger als 18 Zeichen sein!'

def Idea7_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Deine Idee darf nicht länger als 18 Zeichen sein!'

def Idea8_error_message(player, value): 
    if wordlength(player, value) == True:
        return 'Deine Idee darf nicht länger als 18 Zeichen sein!'

def Idea9_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Deine Idee darf nicht länger als 18 Zeichen sein!'

def Idea10_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Deine Idee darf nicht länger als 18 Zeichen sein!'
    
def Idea11_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Deine Idee darf nicht länger als 18 Zeichen sein!'

def Idea12_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Deine Idee darf nicht länger als 18 Zeichen sein!'

class CluegiverWaitPage(WaitPage):
    title_text = "Vielen Dank für deinen Hinweis!"
    body_text = "Bitte warte, bis alle ihre Hinweise and Vermutungen abgegeben haben."
    def is_displayed(player):
        return player.role() == 'Hinweisgeber'

class GuesserWaitPage(WaitPage):
    title_text = "Du kannst deinen Tipp gleich abgeben!"
    body_text = "Bitte warte, bis die anderen Spieler ihre Hinweise für dich abgegeben haben."
    def is_displayed(player): 
        return player.role() == 'Ratender'
    
class ResultsWaitPage(WaitPage):
    title_text = "Deine Gruppe ist fertig!"
    body_text = "Bitte warte, bis alle Gruppen ihre Hinweise und Tipps abgegeben haben."
    wait_for_all_groups = True

class VotingResultPage(Page):
    timeout_seconds = 300
    def is_displayed(player):
        return player.role() == 'Hinweisgeber'
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        mystery_word = mystery_word.lower()
        votes = [player.vote] + [p.vote for p in player.get_others_in_group()]
        while '' in votes:
            votes.remove('')
        votes = [vote.replace(' + ', ' ') for vote in votes]   
        if len(votes) > 0:
            for i in range(len(votes)):
                words = votes[i].split()
                if len(words) >= 3:  
                    votes[i] = 'false false'
        words = [word for vote in votes for word in vote.split()]
        import translators as ts 
        import re            
        def has_numbers(s):
            return bool(re.search(r'\d',s))
        with open('C:/Users/sarrazie/Desktop/otree/testproject/justone_deutsch/wordlist-german.txt', 'r') as file:
            text = file.read()
            wordlist= text.split()
        if len(words) > 0:
            for i in range(len(words)): 
                special_char_map = {ord('ä'):'ae', ord('ü'):'ue', ord('ö'):'oe', ord('ß'):'ss'}
                words[i] = words[i].translate(special_char_map) 
                words[i] = words[i].lower()
                if re.search("[^a-zA-Z0-9s]", words[i]):
                    words[i] = 'false' 
                if has_numbers(words[i]) == False:
                    word_trans = ts.translate_text(query_text=words[i], translator='google', from_language='auto', to_language='de')
                    word_trans = word_trans.lower()
                    if mystery_word in word_trans or word_trans in mystery_word:  
                        words[i] = 'false'
                if words[i] in mystery_word or mystery_word in words[i]:
                    words[i] = 'false'
                if words[i] not in wordlist:
                    words[i] = 'false'
        corrected_votes = []
        for i in range(0, len(words), 2):
            corrected_votes.append(' + '.join(words[i:i+2]))
        player.corrected_votes = str(corrected_votes)
        import random
        valid_votes = [v for v in corrected_votes if 'false' not in v]
        duplicates = [v for v in set(valid_votes) if valid_votes.count(v) >= 2]
        number_duplicates = len(duplicates)
        number_valid_votes = len(valid_votes)
        if len(duplicates) > 0:
            vote_group = random.choice(duplicates)
        else:
            if len(valid_votes) > 0:
                vote_group = random.choice(valid_votes) 
            else:
                vote_group = 'Kein gültiges Hinweispaar'
        player.vote_group = vote_group
        return dict(mystery_word = mystery_word, vote_group = vote_group, duplicates = number_duplicates, valid_votes = number_valid_votes)

class Guess_Page(Page):
    timeout_seconds = 3000
    def is_displayed(player):
        return player.role() == 'Ratender'
    def vars_for_template(player):  
        vote_group = [p.vote_group for p in player.get_others_in_group()]
        vote_group = vote_group[0]
        player.vote_group = vote_group
        vote_other_groups = []
        for other_group in player.subsession.get_groups():
            if other_group != player.group:
                for other_player in other_group.get_players():
                    vote_other_groups.append(other_player.vote_group)
        for vote in vote_other_groups:  
            while (vote_other_groups.count(vote) > 1):
                vote_other_groups.remove(vote)
        while '' in vote_other_groups:
            vote_other_groups.remove('')
        def find_identical_words(str1, str2):
            str1 = str1.replace('+', '')
            str2 = str2.replace('+','')
            words1 = set(str1.split())
            words2 = set(str2.split())
            identical_words = words1.intersection(words2)
            return identical_words
        if len(vote_other_groups) > 0:
            vote_other_groups1 = vote_other_groups[0] 
            identical_words = find_identical_words(vote_group, vote_other_groups1)
            if identical_words:
                vote_group = 'Identisches Hinweispaar'            
        if len(vote_other_groups) > 1:
            vote_other_groups2 = vote_other_groups[1]
            identical_words = find_identical_words(vote_group, vote_other_groups2)
            if identical_words:
                vote_group = 'Identisches Hinweispaar'
        if len(vote_other_groups) > 2:
            vote_other_groups3 = vote_other_groups[2]
            identical_words = find_identical_words(vote_group, vote_other_groups3)
            if identical_words:
                vote_group = 'Identisches Hinweispaar'
        if len(vote_other_groups) > 3:
            vote_other_groups4 = vote_other_groups[3]
            identical_words = find_identical_words(vote_group, vote_other_groups4)
            if identical_words:
                vote_group = 'Identisches Hinweispaar'
        if len(vote_other_groups) > 4:
            vote_other_groups5 = vote_other_groups[4]
            identical_words = find_identical_words(vote_group, vote_other_groups5)
            if identical_words:
                vote_group = 'Identisches Hinweispaar'
        player.vote_group = vote_group
        return dict(vote_group = vote_group, vote_other_groups = vote_other_groups)  
    form_model = 'player'
    form_fields = ['guess'] 
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.guess = 'Kein Tipp gegeben'
        else:
            player.guess = player.guess.lower()
            return player.guess
        
class Results(Page):
    timeout_seconds = 1000
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        mystery_word = mystery_word.lower()
        if player.role() == 'Hinweisgeber':
            vote_group = [p.vote_group for p in player.get_others_in_group()]
            while '' in vote_group:
                vote_group.remove('')
            invalid = '' 
            identical = ''               
            player.identical = False
            player.invalid = False
            if 'Identisches Hinweispaar' in vote_group:
                player.identical = True
                identical = 'Achtung! Euer Hinweispaar war identisch mit dem Hinweispaar einer anderen Gruppe.'
                vote_group = 'Identisches Hinweispaar'
            else:    
                vote_group = vote_group[0]
                if vote_group == 'Kein gültiges Hinweispaar':
                    player.invalid = True
                    invalid = 'Achtung! Euer Hinweispaar war ungültig.'
            guess = [p.guess for p in player.get_others_in_group()]
            while '' in guess:
                guess.remove('')
            guess = guess[0]
            player.guess_missing = False
            player.missing = False
            guess_missing = ''
            missing = ''
            pairs = [player.pair1after] + [player.pair2after] + [player.pair3after] + [player.pair4after] + [player.pair5after] + [player.pair6after]
            for i in range(len(pairs)):
                if pairs[i] == 'empty':
                    pairs[i] = ''
            while '' in pairs:
                pairs.remove('')
            player.quantity = len(pairs)
            if player.quantity == 0:
                player.missing = True
                missing = 'Achtung! Du hast kein Hinweispaar abgegeben.'
        if player.role() == 'Ratender':
            vote_group = player.vote_group
            player.identical = False
            player.invalid = False
            player.quantity = 0
            player.guess_missing = False
            player.missing = False
            identical = ''
            invalid = ''
            missing = ''
            guess_missing = ''
            guess = player.guess
            if guess == 'Kein Tipp gegeben':
                player.guess_missing = True
                guess_missing = 'Achtung! Du hast keinen Tipp abgegeben.'
        if mystery_word == guess:
            player.result = 'richtig'
            player.payoff = 1
        else:
            player.result = 'falsch' 
            player.payoff = 0 
        player.score =  int(player.participant.payoff)
        player.group.payoff =  player.score 
        if player.participant.treatment == 1:
            player.group.payoff = 1000
        return dict(mystery_word = mystery_word, vote_group = vote_group, guess = guess, result = player.result, identical = identical, invalid = invalid, missing = missing, guess_missing = guess_missing, number_ideas = player.quantity)

def score(group: Group):
    subsession = group.subsession
    groups = subsession.get_groups()
    overall_score = []
    for group in groups:
            overall_score.append(group.payoff)
            if group.payoff == 1000:
                overall_score.remove(1000)
            sorted_overall_score = sorted(overall_score, reverse = True) 
    return sorted_overall_score
      
class Score(Page):
    timeout_seconds = 30
    def is_displayed(player):
        return player.participant.treatment == 3
    def vars_for_template(player):
        player.score =  int(player.participant.payoff)
        overall_score = score(player.group)
        rank = 0
        if player.score == overall_score[0]:
            rank = 1
        if player.score == overall_score[1] and player.score != overall_score[0]:
            rank = 2
        if len(overall_score) > 2:
            if player.score == overall_score[2] and player.score != overall_score[0] and player.score != overall_score[1]:
                rank = 3
        if len(overall_score) > 3:
            if player.score == overall_score[3] and player.score != overall_score[0] and player.score != overall_score[1] and player.score != overall_score[2]:
                rank = 4
        if len(overall_score) > 4:
            if player.score == overall_score[4] and player.score != overall_score[0] and player.score != overall_score[1] and player.score != overall_score[2] and player.score != overall_score[3]:
                rank = 5
        number_groups = len(overall_score)
        return dict(overall_score = overall_score, score = player.score, rank = rank, number_groups = number_groups)

class TestQuestions(Page):
    template_name = 'justone_deutsch/TestQuestions.html'
    timeout_seconds = 180
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    form_model = 'player'
    form_fields = ['known', 'understanding', 'role_question', 'comments', 'comments_2', 'strategy', 'strategy_2', 'strategy_3', 'strategy_4', 'strategy_5']

class FredaQuestions(Page):
    template_name = 'justone_deutsch/FredaQuestions.html'
    timeout_seconds = 180
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    form_model = 'player'
    form_fields = ['freda_1', 'freda_2', 'freda_3', 'freda_4', 'freda_5', 'freda_6', 'freda_7', 'freda_8']

class UnderstandPage(Page):
    template_name = 'justone_deutsch/UnderstandPage.html'
    timeout_seconds = 180
    def is_displayed(player):
        return player.round_number == 1
    form_model = 'player'
    form_fields = ['understand_1', 'understand_2', 'understand_3', 'understand_4', 'understand_5', 'understand_6']
    def error_message(player, values):
        if values['understand_1'] == 'false':
            return 'Falsche Antwort bei Frage 1! Versuche es noch einmal.'
        if values['understand_2'] == 'false':
            return 'Falsche Antwort bei Frage 2! Versuche es noch einmal.'
        if values['understand_3'] == 'false':
            return 'Falsche Antwort bei Frage 3! Versuche es noch einmal.'
        if values['understand_4'] == 'false':
            return 'Falsche Antwort bei Frage 4! Versuche es noch einmal.'
        if values['understand_5'] == 'false':
            return 'Falsche Antwort bei Frage 5! Versuche es noch einmal.'
        if values['understand_6'] == 'false':
            return 'Falsche Antwort bei Frage 6! Versuche es noch einmal.'

class Generation_Page(Page):
    timeout_seconds = 180
    def is_displayed(player):
        return player.role() == 'Hinweisgeber'   
    form_model = 'player'
    form_fields = ['Idea1', 'Idea2', 'Idea3', 'Idea4', 'Idea5', 'Idea6', 'Idea7', 'Idea8', 'Idea9', 'Idea10', 'Idea11', 'Idea12']
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        return dict(mystery_word = mystery_word)
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.pair1 = 'empty'
            player.pair2 = 'empty'
            player.pair3 = 'empty'
            player.pair4 = 'empty'
            player.pair5 = 'empty'
            player.pair6 = 'empty'
        else:
            mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
            mystery_word = mystery_word.lower()   
            ideas = [player.Idea1, player.Idea2, player.Idea3, player.Idea4, player.Idea5, player.Idea6, player.Idea7, player.Idea8, player.Idea9, player.Idea10, player.Idea11, player.Idea12]
            import re            
            import translators as ts            
            def has_numbers(s):
                return bool(re.search(r'\d',s))
            with open('C:/Users/sarrazie/Desktop/otree/testproject/justone_deutsch/wordlist-german.txt', 'r') as file:
                text = file.read()
                wordlist= text.split()
            if len(ideas) > 0:
                for i in range(len(ideas)): 
                    special_char_map = {ord('ä'):'ae', ord('ü'):'ue', ord('ö'):'oe', ord('ß'):'ss'}
                    ideas[i] = ideas[i].translate(special_char_map) 
                    ideas[i] = ideas[i].lower()
                    if ' ' in ideas[i]:
                        more = ideas[i].split() 
                        if len(more)>1: 
                            ideas[i] = 'false'
                    if ideas[i] in mystery_word or mystery_word in ideas[i]:
                        ideas[i] = 'false'
                    if ideas[i] not in wordlist:
                        ideas[i] = 'false' 
                    if re.search("[^a-zA-Z0-9s]", ideas[i]):
                        ideas[i] = 'false'          
                    if has_numbers(ideas[i]) == False:
                        idea_trans = ts.translate_text(query_text=ideas[i], translator='google', from_language='auto', to_language='de')
                        idea_trans = idea_trans.lower()
                        if mystery_word in idea_trans or idea_trans in mystery_word:  
                            ideas[i] = 'false'
                
            if ((ideas[0] != '' and ideas[0] != 'false') and (ideas[1] != '' and ideas[1] != 'false')):
                player.pair1 = ideas[0] + ' + ' + ideas[1]
            else:
                player.pair1 = 'empty'
            if ((ideas[2] != '' and ideas[2] != 'false') and (ideas[3] != '' and ideas[3] != 'false')):
                player.pair2 = ideas[2] + ' + ' + ideas[3]
            else:
                player.pair2 = 'empty'
            if ((ideas[4] != '' and ideas[4] != 'false') and (ideas[5] != '' and ideas[5] != 'false')):
                player.pair3 = ideas[4] + ' + ' + ideas[5]
            else:
                player.pair3 = 'empty'
            if ((ideas[6] != '' and ideas[6] != 'false') and (ideas[7] != '' and ideas[7] != 'false')):
                player.pair4 = ideas[6] + ' + ' + ideas[7]
            else:
                player.pair4 = 'empty'
            if ((ideas[8] != '' and ideas[8] != 'false') and (ideas[9] != '' and ideas[9] != 'false')):
                player.pair5 = ideas[8] + ' + ' + ideas[9]
            else:
                player.pair5 = 'empty'
            if ((ideas[10] != '' and ideas[10] != 'false') and (ideas[11] != '' and ideas[11] != 'false')):
                player.pair6 = ideas[10] + ' + ' + ideas[11]
            else:
                player.pair6 = 'empty'
            
def wordlength(player, value):
        value = value.lower()
        if len(value) > 18:
            return True

def Idea1_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Dein Hinweis darf nicht länger als 18 Zeichen sein!'

def Idea2_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Dein Hinweis darf nicht länger als 18 Zeichen sein!'

def Idea3_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Dein Hinweis darf nicht länger als 18 Zeichen sein!'

def Idea4_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Dein Hinweis darf nicht länger als 18 Zeichen sein!'

def Idea5_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Dein Hinweis darf nicht länger als 18 Zeichen sein!'

def Idea6_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Dein Hinweis darf nicht länger als 18 Zeichen sein!'

def Idea7_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Dein Hinweis darf nicht länger als 18 Zeichen sein!'

def Idea8_error_message(player, value): 
    if wordlength(player, value) == True:
        return 'Dein Hinweis darf nicht länger als 18 Zeichen sein!'

def Idea9_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Dein Hinweis darf nicht länger als 18 Zeichen sein!'

def Idea10_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Dein Hinweis darf nicht länger als 18 Zeichen sein!'
    
def Idea11_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Dein Hinweis darf nicht länger als 18 Zeichen sein!'

def Idea12_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Dein Hinweis darf nicht länger als 18 Zeichen sein!'

class Generation_WaitPage(WaitPage):
    title_text = "Vielen Dank für deine Hinweispaare!"
    body_text = "Bitte warte, bis alle ihre Hinweispaare abgegeben haben."
    wait_for_all_players = True
    def is_displayed(player):
        return player.role() == 'Hinweisgeber'

class Discussion(Page):
    timeout_seconds = 240
    def is_displayed(player):
        return player.role() == 'Hinweisgeber'
    form_model = 'player'   
    form_fields = ['rating_before1', 'rating_before2', 'rating_before3', 'rating_before4', 'rating_before5', 'rating_before6', 'rating_before7', 'rating_before8', 'rating_before9', 'rating_before10', 'rating_before11', 'rating_before12', 'replace_word1', 'replace_word2', 'replace_word3', 'replace_word4', 'replace_word5', 'replace_word6', 'replace_word7', 'replace_word8', 'replace_word9', 'replace_word10', 'replace_word11', 'replace_word12', 'discussion1','discussion2', 'discussion3', 'discussion4', 'discussion5', 'discussion6', 'discussion7', 'discussion8', 'discussion9', 'discussion10', 'discussion11', 'discussion12']
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        mystery_word = mystery_word.lower()
        pairs = [player.pair1 for player in player.get_others_in_group()] + [player.pair2 for player in player.get_others_in_group()] + [player.pair3 for player in player.get_others_in_group()] + [player.pair4 for player in player.get_others_in_group()] + [player.pair5 for player in player.get_others_in_group()] + [player.pair6 for player in player.get_others_in_group()]
        while 'empty' in pairs:
            pairs.remove('empty')
        while '' in pairs:
            pairs.remove('')
        delimiter = ', '
        player.other_pairs = delimiter.join(pairs)
        number_pairs = len(pairs)
        Pair1 = ''
        Pair2 = ''
        Pair3 = ''
        Pair4 = ''
        Pair5 = ''
        Pair6 = ''
        Pair7 = ''
        Pair8 = ''
        Pair9 = ''
        Pair10 = ''
        Pair11 = ''
        Pair12 = ''
        if number_pairs > 0:
            Pair1 = pairs[0]
        if number_pairs > 1:
            Pair2 = pairs[1]
        if number_pairs > 2:
            Pair3 = pairs[2]
        if number_pairs > 3:
            Pair4 = pairs[3]
        if number_pairs > 4:
            Pair5 = pairs[4]
        if number_pairs > 5:
            Pair6 = pairs[5]
        if number_pairs > 6:
            Pair7 = pairs[6]
        if number_pairs > 7:
            Pair8 = pairs[7]
        if number_pairs > 8:
            Pair9 = pairs[8]
        if number_pairs > 9:
            Pair10 = pairs[9]
        if number_pairs > 10:
            Pair11 = pairs[10]
        if number_pairs > 11:
            Pair12 = pairs[11]
        return dict(mystery_word = mystery_word, number_pairs = number_pairs, Pair1 = Pair1, Pair2 = Pair2, Pair3 = Pair3, Pair4 = Pair4, Pair5 = Pair5, Pair6 = Pair6, Pair7 = Pair7, Pair8 = Pair8, Pair9 = Pair9, Pair10 = Pair10, Pair11 = Pair11, Pair12 = Pair12)   

    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.discussion1 = 'empty'
            player.discussion2 = 'empty'
            player.discussion3 = 'empty'
            player.discussion4 = 'empty'
            player.discussion5 = 'empty'
            player.discussion6 = 'empty'
            player.discussion7 = 'empty'
            player.discussion8 = 'empty'
            player.discussion9 = 'empty'
            player.discussion10 = 'empty'
            player.discussion11 = 'empty'
            player.discussion12 = 'empty'
        else:
            pairs = [player.pair1 for player in player.get_others_in_group()] + [player.pair2 for player in player.get_others_in_group()] + [player.pair3 for player in player.get_others_in_group()] + [player.pair4 for player in player.get_others_in_group()] + [player.pair5 for player in player.get_others_in_group()] + [player.pair6 for player in player.get_others_in_group()] 
            while 'empty' in pairs:
                pairs.remove('empty')
            while '' in pairs:
                pairs.remove('')
            if len(pairs) > 0:
                feedback_1 = [player.other_pairs.split(',')[0]] + [player.rating_before1] + [player.replace_word1] + [player.discussion1]
                feedback_1 = str(feedback_1)
                player.pair_feedback1 = feedback_1
            if len(pairs) > 1:
                feedback_2 = [player.other_pairs.split(', ')[1]] + [player.rating_before2] + [player.replace_word2] + [player.discussion2]
                feedback_2 = str(feedback_2)
                player.pair_feedback2 = feedback_2
            if len(pairs) > 2:
                feedback_3 = [player.other_pairs.split(', ')[2]] + [player.rating_before3] + [player.replace_word3] + [player.discussion3]
                feedback_3 = str(feedback_3)
                player.pair_feedback3 = feedback_3
            if len(pairs) > 3:
                feedback_4 = [player.other_pairs.split(', ')[3]] + [player.rating_before4] + [player.replace_word4] + [player.discussion4]
                feedback_4 = str(feedback_4)
                player.pair_feedback4 = feedback_4
            if len(pairs) > 4:
                feedback_5 = [player.other_pairs.split(', ')[4]] + [player.rating_before5] + [player.replace_word5] + [player.discussion5]
                feedback_5 = str(feedback_5)
                player.pair_feedback5 = feedback_5
            if len(pairs) > 5:
                feedback_6 = [player.other_pairs.split(', ')[5]] + [player.rating_before6] + [player.replace_word6] + [player.discussion6]
                feedback_6 = str(feedback_6)
                player.pair_feedback6 = feedback_6
            if len(pairs) > 6:
                feedback_7 = [player.other_pairs.split(', ')[6]] + [player.rating_before7] + [player.replace_word7] + [player.discussion7]
                feedback_7 = str(feedback_7)
                player.pair_feedback7 = feedback_7
            if len(pairs) > 7:
                feedback_8 = [player.other_pairs.split(', ')[7]] + [player.rating_before8] + [player.replace_word8] + [player.discussion8]
                feedback_8 = str(feedback_8)
                player.pair_feedback8 = feedback_8
            if len(pairs) > 8:
                feedback_9 = [player.other_pairs.split(', ')[8]] + [player.rating_before9] + [player.replace_word9] + [player.discussion9]
                feedback_9 = str(feedback_9)
                player.pair_feedback9 = feedback_9
            if len(pairs) > 9:
                feedback_10 = [player.other_pairs.split(', ')[9]] + [player.rating_before10] + [player.replace_word10] + [player.discussion10]
                feedback_10 = str(feedback_10)
                player.pair_feedback10 = feedback_10
            if len(pairs) > 10:
                feedback_11 = [player.other_pairs.split(', ')[10]] + [player.rating_before11] + [player.replace_word11] + [player.discussion11]
                feedback_11 = str(feedback_11)
                player.pair_feedback11 = feedback_11
            if len(pairs) > 11:
                feedback_12 = [player.other_pairs.split(', ')[11]] + [player.rating_before12] + [player.replace_word12] + [player.discussion12]
                feedback_12 = str(feedback_12)
                player.pair_feedback12 = feedback_12

def wordlength(player, value):
        value = value.lower()
        if len(value) > 18:
            return True

def discussion1_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Dein Hinweis darf nicht länger als 18 Zeichen sein!'

def discussion2_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Dein Hinweis darf nicht länger als 18 Zeichen sein!'

def discussion3_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Dein Hinweis darf nicht länger als 18 Zeichen sein!'
    
def discussion4_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Dein Hinweis darf nicht länger als 18 Zeichen sein!'

def discussion5_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Dein Hinweis darf nicht länger als 18 Zeichen sein!'

def discussion6_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Dein Hinweis darf nicht länger als 18 Zeichen sein!'

def discussion7_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Dein Hinweis darf nicht länger als 18 Zeichen sein!'

def discussion8_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Dein Hinweis darf nicht länger als 18 Zeichen sein!'

def discussion9_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Dein Hinweis darf nicht länger als 18 Zeichen sein!'

def discussion10_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Dein Hinweis darf nicht länger als 18 Zeichen sein!'

def discussion11_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Dein Hinweis darf nicht länger als 18 Zeichen sein!'

def discussion12_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Dein Hinweis darf nicht länger als 18 Zeichen sein!'

class Voting_Page(Page):
    timeout_seconds = 120
    def is_displayed(player):
        return player.role() == 'Hinweisgeber'
    form_model = 'player'
    form_fields = ['vote']
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        mystery_word = mystery_word.lower()
        pairs = [player.pair1after] + [player.pair1after for player in player.get_others_in_group()] + [player.pair2after] + [player.pair2after for player in player.get_others_in_group()] + [player.pair3after] + [player.pair3after for player in player.get_others_in_group()] + [player.pair4after] + [player.pair4after for player in player.get_others_in_group()] + [player.pair5after] + [player.pair5after for player in player.get_others_in_group()] + [player.pair6after] + [player.pair6after for player in player.get_others_in_group()]
        while 'empty' in pairs:
            pairs.remove('empty')
        while '' in pairs:
            pairs.remove('')
        delimiter = ', '
        player.pairsafter = delimiter.join(pairs)
        number_pairs = len(pairs)
        Pair1 = ''
        Pair2 = ''
        Pair3 = ''
        Pair4 = ''
        Pair5 = ''
        Pair6 = ''
        Pair7 = ''
        Pair8 = ''
        Pair9 = ''
        Pair10 = ''
        Pair11 = ''
        Pair12 = ''
        Pair13 = ''
        Pair14 = ''
        Pair15 = ''
        Pair16 = ''
        Pair17 = ''
        Pair18 = ''
        if number_pairs > 0:
            Pair1 = pairs[0]
        if number_pairs > 1:
            Pair2 = pairs[1]
        if number_pairs > 2:
            Pair3 = pairs[2]
        if number_pairs > 3:
            Pair4 = pairs[3]
        if number_pairs > 4:
            Pair5 = pairs[4]
        if number_pairs > 5:
            Pair6 = pairs[5]
        if number_pairs > 6:
            Pair7 = pairs[6]
        if number_pairs > 7:
            Pair8 = pairs[7]
        if number_pairs > 8:
            Pair9 = pairs[8]
        if number_pairs > 9:
            Pair10 = pairs[9]
        if number_pairs > 10:
            Pair11 = pairs[10]
        if number_pairs > 11:
            Pair12 = pairs[11]
        if number_pairs > 12:
            Pair13 = pairs[12]
        if number_pairs > 13:
            Pair14 = pairs[13]
        if number_pairs > 14:
            Pair15 = pairs[14]
        if number_pairs > 15:
            Pair16 = pairs[15]
        if number_pairs > 16:
            Pair17 = pairs[16]
        if number_pairs > 17:
            Pair18 = pairs[17]
        return dict(mystery_word = mystery_word, number_pairs = number_pairs, Pair1 = Pair1, Pair2 = Pair2, Pair3 = Pair3, Pair4 = Pair4, Pair5 = Pair5, Pair6 = Pair6, Pair7 = Pair7, Pair8 = Pair8, Pair9 = Pair9, Pair10 = Pair10, Pair11 = Pair11, Pair12 = Pair12, Pair13 = Pair13, Pair14 = Pair14, Pair15 = Pair15, Pair16 = Pair16, Pair17 = Pair17, Pair18 = Pair18, pairs = pairs)

class VotingResultWaitPage(WaitPage):
    title_text = "Vielen Dank für deine Abstimmung!"
    body_text = "Bitte warte, bis alle ihre Stimmen abgegeben haben."
    wait_for_all_players = True
    def is_displayed(player):
        return player.role() == 'Hinweisgeber'
    
class CluegiverWaitPage(WaitPage):
    title_text = "Vielen Dank für euer Hinweispaar!"
    body_text = "Euer Hinweispaar wird nun dem Ratenden gezeigt."
    def is_displayed(player):
        return player.role() == 'Hinweisgeber'
    wait_for_all_groups = True

class Clue_WaitPage(WaitPage):
    title_text = "Vielen Dank für dein Feedback!"
    body_text = "Bitte warte, bis all deine Gruppenmitglieder ihr Feedback abgegeben haben."
    wait_for_all_players = True
    def is_displayed(player):
        return player.role() == 'Hinweisgeber'

class VotingWaitPage(WaitPage):
    title_text = "Vielen Dank für deine Hinweispaare"
    body_text = "Bitte warte, bis alle ihre Hinweispaare abgegeben haben."
    wait_for_all_players = True
    def is_displayed(player):
        return player.role() == 'Hinweisgeber'

class GuesserWaitPage(WaitPage):
    title_text = "Du kannst deinen Tipp gleich abgeben!"
    body_text = "Bitte warte, bis die anderen Spieler ihre Hinweise für dich abgegeben haben."
    def is_displayed(player): 
        return player.role() == 'Ratender'
    wait_for_all_groups = True
    
class ResultsWaitPage(WaitPage):
    title_text = "Deine Gruppe ist fertig!"
    body_text = "Bitte warte, bis alle Gruppen ihre Hinweispaare und Tipps abgegeben haben."
    wait_for_all_groups = True

class FinalPage(Page):
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

page_sequence = [GroupWaitPage, Intro, Instructions, UnderstandPage, Round, Generation_Page, Generation_WaitPage, Discussion, Clue_WaitPage, Clue_Page, VotingWaitPage, Voting_Page, VotingResultWaitPage, VotingResultPage, GuesserWaitPage, CluegiverWaitPage, Guess_Page, ResultsWaitPage, Results, Score, TestQuestions, FredaQuestions, DAT, FinalPage]
# %%
