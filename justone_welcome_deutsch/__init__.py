from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    NAME_IN_URL = 'justone_welcome_deutsch'

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass
    
#PAGES

class Welcome(Page):
    timeout_seconds = 180
    pass

page_sequence = [Welcome]
