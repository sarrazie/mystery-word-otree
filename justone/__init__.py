from otree.api import *

from settings import PARTICIPANT_FIELDS

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'Mystery_Word_Game'
    NUM_ROUNDS = 12
    PLAYERS_PER_GROUP = 4
    MYSTERY_WORDS = ['Robot', 'Hair', 'Cheese', 'Forest', 'Letter', 'Shower', 'Idea', 'White', 'Time', 'Penguin', 'Unicorn', 'Market']
    LANGUAGE_CODE = 'en'

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    incentive = models.BooleanField()
    payoff = models.IntegerField(initial=1000)
    
class Player(BasePlayer): 
    def role(player):
        if player.round_number % 4 == 1:
            return {1: 'guesser', 2: 'cluegiver', 3: 'cluegiver', 4: 'cluegiver'}[player.id_in_group]
        if player.round_number % 4 == 2:
            return {1: 'cluegiver', 2: 'guesser', 3: 'cluegiver', 4: 'cluegiver'}[player.id_in_group]
        if player.round_number % 4 == 3:
            return {1: 'cluegiver', 2: 'cluegiver', 3: 'guesser', 4: 'cluegiver'}[player.id_in_group]
        if player.round_number % 4 == 0:
            return {1: 'cluegiver', 2: 'cluegiver', 3: 'cluegiver', 4: 'guesser'}[player.id_in_group]
        
    guess = models.StringField(label="Your guess:", initial='')
    clues = models.StringField(label="Your clue:", initial='')
    score = models.IntegerField()
    result = models.StringField()
    known = models.StringField(choices=[['Yes', 'Yes'], ['No', 'No']], label='Did you ever play the game "Just One" before?', widget=widgets.RadioSelect)
    understanding = models.StringField(choices=[['strongly agree', 'strongly agree'],[' agree', 'agree'],['neutral', 'neutral'],['disagree', 'disagree'],['strongly disagree', 'strongly disagree']], label='"I quickly understood the procedure and the rules of the game."', widget=widgets.RadioSelectHorizontal)
    english = models.StringField(choices=[['strongly agree', 'strongly agree'],[' agree', 'agree'],['neutral', 'neutral'],['disagree', 'disagree'],['strongly disagree', 'strongly disagree']], label='"My limited vocabulary in English made my performance in the game worse."', widget=widgets.RadioSelectHorizontal)
    comments = models.LongStringField(label="Do you have any comments or suggestions for improvement? (optional)", initial='', max_length=500, blank=True)

def creating_session(subsession: Subsession):
    import itertools
    incentives = itertools.cycle([True, False])
    session = subsession.session
    session.vars['incentive_group_list'] = incentives
    
# PAGES
class GroupWaitPage(WaitPage):
    template_name = 'justone/GroupWaitPage.html'
    group_by_arrival_time = True
    def is_displayed(player):
        return player.round_number == 1
    @staticmethod
    def after_all_players_arrive(group: Group):
        session = group.session
        group.incentive = next(session.vars['incentive_group_list'])
        for player in group.get_players():
            participant= player.participant
            participant.vars['treatment'] = group.incentive

class Intro(Page):
    timeout_seconds = 150
    def is_displayed(player):
        return player.round_number == 1

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
    timeout_seconds = 120
    def is_displayed(player):
        return player.role() == 'cluegiver'   
    form_model = 'player'
    form_fields = ['clues'] 
 
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        return dict(mystery_word = mystery_word)

    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.clues = 'No clue given'
        else:  
            player.clues = player.clues.lower()
            return player.clues

def clues_error_message(player, value):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        mystery_word = mystery_word.lower()
        value = value.lower()
        if len(value) > 18:
            return 'Your clue must not be longer than 18 characters!'
        if ' ' in value:
            return 'Your clue must only contain one word!'
        if mystery_word in value or value in mystery_word:
            return 'Your clue must not contain parts of the mystery word!'
        def num_there(s):
         return any(i.isdigit() for i in s)
        if num_there(value) == False:
            from deep_translator import GoogleTranslator
            value_trans = GoogleTranslator(source='auto', target='en').translate(value)
            if mystery_word == value_trans:
                return 'Your clue must not be a translation of the mystery word!'
        from textblob import Word
        word = Word(value)
        result = word.spellcheck()
        if word != result [0][0]:
            return 'Your clue must be spelled correctly and cannot be fictitious!'
        
