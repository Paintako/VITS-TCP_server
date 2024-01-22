from typing import Dict, List, Tuple

from .phoneme_process.syllable import get_syllable

import sys
import os
sys.path.append(f'{os.path.dirname(os.path.abspath(__file__))}/../../')
from logs import service_logger

class id_frontend():
    def __init__(self) -> None:
        self.punc = "：，；。？！“”‘’':,;.?!"
        self.syllable = get_syllable
        self.logger = service_logger.ServiceLogger()
        
    def get_phonemes(self, sentence: str) -> Tuple[List[List[str]], bool]:
        try:
            phonemes = []    
            self.logger.info(f'Processing sentence: {sentence}')
            text = self.syllable(sentence)
            for each in text.split(" "):
                print(each)
                phonemes.append(f'{each}3')
            self.logger.info(f'Converting {sentence} to phonemes: {phonemes}')
            return phonemes, True
        except:
            self.logger.error(f'Error transforming: {sentence}')
            return [], False


if __name__ == '__main__':
    words = input('input: ').split()
    for word in words:
        print(get_syllable(word))