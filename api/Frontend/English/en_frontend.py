from typing import Any, List, Tuple
import os
import sys

sys.path.append(f'{os.path.dirname(os.path.abspath(__file__))}/../../')
from logs import service_logger

dict_path = os.path.dirname(os.path.abspath(__file__))
pinyin = {}
with open(os.path.join(dict_path,'pinyin.dict'), 'r', encoding='utf8') as f:
    lines = f.readlines()

for line in lines:
    line = line.strip().split("\t")
    pinyin[line[0]] = line[1]

class en_frontend():
    def __init__(self) -> None:
        self.punc = "：，；。？！“”‘’':,;.?!"
        self.pinyin = pinyin
        self.logger = service_logger.ServiceLogger()
        
    def get_phonemes(self, sentence: str) -> Tuple[List[List[str]], bool]:
        try:
            phonemes = []    
            self.logger.info(f'Processing sentence: {sentence}')

            for word in sentence.split(" "):
                word = word.upper().strip()
                try:
                    ph = self.pinyin[word]
                    for p in ph.split(" "):    
                        phonemes.append(p.strip())
                except: 
                    self.logger.error(f'Word {word} not found in dictionary')
                    continue
            self.logger.info(f'Converting {sentence} to phonemes: {phonemes}')
            return phonemes, True
        except:
            self.logger.error(f'Error transforming: {sentence}')
            return [], False
            
if __name__ == "__main__":
    frontend = en_frontend()
    sentence = 'Trying to be better'
    phonemes = frontend.get_phonemes(sentence)
    print(phonemes)