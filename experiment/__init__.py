from otree.api import *
import re
import ast
import random
import numpy as np
import scipy.spatial.distance
from concurrent.futures import ThreadPoolExecutor
import fasttext

from settings import PARTICIPANT_FIELDS

doc = """
Ihre App-Beschreibung
"""

class C(BaseConstants):
    NAME_IN_URL = 'mabella_experiment'
    NUM_ROUNDS = 1
    MYSTERY_WORDS = ['Raum','Taube', 'Golf', 'Elektrizitaet', 'Ende', 'Sombrero']
    LANGUAGE_CODE = 'de'
    PLAYERS_PER_GROUP = None
    TABOO_WORDS = [
        ['Hotel', 'Wohnen', 'Zimmer'],
        ['Vogel', 'Gurren', 'Fliegen'],
        ['Volkswagen', 'Schlaeger', 'Par'],
        ['Strom', 'Tesla','Spannung'],
        ['Finale', 'Schluss','Anfang'],
        ['Hut', 'Mexiko', 'Kopfbedeckung']
    ]
    STEM_WORDS = [
        ['raum', 'raeum', 'zimmer', 'hotel', 'wohn'], 
        ['taub', 'taeub', 'gurr', 'flieg', 'flug', 'fluege', 'vogel', 'voegel', 'bot', 'fried'],
        ['golf', 'vw', 'wagen', 'volk', 'voelk', 'schlaeg', 'schlag', 'par', 'birdie', 'mini'],
        ['elektr', 'strom', 'tesla', 'edison', 'spann', 'stati'],  
        ['end', 'final', 'schluss', 'stopp', 'tot', 'tod', 'an', 'fang', 'schluess', 'faeng'],
        ['sombrero', 'hut', 'huet', 'mexik', 'mexic', 'kopf', 'koepf', 'bedeck', 'mariach', 'kremp']
    ]
    ACHIEVEMENTS= ['Bildende_Kunst', 'Musik', 'Tanz', 'Architektur', 'Literatur', 'Humor', 'Erfindungen', 'Wissenschaftliche_Entdeckungen', 'Theater_und_Film', 'Kochen']

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    quality = models.IntegerField(initial=0)
    quantity = models.IntegerField(initial=0)
    originality = models.FloatField(initial=0)

