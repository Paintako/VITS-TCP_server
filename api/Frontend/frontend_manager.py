from .Mandarine import zh_frontend
from .Taiwanese import tw_frontend
# from .Hakka import hakka_frontend
from .English import en_frontend
# from .Indonesian import id_frontend
from .phonemes import symbols
from typing import List
import re

class frontend_manager:
    def __init__(self):
        self.frontend = None
        self.phone_list = symbols.symbols
        # Mappings from symbol to numeric ID and vice versa:
        self._symbol_to_id = {s: i for i, s in enumerate(symbols.symbols)}
        self._id_to_symbol = {i: s for i, s in enumerate(symbols.symbols)}

    def set_frontend(self, language: str):
        if language == 'zh':
            self.frontend = zh_frontend.zh_frontend()
        elif language == 'tw':
            self.frontend = tw_frontend.tw_frontend(g2p_model="tw")
        # elif language == 'hakka':
        #     self.frontend = hakka_frontend.hakka_frontend()
        elif language == 'en':
            self.frontend = en_frontend.en_frontend()
        # elif language == 'id':
        #     self.frontend = id_frontend.id_frontend()
        else:
            raise ValueError('Language not supported')
    
    def spliteKeyWord(self, str: str) -> list:
        regex = r"(?:[.,!?;：，；。？！“”‘’':,;.?!()（）'])|<t>.*?</t>|<ha>.*?</ha>|:<ha>.*?</ha>:|[\u4e00-\ufaff0-9]+|[a-zA-Z\s']+|[^\u4e00-\ufaff0-9a-zA-Z\s']+"
        matches = re.findall(regex, str, re.UNICODE)
        return matches

    def get_phonemes(self, sentence: str) -> List[str]:
        sentences = self.spliteKeyWord(sentence)
        result = []
        for seg in sentences:
            if seg == '':
                continue
            phonemes = self.frontend.get_phonemes(seg)
            result.append(phonemes)
        return result
            
        

    def phonemes_to_id(self, phonemes: List[str]) -> List[int]:
        sequence = []    
        for symbol in phonemes:
            symbol = symbol.strip()
            if symbol == '':
                continue
            try:
                symbol_id = self._symbol_to_id[symbol]
            except:
                symbol_id = 0
            sequence += [symbol_id]
        return sequence

   