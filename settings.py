from os import environ


SESSION_CONFIGS = [
    dict(name='eriks_game', display_name= "Mystery Word Game Control", app_sequence=['justone_welcome', 'justone'], num_demo_participants=24, treatment=1, ),
    dict(name='eriks_game_2', display_name= "Mystery Word Game Quantity", app_sequence=['justone_welcome', 'justone'], num_demo_participants=24, treatment=2,),
    dict(name='eriks_game_3', display_name= "Mystery Word Game Quality", app_sequence=['justone_welcome', 'justone'], num_demo_participants=24, treatment=3,),
    dict(name='eriks_game_4', display_name= "Mystery Word Game Originality", app_sequence=['justone_welcome', 'justone'], num_demo_participants=24, treatment=4,),
    dict(name='eriks_game_5', display_name= "Mystery Word Game deutsch Pre-Test", app_sequence=['justone_welcome_deutsch', 'justone_deutsch'], num_demo_participants=8, treatment=1,),
    dict(name='eriks_game_6', display_name= "Mystery Word Game deutsch Quantity", app_sequence=['justone_welcome_deutsch', 'justone_deutsch'], num_demo_participants=8, treatment=2,),
    dict(name='eriks_game_7', display_name= "Mystery Word Game deutsch Quality", app_sequence=['justone_welcome_deutsch', 'justone_deutsch'], num_demo_participants=8, treatment=3,),
    dict(name='eriks_game_8', display_name= "Mystery Word Game deutsch Originality", app_sequence=['justone_welcome_deutsch', 'justone_deutsch'], num_demo_participants=8, treatment=4,),
    dict(name='eriks_game_9', display_name= "New Mystery Word Game deutsch mit Regel Pre-Test", app_sequence=['justone_welcome_deutsch', 'new_justone_deutsch'], num_demo_participants=8, treatment=1,),
    dict(name='eriks_game_10', display_name= "New Mystery Word Game deutsch Quantity", app_sequence=['justone_welcome_deutsch', 'new_justone_deutsch'], num_demo_participants=8, treatment=2,),
    dict(name='eriks_game_11', display_name= "New Mystery Word Game deutsch Quality", app_sequence=['justone_welcome_deutsch', 'new_justone_deutsch'], num_demo_participants=8, treatment=3,),
    dict(name='eriks_game_12', display_name= "New Mystery Word Game deutsch Originality", app_sequence=['justone_welcome_deutsch', 'new_justone_deutsch'], num_demo_participants=8, treatment=4,),
    dict(name='eriks_game_13', display_name= "New Mystery Word Game deutsch ohne Regel Pre-Test ", app_sequence=['justone_welcome_deutsch', 'new_justone_deutsch_oR'], num_demo_participants=8, treatment=1, ),
    dict(name='eriks_game_14', display_name= "New Mystery Word Game english mit Regel", app_sequence=['justone_welcome_deutsch', 'new_justone'], num_demo_participants=8, treatment=1,),
    dict(name='eriks_game_15', display_name= "Experiment Control", app_sequence=['justone_welcome_deutsch', 'experiment'], num_demo_participants=8, treatment=1,),
    dict(name='eriks_game_16', display_name= "Experiment Quantity", app_sequence=['justone_welcome_deutsch', 'experiment'], num_demo_participants=8, treatment=2,),
    dict(name='eriks_game_17', display_name= "Experiment Quality", app_sequence=['justone_welcome_deutsch', 'experiment'], num_demo_participants=8, treatment=3,),
    dict(name='eriks_game_18', display_name= "Experiment Originality", app_sequence=['justone_welcome_deutsch', 'experiment'], num_demo_participants=8, treatment=4,),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = ['treatment']
SESSION_FIELDS = ['incentive_group_list']

SESSION_CONFIGS

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'de'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = True

ROOMS = [
    dict(name='Players_Room1', display_name='Players Room1', participant_label_file='participant_labels.txt'),
    dict(name='Players_Room2', display_name='Players Room2', participant_label_file='participant_labels.txt'),
    dict(name='Players_Room3', display_name='Players Room3', participant_label_file='participant_labels.txt'),
    dict(name='Players_Room4', display_name='Players Room4', participant_label_file='participant_labels.txt'),
    dict(name='Players_Room5', display_name='Players Room5', participant_label_file='participant_labels.txt'),
    dict(name='Players_Room6', display_name='Players Room6', participant_label_file='participant_labels.txt'),
    ]
ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = 'admin'

DEMO_PAGE_INTRO_HTML = """
Here are some oTree games.
"""

SECRET_KEY = '{{ secret_key }}'

INSTALLED_APPS = ['otree']


