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
    clues = models.StringField(label="Your final clue:", initial='')
    score = models.IntegerField()
    result = models.StringField()
    incentive = models.IntegerField()
    known = models.StringField(choices=[['Yes', 'Yes'], ['No', 'No']], label='Did you ever play the game "Just One" before?', widget=widgets.RadioSelect)
    understanding = models.StringField(choices=[['strongly agree', 'strongly agree'],[' agree', 'agree'],['neutral', 'neutral'],['disagree', 'disagree'],['strongly disagree', 'strongly disagree']], label='"I quickly understood the procedure and the rules of the game."', widget=widgets.RadioSelectHorizontal)
    english = models.StringField(choices=[['strongly agree', 'strongly agree'],[' agree', 'agree'],['neutral', 'neutral'],['disagree', 'disagree'],['strongly disagree', 'strongly disagree']], label='"My limited vocabulary in English made my performance in the game worse."', widget=widgets.RadioSelectHorizontal)
    comments = models.LongStringField(label="Do you have any comments or suggestions for improvement? (optional)", initial='', max_length=500, blank=True)
    Idea1 = models.StringField(label= 'Your ideas:', initial='', blank=True)
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
    Idea13 = models.StringField(label= '', initial='', blank=True)
    Idea14 = models.StringField(label= '', initial='', blank=True)
    Idea15 = models.StringField(label= '', initial='', blank=True)
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
    gender = models.IntegerField(choices=[[1, 'Male'],[2, 'Female'],[3, 'Diverse'],], label='Gender:')
    age = models.IntegerField(min=18, max=100, label='Age:')
    identical = models.BooleanField()
    invalid = models.BooleanField()
    missing = models.BooleanField()
    guess_missing = models.BooleanField()
    quantity = models.IntegerField()
    invalid_DAT= models.BooleanField

def creating_session(subsession: Subsession):
    session = subsession.session
    for player in subsession.get_players():
        participant = player.participant
        participant.vars['treatment'] = session.config['treatment']
        player.incentive = participant.vars['treatment']

# PAGES
class GroupWaitPage(WaitPage):
    template_name = 'justone/GroupWaitPage.html'
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
    timeout_seconds = 180
    def is_displayed(player):
        return player.role() == 'cluegiver'   
    form_model = 'player'
    form_fields = ['clues', 'Idea1', 'Idea2', 'Idea3', 'Idea4', 'Idea5', 'Idea6', 'Idea7', 'Idea8', 'Idea9', 'Idea10', 'Idea11', 'Idea12', 'Idea13', 'Idea14', 'Idea15']
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        return dict(mystery_word = mystery_word)
        
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.clues = 'No clue given'
        else:  
            player.clues = player.clues.lower()
            return player.clues
        
def wordlength(player, value):
    value = value.lower()
    if len(value) > 18:
        return True
    
def clues_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Your clue must not be longer than 18 characters!'

def Idea1_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Your idea must not be longer than 18 characters!'

def Idea2_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Your idea must not be longer than 18 characters!'

def Idea3_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Your idea must not be longer than 18 characters!'

def Idea4_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Your idea must not be longer than 18 characters!'

def Idea5_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Your idea must not be longer than 18 characters!'

def Idea6_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Your idea must not be longer than 18 characters!'

def Idea7_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Your idea must not be longer than 18 characters!'

def Idea8_error_message(player, value): 
    if wordlength(player, value) == True:
        return 'Your idea must not be longer than 18 characters!'

def Idea9_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Your idea must not be longer than 18 characters!'

def Idea10_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Your idea must not be longer than 18 characters!'
    
def Idea11_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Your idea must not be longer than 18 characters!'

def Idea12_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Your idea must not be longer than 18 characters!'

def Idea13_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Your idea must not be longer than 18 characters!'   
    
def Idea14_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Your idea must not be longer than 18 characters!'

def Idea15_error_message(player, value):
    if wordlength(player, value) == True:
        return 'Your idea must not be longer than 18 characters!'