class Player(BasePlayer):        
    guess1 = models.StringField(label="Ihre Vermutung:", initial='', max_length=18, blank=True)
    guess2 = models.StringField(label="Ihre Vermutung:", initial='', max_length=18)
    guess3 = models.StringField(label="Ihre Vermutung:", initial='', max_length=18)
    correct_guess1 = models.BooleanField(field_maybe_empty=True)
    correct_guess2 = models.BooleanField(field_maybe_empty=True)
    correct_guess3 = models.BooleanField(field_maybe_empty=True)
    score = models.IntegerField()
    result = models.StringField()
    player_role = models.StringField()
    player_role2 = models.StringField()
    incentive = models.IntegerField()
    understandHin_1 = models.StringField(choices=[['false', 'Länge, Relevanz, Originalität'],['false', 'Geschwindigkeit, Anzahl, Vielfalt'],['true', 'Quantität, Qualität, Originalität']], label='<b>Frage 1:</b> Welche drei Kriterien werden zur Bewertung der Hinweispaare herangezogen?', widget=widgets.RadioSelect, blank=True)
    understandHin_2 = models.StringField(choices=[['false','Zwei'],['true', 'Drei'],['false', 'Fünf']], label='<b>Frage 2:</b> Wie viele Spielerinnen und Spieler bilden zusammen eine Gruppe?', widget=widgets.RadioSelect, blank=True)
    understandHin_3 = models.StringField(choices=[['false', 'Time'], ['false', 'Zeitpunkt'],['false', 'Zeeeit'],['true', 'keiner der oben genannten Hinweise']], label='<b>Frage 3:</b> Welcher Hinweis wäre gültig in einem Hinweispaar für das geheime Wort "Zeit"?', widget=widgets.RadioSelect, blank=True)
    understandHin_4 = models.StringField(choices=[['false', 'Es wird für die Bewertung berücksichtigt'], ['true', 'Es wird entfernt und nicht gewertet'],['false', 'Es wird für die nächste Runde gespeichert']], label='<b>Frage 4:</b> Was passiert, wenn ein Hinweispaar eines Gruppenmitglieds ein Tabuwort enthält?', widget=widgets.RadioSelect, blank=True)
    understandHin_6_Quality = models.StringField(choices=[['false', 'Anhand der Anzahl der generierten Paare'], ['false', 'Anhand eines Algorithmus, der die semantische Distanz bewertet'],['true', 'Anhand der Anzahl der Versuche, die eine zufällig ausgewählte Person benötigt, um das geheime Wort zu erraten']], label='<b>Frage 6: </b>Wie wird die Qualität eines finalen Hinweispaars gemessen?', widget=widgets.RadioSelect, blank=True)
    understandHin_6_Quantity = models.StringField(choices=[['true', 'Anhand der Anzahl der generierten Paare'], ['false', 'Anhand eines Algorithmus, der die semantische Distanz bewertet'],['false', 'Anhand der Anzahl der Versuche, die eine zufällig ausgewählte Person benötigt, um das geheime Wort zu erraten']], label='<b>Frage 6: </b>Wie wird die Quantität der Hinweispaare gemessen?', widget=widgets.RadioSelect, blank=True)
    understandHin_6_Originality= models.StringField(choices=[['false', 'Anhand der Anzahl der generierten Paare'], ['true', 'Anhand eines Algorithmus, der die semantische Distanz bewertet'],['false', 'Anhand der Anzahl der Versuche, die eine zufällig ausgewählte Person benötigt, um das geheime Wort zu erraten']], label='<b>Frage 6: </b>Wie wird die Originalität eines finalen Hinweispaars gemessen?', widget=widgets.RadioSelect, blank=True)
    understandHin_7_Quality = models.StringField(choices=[['false', 'Keine Punkte'], ['true', '3 Punkte'],['false', '1 Punkt']], label='<b>Frage 7:</b> Was passiert, wenn das geheime Wort im 1. Versuch anhand Ihres finalen Hinweispaars erraten wird?', widget=widgets.RadioSelect, blank=True)
    understandHin_5_Quantity =  models.StringField(choices=[['false', '13€ fix'],['true', '5€ fix plus bis zu 15€ Bonus für die meisten generierten Hinweispaare'],['false', '5€ fix plus bis zu 15€ Bonus für die qualitativ hochwertigsten Hinweispaare'],['false','5€ fix plus bis zu 15€ Bonus für die originellsten Hinweispaare']], label='<b>Frage 5:</b> Wie viel Geld können Sie maximal bei <b><span style="color: red;">Wortaufgabe 1</span></b> verdienen?', widget=widgets.RadioSelect, blank=True)
    understandHin_5_Quality = models.StringField(choices=[['false', '13€ fix'],['false', '5€ fix plus bis zu 15€ Bonus für die meisten generierten Hinweispaare'],['true', '5€ fix plus bis zu 15€ Bonus für die qualitativ hochwertigsten Hinweispaare'],['false','5€ fix plus bis zu 15€ Bonus für die originellsten Hinweispaare']], label='<b>Frage 5:</b> Wie viel Geld können Sie maximal bei <b><span style="color: red;">Wortaufgabe 1</span></b> verdienen?', widget=widgets.RadioSelect, blank=True)
    understandHin_5_Originality = models.StringField(choices=[['false', '13€ fix'],['false', '5€ fix plus bis zu 15€ Bonus für die meisten generierten Hinweispaare'],['false', '5€ fix plus bis zu 15€ Bonus für die qualitativ hochwertigsten Hinweispaare'],['true','5€ fix plus bis zu 15€ Bonus für die originellsten Hinweispaare']], label='<b>Frage 5:</b> Wie viel Geld können Sie maximal bei <b><span style="color: red;">Wortaufgabe 1</span></b> verdienen?', widget=widgets.RadioSelect, blank=True)
    understandHin_5_Control = models.StringField(choices=[['true', '13€ fix'],['false', '5€ fix plus bis zu 15€ Bonus für die meisten generierten Hinweispaare'],['false', '5€ fix plus bis zu 15€ Bonus für die qualitativ hochwertigsten Hinweispaare'],['false','5€ fix plus bis zu 15€ Bonus für die originellsten Hinweispaare']], label='<b>Frage 5:</b> Wie viel Geld können Sie maximal bei <b><span style="color: red;">Wortaufgabe 1</span></b> verdienen?', widget=widgets.RadioSelect, blank=True)
    understandRat_1 = models.StringField(choices=[['false', 'Unbegrenzt viele Versuche'],['true', 'Drei Versuche'],['false', 'Nur einen Versuch']], label='<b>Frage 1:</b> Wie viele Versuche haben Sie, um ein geheimes Wort zu erraten?', widget=widgets.RadioSelect, blank=True)
    understandRat_2 = models.StringField(choices=[['false', '1 Punkt'],['false', '2 Punkte'],['true', '3 Punkte']], label='<b>Frage 2:</b> Wie viele Punkte erhalten Sie, wenn das geheime Wort direkt im 1. Versuch erraten?', widget=widgets.RadioSelect, blank=True)
    understandRat_3 = models.StringField(choices=[['true', '20€'], ['false', '15€'],['false', '10€']], label='<b>Frage 3:</b> Wie viel Geld können Sie maximal bei <b><span style="color: red;">Wortaufgabe 1</span></b> verdienen?', widget=widgets.RadioSelect, blank=True)
    understandRat_4 = models.StringField(choices=[['false', '5 Wörter'],['true', '8 Wörter'],['false', '10 Wörter']], label='<b>Frage 4:</b> Wie viele geheime Wörter können Sie insgesamt erraten?', widget=widgets.RadioSelect, blank=True)
    understandRat_5 = models.StringField(choices=[['true', 'Vom Vergleich Ihrer erreichten Punkte mit den anderen Ratenden'],['false', 'Von der Anzahl der Hinweispaare, die Sie erstellt haben'],['false', 'Von der Qualität Ihrer Bewertung der Hinweispaare']], label='<b>Frage 5:</b> Wovon hängt die Höhe des Bonus ab?', widget=widgets.RadioSelect, blank=True)
    Bildende_Kunst = models.BooleanField(blank=True, initial=False)
    Musik = models.BooleanField(blank=True, initial=False)
    Tanz = models.BooleanField(blank=True, initial=False)
    Architektur = models.BooleanField(blank=True, initial=False)
    Literatur = models.BooleanField(blank=True, initial=False)
    Humor = models.BooleanField(blank=True, initial=False)
    Erfindungen = models.BooleanField(blank=True, initial=False)
    Wissenschaftliche_Entdeckungen = models.BooleanField(blank=True, initial=False)
    Theater_und_Film = models.BooleanField(blank=True, initial=False)
    Kochen = models.BooleanField(blank=True, initial=False)
    Bildende_Kunst_2_1 = models.IntegerField(blank=True)
    Bildende_Kunst_2_2 = models.IntegerField(blank=True)
    Bildende_Kunst_2_3 = models.IntegerField(blank=True)
    Bildende_Kunst_2_4 = models.IntegerField(blank=True)
    Bildende_Kunst_2_5 = models.IntegerField(blank=True)
    Bildende_Kunst_2_6 = models.IntegerField(blank=True)
    Bildende_Kunst_2_7 = models.IntegerField(blank=True)
    Musik_2_1 = models.IntegerField(blank=True) 
    Musik_2_2 = models.IntegerField(blank=True)
    Musik_2_3 = models.IntegerField(blank=True)
    Musik_2_4 = models.IntegerField(blank=True)
    Musik_2_5 = models.IntegerField(blank=True)
    Musik_2_6 = models.IntegerField(blank=True)
    Musik_2_7 = models.IntegerField(blank=True) 
    Tanz_2_1 = models.IntegerField(blank=True)
    Tanz_2_2 = models.IntegerField(blank=True)
    Tanz_2_3 = models.IntegerField(blank=True)
    Tanz_2_4 = models.IntegerField(blank=True)
    Tanz_2_5 = models.IntegerField(blank=True)
    Tanz_2_6 = models.IntegerField(blank=True)
    Tanz_2_7 = models.IntegerField(blank=True)
    Architektur_2_1 = models.IntegerField(blank=True)
    Architektur_2_2 = models.IntegerField(blank=True)
    Architektur_2_3 = models.IntegerField(blank=True)
    Architektur_2_4 = models.IntegerField(blank=True)
    Architektur_2_5 = models.IntegerField(blank=True)
    Architektur_2_6 = models.IntegerField(blank=True)
    Architektur_2_7 = models.IntegerField(blank=True)
    Literatur_2_1 = models.IntegerField(blank=True)
    Literatur_2_2 = models.IntegerField(blank=True)
    Literatur_2_3 = models.IntegerField(blank=True)
    Literatur_2_4 = models.IntegerField(blank=True)
    Literatur_2_5 = models.IntegerField(blank=True)
    Literatur_2_6 = models.IntegerField(blank=True)
    Literatur_2_7 = models.IntegerField(blank=True)
    Humor_2_1 = models.IntegerField(blank=True)
    Humor_2_2 = models.IntegerField(blank=True)
    Humor_2_3 = models.IntegerField(blank=True)
    Humor_2_4 = models.IntegerField(blank=True)
    Humor_2_5 = models.IntegerField(blank=True)
    Humor_2_6 = models.IntegerField(blank=True)
    Humor_2_7 = models.IntegerField(blank=True)
    Erfindungen_2_1 = models.IntegerField(blank=True)
    Erfindungen_2_2 = models.IntegerField(blank=True)
    Erfindungen_2_3 = models.IntegerField(blank=True)
    Erfindungen_2_4 = models.IntegerField(blank=True)
    Erfindungen_2_5 = models.IntegerField(blank=True)
    Erfindungen_2_6 = models.IntegerField(blank=True)
    Erfindungen_2_7 = models.IntegerField(blank=True)
    Wissenschaftliche_Entdeckungen_2_1 = models.IntegerField(blank=True)
    Wissenschaftliche_Entdeckungen_2_2 = models.IntegerField(blank=True)
    Wissenschaftliche_Entdeckungen_2_3 = models.IntegerField(blank=True)
    Wissenschaftliche_Entdeckungen_2_4 = models.IntegerField(blank=True)
    Wissenschaftliche_Entdeckungen_2_5 = models.IntegerField(blank=True)
    Wissenschaftliche_Entdeckungen_2_6 = models.IntegerField(blank=True)
    Wissenschaftliche_Entdeckungen_2_7 = models.IntegerField(blank=True)
    Theater_und_Film_2_1 = models.IntegerField(blank=True)
    Theater_und_Film_2_2 = models.IntegerField(blank=True)
    Theater_und_Film_2_3 = models.IntegerField(blank=True)
    Theater_und_Film_2_4 = models.IntegerField(blank=True)
    Theater_und_Film_2_5 = models.IntegerField(blank=True)
    Theater_und_Film_2_6 = models.IntegerField(blank=True)
    Theater_und_Film_2_7 = models.IntegerField(blank=True)
    Kochen_2_1 = models.IntegerField(blank=True)
    Kochen_2_2 = models.IntegerField(blank=True)
    Kochen_2_3 = models.IntegerField(blank=True)
    Kochen_2_4 = models.IntegerField(blank=True)
    Kochen_2_5 = models.IntegerField(blank=True)
    Kochen_2_6 = models.IntegerField(blank=True)
    Kochen_2_7 = models.IntegerField(blank=True)
    Idea1 = models.StringField(label= '', initial='', blank=True, max_length=18)
    Idea2 = models.StringField(label= '', initial='', blank=True, max_length=18)
    Idea3 = models.StringField(label= '', initial='', blank=True, max_length=18)
    Idea4 = models.StringField(label= '', initial='', blank=True, max_length=18)
    Idea5 = models.StringField(label= '', initial='', blank=True, max_length=18)
    Idea6 = models.StringField(label= '', initial='', blank=True, max_length=18)
    Idea7 = models.StringField(label= '', initial='', blank=True, max_length=18)
    Idea8 = models.StringField(label= '', initial='', blank=True, max_length=18)
    Idea9 = models.StringField(label= '', initial='', blank=True, max_length=18)
    Idea10 = models.StringField(label= '', initial='', blank=True, max_length=18)
    Idea11 = models.StringField(label= '', initial='', blank=True, max_length=18)
    Idea12 = models.StringField(label= '', initial='', blank=True, max_length=18)
    Idea13 = models.StringField(label= '', initial='', blank=True, max_length=18)
    Idea14 = models.StringField(label= '', initial='', blank=True, max_length=18)
    Idea15 = models.StringField(label= '', initial='', blank=True, max_length=18)
    Idea16 = models.StringField(label= '', initial='', blank=True, max_length=18)
    Idea17 = models.StringField(label= '', initial='', blank=True, max_length=18)
    Idea18 = models.StringField(label= '', initial='', blank=True, max_length=18)
    Idea19 = models.StringField(label= '', initial='', blank=True, max_length=18)
    Idea20 = models.StringField(label= '', initial='', blank=True, max_length=18)
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
    gender = models.IntegerField(choices=[[1, 'Männlich'],[2, 'Weiblich'],[3, 'Divers'],], label='<b>2. </b>Geschlecht:', widget=widgets.RadioSelectHorizontal, blank=False)
    age = models.IntegerField(min=18, max=100, label='<b>1. </b>Alter:', blank=False)
    study = models.StringField(choices=[['Geisteswissenschaften', 'Geisteswissenschaften'],['Sport', 'Sport'],['Rechts-, Wirtschafts- und Sozialwissenschaften', 'Rechts-, Wirtschafts- und Sozialwissenschaften'],['Mathematik, Naturwissenschaften', 'Mathematik, Naturwissenschaften'],['Humanmedizin, Gesundheitswissenschaften', 'Humanmedizin, Gesundheitswissenschaften'],['Agrar-, Forst- und Ernährungswissenschaften, Veterinärmedizin', 'Agrar-, Forst- und Ernährungswissenschaften, Veterinärmedizin'], ['Ingenieurwissenschaften', 'Ingenieurwissenschaften'],['Kunst, Kunstwissenschaft', 'Kunst, Kunstwissenschaft'],['Sonstiges', 'Sonstiges'],], label='<b>3. </b>Studienbereich:', widget=widgets.RadioSelectHorizontal, blank=False)
    german = models.IntegerField(choices=[[1, 'Muttersprache'],[2, 'Sehr gut'],[3, 'Gut'],[4, 'Es geht'],[5, 'Eher schlecht'],[6, 'Gar nicht'],], label='<b>4. </b>Wie gut können Sie die deutsche Sprache lesen und schreiben?', widget=widgets.RadioSelectHorizontal, blank=False)
    risk = models.FloatField(min=0, max=100, label='<b>5. </b>Wie viel Euro würden Sie investieren?', blank=False)
    ambiguity = models.FloatField(min=0, max=100, label='<b>6. </b>Wie viel Euro würden Sie investieren?', blank=False)
    general_motivation1 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>17. </b>Ich genieße es, mich mit anderen zu messen.', widget=widgets.RadioSelectHorizontal, blank=False)
    general_motivation2 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>18. </b>Ich erbringe bessere Leistungen, wenn ich gegen andere antrete.', widget=widgets.RadioSelectHorizontal, blank=False)
    general_group1 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>19. </b>Ich arbeite grundsätzlich lieber in einer Gruppe als alleine.', widget=widgets.RadioSelectHorizontal, blank=True)
    general_group2 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>20. </b>Menschen in einer Gruppe sind in der Regel produktiver als Menschen, die allein arbeiten.', widget=widgets.RadioSelectHorizontal, blank=True)
    general_group3 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>21. </b>Menschen in einer Gruppe sollten bereit sein, Opfer zu bringen, um das Wohl der Gruppe zu fördern. ', widget=widgets.RadioSelectHorizontal, blank=True)
    cognitive1 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>12. </b>Kreatives Arbeiten ist hauptsächlich „Trial and Error“ ohne präzises Ziel und detaillierten Plan.', widget=widgets.RadioSelectHorizontal, blank=False)
    cognitive2 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>13. </b>Ich finde es langweilig, immer die gleichen alten Gesichter zu sehen.', widget=widgets.RadioSelectHorizontal, blank=False)
    cognitive3 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>14. </b>Ich arbeite kreativ, um etwas zu produzieren, das einen Zweck erfüllt.', widget=widgets.RadioSelectHorizontal, blank=False)
    cognitive4 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>15. </b>Meine neueren Ideen unterscheiden sich stark von meinen älteren Ideen.', widget=widgets.RadioSelectHorizontal, blank=False)
    cognitive5 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>16. </b>Ich erkunde gerne fremde Städte auf eigene Faust, auch auf die Gefahr hin, mich zu verlaufen.', widget=widgets.RadioSelectHorizontal, blank=False)
    invalid = models.BooleanField()
    missing = models.BooleanField()
    guess_missing = models.BooleanField()
    quantity = models.IntegerField()
    originality = models.FloatField()
    invalid_DAT = models.BooleanField()
    pair1 = models.StringField(initial='')
    pair2 = models.StringField(initial='')
    pair3 = models.StringField(initial='')
    pair4 = models.StringField(initial='')
    pair5 = models.StringField(initial='')
    pair6 = models.StringField(initial='')
    pair7 = models.StringField(initial='')
    pair8 = models.StringField(initial='')
    pair9 = models.StringField(initial='')
    pair10 = models.StringField(initial='')
    pair1after = models.StringField(initial='')
    pair2after = models.StringField(initial='')
    pair3after = models.StringField(initial='')
    pair4after = models.StringField(initial='')
    pair5after = models.StringField(initial='')
    pair6after = models.StringField(initial='')
    pair7after = models.StringField(initial='')
    pair8after = models.StringField(initial='')
    pair9after = models.StringField(initial='')
    pair10after = models.StringField(initial='')
    rating_before1 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    rating_before2 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    rating_before3 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    rating_before4 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    rating_before5 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    rating_before6 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    rating_before7 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    rating_before8 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    rating_before9 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    rating_before10 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    rating_before11 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    rating_before12 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    rating_before13 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    rating_before14 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    rating_before15 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    rating_before16 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    rating_before17 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    rating_before18 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    rating_before19 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    rating_before20 = models.StringField(widget=widgets.RadioSelectHorizontal, choices=[['&#128077;', '&#128077;'],['&#128078;', '&#128078;'],], label='', blank=True, initial='')
    discussion1 = models.StringField(label= '', initial='', blank=True, max_length=18)
    discussion2 = models.StringField(label= '', initial='', blank=True, max_length=18)
    discussion3 = models.StringField(label= '', initial='', blank=True, max_length=18)
    discussion4 = models.StringField(label= '', initial='', blank=True, max_length=18)
    discussion5 = models.StringField(label= '', initial='', blank=True, max_length=18)
    discussion6 = models.StringField(label= '', initial='', blank=True, max_length=18)
    discussion7 = models.StringField(label= '', initial='', blank=True, max_length=18)
    discussion8 = models.StringField(label= '', initial='', blank=True, max_length=18)
    discussion9 = models.StringField(label= '', initial='', blank=True, max_length=18)
    discussion10 = models.StringField(label= '', initial='', blank=True, max_length=18)
    discussion11 = models.StringField(label= '', initial='', blank=True, max_length=18)
    discussion12 = models.StringField(label= '', initial='', blank=True, max_length=18)
    discussion13 = models.StringField(label= '', initial='', blank=True, max_length=18)
    discussion14 = models.StringField(label= '', initial='', blank=True, max_length=18)
    discussion15 = models.StringField(label= '', initial='', blank=True, max_length=18)
    discussion16 = models.StringField(label= '', initial='', blank=True, max_length=18)
    discussion17 = models.StringField(label= '', initial='', blank=True, max_length=18)
    discussion18 = models.StringField(label= '', initial='', blank=True, max_length=18)
    discussion19 = models.StringField(label= '', initial='', blank=True, max_length=18)
    discussion20 = models.StringField(label= '', initial='', blank=True, max_length=18)
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
    replace_word10 = models.StringField(widget = widgets.RadioSelectHorizontal, choices=[['erste', 'erste Wort durch:'],['zweite', 'zweite Wort durch:'],], label='Ersetze das', blank=True, initial='')
    replace_word11 = models.StringField(widget = widgets.RadioSelectHorizontal, choices=[['erste', 'erste Wort durch:'],['zweite', 'zweite Wort durch:'],], label='Ersetze das', blank=True, initial='')
    replace_word12 = models.StringField(widget = widgets.RadioSelectHorizontal, choices=[['erste', 'erste Wort durch:'],['zweite', 'zweite Wort durch:'],], label='Ersetze das', blank=True, initial='')
    replace_word13 = models.StringField(widget = widgets.RadioSelectHorizontal, choices=[['erste', 'erste Wort durch:'],['zweite', 'zweite Wort durch:'],], label='Ersetze das', blank=True, initial='')
    replace_word14 = models.StringField(widget = widgets.RadioSelectHorizontal, choices=[['erste', 'erste Wort durch:'],['zweite', 'zweite Wort durch:'],], label='Ersetze das', blank=True, initial='')
    replace_word15 = models.StringField(widget = widgets.RadioSelectHorizontal, choices=[['erste', 'erste Wort durch:'],['zweite', 'zweite Wort durch:'],], label='Ersetze das', blank=True, initial='')
    replace_word16 = models.StringField(widget = widgets.RadioSelectHorizontal, choices=[['erste', 'erste Wort durch:'],['zweite', 'zweite Wort durch:'],], label='Ersetze das', blank=True, initial='')
    replace_word17 = models.StringField(widget = widgets.RadioSelectHorizontal, choices=[['erste', 'erste Wort durch:'],['zweite', 'zweite Wort durch:'],], label='Ersetze das', blank=True, initial='')
    replace_word18 = models.StringField(widget = widgets.RadioSelectHorizontal, choices=[['erste', 'erste Wort durch:'],['zweite', 'zweite Wort durch:'],], label='Ersetze das', blank=True, initial='')
    replace_word19 = models.StringField(widget = widgets.RadioSelectHorizontal, choices=[['erste', 'erste Wort durch:'],['zweite', 'zweite Wort durch:'],], label='Ersetze das', blank=True, initial='')
    replace_word20 = models.StringField(widget = widgets.RadioSelectHorizontal, choices=[['erste', 'erste Wort durch:'],['zweite', 'zweite Wort durch:'],], label='Ersetze das', blank=True, initial='')
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
    pair_feedback13 = models.StringField(label= '', initial='', blank=True)
    pair_feedback14 = models.StringField(label= '', initial='', blank=True)
    pair_feedback15 = models.StringField(label= '', initial='', blank=True)
    pair_feedback16 = models.StringField(label= '', initial='', blank=True)
    pair_feedback17 = models.StringField(label= '', initial='', blank=True)
    pair_feedback18 = models.StringField(label= '', initial='', blank=True)
    pair_feedback19 = models.StringField(label= '', initial='', blank=True)
    pair_feedback20 = models.StringField(label= '', initial='', blank=True)
    vote = models.StringField(initial='')
    vote_group = models.StringField(initial='')
    pairsafter = models.StringField(label= '', initial='', blank=True)
    number_pairs = models.IntegerField()
    before_quantity = models.IntegerField()
    before_missing = models.BooleanField()
    before_invalid = models.IntegerField()
    after_invalid = models.IntegerField()
    check_invalid_1 = models.StringField(blank=True)
    check_invalid_2 = models.StringField(blank=True)
    check_invalid_3 = models.StringField(blank=True)
    check_invalid_4 = models.StringField(blank=True)
    check_invalid_5 = models.StringField(blank=True)
    check_invalid_6 = models.StringField(blank=True)
    check_invalid_7 = models.StringField(blank=True)
    check_invalid_8 = models.StringField(blank=True)
    check_invalid_9 = models.StringField(blank=True)
    check_invalid_10 = models.StringField(blank=True)
    check_invalid_11 = models.StringField(blank=True)
    check_invalid_12 = models.StringField(blank=True)
    check_invalid_13 = models.StringField(blank=True)
    check_invalid_14 = models.StringField(blank=True)
    check_invalid_15 = models.StringField(blank=True)
    check_invalid_16 = models.StringField(blank=True)
    check_invalid_17 = models.StringField(blank=True)
    check_invalid_18 = models.StringField(blank=True)
    check_invalid_19 = models.StringField(blank=True)
    check_invalid_20 = models.StringField(blank=True)
    check_invalid_21 = models.StringField(blank=True)
    check_invalid_22 = models.StringField(blank=True)
    check_invalid_23 = models.StringField(blank=True)
    check_invalid_24 = models.StringField(blank=True)
    check_invalid_25 = models.StringField(blank=True)
    check_invalid_26 = models.StringField(blank=True)
    check_invalid_27 = models.StringField(blank=True)
    check_invalid_28 = models.StringField(blank=True)
    check_invalid_29 = models.StringField(blank=True)
    check_invalid_30 = models.StringField(blank=True)
    group_number_check = models.IntegerField()
    group_number_guess = models.IntegerField()
    group_number_rating = models.IntegerField()
    usefulness_1 = models.StringField(blank=True)
    usefulness_2 = models.StringField(blank=True)
    usefulness_3 = models.StringField(blank=True)
    usefulness_4 = models.StringField(blank=True)
    usefulness_5 = models.StringField(blank=True)
    usefulness_6 = models.StringField(blank=True)
    usefulness_7 = models.StringField(blank=True)
    usefulness_8 = models.StringField(blank=True)
    usefulness_9 = models.StringField(blank=True)
    usefulness_10 = models.StringField(blank=True)
    usefulness_11 = models.StringField(blank=True)
    usefulness_12 = models.StringField(blank=True)
    usefulness_13 = models.StringField(blank=True)
    usefulness_14 = models.StringField(blank=True)
    usefulness_15 = models.StringField(blank=True)
    usefulness_16 = models.StringField(blank=True)
    usefulness_17 = models.StringField(blank=True)
    usefulness_18 = models.StringField(blank=True)
    usefulness_19 = models.StringField(blank=True)
    usefulness_20 = models.StringField(blank=True)
    usefulness_21 = models.StringField(blank=True)
    usefulness_22 = models.StringField(blank=True)
    usefulness_23 = models.StringField(blank=True)
    usefulness_24 = models.StringField(blank=True)
    usefulness_25 = models.StringField(blank=True)
    usefulness_26 = models.StringField(blank=True)
    usefulness_27 = models.StringField(blank=True)
    usefulness_28 = models.StringField(blank=True)
    usefulness_29 = models.StringField(blank=True)
    usefulness_30 = models.StringField(blank=True)
    originality_1 = models.StringField(blank=True)
    originality_2 = models.StringField(blank=True)
    originality_3 = models.StringField(blank=True)
    originality_4 = models.StringField(blank=True)
    originality_5 = models.StringField(blank=True)
    originality_6 = models.StringField(blank=True)
    originality_7 = models.StringField(blank=True)
    originality_8 = models.StringField(blank=True)
    originality_9 = models.StringField(blank=True)
    originality_10 = models.StringField(blank=True)
    originality_11 = models.StringField(blank=True)
    originality_12 = models.StringField(blank=True)
    originality_13 = models.StringField(blank=True)
    originality_14 = models.StringField(blank=True)
    originality_15 = models.StringField(blank=True)
    originality_16 = models.StringField(blank=True)
    originality_17 = models.StringField(blank=True)
    originality_18 = models.StringField(blank=True)
    originality_19 = models.StringField(blank=True)
    originality_20 = models.StringField(blank=True)
    originality_21 = models.StringField(blank=True)
    originality_22 = models.StringField(blank=True)
    originality_23 = models.StringField(blank=True)
    originality_24 = models.StringField(blank=True)
    originality_25 = models.StringField(blank=True)
    originality_26 = models.StringField(blank=True)
    originality_27 = models.StringField(blank=True)
    originality_28 = models.StringField(blank=True)
    originality_29 = models.StringField(blank=True)
    originality_30 = models.StringField(blank=True)
    creativity_1 = models.StringField(blank=True)
    creativity_2 = models.StringField(blank=True)
    creativity_3 = models.StringField(blank=True)
    creativity_4 = models.StringField(blank=True)
    creativity_5 = models.StringField(blank=True)
    creativity_6 = models.StringField(blank=True)
    creativity_7 = models.StringField(blank=True)
    creativity_8 = models.StringField(blank=True)
    creativity_9 = models.StringField(blank=True)
    creativity_10 = models.StringField(blank=True)
    creativity_11 = models.StringField(blank=True)
    creativity_12 = models.StringField(blank=True)
    creativity_13 = models.StringField(blank=True)
    creativity_14 = models.StringField(blank=True)
    creativity_15 = models.StringField(blank=True)
    creativity_16 = models.StringField(blank=True)
    creativity_17 = models.StringField(blank=True)
    creativity_18 = models.StringField(blank=True)
    creativity_19 = models.StringField(blank=True)
    creativity_20 = models.StringField(blank=True)
    creativity_21 = models.StringField(blank=True)
    creativity_22 = models.StringField(blank=True)
    creativity_23 = models.StringField(blank=True)
    creativity_24 = models.StringField(blank=True)
    creativity_25 = models.StringField(blank=True)
    creativity_26 = models.StringField(blank=True)
    creativity_27 = models.StringField(blank=True)
    creativity_28 = models.StringField(blank=True)
    creativity_29 = models.StringField(blank=True)
    creativity_30 = models.StringField(blank=True)
    number_pairs_after = models.IntegerField()
    circle_overlap = models.FloatField(label="Overlap Percentage",blank=True)
    explanation = models.LongStringField(label='<b>5. </b>Bitte beschreiben Sie in Stichpunkten, warum sich Ihre Gruppe final für dieses Hinweispaar entschieden hat. (optional)', blank=True, max_length=500)
    subjective_originality = models.IntegerField(choices=[0, 1, 2, 3 ,4, 5, 6, 7, 8, 9, 10],label = '<b>3. </b>Bitte bewerten Sie ihr finales Hinweispaar auf einer Skala von 0 bis 10, wie <b>originell und neu</b> Sie es finden. <br> (0 = überhaupt nicht originell, 10 = sehr originell)', widget=widgets.RadioSelectHorizontal, blank= False)
    subjective_quality = models.IntegerField(choices=[0, 1, 2, 3 ,4, 5, 6, 7, 8, 9, 10,],label = '<b>4. </b>Bitte bewerten Sie ihr finales Hinweispaar auf einer Skala von 0 bis 10, wie <b>nützlich</b> es zur Erratung des geheimen Wortes ist. <br> (0 = überhaupt nicht nützlich, 10 = sehr nützlich)', widget=widgets.RadioSelectHorizontal, blank= False)
    rat1 = models.StringField(label= '', initial='', blank=True, max_length=18)
    rat2 = models.StringField(label= '', initial='', blank=True, max_length=18)
    rat3 = models.StringField(label= '', initial='', blank=True, max_length=18)
    rat4 = models.StringField(label= '', initial='', blank=True, max_length=18)
    rat5 = models.StringField(label= '', initial='', blank=True, max_length=18)
    creative_self1 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], widget=widgets.RadioSelectHorizontal, blank=False, label = '<b> 7. </b>Ich denke, dass ich eine kreative Person bin.')
    creative_self2 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], widget=widgets.RadioSelectHorizontal, blank=False, label = '<b> 8. </b>Meine Vorstellungskraft und mein Einfallsreichtum unterscheiden mich von meinen Freunden.')
    creative_self3 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], widget=widgets.RadioSelectHorizontal, blank=False, label = '<b> 9. </b>Es ist mir wichtig, eine kreative Person zu sein.')
    creative_self4 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], widget=widgets.RadioSelectHorizontal, blank=False, label = '<b> 10. </b>Ich weiß, dass ich auch komplizierte Probleme effizient lösen kann.')
    creative_self5 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], widget=widgets.RadioSelectHorizontal, blank=False, label = '<b> 11. </b>Ich bin gut darin, kreative Lösungen für Probleme zu finden.')
    dictator_game = models.CurrencyField(max=10, min=0, blank=False, label= 'Wie viel von Ihren 10€ möchten Sie an den Empfänger überweisen?')
    AUT = models.LongStringField(label='Geben Sie jeweils eine alternative Verwendungsmöglichkeit <b>pro Zeile</b> an.', blank=True, max_length=800)
    AUT2 = models.LongStringField(label='Geben Sie jeweils eine alternative Verwendungsmöglichkeit <b>pro Zeile</b> an.', blank=True, max_length=800)
    quality_score = models.IntegerField(initial=0)
    communication = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>1. </b>Die Kommunikation in meiner Gruppe war effektiv.', widget=widgets.RadioSelectHorizontal, blank=False)
    decision = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>2. </b>Wir haben am Ende das beste Hinweispaar ausgewählt.', widget=widgets.RadioSelectHorizontal, blank=False)
    ideagen1 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>1. </b>Es fiel mir schwer, nützliche Hinweispaare zu generieren.', widget=widgets.RadioSelectHorizontal, blank=True)
    ideagen2 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>2. </b>Es fiel mir schwer, originelle Hinweispaare zu generieren.', widget=widgets.RadioSelectHorizontal, blank=True)
    ideagen3 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>3. </b>Es fiel mir schwer, viele Hinweispaare zu generieren.', widget=widgets.RadioSelectHorizontal, blank=True)
    ideagen4 = models.LongStringField(label='<b>4. </b>Welche Strategie haben Sie bei der Ideengenerierung verfolgt?', initial = '', max_length=500, blank=True)
    feedback1 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>5. </b>Ich schätze mein gegebenes Feedback als hilfreich ein.', widget=widgets.RadioSelectHorizontal, blank=True)
    feedback2 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>6. </b>Das empfangene Feedback hat mir geholfen.', widget=widgets.RadioSelectHorizontal, blank=True)
    feedback3 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>7. </b>Die Bereitschaft meiner Gruppenmitglieder, Feedback anzunehmen, war groß.', widget=widgets.RadioSelectHorizontal, blank=True)
    feedback4 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>8. </b>Ich habe mich und meine Ideen wertgeschätzt gefühlt.', widget=widgets.RadioSelectHorizontal, blank=True)
    group1 = models.IntegerField(choices = [[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>9. </b>Unsere Zusammenarbeit in der Gruppe war produktiv.', widget=widgets.RadioSelectHorizontal, blank=True)
    group2 = models.IntegerField(choices = [[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>10. </b>Eine Person war  dominant in der Führung der Gruppe.', widget=widgets.RadioSelectHorizontal, blank=True) 
    group3 = models.IntegerField(choices = [[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>11. </b>Damit eine Gruppe eine gute Entscheidung treffen kann, muss immer jemand die Führung übernehmen.', widget=widgets.RadioSelectHorizontal, blank=True)
    group4 = models.IntegerField(choices = [[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>12. </b>Meine Gruppe hat einen echten Teamgeist entwickelt.', widget=widgets.RadioSelectHorizontal, blank=True)
    group5 = models.IntegerField(choices = [[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>13. </b>Unsere individuellen Fähigkeiten und Perspektiven haben sich gut ergänzt.', widget=widgets.RadioSelectHorizontal, blank=True)
    group6 = models.IntegerField(choices = [[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>14. </b>Alle Gruppenmitglieder haben sich angestrengt.', widget=widgets.RadioSelectHorizontal, blank=True)
    group7 = models.IntegerField(choices = [[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>15. </b>Alle Gruppenmitglieder haben gleich viel beigetragen.', widget=widgets.RadioSelectHorizontal, blank=True)
    group8 = models.IntegerField(choices = [[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>16. </b>Im Allgemeinen stimme ich der Mehrheit lieber zu, anstatt Konflikte zu verursachen. ', widget=widgets.RadioSelectHorizontal, blank=True)
    group9 = models.IntegerField(choices = [[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>21. </b>Da unsere Bezahlung vom Gruppenerfolg abhing, haben wir uns gegenseitig stark unterstützt.', widget=widgets.RadioSelectHorizontal, blank=True)
    group10 = models.IntegerField(choices = [[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>22. </b>Da unsere Bezahlung vom Gruppenerfolg abhing, fühlten wir uns alle verpflichtet, unser Bestes zu geben. ', widget=widgets.RadioSelectHorizontal, blank=True)
    motivation1 = models.IntegerField(choices = [[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>17. </b>Mir hat die Arbeit an der Aufgabe Spaß gemacht.', widget=widgets.RadioSelectHorizontal, blank=True)
    motivation2 = models.IntegerField(choices = [[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>18. </b>Ich wollte nicht weniger beitragen als die anderen in meiner Gruppe.', widget=widgets.RadioSelectHorizontal, blank=True)
    motivation3 = models.IntegerField(choices = [[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>19. </b>Der Wettkampf mit den anderen Gruppen hat mich motiviert.', widget=widgets.RadioSelectHorizontal, blank=True)    
    motivation4 = models.IntegerField(choices = [[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>20. </b>Die Bonuszahlung hat mich motiviert.', widget=widgets.RadioSelectHorizontal, blank=True)
    incentives1 = models.IntegerField(choices = [[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], widget=widgets.RadioSelectHorizontal, blank=True)
    incentives2 = models.IntegerField(choices = [[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], widget=widgets.RadioSelectHorizontal, blank=True)
    incentives3 = models.IntegerField(choices = [[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], widget=widgets.RadioSelectHorizontal, blank=True)
    guesser1 = models.LongStringField(label='<b>1. </b>Welche Strategie haben Sie beim Raten verfolgt?', initial = '', max_length=500, blank=True)
    guesser2 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>2. </b>Ich habe die beiden Hinweiswörter zunächst einzeln betrachtet, bevor ich nach einer Verbindung zwischen ihnen gesucht habe.', widget=widgets.RadioSelectHorizontal, blank=True)
    guesser3 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>3. </b>Ich habe intuitiv Assoziationen zu den Hinweispaaren gesucht.', widget=widgets.RadioSelectHorizontal, blank=True)
    guesser4 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>4. </b>Ich habe versucht, ein übergeordnetes Konzept oder Thema zu finden, das beide Hinweiswörter vereint.', widget=widgets.RadioSelectHorizontal, blank=True)
    guesser5 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>5. </b>Ich habe bewusst versucht, „um die Ecke“ zu denken, um ungewöhnlichere Verbindungen zu entdecken.', widget=widgets.RadioSelectHorizontal, blank=True)
    guesser6 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>6. </b>Ich habe berücksichtigt, dass offensichtliche Wörter durch Tabuwörter ausgeschlossen sein könnten.', widget=widgets.RadioSelectHorizontal, blank=True)
    guesser7 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>7. </b>Ich habe oft das erste Wort gewählt, das mir eingefallen ist.', widget=widgets.RadioSelectHorizontal, blank=True)
    guesser8 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>8. </b>Es fiel mir schwer, Antworten auf Basis der Hinweispaare zu finden.', widget=widgets.RadioSelectHorizontal, blank=True)
    guesser9 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>9. </b>Mir fiel die Entscheidung für eine finale Antwort schwer.', widget=widgets.RadioSelectHorizontal, blank=True)
    guesser10 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>10. </b>Mir hat die Aufgabe Spaß gemacht.', widget=widgets.RadioSelectHorizontal, blank=True)
    guesser11 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>11. </b>Der Wettkampf mit den anderen Ratenden hat mich motiviert.', widget=widgets.RadioSelectHorizontal, blank=True)
    guesser12 = models.IntegerField(choices=[[2, 'stimme vollkommen zu'], [1, 'stimme zu'], [0, 'neutral'], [-1, 'stimme nicht zu'], [-2, 'stimme überhaupt nicht zu']], label='<b>12. </b>Die Bonuszahlung hat mich motiviert.', widget=widgets.RadioSelectHorizontal, blank=True)
    payment_allocator = models.BooleanField(initial=False)
    payment_receiver = models.BooleanField(initial=False)
    payoff_calculated = models.BooleanField(initial=False)

class Model:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Model, cls).__new__(cls)
        return cls._instance
    def __init__(player, model='cc.de.300.bin'):
        if not hasattr(player, 'model'):  # Lade das Modell nur, wenn es noch nicht geladen wurde
            player.model_file = model
            print(f'Loading FastText model from {player.model_file}...')
            player.model = fasttext.load_model(player.model_file)
            print('Model loaded successfully.')
    def get_vector(player, word):
        return player.model.get_word_vector(word)
    def distance(player, word1: str, word2: str):
        vector1 = player.get_vector(word1)
        vector2 = player.get_vector(word2)
        if vector1 is not None and vector2 is not None:
            return scipy.spatial.distance.cosine(vector1, vector2) * 100
        return None
    def calculate_originality(player, word_pair, mystery_word):
        dist_1 = player.distance(word_pair.split(" + ")[0], mystery_word)
        dist_2 = player.distance(word_pair.split(" + ")[1], mystery_word)
        if dist_1 is not None and dist_2 is not None:
            return (dist_1 + dist_2) / 2
        return None
        
model_instance = Model()  

def creating_session(subsession: Subsession):
    session = subsession.session
    players = subsession.get_players()
    num_players = len(players)
    num_hintgiver_groups = num_players // 4
    hintgiver_groups = [] 
    ratender_group = []

    for i in range(num_hintgiver_groups):
        start_index = i * 3
        end_index = start_index + 3
        hintgiver_groups.append(players[start_index:end_index])

    ratender_group = players[num_hintgiver_groups * 3:]
    matrix = hintgiver_groups + [ratender_group]
    subsession.set_group_matrix(matrix)
    
    treatment = session.config['treatment']
    ingroup_count = 0
    outgroup_count = 0
    for player in players:
        participant = player.participant
        participant.vars['treatment'] = treatment
        player.incentive = treatment
        player.player_role = 'Hinweisgebende' if player in [p for group in hintgiver_groups for p in group] else 'Ratender'
        if player.player_role == 'Hinweisgebende':
            if ingroup_count < (num_players - (num_players // 4)) // 2:
                player.player_role2 = 'ingroup'
                ingroup_count += 1
            elif outgroup_count < (num_players - (num_players // 4)) // 2:
                player.player_role2 = 'outgroup'
                outgroup_count += 1
            else: 
                player.player_role2 = random.choice(['outgroup', 'ingroup'])
        else: 
            player.player_role2 = None
    hintgiver_players = [player for player in players if player.player_role == 'Hinweisgebende']
    selected_allocator = random.sample(hintgiver_players, 1)
    selected_receiver = []
    for player in players:
        if player in selected_allocator:
            player.payment_allocator = True
        if player.payment_allocator == True: 
            if player.player_role2 == 'ingroup':
                ingroup_players = player.get_others_in_group()
                if ingroup_players:
                    selected_receiver = random.sample(ingroup_players, 1)  
            else:
                outgroup_players = [p for p in hintgiver_players if p.group != player.group]
                if outgroup_players:
                    selected_receiver = random.sample(outgroup_players, 1)
    for player in players:
        if player in selected_receiver: 
            player.payment_receiver = True

def validate_ideas(player, ideas):
    stem_words = C.STEM_WORDS[player.round_number - 1]     
    wordlist = set()
    with open("fasttext_words_de.txt", 'r', encoding = 'utf-8') as file:
        for line in file:
            words = line.strip().split()      
            wordlist.update(words)                                  
    occurrences = {}
    if len(ideas) > 0:
        ideas_low = [idea.lower() for idea in ideas]
        for i in range(len(ideas)): 
            if ideas[i] != '':
                # Check if the idea is a taboo word or a modification of the mystery word
                for j in range(len(stem_words)):
                    if stem_words[j] in ideas_low[i]:
                        ideas[i] = 'false'
                    continue
                # Check if there's a space-separated word
                if ' ' in ideas[i] and re.search(r'\b\w+\s+\w+\b', ideas[i]):
                    ideas[i] = 'false'
                    continue
                 # Remove spaces from individual words (single words shouldn't contain spaces)
                if ' ' in ideas[i]:
                    ideas[i] = ideas[i].replace(' ', '')
                # Check for special characters
                if re.search(r"[^a-zA-Z0-9äöüÄÖÜß\s]", ideas_low[i]):
                    ideas[i] = 'false'
                    continue
                # Check for numbers
                if bool(re.search(r'\d', ideas[i])):
                    ideas[i] = 'false'
                    continue
                # Check if the word is not in the word list
                if ideas[i].lower() not in wordlist:
                    ideas[i] = 'false'
                    continue
                # Check for duplicate occurrences
                if ideas[i] != 'false':
                    if ideas[i] in occurrences:
                        occurrences[ideas[i]] += 1
                        ideas[i] = 'false'
                    else:
                        occurrences[ideas[i]] = 1
        return ideas    

# PAGES

class Overview(Page):
    def is_displayed(player):
        return player.round_number == 1

class Intro(Page):
    timeout_seconds = 1000
    def is_displayed(player):
        return player.round_number == 1

class Intro2(Page):
    timeout_seconds = 120
    def is_displayed(player):
        return player.round_number == 1 and player.player_role == 'Hinweisgebende'
    
class Procedure(Page):
    timeout_seconds = 1000
    def is_displayed(player):
        return player.round_number == 1 and player.player_role == 'Hinweisgebende'
    
class Rules(Page):
    timeout_seconds = 70
    def is_displayed(player):
        return player.round_number == 1 
   
class Instructions(Page):
    timeout_seconds = 120
    def is_displayed(player):
        return player.round_number == 1 and player.player_role == 'Hinweisgebende'
    
class Payment(Page):
    timeout_seconds = 1000
    def is_displayed(player):
        return player.round_number == 1
    
class UnderstandPage(Page):
    template_name = 'experiment/UnderstandPage.html'
    timeout_seconds = 1000
    def is_displayed(player):
        return player.round_number == 1
    form_model = 'player'
    form_fields = ['understandHin_1', 'understandHin_2', 'understandHin_3', 'understandHin_4', 'understandHin_5_Control', 'understandHin_5_Quantity', 'understandHin_5_Quality', 'understandHin_5_Originality', 'understandHin_6_Quantity', 'understandHin_6_Quality', 'understandHin_6_Originality', 'understandHin_7_Quality', 'understandRat_1', 'understandRat_2', 'understandRat_3', 'understandRat_4', 'understandRat_5']
    def error_message(player, values):
        if player.player_role == 'Hinweisgebende':
            for i in range(1, 5):
                if values[f'understandHin_{i}'] == 'false' or values[f'understandHin_{i}'] == None:
                    return f'Falsche Antwort bei Frage {i}! Versuchen Sie es noch einmal.'         
            if (values['understandHin_5_Control'] == 'false' or values[f'understandHin_5_Control'] == None) and player.participant.treatment == 1:
                return 'Falsche Antwort bei Frage 5! Versuchen Sie es noch einmal.'
            if (values['understandHin_5_Quantity'] == 'false' or values[f'understandHin_5_Quantity'] == None) and player.participant.treatment == 2:
                return 'Falsche Antwort bei Frage 5! Versuchen Sie es noch einmal.'
            if (values['understandHin_5_Quality'] == 'false' or values[f'understandHin_5_Quality'] == None) and player.participant.treatment == 3:
                return 'Falsche Antwort bei Frage 5! Versuchen Sie es noch einmal.'
            if (values['understandHin_5_Originality'] == 'false' or values[f'understandHin_5_Originality'] == None) and player.participant.treatment == 4:
                return 'Falsche Antwort bei Frage 5! Versuchen Sie es noch einmal.'
            if (values['understandHin_6_Quantity'] == 'false' or values[f'understandHin_6_Quantity'] == None) and player.participant.treatment == 2:
                return 'Falsche Antwort bei Frage 6! Versuchen Sie es noch einmal.'
            if (values['understandHin_6_Quality'] == 'false' or values[f'understandHin_6_Quality'] == None) and player.participant.treatment == 3:
                return 'Falsche Antwort bei Frage 6! Versuchen Sie es noch einmal.'
            if (values['understandHin_6_Originality'] == 'false' or values[f'understandHin_6_Originality'] == None) and player.participant.treatment == 4:
                return 'Falsche Antwort bei Frage 6! Versuchen Sie es noch einmal.'
            if (values['understandHin_7_Quality'] == 'false' or values[f'understandHin_7_Quality'] == None) and player.participant.treatment == 3:
                return 'Falsche Antwort bei Frage 7! Versuchen Sie es noch einmal.'
        else:
             for i in range(1, 6):  
                if values[f'understandRat_{i}'] == 'false' or values[f'understandRat_{i}'] == None:
                    return f'Falsche Antwort bei Frage {i}! Versuchen Sie es noch einmal.'

class Round(Page):
    timeout_seconds = 30
    def vars_for_template(player):
        round_number = player.round_number 
        remaining_rounds = C.NUM_ROUNDS - round_number 
        return dict(round_number = round_number, remaining_rounds = remaining_rounds) 
    
class Generation_Page(Page):
    timeout_seconds = 160
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende'   
    form_model = 'player'
    form_fields = ['Idea1', 'Idea2', 'Idea3', 'Idea4', 'Idea5', 'Idea6', 'Idea7', 'Idea8', 'Idea9', 'Idea10','Idea11', 'Idea12', 'Idea13', 'Idea14', 'Idea15', 'Idea16', 'Idea17', 'Idea18', 'Idea19', 'Idea20']
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        taboo_words = C.TABOO_WORDS[player.round_number - 1]
        return dict(mystery_word = mystery_word, taboo_words = taboo_words)

    def before_next_page(player, timeout_happened):
        if timeout_happened:        
            ideas = [player.Idea1, player.Idea2, player.Idea3, player.Idea4, player.Idea5, player.Idea6, player.Idea7, player.Idea8, player.Idea9, player.Idea10, player.Idea11, player.Idea12, player.Idea13, player.Idea14, player.Idea15, player.Idea16, player.Idea17, player.Idea18, player.Idea19, player.Idea20]
            ideas = validate_ideas(player, ideas)
            player.before_missing = False
            player.before_invalid = 0
            for i in range(len(ideas)):
                if ideas[i] == 'false':
                    player.before_invalid = player.before_invalid + 1
            for i in range(0, len(ideas), 2):
                if (ideas[i] != '' and ideas[i] != 'false') and (ideas[i + 1] != '' and ideas[i + 1] != 'false'):
                    setattr(player, f'pair{(i // 2) + 1}', f"{ideas[i]} + {ideas[i + 1]}")
                else:
                    setattr(player, f'pair{(i // 2) + 1}', 'empty') 
            pairs = [player.pair1] + [player.pair2] + [player.pair3] + [player.pair4] + [player.pair5] + [player.pair6] + [player.pair7] + [player.pair8] + [player.pair9] + [player.pair10]
            while 'empty' in pairs:
                pairs.remove('empty')
            player.before_quantity = len(pairs)        
            if player.before_quantity == 0:
                player.before_missing = True
        else:
            player.before_invalid = 0
            player.before_missing = False
            ideas = [player.Idea1, player.Idea2, player.Idea3, player.Idea4, player.Idea5, player.Idea6, player.Idea7, player.Idea8, player.Idea9, player.Idea10, player.Idea11, player.Idea12, player.Idea13, player.Idea14, player.Idea15, player.Idea16, player.Idea17, player.Idea18, player.Idea19, player.Idea20]
            ideas = validate_ideas(player, ideas)
            for i in range(len(ideas)):
                if ideas[i] == 'false':  
                    player.before_invalid = player.before_invalid + 1
            for i in range(0, len(ideas), 2):
                if (ideas[i] != '' and ideas[i] != 'false') and (ideas[i + 1] != '' and ideas[i + 1] != 'false'):
                    setattr(player, f'pair{(i // 2) + 1}', f"{ideas[i]} + {ideas[i + 1]}")
                else:
                    setattr(player, f'pair{(i // 2) + 1}', 'empty')
            pairs = [player.pair1] + [player.pair2] + [player.pair3] + [player.pair4] + [player.pair5] + [player.pair6] + [player.pair7] + [player.pair8] + [player.pair9] + [player.pair10]
            while 'empty' in pairs:
                pairs.remove('empty')
            player.before_quantity = len(pairs)
            if player.before_quantity == 0:
                player.before_missing = True       

class Discussion(Page):
    timeout_seconds = 5000
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende'
    form_model = 'player'   
    form_fields = ['rating_before1', 'rating_before2', 'rating_before3', 'rating_before4', 'rating_before5', 'rating_before6', 'rating_before7', 'rating_before8', 'rating_before9', 'rating_before10', 'rating_before11', 'rating_before12', 'rating_before13', 'rating_before14', 'rating_before15', 'rating_before16', 'rating_before17', 'rating_before18', 'rating_before19', 'rating_before20', 'replace_word1', 'replace_word2', 'replace_word3', 'replace_word4', 'replace_word5', 'replace_word6', 'replace_word7', 'replace_word8', 'replace_word9', 'replace_word10', 'replace_word11', 'replace_word12', 'replace_word13', 'replace_word14', 'replace_word15', 'replace_word16', 'replace_word17', 'replace_word18', 'replace_word19', 'replace_word20', 'discussion1','discussion2', 'discussion3', 'discussion4', 'discussion5', 'discussion6', 'discussion7', 'discussion8', 'discussion9', 'discussion10', 'discussion11', 'discussion12', 'discussion13', 'discussion14', 'discussion15', 'discussion16', 'discussion17', 'discussion18', 'discussion19', 'discussion20']
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        taboo_words = C.TABOO_WORDS[player.round_number - 1]
        pairs = [player.pair1 for player in player.get_others_in_group()] + [player.pair2 for player in player.get_others_in_group()] + [player.pair3 for player in player.get_others_in_group()] + [player.pair4 for player in player.get_others_in_group()] + [player.pair5 for player in player.get_others_in_group()] + [player.pair6 for player in player.get_others_in_group()] + [player.pair7 for player in player.get_others_in_group()] + [player.pair8 for player in player.get_others_in_group()] + [player.pair9 for player in player.get_others_in_group()] + [player.pair10 for player in player.get_others_in_group()]
        while 'empty' in pairs:
            pairs.remove('empty')
        while '' in pairs:
            pairs.remove('')
        player.other_pairs = ', '.join(pairs)
        player.number_pairs = len(pairs)
        pairs_output = [pairs[i] if i < player.number_pairs else 'empty'for i in range(20)]
        return dict(mystery_word = mystery_word, taboo_words = taboo_words, number_pairs = player.number_pairs, Pair1 = pairs_output[0], Pair2 = pairs_output[1], Pair3 = pairs_output[2], Pair4 = pairs_output[3], Pair5 = pairs_output[4], Pair6 = pairs_output[5], Pair7 = pairs_output[6], Pair8 = pairs_output[7], Pair9 = pairs_output[8], Pair10 = pairs_output[9], Pair11 = pairs_output[10], Pair12 = pairs_output[11], Pair13 = pairs_output[12], Pair14 = pairs_output[13], Pair15 = pairs_output[14], Pair16 = pairs_output[15], Pair17 = pairs_output[16], Pair18 = pairs_output[17], Pair19 = pairs_output[18], Pair20 = pairs_output[19])  
    
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            pairs = [player.pair1 for player in player.get_others_in_group()] + [player.pair2 for player in player.get_others_in_group()] + [player.pair3 for player in player.get_others_in_group()] + [player.pair4 for player in player.get_others_in_group()] + [player.pair5 for player in player.get_others_in_group()] + [player.pair6 for player in player.get_others_in_group()] + [player.pair7 for player in player.get_others_in_group()] + [player.pair8 for player in player.get_others_in_group()] + [player.pair9 for player in player.get_others_in_group()] + [player.pair10 for player in player.get_others_in_group()]
            while 'empty' in pairs:
                pairs.remove('empty')
            while '' in pairs:
                pairs.remove('')
            for i in range(player.number_pairs):
                feedback = [player.other_pairs.split(', ')[i], getattr(player, f'rating_before{i + 1}'), getattr(player, f'replace_word{i + 1}'), getattr(player, f'discussion{i + 1}')]
                setattr(player, f'pair_feedback{i + 1}', str(feedback))
        else:
            pairs = [player.pair1 for player in player.get_others_in_group()] + [player.pair2 for player in player.get_others_in_group()] + [player.pair3 for player in player.get_others_in_group()] + [player.pair4 for player in player.get_others_in_group()] + [player.pair5 for player in player.get_others_in_group()] + [player.pair6 for player in player.get_others_in_group()] + [player.pair7 for player in player.get_others_in_group()] + [player.pair8 for player in player.get_others_in_group()] + [player.pair9 for player in player.get_others_in_group()] + [player.pair10 for player in player.get_others_in_group()]
            while 'empty' in pairs:
                pairs.remove('empty')
            while '' in pairs:
                pairs.remove('')
            for i in range(player.number_pairs):
                feedback = [player.other_pairs.split(', ')[i], getattr(player, f'rating_before{i + 1}'), getattr(player, f'replace_word{i + 1}'), getattr(player, f'discussion{i + 1}')]
                setattr(player, f'pair_feedback{i + 1}', str(feedback))
    
class Clue_Page(Page):
    timeout_seconds = 130
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende'   
    form_model = 'player'
    form_fields = ['Idea1', 'Idea2', 'Idea3', 'Idea4', 'Idea5', 'Idea6', 'Idea7', 'Idea8', 'Idea9', 'Idea10', 'Idea11', 'Idea12', 'Idea13', 'Idea14', 'Idea15', 'Idea16', 'Idea17', 'Idea18', 'Idea19', 'Idea20']
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        taboo_words = C.TABOO_WORDS[player.round_number - 1]
        feedback_groups = [
            [p.pair_feedback1 for p in player.get_others_in_group()],
            [p.pair_feedback2 for p in player.get_others_in_group()],
            [p.pair_feedback3 for p in player.get_others_in_group()],
            [p.pair_feedback4 for p in player.get_others_in_group()],
            [p.pair_feedback5 for p in player.get_others_in_group()],
            [p.pair_feedback6 for p in player.get_others_in_group()],
            [p.pair_feedback7 for p in player.get_others_in_group()],
            [p.pair_feedback8 for p in player.get_others_in_group()],
            [p.pair_feedback9 for p in player.get_others_in_group()],
            [p.pair_feedback10 for p in player.get_others_in_group()],
            [p.pair_feedback11 for p in player.get_others_in_group()],
            [p.pair_feedback12 for p in player.get_others_in_group()],
            [p.pair_feedback13 for p in player.get_others_in_group()],
            [p.pair_feedback14 for p in player.get_others_in_group()],
            [p.pair_feedback15 for p in player.get_others_in_group()],
            [p.pair_feedback16 for p in player.get_others_in_group()],
            [p.pair_feedback17 for p in player.get_others_in_group()],
            [p.pair_feedback18 for p in player.get_others_in_group()],
            [p.pair_feedback19 for p in player.get_others_in_group()],
            [p.pair_feedback20 for p in player.get_others_in_group()]
            ]
        filtered_feedback_groups = [list(filter(bool, group)) for group in feedback_groups]
        feedback1_group, feedback2_group, feedback3_group, feedback4_group, feedback5_group, feedback6_group, feedback7_group, feedback8_group, feedback9_group, feedback10_group, feedback11_group, feedback12_group, feedback13_group, feedback14_group, feedback15_group, feedback16_group, feedback17_group, feedback18_group, feedback19_group, feedback20_group = filtered_feedback_groups
        all_feedback_groups = []
        for group in filtered_feedback_groups:
            if group:
                all_feedback_groups.extend(group)
        ratings = [[] for _ in range(10)]
        replaces = [[] for _ in range(10)]
        r_words = [[] for _ in range(10)]
        pairs = [player.pair1, player.pair2, player.pair3, player.pair4, player.pair5, player.pair6, player.pair7, player.pair8, player.pair9, player.pair10]
        for element in all_feedback_groups:
            element_list = ast.literal_eval(element)
            for i, pair in enumerate(pairs):
                if element_list[0] == pair:
                    ratings[i].append(element_list[1])
                    replaces[i].append(element_list[2])
                    r_words[i].append(element_list[3])
        rating_1, rating_2, rating_3, rating_4, rating_5, rating_6, rating_7, rating_8, rating_9, rating_10 = ratings
        replace_1, replace_2, replace_3, replace_4, replace_5, replace_6, replace_7, replace_8, replace_9, replace_10 = replaces
        r_word_1, r_word_2, r_word_3, r_word_4, r_word_5, r_word_6, r_word_7, r_word_8, r_word_9, r_word_10 = r_words
        return dict(mystery_word = mystery_word, taboo_words = taboo_words, Rating_1 = rating_1, Replace_1 = replace_1, R_word_1 = r_word_1, Rating_2 = rating_2, Replace_2 = replace_2, R_word_2 = r_word_2, Rating_3 = rating_3, Replace_3 = replace_3, R_word_3 = r_word_3, Rating_4 = rating_4, Replace_4 = replace_4, R_word_4 = r_word_4, Rating_5 = rating_5, Replace_5 = replace_5, R_word_5 = r_word_5, Rating_6 = rating_6, Replace_6 = replace_6, R_word_6 = r_word_6, Rating_7 = rating_7, Replace_7 = replace_7, R_word_7 = r_word_7, Rating_8 = rating_8, Replace_8 = replace_8, R_word_8 = r_word_8, Rating_9 = rating_9, Replace_9 = replace_9, R_word_9 = r_word_9, Rating_10 = rating_10, Replace_10 = replace_10, R_word_10 = r_word_10, Feedback1 = feedback1_group, Feedback2 = feedback2_group, Feedback3 = feedback3_group, Feedback4 = feedback4_group, Feedback5 = feedback5_group, Feedback6 = feedback6_group, Feedback7 = feedback7_group, Feedback8 = feedback8_group, Feedback9 = feedback9_group, Feedback10 = feedback10_group)
    
    def before_next_page(player, timeout_happened):
        if timeout_happened:        
            player.after_invalid = 0
            ideas = [player.Idea1, player.Idea2, player.Idea3, player.Idea4, player.Idea5, player.Idea6, player.Idea7, player.Idea8, player.Idea9, player.Idea10, player.Idea11, player.Idea12, player.Idea13, player.Idea14, player.Idea15, player.Idea16, player.Idea17, player.Idea18, player.Idea19, player.Idea20]
            ideas = validate_ideas(player, ideas)
            for i in range(len(ideas)):
                if ideas[i] == 'false':
                    player.after_invalid = player.after_invalid + 1
            for i in range(0, len(ideas), 2):
                if (ideas[i] != '' and ideas[i] != 'false') and (ideas[i + 1] != '' and ideas[i + 1] != 'false'):
                    setattr(player, f'pair{(i // 2) + 1}after', f"{ideas[i]} + {ideas[i + 1]}")
                else:
                    setattr(player, f'pair{(i // 2) + 1}after', 'empty')
        else:
            player.after_invalid = 0
            ideas = [player.Idea1, player.Idea2, player.Idea3, player.Idea4, player.Idea5, player.Idea6, player.Idea7, player.Idea8, player.Idea9, player.Idea10, player.Idea11, player.Idea12, player.Idea13, player.Idea14, player.Idea15, player.Idea16, player.Idea17, player.Idea18, player.Idea19, player.Idea20]
            ideas = validate_ideas(player, ideas)
            for i in range(len(ideas)):
                if ideas[i] == 'false':  
                    player.after_invalid = player.after_invalid + 1
            for i in range(0, len(ideas), 2):
                if (ideas[i] != '' and ideas[i] != 'false') and (ideas[i + 1] != '' and ideas[i + 1] != 'false'):
                    setattr(player, f'pair{(i // 2) + 1}after', f"{ideas[i]} + {ideas[i + 1]}")
                else:
                    setattr(player, f'pair{(i // 2) + 1}after', 'empty')

class Voting_Page(Page):
    timeout_seconds = 90
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende' 
    form_model = 'player'
    form_fields = ['vote']
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        taboo_words = C.TABOO_WORDS[player.round_number - 1]
        pairs = [player.pair1after] + [player.pair1after for player in player.get_others_in_group()] + [player.pair2after] + [player.pair2after for player in player.get_others_in_group()] + [player.pair3after] + [player.pair3after for player in player.get_others_in_group()] + [player.pair4after] + [player.pair4after for player in player.get_others_in_group()] + [player.pair5after] + [player.pair5after for player in player.get_others_in_group()] + [player.pair6after] + [player.pair6after for player in player.get_others_in_group()] + [player.pair7after] + [player.pair7after for player in player.get_others_in_group()] + [player.pair8after] + [player.pair8after for player in player.get_others_in_group()] + [player.pair9after] + [player.pair9after for player in player.get_others_in_group()] + [player.pair10after] + [player.pair10after for player in player.get_others_in_group()]
        while 'empty' in pairs:
            pairs.remove('empty')
        while '' in pairs:
            pairs.remove('')
        pairsafter = []
        for item in pairs:
            if pairs.count(item) > 1 and item not in pairsafter:
                pairsafter.append(item)
            elif pairs.count(item) == 1:
                pairsafter.append(item)
        pairsafter = sorted(pairsafter)
        player.pairsafter = ', '.join(pairsafter)
        number_pairs = len(pairsafter)
        pairs_dict = {f'Pair{i+1}': pairsafter[i] if i < number_pairs else '' for i in range(30)}
        Pair1, Pair2, Pair3, Pair4, Pair5, Pair6, Pair7, Pair8, Pair9, Pair10, Pair11, Pair12, Pair13, Pair14, Pair15, Pair16, Pair17, Pair18, Pair19, Pair20, Pair21, Pair22, Pair23, Pair24, Pair25, Pair26, Pair27, Pair28, Pair29, Pair30 = pairs_dict.values()
        return dict(mystery_word = mystery_word, taboo_words= taboo_words, number_pairs = number_pairs, Pair1 = Pair1, Pair2 = Pair2, Pair3 = Pair3, Pair4 = Pair4, Pair5 = Pair5, Pair6 = Pair6, Pair7 = Pair7, Pair8 = Pair8, Pair9 = Pair9, Pair10 = Pair10, Pair11 = Pair11, Pair12 = Pair12, Pair13 = Pair13, Pair14 = Pair14, Pair15 = Pair15, Pair16 = Pair16, Pair17 = Pair17, Pair18 = Pair18, Pair19 = Pair19, Pair20 = Pair20, Pair21 = Pair21, Pair22 = Pair22, Pair23 = Pair23, Pair24 = Pair24, Pair25 = Pair25, Pair26 = Pair26, Pair27 = Pair27, Pair28 = Pair28, Pair29 = Pair29, Pair30 = Pair30, pairs = pairsafter) 
  
class VotingResultPage(Page):
    timeout_seconds = 5000
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende'
    form_model = 'player'
    form_fields = ['communication', 'decision', 'subjective_originality', 'subjective_quality', 'explanation']
    def vars_for_template(player):
        pairs = player.pairsafter.split(', ')
        votes = [player.vote] + [p.vote for p in player.get_others_in_group()]
        while '' in votes:
            votes.remove('')
        random.seed(42)
        duplicates = [v for v in set(votes) if votes.count(v) >= 2]
        number_duplicates = len(duplicates)
        votes = sorted(votes)
        empty_pairs = 1 if pairs == [''] else 0
        if len(duplicates) > 0:
            vote_group = duplicates[0]
        else:
            if len(votes) == 1:
                vote_group = votes[0]
            elif len(votes) > 1:
                i = random.randint(0, len(votes) - 1) 
                vote_group = votes[i]
            else:
                if pairs != ['']:
                    i = random.randint(0, len(pairs) - 1)
                    vote_group = pairs[i]  
                else:
                    vote_group = 'Kein gültiges Hinweispaar'
        player.vote_group = vote_group
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        own_vote = player.vote
        return dict(vote_group=vote_group, duplicates=number_duplicates, empty_pairs=empty_pairs, mystery_word=mystery_word, own_vote=own_vote)
    
class Guess_Page1(Page):
    timeout_seconds = 5000
    def is_displayed(player):
        return player.player_role == 'Ratender'
    
    def vars_for_template(player):  
        hint_groups = [g for g in player.subsession.get_groups() if g.get_players()[0].player_role == 'Hinweisgebende']
        index = (player.id_in_group - 1 + player.round_number - 1) % len(hint_groups)
        vote_group = hint_groups[index].get_players()[0].vote_group
        player.vote_group = vote_group
        player.group_number_guess = hint_groups[index].id_in_subsession 
        return dict(vote_group=vote_group)
    
    form_model = 'player'
    form_fields = ['guess1'] 

    def error_message(player, values):
        if player.vote_group != "Kein gültiges Hinweispaar":            
            if values[f'guess1'] == '':
                    return f'Bitte geben Sie eine Vermutung ab!'
    
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.guess1 = 'Kein Tipp gegeben'
            player.correct_guess1 = False
        else:
            special_char_map = {ord('ä'):'ae', ord('ü'):'ue', ord('ö'):'oe', ord('ß'):'ss'}
            if ' ' in player.guess1:
                player.guess1 = player.guess1.replace(' ', '')
            if player.guess1.lower().translate(special_char_map)  == C.MYSTERY_WORDS[player.round_number - 1].lower():
                player.correct_guess1 = True
            else:
                player.correct_guess1 = False
        
class Guess_Page2(Page):
    timeout_seconds = 5000
    def is_displayed(player):
        return player.player_role == 'Ratender' and player.correct_guess1 == False and player.vote_group != 'Kein gültiges Hinweispaar'
    
    def vars_for_template(player):  
        vote_group = player.vote_group
        return dict(vote_group=vote_group)
    
    form_model = 'player'
    form_fields = ['guess2'] 
    
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.guess2 = 'Kein Tipp gegeben'
            player.correct_guess2 = False
        else:
            special_char_map = {ord('ä'):'ae', ord('ü'):'ue', ord('ö'):'oe', ord('ß'):'ss'}
            if ' ' in player.guess2:
                player.guess2 = player.guess2.replace(' ', '')
            if player.guess2.lower().translate(special_char_map)  == C.MYSTERY_WORDS[player.round_number - 1].lower():
                player.correct_guess2 = True
            else:
                player.correct_guess2 = False

class Guess_Page3(Page):
    timeout_seconds = 5000
    def is_displayed(player): 
        return player.player_role == 'Ratender' and player.field_maybe_none('correct_guess2') == False and player.vote_group != 'Kein gültiges Hinweispaar'
    
    def vars_for_template(player):  
        vote_group = player.vote_group
        return dict(vote_group=vote_group)
    
    form_model = 'player'
    form_fields = ['guess3'] 
    
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.guess3 = 'Kein Tipp gegeben'
            player.correct_guess3 = False
        else:
            special_char_map = {ord('ä'):'ae', ord('ü'):'ue', ord('ö'):'oe', ord('ß'):'ss'}
            if ' ' in player.guess3:
                player.guess3 = player.guess3.replace(' ', '')
            if player.guess3.lower().translate(special_char_map)  == C.MYSTERY_WORDS[player.round_number - 1].lower():
                player.correct_guess3 = True
            else:
                player.correct_guess3 = False

class PairCheck(Page):
    timeout_seconds = 5000
    def is_displayed(player):
        return player.player_role == 'Ratender'
    
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        hint_groups = [g for g in player.subsession.get_groups() if g.get_players()[0].player_role == 'Hinweisgebende']
        index = (player.id_in_group -1 + player.round_number) % len(hint_groups)  
        pairs = hint_groups[index].get_players()[0].pairsafter.split(', ')
        player.group_number_check = hint_groups[index].id_in_subsession
        while '' in pairs:
            pairs.remove('')
        number_pairs = len(pairs)
        return dict(mystery_word=mystery_word, pairs=pairs, number_pairs = number_pairs)
    
    form_model = 'player'
    def get_form_fields(player:Player):
        hint_groups = [g for g in player.subsession.get_groups() if g.get_players()[0].player_role == 'Hinweisgebende']
        index = (player.id_in_group - 1 + player.round_number) % len(hint_groups)  
        pairs = hint_groups[index].get_players()[0].pairsafter.split(', ')
        form_fields = ['check_invalid_' + str(i+1) for i in range(len(pairs))]
        return form_fields
    
class Results(Page):
    timeout_seconds = 50000
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        taboo_words = C.TABOO_WORDS[player.round_number - 1]
        guesser = next((p for p in player.subsession.get_players() if p.player_role == 'Ratender' and p.group_number_guess == player.group.id_in_subsession), None)
        rater = next((p for p in player.subsession.get_players() if p.player_role == 'Ratender' and p.group_number_check == player.group.id_in_subsession), None)

        def calculate_result(player, guesses, mystery_word):
            mystery_word_lower = mystery_word.lower()
            guesses_lower = [guess.lower() for guess in guesses if guess] 
            if mystery_word_lower == guesses_lower[0]:
                return 'richtig', 3
            elif len(guesses_lower) > 1 and mystery_word_lower == guesses_lower[1]:
                return 'richtig', 2
            elif len(guesses_lower) > 2 and mystery_word_lower == guesses_lower[2]:
                return 'richtig', 1
            else:
                return 'falsch', 0

        if player.player_role == 'Hinweisgebende':
            vote_group = [p.vote_group for p in player.get_others_in_group()]
            while '' in vote_group:
                vote_group.remove('')
            pairs = player.pairsafter.split(', ')
            check_invalid = []
            if guesser is not None:
                guesses = [guesser.guess1, guesser.guess2, guesser.guess3]
            else:
                guesses = [None, None, None]
            if rater is not None:
                for i in range(len(pairs)):
                    attr_name = f"check_invalid_{i+1}"
                    attr_value = getattr(rater, attr_name, None)
                    if attr_value is not None:
                        check_invalid.append(attr_value)
            player.missing = False
            missing = ''
            while '' in check_invalid:
                check_invalid.remove('')
            while '' in pairs:
                pairs.remove('')
            player.quantity = len(pairs) - len(check_invalid)
            vote_group = vote_group[0] if vote_group else 'Kein gültiges Hinweispaar'
            if vote_group in check_invalid:
                vote_group = 'Kein gültiges Hinweispaar'
                player.vote_group = 'Kein gültiges Hinweispaar'
            invalid = ''
            player.invalid = False
            player.result, player.score = calculate_result(player, guesses, mystery_word)
            if vote_group == 'Kein gültiges Hinweispaar':
                player.invalid = True
                invalid = 'Achtung! Das Hinweispaar Ihrer Gruppe war ungültig.'
                player.result = 'ungültig'
                player.score = 0
            if player.quantity == 0:
                player.missing = True
                missing = 'Achtung! Sie haben kein gültiges Hinweispaar abgegeben.'
            # Berechnung der Originalität
            originality = 0.0
            if vote_group != 'Kein gültiges Hinweispaar':
                mystery_word_lower = mystery_word.lower()
                vote_group_lower = vote_group.lower()
                model = model_instance  # with Model() as model:
                with ThreadPoolExecutor() as executor:
                    future = executor.submit(model.calculate_originality, vote_group_lower, mystery_word_lower)
                    originality = future.result()
                    originality = float(originality)
                    player.originality = originality
                originality = round(originality, 2)
            else:
                player.originality = originality
            # Scores berechnen
            quality_scores = []
            originality_scores = []
            quantity_scores = []
            for i in range(player.round_number):
                quality_scores.append(player.in_round(player.round_number - i).score)
                player.group.quality = sum(quality_scores)
                quantity_scores.append(player.in_round(player.round_number - i).quantity)
                player.group.quantity = sum(quantity_scores)
                if player.in_round(player.round_number - i).field_maybe_none('originality') is not None:
                        originality_scores.append(float(player.in_round(player.round_number - i).originality))
                        player.group.originality = sum(originality_scores) / len(originality_scores)
            return dict(mystery_word=mystery_word, taboo_words=taboo_words, vote_group=player.vote_group, missing=missing, invalid=invalid, originality=originality)
        else:
            player.guess_missing = False
            guess_missing = ''
            guesses = [player.guess1, player.guess2, player.guess3]
            if player.guess1 == 'Kein Tipp gegeben':
                player.guess_missing = True
                guess_missing = 'Achtung! Sie haben keinen Tipp abgegeben.'
            player.result, player.score = calculate_result(player, guesses, mystery_word)
            guesser_scores = []
            for i in range(player.round_number):
                guesser_scores.append(player.in_round(player.round_number - i).score)
                player.quality_score = sum(guesser_scores)
            return dict(mystery_word=mystery_word, taboo_words=taboo_words, vote_group=player.vote_group, guess_missing=guess_missing, guess_1 = player.guess1 , guess_2 = player.guess2, guess_3 = player.guess3)

class Usefulness(Page):
    timeout_seconds = 5000
    def is_displayed(player):
        return player.player_role == 'Ratender'
    
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        hint_groups = [g for g in player.subsession.get_groups() if g.get_players()[0].player_role == 'Hinweisgebende']
        index = (player.id_in_group + player.round_number) % len(hint_groups)  
        pairs = hint_groups[index].get_players()[0].pairsafter.split(', ')
        player.group_number_rating = hint_groups[index].id_in_subsession
        while '' in pairs:
            pairs.remove('')
        player.number_pairs_after = len(pairs)
        choices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        return dict(mystery_word=mystery_word, pairs=pairs, choices = choices, number_pairs = player.number_pairs_after)
    
    form_model = 'player'
    form_fields = ['usefulness_1', 'usefulness_2', 'usefulness_3', 'usefulness_4', 'usefulness_5', 'usefulness_6', 'usefulness_7', 'usefulness_8', 'usefulness_9', 'usefulness_10', 'usefulness_11', 'usefulness_12', 'usefulness_13', 'usefulness_14', 'usefulness_15', 'usefulness_16', 'usefulness_17', 'usefulness_18', 'usefulness_19', 'usefulness_20', 'usefulness_21', 'usefulness_22', 'usefulness_23', 'usefulness_24', 'usefulness_25', 'usefulness_26', 'usefulness_27', 'usefulness_28', 'usefulness_29', 'usefulness_30']

def dimension_error_message(player, value, threshold):
    if value == '' and player.number_pairs_after > threshold:
        return f'Bitte wählen Sie eine Antwort für Paar {threshold + 1} aus!'

def usefulness_1_error_message(player, value):
    return dimension_error_message(player, value, 0)

def usefulness_2_error_message(player, value):
    return dimension_error_message(player, value, 1)

def usefulness_3_error_message(player, value):
    return dimension_error_message(player, value, 2)

def usefulness_4_error_message(player, value):
    return dimension_error_message(player, value, 3)

def usefulness_5_error_message(player, value):
    return dimension_error_message(player, value, 4)

def usefulness_6_error_message(player, value):
    return dimension_error_message(player, value, 5)

def usefulness_7_error_message(player, value):
    return dimension_error_message(player, value, 6)

def usefulness_8_error_message(player, value):
    return dimension_error_message(player, value, 7)

def usefulness_9_error_message(player, value):
    return dimension_error_message(player, value, 8)

def usefulness_10_error_message(player, value):
    return dimension_error_message(player, value, 9)

def usefulness_11_error_message(player, value):
    return dimension_error_message(player, value, 10)

def usefulness_12_error_message(player, value):
    return dimension_error_message(player, value, 11)

def usefulness_13_error_message(player, value):
    return dimension_error_message(player, value, 12)

def usefulness_14_error_message(player, value):
    return dimension_error_message(player, value, 13)

def usefulness_15_error_message(player, value):
    return dimension_error_message(player, value, 14)

def usefulness_16_error_message(player, value):
    return dimension_error_message(player, value, 15)

def usefulness_17_error_message(player, value):
    return dimension_error_message(player, value, 16)

def usefulness_18_error_message(player, value):
    return dimension_error_message(player, value, 17)

def usefulness_19_error_message(player, value):
    return dimension_error_message(player, value, 18)

def usefulness_20_error_message(player, value):
    return dimension_error_message(player, value, 19)

def usefulness_21_error_message(player, value):
    return dimension_error_message(player, value, 20)

def usefulness_22_error_message(player, value):
    return dimension_error_message(player, value, 21)

def usefulness_23_error_message(player, value):
    return dimension_error_message(player, value, 22)

def usefulness_24_error_message(player, value):
    return dimension_error_message(player, value, 23)

def usefulness_25_error_message(player, value):
    return dimension_error_message(player, value, 24)

def usefulness_26_error_message(player, value):
    return dimension_error_message(player, value, 25)

def usefulness_27_error_message(player, value):
    return dimension_error_message(player, value, 26)

def usefulness_28_error_message(player, value):
    return dimension_error_message(player, value, 27)

def usefulness_29_error_message(player, value):
    return dimension_error_message(player, value, 28)

def usefulness_30_error_message(player, value):
    return dimension_error_message(player, value, 29)
   
class Originality(Page):
    timeout_seconds = 5000
    def is_displayed(player):
        return player.player_role == 'Ratender'
    
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        hint_groups = [g for g in player.subsession.get_groups() if g.get_players()[0].player_role == 'Hinweisgebende']
        index = (player.id_in_group + player.round_number) % len(hint_groups)  
        pairs = hint_groups[index].get_players()[0].pairsafter.split(', ')
        while '' in pairs:
            pairs.remove('')
        player.number_pairs_after = len(pairs)
        choices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        return dict(mystery_word=mystery_word, pairs=pairs, choices = choices, number_pairs = player.number_pairs_after)
    
    form_model = 'player'
    form_fields = ['originality_1', 'originality_2', 'originality_3', 'originality_4', 'originality_5', 'originality_6', 'originality_7', 'originality_8', 'originality_9', 'originality_10', 'originality_11', 'originality_12', 'originality_13', 'originality_14', 'originality_15', 'originality_16', 'originality_17', 'originality_18', 'originality_19', 'originality_20', 'originality_21', 'originality_22', 'originality_23', 'originality_24', 'originality_25', 'originality_26', 'originality_27', 'originality_28', 'originality_29', 'originality_30']

def originality_1_error_message(player, value):
    return dimension_error_message(player, value, 0)

def originality_2_error_message(player, value):
    return dimension_error_message(player, value, 1)

def originality_3_error_message(player, value):
    return dimension_error_message(player, value, 2)

def originality_4_error_message(player, value):
    return dimension_error_message(player, value, 3)

def originality_5_error_message(player, value):
    return dimension_error_message(player, value, 4)

def originality_6_error_message(player, value):
    return dimension_error_message(player, value, 5)

def originality_7_error_message(player, value):
    return dimension_error_message(player, value, 6)

def originality_8_error_message(player, value):
    return dimension_error_message(player, value, 7)

def originality_9_error_message(player, value):
    return dimension_error_message(player, value, 8)

def originality_10_error_message(player, value):
    return dimension_error_message(player, value, 9)

def originality_11_error_message(player, value):
    return dimension_error_message(player, value, 10)

def originality_12_error_message(player, value):
    return dimension_error_message(player, value, 11)

def originality_13_error_message(player, value):
    return dimension_error_message(player, value, 12)

def originality_14_error_message(player, value):
    return dimension_error_message(player, value, 13)

def originality_15_error_message(player, value):
    return dimension_error_message(player, value, 14)

def originality_16_error_message(player, value):
    return dimension_error_message(player, value, 15)

def originality_17_error_message(player, value):
    return dimension_error_message(player, value, 16)

def originality_18_error_message(player, value):
    return dimension_error_message(player, value, 17)

def originality_19_error_message(player, value):
    return dimension_error_message(player, value, 18)

def originality_20_error_message(player, value):
    return dimension_error_message(player, value, 19)

def originality_21_error_message(player, value):
    return dimension_error_message(player, value, 20)

def originality_22_error_message(player, value):
    return dimension_error_message(player, value, 21)

def originality_23_error_message(player, value):
    return dimension_error_message(player, value, 22)

def originality_24_error_message(player, value):
    return dimension_error_message(player, value, 23)

def originality_25_error_message(player, value):
    return dimension_error_message(player, value, 24)

def originality_26_error_message(player, value):
    return dimension_error_message(player, value, 25)

def originality_27_error_message(player, value):
    return dimension_error_message(player, value, 26)

def originality_28_error_message(player, value):
    return dimension_error_message(player, value, 27)

def originality_29_error_message(player, value):
    return dimension_error_message(player, value, 28)

def originality_30_error_message(player, value):
    return dimension_error_message(player, value, 29)

class Overall_Creativity(Page):
    timeout_seconds = 5000
    def is_displayed(player):
        return player.player_role == 'Ratender'
    
    def vars_for_template(player):
        mystery_word = C.MYSTERY_WORDS[player.round_number - 1]
        hint_groups = [g for g in player.subsession.get_groups() if g.get_players()[0].player_role == 'Hinweisgebende']
        index = (player.id_in_group + player.round_number) % len(hint_groups)  
        pairs = hint_groups[index].get_players()[0].pairsafter.split(', ')
        while '' in pairs:
            pairs.remove('')
        player.number_pairs_after = len(pairs)
        choices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        return dict(mystery_word=mystery_word, pairs=pairs, choices = choices, number_pairs = player.number_pairs_after)
    
    form_model = 'player'
    form_fields = ['creativity_1', 'creativity_2', 'creativity_3', 'creativity_4', 'creativity_5', 'creativity_6', 'creativity_7', 'creativity_8', 'creativity_9', 'creativity_10', 'creativity_11', 'creativity_12', 'creativity_13', 'creativity_14', 'creativity_15', 'creativity_16', 'creativity_17', 'creativity_18', 'creativity_19', 'creativity_20', 'creativity_21', 'creativity_22', 'creativity_23', 'creativity_24', 'creativity_25', 'creativity_26', 'creativity_27', 'creativity_28', 'creativity_29', 'creativity_30']
    
def creativity_1_error_message(player, value):
    return dimension_error_message(player, value, 0)

def creativity_2_error_message(player, value):
    return dimension_error_message(player, value, 1)
    
def creativity_3_error_message(player, value):
    return dimension_error_message(player, value, 2)

def creativity_4_error_message(player, value):
    return dimension_error_message(player, value, 3)

def creativity_5_error_message(player, value):
    return dimension_error_message(player, value, 4)
    
def creativity_6_error_message(player, value):
    return dimension_error_message(player, value, 5)

def creativity_7_error_message(player, value):
    return dimension_error_message(player, value, 6)
    
def creativity_8_error_message(player, value):
    return dimension_error_message(player, value, 7)

def creativity_9_error_message(player, value):
    return dimension_error_message(player, value, 8)
    
def creativity_10_error_message(player, value):
    return dimension_error_message(player, value, 9)
    
def creativity_11_error_message(player, value):
    return dimension_error_message(player, value, 10)
    
def creativity_12_error_message(player, value):
    return dimension_error_message(player, value, 11)
    
def creativity_13_error_message(player, value):
    return dimension_error_message(player, value, 12)
    
def creativity_14_error_message(player, value):
    return dimension_error_message(player, value, 13)
    
def creativity_15_error_message(player, value):
    return dimension_error_message(player, value, 14)

def creativity_16_error_message(player, value):
    return dimension_error_message(player, value, 15)

def creativity_17_error_message(player, value):
    return dimension_error_message(player, value, 16)

def creativity_18_error_message(player, value):
    return dimension_error_message(player, value, 17)

def creativity_19_error_message(player, value):
    return dimension_error_message(player, value, 18)

def creativity_20_error_message(player, value):
    return dimension_error_message(player, value, 19)

def creativity_21_error_message(player, value):
    return dimension_error_message(player, value, 20)

def creativity_22_error_message(player, value):
    return dimension_error_message(player, value, 21)

def creativity_23_error_message(player, value):
    return dimension_error_message(player, value, 22)

def creativity_24_error_message(player, value):
    return dimension_error_message(player, value, 23)

def creativity_25_error_message(player, value):
    return dimension_error_message(player, value, 24)

def creativity_26_error_message(player, value):
    return dimension_error_message(player, value, 25)

def creativity_27_error_message(player, value):
    return dimension_error_message(player, value, 26)

def creativity_28_error_message(player, value):
    return dimension_error_message(player, value, 27)

def creativity_29_error_message(player, value):
    return dimension_error_message(player, value, 28)

def creativity_30_error_message(player, value):
    return dimension_error_message(player, value, 29)

def get_sorted_scores(groups, attribute):
    scores = [getattr(group, attribute) for group in groups]
    return sorted(scores, reverse=True)

def get_overall_scores(group, attribute):
    subsession = group.subsession
    groups = [g for g in subsession.get_groups() if g.get_players()[0].player_role == 'Hinweisgebende']
    return get_sorted_scores(groups, attribute)

def get_overall_scores2(player, attribute):
    players = [player] + player.get_others_in_group() 
    return get_sorted_scores2(players, attribute)

def get_sorted_scores2(players, attribute):
    scores = [getattr(player, attribute) for player in players]
    return sorted(scores, reverse=True)

def calculate_rank(score, sorted_scores):
    rank = 1
    ranks = []
    for i in range(len(sorted_scores)):
        if i > 0 and sorted_scores[i] != sorted_scores[i - 1]:
            rank = len(ranks) + 1
        ranks.append(rank)
    return ranks[sorted_scores.index(score)], ranks

def calculate_payoff(rank, ranks):
    payoffs = {1: 20, 2: 15, 3: 12, 4: 10}
    rank_count = ranks.count(rank)
    if rank_count > 1:
        total_payoff = 0
        for r in range(rank, rank + rank_count):
            total_payoff += payoffs.get(r, 8) 
        return total_payoff / rank_count
    else:
        return payoffs.get(rank, 8)

class Score(Page):
    timeout_seconds = 2000
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende' and player.participant.treatment == 3 and player.round_number	== C.NUM_ROUNDS
    def vars_for_template(player):
        overall_score = get_overall_scores(player.group, 'quality')
        rank, ranks = calculate_rank(player.group.quality, overall_score)
        player.payoff = round(calculate_payoff(rank, ranks), 0)
        number_groups = len(overall_score)
        return dict(overall_score = overall_score, score = player.group.quality, payoff = player.payoff, rank = rank, number_groups = number_groups)
    
class Score2(Page):
    timeout_seconds = 2000
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende' and player.participant.treatment == 2 and player.round_number	== C.NUM_ROUNDS
    def vars_for_template(player):
        overall_quantity = get_overall_scores(player.group, 'quantity')
        rank, ranks = calculate_rank(player.group.quantity, overall_quantity)
        player.payoff = round(calculate_payoff(rank, ranks), 0)
        number_groups = len(overall_quantity)
        return dict(overall_quantity = overall_quantity, quantity = player.group.quantity, payoff = player.payoff, rank = rank, number_groups = number_groups)
    
class Score3(Page): 
    timeout_seconds = 2000
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende' and player.participant.treatment == 4 and player.round_number	== C.NUM_ROUNDS
    def vars_for_template(player):
        originality = round(player.group.originality, 2)
        overall_originality = get_overall_scores(player.group, 'originality')
        rank, ranks = calculate_rank(player.group.originality, overall_originality)
        player.payoff = round(calculate_payoff(rank, ranks), 0)
        number_groups = len(overall_originality)
        overall_originality = [round(score, 2) for score in overall_originality]
        return dict(overall_originality = overall_originality, originality = originality, payoff = player.payoff, rank = rank, number_groups = number_groups)
    
class Score4(Page):
    timeout_seconds = 2000
    def is_displayed(player):
        return player.player_role == 'Ratender' and player.round_number	== C.NUM_ROUNDS
    def vars_for_template(player):
        overall_score = get_overall_scores2(player, 'quality_score')
        rank, ranks = calculate_rank(player.quality_score, overall_score)
        player.payoff = round(calculate_payoff(rank, ranks), 0)
        number_groups = len(overall_score)
        return dict(overall_score = overall_score, score = player.quality_score, payoff = player.payoff, rank = rank, number_groups = number_groups)

class Questions1(Page):
    template_name = 'experiment/Questions1.html'
    timeout_seconds = 3000
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    form_model = 'player'
    form_fields = ['ideagen1', 'ideagen2', 'ideagen3', 'ideagen4', 'feedback1', 'feedback2', 'feedback3', 'feedback4', 'group1', 'group2', 'group3', 'group4', 'group5', 'group6', 'group7', 'group8', 'group9', 'group10', 'motivation1', 'motivation2', 'motivation3', 'motivation4', 'incentives1', 'incentives2', 'incentives3', 'guesser1', 'guesser2', 'guesser3', 'guesser4', 'guesser5', 'guesser6', 'guesser7', 'guesser8', 'guesser9', 'guesser10', 'guesser11', 'guesser12']
    def error_message(player, values):
        if player.player_role == 'Hinweisgebende':            
            for i in range(1, 5):
                if values[f'ideagen{i}'] == None:
                    return f'Bitte beantworten Sie Frage {i}!'
            for i in range(1, 5):
                if values[f'feedback{i}'] == None:
                    return f'Bitte beantworten Sie Frage {i+4}!'
            for i in range(1, 9):
                if values[f'group{i}'] == None:
                    return f'Bitte beantworten Sie Frage {i+8}!'
            if player.participant.treatment == 1:
                for i in range(1, 3):
                    if values[f'motivation{i}'] == None:
                        return f'Bitte beantworten Sie Frage {i+16}!'
            else:
                for i in range(1, 5):
                    if values[f'motivation{i}'] == None:
                        return f'Bitte beantworten Sie Frage {i+16}!'
                for i in range(1, 3):
                    if values[f'group{i+8}'] == None:
                        return f'Bitte beantworten Sie Frage {i+20}!'
                for i in range(1, 4):
                    if values[f'incentives{i}'] == None:
                        return f'Bitte beantworten Sie Frage {i+22}!'
        else:
            for i in range(2, 13):
                if values[f'guesser{i}'] == None:
                    return f'Bitte beantworten Sie Frage {i}!'
    def vars_for_template(player):
        treatment = player.participant.treatment
        if treatment == 1:
            label1 = ''
            label2 = ''
            label3 = ''
        if treatment == 2:
            label1 = '<b>23. </b>Meine Gruppenmitglieder und ich haben uns stark auf die Quantität der Hinweispaare konzentriert.'
            label2 = '<b>24. </b>Durch die Fokussierung auf Quantität, haben wir Qualität und Originalität vernachlässigt.'
            label3 = '<b>25. </b>Durch mehr Anstrengung konnte ich meine Ideen in Bezug auf Quantität verbessern.'
        elif treatment == 3:
            label1 = '<b>23. </b>Meine Gruppenmitglieder und ich haben uns stark auf die Qualität der Hinweispaare konzentriert.'
            label2 = '<b>24. </b>Durch die Fokussierung auf Qualität, haben wir Quantität und Originalität vernachlässigt.'
            label3 = '<b>25. </b>Durch mehr Anstrengung konnte ich meine Ideen in Bezug auf Qualität verbessern.'
        elif treatment == 4:
            label1 = '<b>23. </b>Meine Gruppenmitglieder und ich haben uns stark auf die Originalität der Hinweispaare konzentriert.'
            label2 = '<b>24. </b>Durch die Fokussierung auf Originalität, haben wir Quantität und Qualität vernachlässigt.'
            label3 = '<b>25. </b>Durch mehr Anstrengung konnte ich meine Ideen in Bezug auf Originalität verbessern.'
        return {'incentives1_label': label1, 'incentives2_label': label2, 'incentives3_label': label3}

class Questions2(Page):
    template_name = 'experiment/Questions2.html'
    timeout_seconds = 300
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    form_model = 'player'
    form_fields = ['age', 'gender', 'study', 'german','risk', 'ambiguity', 'creative_self1', 'creative_self2', 'creative_self3', 'creative_self4', 'creative_self5', 'cognitive1', 'cognitive2', 'cognitive3', 'cognitive4', 'cognitive5', 'general_motivation1', 'general_motivation2', 'general_group1', 'general_group2', 'general_group3', 'Bildende_Kunst', 'Musik', 'Tanz', 'Architektur', 'Literatur', 'Humor', 'Erfindungen', 'Wissenschaftliche_Entdeckungen', 'Theater_und_Film', 'Kochen']
    def error_message(player, values):
        if player.player_role == 'Hinweisgebende':
            for i in range(1, 4):
                if values[f'general_group{i}'] == None:
                    return f'Bitte beantworten Sie Frage {i+18}!'

class CreativeActivities(Page):
    timeout_seconds = 1000
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    def vars_for_template(player):
        choices = [1, 2, 3, 4, 5, 6, 7]
        ratings = [player.Bildende_Kunst, player.Musik, player.Tanz, player.Architektur, player.Literatur, player.Humor, player.Erfindungen, player.Wissenschaftliche_Entdeckungen, player.Theater_und_Film, player.Kochen]
        return dict(ratings = ratings, choices = choices)
    form_model = 'player'
    form_fields = ['Bildende_Kunst_2_1', 'Bildende_Kunst_2_2', 'Bildende_Kunst_2_3', 'Bildende_Kunst_2_4', 'Bildende_Kunst_2_5', 'Bildende_Kunst_2_6', 'Bildende_Kunst_2_7', 'Musik_2_1', 'Musik_2_2', 'Musik_2_3', 'Musik_2_4', 'Musik_2_5', 'Musik_2_6', 'Musik_2_7', 'Tanz_2_1', 'Tanz_2_2', 'Tanz_2_3', 'Tanz_2_4', 'Tanz_2_5', 'Tanz_2_6', 'Tanz_2_7', 'Architektur_2_1', 'Architektur_2_2', 'Architektur_2_3', 'Architektur_2_4', 'Architektur_2_5', 'Architektur_2_6', 'Architektur_2_7', 'Literatur_2_1', 'Literatur_2_2', 'Literatur_2_3', 'Literatur_2_4', 'Literatur_2_5', 'Literatur_2_6', 'Literatur_2_7', 'Humor_2_1', 'Humor_2_2', 'Humor_2_3', 'Humor_2_4', 'Humor_2_5', 'Humor_2_6', 'Humor_2_7', 'Erfindungen_2_1', 'Erfindungen_2_2', 'Erfindungen_2_3', 'Erfindungen_2_4', 'Erfindungen_2_5', 'Erfindungen_2_6', 'Erfindungen_2_7', 'Wissenschaftliche_Entdeckungen_2_1', 'Wissenschaftliche_Entdeckungen_2_2', 'Wissenschaftliche_Entdeckungen_2_3', 'Wissenschaftliche_Entdeckungen_2_4', 'Wissenschaftliche_Entdeckungen_2_5', 'Wissenschaftliche_Entdeckungen_2_6', 'Wissenschaftliche_Entdeckungen_2_7', 'Theater_und_Film_2_1', 'Theater_und_Film_2_2', 'Theater_und_Film_2_3', 'Theater_und_Film_2_4', 'Theater_und_Film_2_5', 'Theater_und_Film_2_6', 'Theater_und_Film_2_7', 'Kochen_2_1', 'Kochen_2_2', 'Kochen_2_3', 'Kochen_2_4', 'Kochen_2_5', 'Kochen_2_6', 'Kochen_2_7']

class Identification(Page):
    timeout_seconds = 270
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende' and player.round_number == C.NUM_ROUNDS
    form_model = 'player'
    form_fields = ['circle_overlap']
 
    def js_vars(player: Player):
        return {}
    
class AUT(Page):    
    timeout_seconds = 240
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS and player.player_role == 'Hinweisgebende' 
    form_model = 'player'
    form_fields = ['AUT', 'AUT2']

class DAT(Page):
    timeout_seconds = 270
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    form_model = 'player'
    form_fields = ['word1', 'word2', 'word3', 'word4', 'word5', 'word6', 'word7', 'word8', 'word9', 'word10']
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.invalid_DAT = True
            return player.invalid_DAT
        else:
            player.invalid_DAT = False
            return player.invalid_DAT

class RAT_Instructions(Page):
    timeout_seconds = 300
    def is_displayed(player):
        return player.player_role == 'Ratender' and player.round_number == C.NUM_ROUNDS

class RAT(Page):
    timeout_seconds = 300
    def is_displayed(player):
        return player.player_role == 'Ratender' and player.round_number == C.NUM_ROUNDS
    form_model = 'player'
    form_fields = ['rat1', 'rat2', 'rat3', 'rat4', 'rat5']
    
class DictatorGame(Page):
    timeout_seconds = 60000
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS and player.player_role == 'Hinweisgebende' 
    form_model = 'player'
    form_fields = ['dictator_game']

class FinalPage(Page):
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    def vars_for_template(player):
        if player.player_role == 'Hinweisgebende' and player.participant.treatment == 1:
            player.payoff = 13
            player.payoff_calculated = False
        if player.payment_allocator == 1:
            allocator_payoff = 10 - player.dictator_game
        else:
            allocator_payoff = 0
        if player.payment_receiver == 1:
            for p in player.subsession.get_players():
                if p.payment_allocator == 1:
                    receiver_payoff = p.dictator_game
        else:
            receiver_payoff = 0
        if player.payoff_calculated == False:
            player.payoff = player.payoff + receiver_payoff + allocator_payoff
            player.payoff_calculated = True
        player.payoff = round(player.payoff)
        return dict(allocator_payoff = allocator_payoff, receiver_payoff = receiver_payoff, payoff = player.payoff)

# WAIT PAGES

class GroupWaitPage(WaitPage):
    template_name = 'experiment/GroupWaitPage.html'
    def is_displayed(player):
        return player.round_number == 1
        
class Generation_WaitPage(WaitPage):
    title_text = "Vielen Dank für Ihre Hinweispaare!"
    body_text = "Bitte warten Sie, bis alle ihre Hinweispaare abgegeben haben."
    wait_for_all_players = True
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende'
    
class Clue_WaitPage(WaitPage):
    title_text = "Vielen Dank für Ihr Feedback!"
    body_text = "Bitte warten Sie, bis all Ihre Gruppenmitglieder ihr Feedback abgegeben haben."
    wait_for_all_players = True
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende'

class VotingWaitPage(WaitPage):
    title_text = "Vielen Dank für Ihre Hinweispaare"
    body_text = "Bitte warten Sie, bis alle ihre Hinweispaare abgegeben haben."
    wait_for_all_players = True
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende'   

class VotingResultWaitPage(WaitPage):
    title_text = "Vielen Dank für Ihre Abstimmung"
    body_text = "Bitte warten Sie, bis alle ihre Stimmen abgegeben haben."
    wait_for_all_players = True
    def is_displayed(player):
        return player.player_role == 'Hinweisgebende'
       
class GuesserWaitPage(WaitPage):
    title_text = "Sie können bald das geheime Wort erraten!"
    body_text = "Bitte warten Sie, bis die Gruppen ihre Hinweispaare generiert haben. Dies kann einige Minuten dauern."
    def is_displayed(player): 
        return player.player_role == 'Ratender'   
    wait_for_all_groups = True    
   
class ResultsWaitPage(WaitPage):
    title_text = "Sie sind fertig für diese Runde!"
    body_text = "Bitte warten Sie, bis alle Teilnehmenden die Runde abgeschlossen haben. Dies kann einige Minuten dauern."
    wait_for_all_groups = True

page_sequence = [GroupWaitPage, Overview, Intro, Intro2, Procedure, Rules, Instructions, Payment, UnderstandPage, Round, Generation_Page, Generation_WaitPage, Discussion, Clue_WaitPage, Clue_Page, VotingWaitPage, Voting_Page, VotingResultWaitPage, GuesserWaitPage, Guess_Page1, Guess_Page2, Guess_Page3, PairCheck, VotingResultPage, ResultsWaitPage, Results, Usefulness, Originality, Overall_Creativity, Score, Score2, Score3, Score4, DictatorGame, Questions1, Identification, Questions2, CreativeActivities, AUT, RAT_Instructions, RAT, DAT, FinalPage]