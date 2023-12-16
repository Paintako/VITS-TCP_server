""" from https://github.com/keithito/tacotron """

'''
Defines the set of symbols used in text input to the model.
'''
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, 'phone_collection', 'mix_5_phone.txt')

_pad        = '_'
__punctuation = ', '
# Export all symbols:
_phones = []
with open(file_path,'r',encoding='utf8') as f:
    lines = f.readlines()
    for each in lines:
        _phones.append(each.split(" ")[1].strip())
symbols = [_pad] + _phones + list(__punctuation)
# Special symbol ids
SPACE_ID = symbols.index(" ")
 