class CluegiverWaitPage(WaitPage):
    title_text = "Thank you for your clue!"
    body_text = "Please wait until the other players have submitted their clues and the guesser has made a guess."
    def is_displayed(player):
        return player.role() == 'cluegiver'

class GuesserWaitPage(WaitPage):
    title_text = "You can make your guess very soon!"
    body_text = "Please wait until the other players have submitted their clues for you."
    def is_displayed(player): 
        return player.role() == 'guesser'
    
class ResultsWaitPage(WaitPage):
    title_text = "Your group is done!"
    body_text = "Please wait until all groups have submitted their clues and guesses."
    wait_for_all_groups = True

class Guess_Page(Page):
    timeout_seconds = 120
    def is_displayed(player):
        return player.role() == 'guesser'
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        mystery_word = mystery_word.lower()
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
        if ' ' in clues_group[0] and clues_group[0] != 'Identical clue' and clues_group[0] != 'No clue given':
            clues_group[0] = 'Invalid clue'
        if ' ' in clues_group[1] and clues_group[1] != 'Identical clue' and clues_group[1] != 'No clue given':
            clues_group[1] = 'Invalid clue'
        if ' ' in clues_group[2] and clues_group[2] != 'Identical clue' and clues_group[2] != 'No clue given':
            clues_group[2] = 'Invalid clue'
        import re
        if re.search("[^a-zA-Z0-9s]", clues_group[0]) and clues_group[0] != 'Identical clue' and clues_group[0] != 'No clue given':
            clues_group[0] = 'Invalid clue'
        if re.search("[^a-zA-Z0-9s]", clues_group[1]) and clues_group[1] != 'Identical clue' and clues_group[1] != 'No clue given':
            clues_group[1] = 'Invalid clue'
        if re.search("[^a-zA-Z0-9s]", clues_group[2]) and clues_group[2] != 'Identical clue' and clues_group[2] != 'No clue given':
            clues_group[2] = 'Invalid clue'
        if mystery_word in clues_group[0] or clues_group[0] in mystery_word:
            clues_group[0] = 'Invalid clue' 
        if mystery_word in clues_group[1] or clues_group[1] in mystery_word:
            clues_group[1] = 'Invalid clue' 
        if mystery_word in clues_group[2] or clues_group[2] in mystery_word:
            clues_group[2] = 'Invalid clue'
        def num_there(s):
            return any(i.isdigit() for i in s)
        from deep_translator import GoogleTranslator
        if num_there(clues_group[0]) == False:
            clue_trans = GoogleTranslator(source='auto', target='en').translate(clues_group[0])
            if mystery_word == clue_trans:
                clues_group[0] = 'Invalid clue'
        if num_there(clues_group[1]) == False:
            clue_trans = GoogleTranslator(source='auto', target='en').translate(clues_group[1])
            if mystery_word == clue_trans:
                clues_group[1] = 'Invalid clue'
        if num_there(clues_group[2]) == False:
             clue_trans = GoogleTranslator(source='auto', target='en').translate(clues_group[2])
             if mystery_word == clue_trans:
                clues_group[2] = 'Invalid clue'
        from textblob import Word
        word = Word(clues_group[0])
        result = word.spellcheck()
        if word != result [0][0]:
            clues_group[0] = 'Invalid clue'
        word = Word(clues_group[1])
        result = word.spellcheck()
        if word != result [0][0]:
            clues_group[1] = 'Invalid clue' 
        word = Word(clues_group[2])
        result = word.spellcheck()
        if word != result [0][0]:
            clues_group[2] = 'Invalid clue'
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
    timeout_seconds = 45
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        mystery_word = mystery_word.lower()
        if player.role() == 'cluegiver':
            own_clue = player.clues
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
            if own_clue == 'No clue given':
                    player.missing = True
                    missing = 'Watch out! You did not give a clue.'
            else:
                if own_clue in clues[0] or clues[0] in own_clue or own_clue in clues[1] or clues[1] in own_clue:
                    player.identical = True
                    identical = 'Watch out! You gave an identical clue.'     
                if own_clue in mystery_word or mystery_word in own_clue:
                    player.invalid = True 
                    invalid = 'Watch out! Your clue was invalid (same word family as mystery word).'
                if ' ' in own_clue and player.invalid == False:
                    player.invalid = True    
                    invalid = 'Watch out! Your clue was invalid (more than one word).'
                import re
                if re.search("[^a-zA-Z0-9s]", own_clue) and player.invalid == False:
                    player.invalid = True
                    invalid = 'Watch out! Your clue was invalid (use of special characters).'
                def num_there(s):
                    return any(i.isdigit() for i in s)
                from deep_translator import GoogleTranslator
                if num_there(own_clue) == False:
                    clue_trans = GoogleTranslator(source='auto', target='en').translate(own_clue)
                    if mystery_word == clue_trans and player.invalid == False:
                        player.invalid = True
                        invalid = 'Watch out! Your clue was invalid (translation of mystery word).'
                from textblob import Word
                word = Word(own_clue)
                result = word.spellcheck()
                if word != result [0][0] and player.invalid == False:
                    player.invalid = True
                    invalid = 'Watch out! Your clue was invalid (spelling mistake or no real word).'
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
            player.Idea11 = player.Idea11.lower()
            player.Idea12 = player.Idea12.lower()
            player.Idea13 = player.Idea13.lower()
            player.Idea14 = player.Idea14.lower()
            player.Idea15 = player.Idea15.lower()
            own_ideas = [player.Idea1, player.Idea2, player.Idea3, player.Idea4, player.Idea5, player.Idea6, player.Idea7, player.Idea8, player.Idea9, player.Idea10, player.Idea11, player.Idea12, player.Idea13, player.Idea14, player.Idea15] 
            while '' in own_ideas:
                own_ideas.remove('')
            import re
            from deep_translator import GoogleTranslator
            from textblob import Word
            if len(own_ideas) > 0:
                for i in range(len(own_ideas)):  
                    if ' ' in own_ideas[i]:
                        own_ideas[i] = 'false'
            if len(own_ideas) > 0:
                for i in range(len(own_ideas)):
                    if own_ideas[i] in mystery_word or mystery_word in own_ideas[i]:
                        own_ideas[i] = 'false'
            if len(own_ideas) > 0:
                for i in range(len(own_ideas)):
                    word = Word(own_ideas[i])
                    result = word.spellcheck() 
                    if word != result [0][0]:
                        own_ideas[i] = 'false'
            if len(own_ideas) > 0:
                for i in range(len(own_ideas)):
                    if re.search("[^a-zA-Z0-9s]", own_ideas[i]):
                        own_ideas[i] = 'false'
            def has_numbers(s):
                return bool(re.search(r'\d',s))
            if len(own_ideas) > 0:
                for i in range(len(own_ideas)):
                    if has_numbers(own_ideas[i]) == False:
                        clue_trans = GoogleTranslator(source='auto', target='en').translate(own_ideas[i])
                        if mystery_word == clue_trans:
                            own_ideas[i] = 'false'
            while 'false' in own_ideas:
                own_ideas.remove('false')
            own_ideas = list(dict.fromkeys(own_ideas))
            player.quantity = len(own_ideas)
        if player.role() == 'guesser':
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
            if guess == 'No guess given':
                player.guess_missing = True
                guess_missing = 'Watch out! You did not give a guess.'
            else:
                guess = guess.lower()
        if mystery_word == guess:
            player.result = 'correct'
            player.payoff = 1
        else:
            player.result = 'incorrect' 
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

page_sequence = [GroupWaitPage, Intro, Instructions, Round, Clue_Page, GuesserWaitPage, Guess_Page, CluegiverWaitPage, ResultsWaitPage, Results, Score, TestQuestions, DAT, FinalPage]
