from otree.api import *

from settings import PARTICIPANT_FIELDS

doc = """
Ihre App-Beschreibung
"""

class C(BaseConstants):
    NAME_IN_URL = 'Mystery_Word_deutsch'
    NUM_ROUNDS = 8
    PLAYERS_PER_GROUP = 4
    MYSTERY_WORDS = ['Raum','Taube', 'Golf', 'Elektrizitaet', 'Leiter', 'Schraube', 'Ende', 'Sombrero']
    LANGUAGE_CODE = 'de'
    STEM_WORDS_1 = ['raum', 'raeum'] 
    STEM_WORDS_2 = ['taub', 'taeub']
    STEM_WORDS_3 = ['golf']
    STEM_WORDS_4 = ['elektr']  
    STEM_WORDS_5 = ['leit'] 
    STEM_WORDS_6 = ['schraub']
    STEM_WORDS_7 = ['end']
    STEM_WORDS_8 = ['sombrero']
    STEM_WORDS = [STEM_WORDS_1, STEM_WORDS_2, STEM_WORDS_3, STEM_WORDS_4, STEM_WORDS_5, STEM_WORDS_6, STEM_WORDS_7, STEM_WORDS_8]

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    payoff = models.IntegerField(initial=1000)
    
class Player(BasePlayer): 
    def role(player):
        if player.round_number % 4 == 1:
            return {1: 'Ratender', 2: 'Hinweisgebende', 3: 'Hinweisgebende', 4: 'Hinweisgebende'}[player.id_in_group]
        if player.round_number % 4 == 2:
            return {1: 'Hinweisgebende', 2: 'Ratender', 3: 'Hinweisgebende', 4: 'Hinweisgebende'}[player.id_in_group]
        if player.round_number % 4 == 3:
            return {1: 'Hinweisgebende', 2: 'Hinweisgebende', 3: 'Ratender', 4: 'Hinweisgebende'}[player.id_in_group]
        if player.round_number % 4 == 0:
            return {1: 'Hinweisgebende', 2: 'Hinweisgebende', 3: 'Hinweisgebende', 4: 'Ratender'}[player.id_in_group]
        
    guess = models.StringField(label="Ihre Vermutung:", initial='')
    clues = models.StringField(label="Ihr finaler Hinweis:", initial='')
    score = models.IntegerField()
    result = models.StringField()
    incentive = models.IntegerField()
    known = models.StringField(choices=[['Ja', 'Ja'], ['Nein', 'Nein']], label='<b>1. </b>Kennen Sie das Spiel "Just One"?', widget=widgets.RadioSelect)
    role_question = models.StringField(choices=[['Hinweisgebende', 'Hinweisgebende'], ['Ratender', 'Ratender']], label='<b>3. </b>In welcher Rolle haben sie sich wohler gefühlt?', widget=widgets.RadioSelect)
    understanding = models.StringField(choices=[['stimme vollkommen zu', 'stimme vollkommen zu'], ['stimme zu', 'stimme zu'], ['neutral', 'neutral'], ['stimme nicht zu', 'stimme nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='<b>2. </b>"Ich habe die Verfahrensweise und die Regeln schnell verstanden."', widget=widgets.RadioSelectHorizontal)
    comments = models.LongStringField(label="<b>4. </b>Welche Strategie haben sie als Hinweisgebende verfolgt?", initial='', max_length=500, blank=True)
    comments_2 = models.LongStringField(label="<b>5. </b>Welche Strategie haben sie als Ratender verfolgt?", initial='', max_length=500, blank=True)
    freda_1 = models.StringField(choices=[['stimme voll zu', 'stimme voll zu'], ['stimme eher zu', 'stimme eher zu'], ['weder noch', 'weder noch'], ['stimme eher nicht zu', 'stimme eher nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='<b>1. </b>"In meiner Familie werden Werte und Familienrituale über Generationen weitergegeben."', widget=widgets.RadioSelectHorizontal)
    freda_2 = models.StringField(choices=[['stimme voll zu', 'stimme voll zu'], ['stimme eher zu', 'stimme eher zu'], ['weder noch', 'weder noch'], ['stimme eher nicht zu', 'stimme eher nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='<b>2. </b>"Die Zuneigung und Unterstützung meiner Eltern hängen davon ab, inwiefern ich ihre Erwartungen erfülle."', widget=widgets.RadioSelectHorizontal)
    freda_3 = models.StringField(choices=[['stimme voll zu', 'stimme voll zu'], ['stimme eher zu', 'stimme eher zu'], ['weder noch', 'weder noch'], ['stimme eher nicht zu', 'stimme eher nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='<b>3. </b>"Ich weiß besser, was gut für mein (künftiges) Kind ist, als mein (künftiges) Kind selbst."', widget=widgets.RadioSelectHorizontal)
    freda_4 = models.StringField(choices=[['stimme voll zu', 'stimme voll zu'], ['stimme eher zu', 'stimme eher zu'], ['weder noch', 'weder noch'], ['stimme eher nicht zu', 'stimme eher nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='<b>4. </b>"Ich möchte, dass mein (künftiges) Kind wie ich ist, wenn es erwachsen ist."', widget=widgets.RadioSelectHorizontal)
    freda_5 = models.StringField(choices=[['stimme voll zu', 'stimme voll zu'], ['stimme eher zu', 'stimme eher zu'], ['weder noch', 'weder noch'], ['stimme eher nicht zu', 'stimme eher nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='<b>5. </b>"Es gibt eine gute Übereinstimmung zwischen dem, was mein Job mir bietet, und dem, was ich von einem Job erwarte."', widget=widgets.RadioSelectHorizontal)
    freda_6 = models.StringField(choices=[['stimme voll zu', 'stimme voll zu'], ['stimme eher zu', 'stimme eher zu'], ['weder noch', 'weder noch'], ['stimme eher nicht zu', 'stimme eher nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='<b>6. </b>"In meinem Job lerne ich häufig dazu, indem ich mich zum Beispiel auf den neuesten Stand bringe oder neue Aufgaben praktisch durchführe (“learning by doing”)."', widget=widgets.RadioSelectHorizontal)
    freda_7 = models.StringField(choices=[['stimme voll zu', 'stimme voll zu'], ['stimme eher zu', 'stimme eher zu'], ['weder noch', 'weder noch'], ['stimme eher nicht zu', 'stimme eher nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='<b>7. </b>"Meine Eltern gaben mir immer alle Freiheiten."', widget=widgets.RadioSelectHorizontal)
    freda_8 = models.StringField(choices=[['stimme voll zu', 'stimme voll zu'], ['stimme eher zu', 'stimme eher zu'], ['weder noch', 'weder noch'], ['stimme eher nicht zu', 'stimme eher nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='<b>8. </b>"Ich versuche, meinem (künftigen) Kind so viele Freiheiten zu geben, wie ich von meinen Eltern erhalten habe."', widget=widgets.RadioSelectHorizontal)
    understand_1 = models.StringField(choices=[['false', 'Die Hinweise werden dem Ratenden gezeigt'], ['true', 'Die Hinweise werden entfernt, bevor der Ratende sie sieht'], ['false', 'Die Hinweise zählen doppelt'],['false', 'Der Gewinn der Gruppe wird verdoppelt']], label='<b>Frage 1:</b> Was passiert, wenn Spielende identische Hinweise geben?', widget=widgets.RadioSelect)
    understand_2 = models.StringField(choices=[['false', 'Unbegrenzt viele Versuche'],['false', 'Zwei Versuche'],['false', 'Drei Versuche'],['true', 'Nur einen Versuch']], label='<b>Frage 2:</b> Wie viele Versuche hat der Ratende, um das geheime Wort zu erraten?', widget=widgets.RadioSelect)
    understand_3 = models.StringField(choices=[['false,','Zwei'],['false', 'Drei'],['true', 'Vier'],['false', 'Fünf']], label='<b>Frage 3:</b> Wie viele Spielerinnen und Spieler bilden zusammen eine Gruppe?', widget=widgets.RadioSelect)
    understand_4 = models.StringField(choices=[['true', '10 Euro fix für die Teilnahme an allen Runden'],['false', '5 Euro fix plus 5 Euro Bonus für die meisten Ideen'],['false', '5 Euro fix plus 5 Euro Bonus für die meisten erratenen geheimen Wörter'],['false','5 Euro fix plus 5 Euro Bonus für die originellsten Hinweise, die zur richtigen Erratung des Wortes führen']], label='<b>Frage 4:</b> Wie viel Geld können Sie maximal in diesem Experiment verdienen?', widget=widgets.RadioSelect)
    understand_5 = models.StringField(choices=[['false', 'Time'], ['false', 'Zeitpunkt'],['false', 'ist Geld'],['false', 'Zeeeit'],['true', 'keiner der oben genannten Hinweise']], label='<b>Frage 5:</b> Welcher der folgenden Hinweise wäre ein gültiger Hinweis für das geheime Wort "Zeit"?', widget=widgets.RadioSelect)
    strategy = models.StringField(choices=[['stimme vollkommen zu', 'stimme vollkommen zu'], ['stimme zu', 'stimme zu'], ['neutral', 'neutral'], ['stimme nicht zu', 'stimme nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='<b>6. </b>"Ich habe ständig nur daran gedacht, welche Hinweise meine Mitspielenden abgeben."', widget=widgets.RadioSelectHorizontal)
    strategy_2 = models.StringField(choices=[['stimme vollkommen zu', 'stimme vollkommen zu'], ['stimme zu', 'stimme zu'], ['neutral', 'neutral'], ['stimme nicht zu', 'stimme nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='<b>7. </b>"Erst möglichst viele Ideen aufzuschreiben, hilft mir dabei, später bessere Hinweise zu geben."', widget=widgets.RadioSelectHorizontal)
    strategy_3 = models.StringField(choices=[['stimme vollkommen zu', 'stimme vollkommen zu'], ['stimme zu', 'stimme zu'], ['neutral', 'neutral'], ['stimme nicht zu', 'stimme nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='<b>8. </b>"Ich habe versucht, möglichst originelle und einzigartige Hinweise zu geben, damit ich keine identischen Hinweise wie meine Mitspielenden abgebe."', widget=widgets.RadioSelectHorizontal)
    strategy_4 = models.StringField(choices=[['stimme vollkommen zu', 'stimme vollkommen zu'], ['stimme zu', 'stimme zu'], ['neutral', 'neutral'], ['stimme nicht zu', 'stimme nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='<b>9. </b>"Ich habe versucht, eindeutige und naheliegende Hinweise zu geben, auch auf die Gefahr hin, dass meine Mitspielenden identische Hinweise abgeben."', widget=widgets.RadioSelectHorizontal)
    strategy_5 = models.StringField(choices=[['stimme vollkommen zu', 'stimme vollkommen zu'], ['stimme zu', 'stimme zu'], ['neutral', 'neutral'], ['stimme nicht zu', 'stimme nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='<b>10. </b>"Ein Wettkampf mit anderen Gruppen würde mich motivieren, möglichst gute Hinweise zu geben und das geheime Wort zu erraten."', widget=widgets.RadioSelectHorizontal)
    strategy_6 = models.StringField(choices=[['stimme vollkommen zu', 'stimme vollkommen zu'], ['stimme zu', 'stimme zu'], ['neutral', 'neutral'], ['stimme nicht zu', 'stimme nicht zu'], ['stimme überhaupt nicht zu', 'stimme überhaupt nicht zu']], label='<b>11. </b>"Eine Bonuszahlung geknüpft an unsere Gruppenperformance würde mich motivieren, möglichst gute Hinweise zu geben und das geheime Wort zu erraten."', widget=widgets.RadioSelectHorizontal)
    individualism_1 = models.IntegerField(choices=[-3, -2, -1, 0, 1, 2, 3], widget=widgets.RadioSelect)
    individualism_2 = models.IntegerField(choices=[-3, -2, -1, 0, 1, 2, 3], widget=widgets.RadioSelect)
    individualism_3 = models.IntegerField(choices=[-3, -2, -1, 0, 1, 2, 3], widget=widgets.RadioSelect)
    individualism_4 = models.IntegerField(choices=[-3, -2, -1, 0, 1, 2, 3], widget=widgets.RadioSelect)
    individualism_5 = models.IntegerField(choices=[-3, -2, -1, 0, 1, 2, 3], widget=widgets.RadioSelect)
    future_1 = models.StringField(choices=[['mindestens einmal täglich', 'mindestens einmal täglich'], ['mindestens einmal wöchentlich', 'mindestens einmal wöchentlich'], ['mindestens einmal monatlich', 'mindestens einmal monatlich'], ['seltener als einmal im Monat', 'seltener als einmal im Monat']], label='<b>6. </b>Wie oft denken Sie darüber nach, wie der Klimawandel Ihre persönliche Zukunft beeinflusst?', widget=widgets.RadioSelect)
    future_2 = models.StringField(choices=[['mindestens einmal täglich', 'mindestens einmal täglich'], ['mindestens einmal wöchentlich', 'mindestens einmal wöchentlich'], ['mindestens einmal monatlich', 'mindestens einmal monatlich'], ['seltener als einmal im Monat', 'seltener als einmal im Monat']], label='<b>7. </b>	Wie oft denken Sie darüber nach, wie der Klimawandel die Zukunft der Gesellschaft beeinflusst?', widget=widgets.RadioSelect)
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
    identical = models.BooleanField()
    invalid = models.BooleanField()
    missing = models.BooleanField()
    guess_missing = models.BooleanField()
    quantity = models.IntegerField()
    invalid_DAT = models.BooleanField

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
    
class Intro2(Page):
    timeout_seconds = 150
    def is_displayed(player):
        return player.round_number == 1
    
class Rules(Page):
    timeout_seconds = 90
    def is_displayed(player):
        return player.round_number == 1
    
class DAT(Page):
    timeout_seconds = 300
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
   
class Instructions(Page):
    timeout_seconds = 150
    def is_displayed(player):
        return player.round_number == 1
    
class Instructions_2(Page):
    timeout_seconds = 150
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
    timeout_seconds = 210
    def is_displayed(player):
        return player.role() == 'Hinweisgebende'   
    form_model = 'player'
    form_fields = ['clues', 'Idea1', 'Idea2', 'Idea3', 'Idea4', 'Idea5', 'Idea6', 'Idea7', 'Idea8', 'Idea9', 'Idea10']
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        return dict(mystery_word = mystery_word)
        
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.clues = 'Kein Hinweis gegeben'
        else:  
            player.clues = player.clues.lower()
            return player.clues
        
def wordlength(player, value):
    value = value.lower()
    if len(value) > 18:
        return True
    
def clues_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Ihr Hinweis darf nicht länger als 18 Zeichen sein!'

def Idea1_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Ihre Idee darf nicht länger als 18 Zeichen sein!'

def Idea2_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Ihre Idee darf nicht länger als 18 Zeichen sein!'

def Idea3_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Ihre Idee darf nicht länger als 18 Zeichen sein!'

def Idea4_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Ihre Idee darf nicht länger als 18 Zeichen sein!'

def Idea5_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Ihre Idee darf nicht länger als 18 Zeichen sein!'

def Idea6_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Ihre Idee darf nicht länger als 18 Zeichen sein!'

def Idea7_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Ihre Idee darf nicht länger als 18 Zeichen sein!'

def Idea8_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Ihre Idee darf nicht länger als 18 Zeichen sein!'

def Idea9_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Ihre Idee darf nicht länger als 18 Zeichen sein!'

def Idea10_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Ihre Idee darf nicht länger als 18 Zeichen sein!'
    
class CluegiverWaitPage(WaitPage):
    title_text = "Vielen Dank für Ihren Hinweis!"
    body_text = "Bitte warten Sie, bis alle ihre Hinweise abgegeben haben und diese dem Ratenden angezeigt werden."
    def is_displayed(player):
        return player.role() == 'Hinweisgebende'

class GuesserWaitPage(WaitPage):
    title_text = "Sie können Ihren Tipp bald abgeben"
    body_text = "Bitte warten Sie, bis die anderen Spielenden ihre Hinweise für Sie abgegeben haben. Dies kann ein paar Minuten dauern."
    def is_displayed(player): 
        return player.role() == 'Ratender'
    
class ResultsWaitPage(WaitPage):
    title_text = "Ihre Gruppe ist fertig!"
    body_text = "Bitte warten Sie, bis alle Gruppen ihre Hinweise und Tipps abgegeben haben."
    wait_for_all_groups = True

class Guess_Page(Page):
    timeout_seconds = 120
    def is_displayed(player):
        return player.role() == 'Ratender'
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        mystery_word = mystery_word.lower()
        stem_words = C.STEM_WORDS[player.round_number - 1]
        clues_group = [p.clues for p in player.get_others_in_group()]
        special_char_map = {ord('ä'):'ae', ord('ü'):'ue', ord('ö'):'oe', ord('ß'):'ss'}
        clues_group[0] = clues_group[0].translate(special_char_map)
        clues_group[1] = clues_group[1].translate(special_char_map)
        clues_group[2] = clues_group[2].translate(special_char_map)
        if (clues_group[0] in clues_group[1] or clues_group[1] in clues_group[0]) and (clues_group[0] in clues_group[2] or clues_group[2] in clues_group[0]) and (clues_group[1] in clues_group[2] or clues_group[2] in clues_group[1]):
            clues_group[0] = 'Identischer Hinweis'
            clues_group[1] = 'Identischer Hinweis'
            clues_group[2] = 'Identischer Hinweis'
        if clues_group[0] in clues_group[1] or clues_group[1] in clues_group[0]:
            clues_group[0] = 'Identischer Hinweis'
            clues_group[1] = 'Identischer Hinweis'
        if clues_group[0] in clues_group[2] or  clues_group[2] in clues_group[0]:
            clues_group[0] = 'Identischer Hinweis'
            clues_group[2] = 'Identischer Hinweis'
        if clues_group[1] in clues_group[2] or clues_group[2] in clues_group[1]:
            clues_group[1] = 'Identischer Hinweis'
            clues_group[2] = 'Identischer Hinweis'
        if ' ' in clues_group[0] and clues_group[0] != 'Identischer Hinweis' and clues_group[0] != 'Kein Hinweis gegeben':
            more = clues_group[0].split() 
            if len(more)>1:
                clues_group[0] = 'Ungültiger Hinweis'
        if ' ' in clues_group[1] and clues_group[1] != 'Identischer Hinweis' and clues_group[1] != 'Kein Hinweis gegeben':
            more = clues_group[1].split() 
            if len(more)>1:
                clues_group[1] = 'Ungültiger Hinweis'
        if ' ' in clues_group[2] and clues_group[2] != 'Identischer Hinweis' and clues_group[2] != 'Kein Hinweis gegeben':
            more = clues_group[2].split() 
            if len(more)>1:
                clues_group[2] = 'Ungültiger Hinweis'
        import re
        if re.search("[^a-zA-Z0-9s]", clues_group[0]) and clues_group[0] != 'Identischer Hinweis' and clues_group[0] != 'Kein Hinweis gegeben':
            clues_group[0] = 'Ungültiger Hinweis'
        if re.search("[^a-zA-Z0-9s]", clues_group[1]) and clues_group[1] != 'Identischer Hinweis' and clues_group[1] != 'Kein Hinweis gegeben':
            clues_group[1] = 'Ungültiger Hinweis'
        if re.search("[^a-zA-Z0-9s]", clues_group[2]) and clues_group[2] != 'Identischer Hinweis' and clues_group[2] != 'Kein Hinweis gegeben':
            clues_group[2] = 'Ungültiger Hinweis'
        for i in range(len(stem_words)):
            if stem_words[i] in clues_group[0] or clues_group[0] in stem_words[i]:
                clues_group[0] = 'Ungültiger Hinweis'
            if stem_words[i] in clues_group[1] or clues_group[1] in stem_words[i]:
                clues_group[1] = 'Ungültiger Hinweis'
            if stem_words[i] in clues_group[2] or clues_group[2] in stem_words[i]:
                clues_group[2] = 'Ungültiger Hinweis'
        def num_there(s):
            return any(i.isdigit() for i in s)
        if num_there(clues_group[0]) == True:
            clues_group[0] = 'Ungültiger Hinweis'
        if num_there(clues_group[1]) == True:
            clues_group[1] = 'Ungültiger Hinweis'
        if num_there(clues_group[2]) == True:
            clues_group[2] = 'Ungültiger Hinweis'
        with open("wordlist-german.txt", 'r') as file:
            text = file.read()
            wordlist= text.split()
        if clues_group[0] != 'Identischer Hinweis' and clues_group[0] != 'Kein Hinweis gegeben':
            if clues_group[0] not in wordlist:
                clues_group[0] = 'Ungültiger Hinweis'
        if clues_group[1] != 'Identischer Hinweis' and clues_group[1] != 'Kein Hinweis gegeben':
            if clues_group[1] not in wordlist:
                clues_group[1] = 'Ungültiger Hinweis'
        if clues_group[2] != 'Identischer Hinweis' and clues_group[2] != 'Kein Hinweis gegeben':
            if clues_group[2] not in wordlist:
                clues_group[2] = 'Ungültiger Hinweis'
        return dict(clues = clues_group)
    form_model = 'player'
    form_fields = ['guess'] 
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.guess = 'Kein Tipp gegeben'
        else:
            player.guess = player.guess.lower()
            special_char_map = {ord('ä'):'ae', ord('ü'):'ue', ord('ö'):'oe', ord('ß'):'ss'}
            player.guess = player.guess.translate(special_char_map)
            return player.guess
        
class Results(Page):
    timeout_seconds = 45
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        mystery_word = mystery_word.lower()
        stem_words = C.STEM_WORDS[player.round_number - 1]
        if player.role() == 'Hinweisgebende':
            own_clue = player.clues
            special_char_map = {ord('ä'):'ae', ord('ü'):'ue', ord('ö'):'oe', ord('ß'):'ss'}
            own_clue = own_clue.translate(special_char_map)
            clues = [p.clues for p in player.get_others_in_group()]
            guess = [p.guess for p in player.get_others_in_group()]
            while '' in clues:
                clues.remove('')
            while '' in guess:
                guess.remove('')
            guess = guess[0]
            player.missing = False
            player.guess_missing = False
            player.identical = False
            player.invalid = False
            identical = ''
            invalid = ''
            missing = ''
            guess_missing = ''
            if own_clue == 'Kein Hinweis gegeben':
                player.missing = True
                missing = 'Achtung! Sie haben keinen Hinweis gegeben.'
            else:
                if own_clue in clues[0] or clues[0] in own_clue or own_clue in clues[1] or clues[1] in own_clue:
                    player.identical = True
                    identical = 'Achtung! Sie haben einen identischen Hinweis gegeben.'
                for i in range(len(stem_words)):
                    if own_clue in stem_words[i] or stem_words[i] in own_clue:
                        player.invalid = True
                        invalid = 'Achtung! Ihr Hinweis war ungültig (gleiche Wortfamilie wie das geheimnisvolle Wort).'
                if ' ' in own_clue and player.invalid == False:
                    more = own_clue.split() 
                    if len(more)>1:
                        player.invalid = True
                        invalid = 'Achtung! Ihr Hinweis war ungültig (mehr als ein Wort).'
                import re
                if re.search("[^a-zA-Z0-9s]", own_clue) and player.invalid == False:
                    player.invalid = True
                    invalid = 'Achtung! Ihr Hinweis war ungültig (Verwendung von Sonderzeichen).'
                def num_there(s):
                    return any(i.isdigit() for i in s)
                if num_there(own_clue) == True and player.invalid == False:
                    player.invalid = True
                    invalid = 'Achtung! Ihr Hinweis war ungültig (Verwendung von Zahlen).'
                with open("wordlist-german.txt", 'r') as file:
                    text = file.read()
                    wordlist= text.split()
                    if own_clue not in wordlist and player.invalid == False:
                        player.invalid = True
                        invalid = 'Achtung! Ihr Hinweis war ungültig (Rechtschreibfehler oder kein echtes Wort).'
            clues.append(own_clue)
            player.Idea1 = player.Idea1.lower()
            player.Idea2 = player.Idea2.lower()
            player.Idea3 = player.Idea3.lower()
            player.Idea4 = player.Idea4.lower()
            player.Idea5 = player.Idea5.lower()
            player.Idea6 = player.Idea6.lower()
            player.Idea7 = player.Idea7.lower()
            player.Idea8 = player.Idea8.lower()
            player.Idea9 = player.Idea9.lower()
            player.Idea10 = player.Idea10.lower()
            own_ideas = [player.Idea1, player.Idea2, player.Idea3, player.Idea4, player.Idea5, player.Idea6, player.Idea7, player.Idea8, player.Idea9, player.Idea10] 
            while '' in own_ideas:
                own_ideas.remove('')
            if len(own_ideas) > 0:
                for i in range(len(own_ideas)):  
                    special_char_map = {ord('ä'):'ae', ord('ü'):'ue', ord('ö'):'oe', ord('ß'):'ss'}
                    own_ideas[i] = own_ideas[i].translate(special_char_map)
                    if ' ' in own_ideas[i]:
                        more = own_ideas[i].split() 
                        if len(more)>1: 
                            own_ideas[i] = 'false'
            if len(own_ideas) > 0:
                for i in range(len(own_ideas)):
                    for j in range(len(stem_words)):
                        if own_ideas[i] in stem_words[j] or stem_words[j] in own_ideas[i]:
                            own_ideas[i] = 'false'     
            with open("wordlist-german.txt", 'r') as file:
                text = file.read()
                wordlist= text.split()
                if len(own_ideas) > 0:
                    for i in range(len(own_ideas)):
                        if own_ideas[i] not in wordlist:
                            own_ideas[i] = 'false'
            import re
            if len(own_ideas) > 0:
                for i in range(len(own_ideas)):
                    if re.search("[^a-zA-Z0-9s]", own_ideas[i]):
                        own_ideas[i] = 'false'          
            def has_numbers(s):
                return bool(re.search(r'\d',s))
            if len(own_ideas) > 0:
                for i in range(len(own_ideas)):
                    if has_numbers(own_ideas[i]) == True:
                        own_ideas[i] = 'false'
            while 'false' in own_ideas:
                own_ideas.remove('false')
            own_ideas = list(dict.fromkeys(own_ideas))
            player.quantity = len(own_ideas)
        if player.role() == 'Ratender':
            player.missing = False
            player.identical = False
            player.invalid = False
            player.quantity = 0
            player.guess_missing = False
            identical = ''
            invalid = ''
            missing = ''
            guess_missing = ''
            guess = player.guess
            clues = [p.clues for p in player.get_others_in_group()]
            if guess == 'Kein Tipp gegeben':
                player.guess_missing = True
                guess_missing = 'Achtung! Sie haben keinen Tipp abgegeben.'
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
        return dict(mystery_word = mystery_word, clues = clues, guess = guess, result = player.result, identical = identical, invalid = invalid, missing = missing, guess_missing = guess_missing, number_ideas = player.quantity)

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
    timeout_seconds = 270
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    form_model = 'player'
    form_fields = ['known', 'understanding', 'role_question', 'comments', 'comments_2', 'strategy', 'strategy_2', 'strategy_3', 'strategy_4', 'strategy_5', 'strategy_6']

class FredaQuestions(Page):
    template_name = 'justone_deutsch/FredaQuestions.html'
    timeout_seconds = 150
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    form_model = 'player'
    form_fields = ['freda_1', 'freda_2', 'freda_3', 'freda_4', 'freda_5', 'freda_6', 'freda_7', 'freda_8']

class IndividualismQuestions(Page):
    template_name = 'justone_deutsch/IndividualismQuestions.html'
    timeout_seconds = 150
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    form_model = 'player'
    form_fields = ['individualism_1', 'individualism_2', 'individualism_3', 'individualism_4', 'individualism_5', 'future_1', 'future_2']

class UnderstandPage(Page):
    template_name = 'justone_deutsch/UnderstandPage.html'
    timeout_seconds = 150
    def is_displayed(player):
        return player.round_number == 1
    form_model = 'player'
    form_fields = ['understand_1', 'understand_2', 'understand_3', 'understand_4', 'understand_5']
    def error_message(player, values):
        if values['understand_1'] == 'false':
            return 'Falsche Antwort bei Frage 1! Versuchen Sie es noch einmal.'
        if values['understand_2'] == 'false':
            return 'Falsche Antwort bei Frage 2! Versuchen Sie es noch einmal.'
        if values['understand_3'] == 'false':
            return 'Falsche Antwort bei Frage 3! Versuchen Sie es noch einmal.'
        if values['understand_4'] == 'false':
            return 'Falsche Antwort bei Frage 4! Versuchen Sie es noch einmal.'
        if values['understand_5'] == 'false':
            return 'Falsche Antwort bei Frage 5! Versuchen Sie es noch einmal.'

class FinalPage(Page):
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

page_sequence = [GroupWaitPage, Intro, Intro2, Rules, Instructions, Instructions_2, UnderstandPage, Round, Clue_Page, GuesserWaitPage, Guess_Page, CluegiverWaitPage, ResultsWaitPage, Results, Score, TestQuestions, FredaQuestions, IndividualismQuestions, DAT, FinalPage]
