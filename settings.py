from os import environ


SESSION_CONFIGS = [
    dict(
        name='eriks_game', display_name= "Mystery Word Game", app_sequence=['justone_welcome', 'justone', 'justone_survey'], num_demo_participants=12, ),
    dict(name='eriks_game_2', display_name= "Mystery Word Game 2", app_sequence=['justone_welcome', 'justone_survey'], num_demo_participants=12, ),
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
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ROOMS = [
    dict(name='Players_Room1', display_name='Players Room1', participant_label_file='participant_ labels.txt', use_secure_urls=True),
    dict(name='Players_Room2', display_name='Players Room2', participant_label_file='participant_labels_2.txt', use_secure_urls=True),
    dict(name='Rest_Room', display_name='Rest Room', participant_label_file='participant_labels_rest.txt', use_secure_urls=True),
    ]
ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """
Here are some oTree games.
"""

SECRET_KEY = '{{ secret_key }}'

INSTALLED_APPS = ['otree']


