from .Mandarine import zh_frontend
from .Taiwanese import tw_frontend
from .Hakka import hakka_frontend
from .English import en_frontend
from .Indonesian import id_frontend
from .phonemes import symbols
from typing import List, Tuple
import re

import os
import sys
sys.path.append(f'{os.path.dirname(os.path.abspath(__file__))}/..//')
from logs import service_logger

class frontend_manager:
    def __init__(self):
        self.frontend = None
        self.phone_list = symbols.symbols
        # Mappings from symbol to numeric ID and vice versa:
        self._symbol_to_id = {s: i for i, s in enumerate(symbols.symbols)}
        self._id_to_symbol = {i: s for i, s in enumerate(symbols.symbols)}
        self.language = None
        self.logger = service_logger.ServiceLogger()

    def set_frontend(self, language: str):
        if language == 'zh':
            self.frontend = zh_frontend.zh_frontend()
            self.language = 'zh'

        elif language == 'tw':
            self.frontend = tw_frontend.tw_frontend(g2p_model="tw")
            self.language = 'tw'

        elif language == 'hakka':
            self.frontend = hakka_frontend.hakka_frontend(g2p_model='hedusi')
            self.language = 'hakka' 

        elif language == 'en':
            self.frontend = en_frontend.en_frontend()
            self.language = 'en'

        elif language == 'id':
            self.frontend = id_frontend.id_frontend()
            self.language = 'id'
        
        elif language == 'tw_tl':
            self.frontend = tw_frontend.tw_frontend(g2p_model="tw_tl")
            self.language = 'tw_tl'

        else:
            raise ValueError('Language not supported')
    
    def spliteKeyWord(self, text: str) -> list:
        if self.language == 'en':
            regex = r"(?:[.,!?;：，；。？！“”‘’':,;.?!()（）'])|<t>.*?</t>|<ha>.*?</ha>|:<ha>.*?</ha>:|[\u4e00-\ufaff0-9]+|[a-zA-Z\s']+|[^\u4e00-\ufaff0-9a-zA-Z\s']+"
        elif self.language == 'id':
            regex = r"[^.,!?;:]+[.,!?;:]?"
        else:
            regex = r"(?:[.,!?;：，；。？！“”‘’':,;.?!()（）'])|<t>.*?</t>|<ha>.*?</ha>|:<ha>.*?</ha>:|[\u4e00-\ufaff0-9]+|[a-zA-Z\s]+|[^\u4e00-\ufaff0-9a-zA-Z\s']+"
        sentences = re.findall(regex, text, re.UNICODE)
        return sentences

    def get_phonemes(self, sentence: str) -> Tuple[List[str], bool]:
        if self.language == 'tw_tl':
            sentences = [sentence]
        else:
            sentences = self.spliteKeyWord(sentence)
        self.logger.info(f'length of segmentations: {len(sentences)}, After spliting puncs: {sentences}')
        result = []
        for seg in sentences:
            if seg == '':
                continue
            phonemes, status = self.frontend.get_phonemes(seg)
            if status == False:
                self.logger.error(f'Error transforming: {seg}, result: {phonemes}')
                return [], False
            result.append(phonemes)
        return result, True
            
        

    def phonemes_to_id(self, phonemes: List[str]) -> List[int]:
        sequence = []    
        for symbol in phonemes:
            symbol = symbol.strip()
            if symbol == '':
                continue
            try:
                symbol_id = self._symbol_to_id[symbol]
            except:
                # self.logger.error(f'None existing {symbol}')
                self.logger.info(f'None existing {symbol}')
                symbol_id = 0
            sequence += [symbol_id]
        return sequence

   