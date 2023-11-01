with open('C:/Users/sarrazie/Desktop/otree/testproject/justone_deutsch/wordlist-german.txt', 'r', encoding='utf-8') as file:
    text = file.read()

special_char_map = {'ä':'ae', 'ü':'ue', 'ö':'oe', 'ß':'ss'}
text = text.translate(special_char_map)
text_lower = text.lower()

text_replaced = (
    text
    .replace('ä', 'ae')
    .replace('ö', 'oe')
    .replace('ü', 'ue')
    .replace('ß', 'ss')
    .replace('Ä', 'Ae')
    .replace('Ö', 'Oe')
    .replace('Ü', 'Ue')
)
text_lower = text_replaced.lower()
with open('C:/Users/sarrazie/Desktop/otree/testproject/justone_deutsch/wordlist-german-2.txt', 'w', encoding='utf-8') as new_file:
    new_file.write(text_lower)