class ResultsWaitPage(WaitPage):
    title_text = "Thank you for your clue!"
    body_text = "Please wait until all other players have submitted their clues and the guesser has made a guess."
    def is_displayed(player):
        return player.role() == 'cluegiver'

class GuesserWaitPage(WaitPage):
    title_text = "You can make your guess very soon!"
    body_text = "Please wait until all players have submitted their clues for you."
    def is_displayed(player): 
        return player.role() == 'guesser'
    
class Guess_Page(Page):
    timeout_seconds = 120
    def is_displayed(player):
        return player.role() == 'guesser'
    def vars_for_template(player):
        clues_group = [p.clues for p in player.get_others_in_group()]
        if (clues_group[0] in clues_group[1] or clues_group[1] in clues_group[0]) and (clues_group[0] in clues_group[2] or clues_group[2] in clues_group[0]) and (clues_group[1] in clues_group[2] or clues_group[2] in clues_group[1]):
                clues_group[0] = 'Identical clue'
                clues_group[1] = 'Identical clue'
                clues_group[2] = 'Identical clue'
        if clues_group[0] in clues_group[1] or clues_group[1] in clues_group[0]:
                clues_group[0] = 'Identical clue'
                clues_group[1] = 'Identical clue'
        if clues_group[0] in clues_group[2] or  clues_group[2] in clues_group[0]:
                clues_group[0] = 'Identical clue'
                clues_group[2] = 'Identical clue'
        if clues_group[1] in clues_group[2] or clues_group[2] in clues_group[1]:
                clues_group[1] = 'Identical clue'
                clues_group[2] = 'Identical clue'
        return dict(clues = clues_group)
    form_model = 'player'
    form_fields = ['guess'] 
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.guess = 'No guess given'
        else:
            player.guess = player.guess.lower()
            return player.guess

class Results(Page): 
    timeout_seconds = 60
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        if player.role() == 'cluegiver':
            own_clue = player.clues
            clues = [p.clues for p in player.get_others_in_group()]
            guess = [p.guess for p in player.get_others_in_group()]
            clues.append(own_clue)
            while '' in clues:
                clues.remove('')
            while '' in guess:
                guess.remove('')
            guess = guess[0]
        if player.role() == 'guesser':
            guess = player.guess
            clues = [p.clues for p in player.get_others_in_group()]
        mystery_word = mystery_word.lower()
        guess = guess.lower()
        if mystery_word == guess:
            player.result = 'correct'
            player.payoff = 1
        else:
            player.result = 'incorrect' 
            player.payoff = 0 
        player.score =  int(player.participant.payoff)
        player.group.payoff =  player.score 
        if player.participant.treatment == False:
            player.group.payoff = 1000
        overall_score = score(player.group)
        return dict(mystery_word = mystery_word, clues = clues, guess = guess, result = player.result, score = player.score, overall_score = overall_score)
    
def score (group: Group):
    subsession = group.subsession
    groups = subsession.get_groups()
    overall_score = []
    for group in groups:
            overall_score.append(group.payoff)
            if group.payoff == 1000:
                overall_score.remove(1000)
            sorted_overall_score = sorted(overall_score, reverse = True) 
    return sorted_overall_score
      
class TestQuestions(Page):
    template_name = 'justone/TestQuestions.html'
    timeout_seconds = 180
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    form_model = 'player'
    form_fields = ['known', 'understanding', 'english', 'comments']
    
class FinalPage(Page):
    timeout_seconds = 30
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

page_sequence = [GroupWaitPage, Intro, Instructions, Round, Clue_Page, GuesserWaitPage, Guess_Page, ResultsWaitPage, Results, TestQuestions, FinalPage]
