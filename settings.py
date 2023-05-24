from os import environ


SESSION_CONFIGS = [
    dict(
        name='eriks_game', display_name= "Mystery Word Game", app_sequence=['justone_welcome', 'justone', 'justone_survey'], num_demo_participants=24, ),
    dict(
        name='eriks_game_2', display_name= "Mystery Word Game_2", app_sequence=['justone_welcome', 'justone_survey'], num_demo_participants=2, ),
    ]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = ['incentive']
SESSION_FIELDS = []

SESSION_CONFIGS

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """
Here are some oTree games.
"""

SECRET_KEY = '{{ secret_key }}'

INSTALLED_APPS = ['otree']


