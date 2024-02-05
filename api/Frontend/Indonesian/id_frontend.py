from typing import Dict, List, Tuple

from .phoneme_process.syllable import get_syllable

import sys
import os
sys.path.append(f'{os.path.dirname(os.path.abspath(__file__))}/../../')
from logs.service_logger import service_logger


dict_path = os.path.dirname(os.path.abspath(__file__)).replace("Indonesian", "English")
pinyin = {}
with open(os.path.join(dict_path,'pinyin.dict'), 'r', encoding='utf8') as f:
    lines = f.readlines()

for line in lines:
    line = line.strip().split("\t")
    pinyin[line[0]] = line[1]


class id_frontend():
    def __init__(self) -> None:
        self.punc = "：，；。？！“”‘’':,;.?!"
        self.syllable = get_syllable
        self.logger = service_logger()
        self.pinyin = pinyin
        
    def get_phonemes(self, sentence: str) -> Tuple[List[List[str]], bool]:
        try:
            phonemes = []    
            self.logger.info(f'Processing sentence: {sentence}', extra={"ipaddr":""})

            # saya suka apel A pel
            for each in sentence.split(" "):   
                flag = 0
                for char in each:
                    if char.isupper():    
                        flag = 1
                        # this segment is for English, not Indonesian
                        ph = self.pinyin[each]
                        for p in ph.split(" "):    
                            phonemes.append(p.strip())
                        break
                
                if flag == 1:
                    continue                    
                tmp = self.syllable(each)
                for each in tmp.split(" "):
                    print(each)
                    phonemes.append(f'{each}3')
            
            phonemes = [ph for ph in phonemes if ph != "3"]
            print(phonemes)
            # text = self.syllable(sentence)
            # for each in text.split(" "):
            #     print(each)
            #     phonemes.append(f'{each}3')
            self.logger.info(f'Converting {sentence} to phonemes: {phonemes}', extra={"ipaddr":""})
            return phonemes, True
        except:
            self.logger.error(f'Error transforming: {sentence}', extra={"ipaddr":""}, exc_info=True)
            return [], False


if __name__ == '__main__':
    words = input('input: ').split()
    for word in words:
        print(get_syllable(word))