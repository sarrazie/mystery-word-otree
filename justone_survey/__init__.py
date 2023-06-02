from otree.api import *

doc = """ Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'justone_survey'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    FAMILY_MEMBERS = [dict(name='Parents', label='Parents'),
                      dict(name='Grandparents', label='Grandparents'), 
                      dict(name='Siblings', label='Siblings'),
                      dict(name='Aunts_Uncles', label='Aunts/Uncles'),
                      dict(name='Cousins', label='Cousins'),
                      dict(name='Other', label='Other family members')]
class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass

class Player(BasePlayer):
    number_family_gathering= models.IntegerField(label='In your family, how many people typically attend a family gathering or celebration of a holiday?', min=1, max=10000)
    number_wedding_funeral= models.IntegerField(label='In your family, how many people typically attend a wedding or funeral?', min=1, max=10000)
    Parents = models.BooleanField(blank=True, initial=0)
    Grandparents = models.BooleanField(blank=True, initial=0)
    Siblings = models.BooleanField(blank=True, initial=0)
    Aunts_Uncles = models.BooleanField(blank=True, initial=0)
    Cousins = models.BooleanField(blank=True, initial=0)
    Other = models.BooleanField(blank=True, initial=0)
 
# PAGES

class Survey_1(Page):
    template_name = 'justone_survey/Survey_1.html'
    timeout_seconds = 150
    form_model = 'player'
    form_fields = ['number_family_gathering', 'number_wedding_funeral']
   
class Survey(Page):
    form_model = 'player'
    template_name = 'justone_survey/Survey.html'
    timeout_seconds = 150
    def get_form_fields(player):
      return [member['name'] for member in C.FAMILY_MEMBERS]
    def error_message(player, values):
        num_selected = 0
        for member in C.FAMILY_MEMBERS:
            if values[member['name']]:
                num_selected += 1
        if num_selected < 1:
            return 'Please select at least one family member.'

class FinalPage(Page):
    pass

page_sequence = [Survey_1, Survey, FinalPage]
