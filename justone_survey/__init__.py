from otree.api import *


doc = """ Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'justone_survey'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass

class Player(BasePlayer):
    number_family_gathering= models.IntegerField(label='In your family, how many people typically attend a family gathering or celebration of a holiday?', min=1, max=10000)
    number_wedding_funeral= models.IntegerField(label='In your family, how many people typically attend a wedding or funeral?', min=1, max=10000)
    choice1 = models.BooleanField(blank=True)
    choice2 = models.BooleanField(blank=True)
    choice3 = models.BooleanField(blank=True)
    choice4 = models.BooleanField(blank=True)
    choice5 = models.BooleanField(blank=True)
    choice6 = models.BooleanField(blank=True)

# PAGES

class Survey(Page):
    template_name = 'justone_survey/Survey.html'
    timeout_seconds = 300
    form_model = 'player'
    form_fields = ['number_family_gathering', 'number_wedding_funeral']

class FinalPage(Page):
    pass

page_sequence = [Survey, FinalPage]
