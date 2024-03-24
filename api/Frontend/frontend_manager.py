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
from logs.service_logger import service_logger

class frontend_manager:
    def __init__(self):
        self.frontend = None
        self.phone_list = symbols.symbols
        # Mappings from symbol to numeric ID and vice versa:
        self._symbol_to_id = {s: i for i, s in enumerate(symbols.symbols)}
        self._id_to_symbol = {i: s for i, s in enumerate(symbols.symbols)}
        self.language = None
        self.logger = service_logger()

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

        elif language == 'mix':
            self.frontend = None
            self.language = 'mix'

        else:
            raise ValueError('Language not supported')
    
    def spliteKeyWord(self, text: str) -> list:
        if self.language == 'en' or self.language == 'id':
            regex = r'[.,;!?]'
            sentences = re.split(regex, text)
            print(sentences)

        elif self.language == 'mix':
            pattern = re.compile(r'<(en|zh|t|ha|tw|id)>(.*?)<\/\1>')
            matches = pattern.findall(text)
            sentences = [(tag, content) for tag, content in matches]

        else:
            regex = r"(?:[.,!?;：，；。？！“”‘’':,;.?!()（）'])|<t>.*?</t>|<ha>.*?</ha>|:<ha>.*?</ha>:|[\u4e00-\ufaff0-9]+|[a-zA-Z\s]+|[^\u4e00-\ufaff0-9a-zA-Z\s']+"
            sentences = re.findall(regex, text, re.UNICODE)
            print(sentences)
        
        
        return sentences


    def get_phonemes(self, sentence: str) -> Tuple[List[str], bool]:

        # process punctuations
        sentence = re.sub(r'[「」]', '', sentence)
        sentence = re.sub(r'[“”]', '', sentence)
        sentence = re.sub(r'[‘’]', '', sentence)
        sentence = re.sub(r'[（(：)）＿]', '', sentence)
        sentence = re.sub(r'[、]', '，', sentence)

        if self.language == 'tw_tl':
            regex = r"[.,;!?.,!?;：，；。？！“”‘’':,;.?!()（）]"
            sentences = re.split(regex, sentence)
        else:
            sentences = self.spliteKeyWord(sentence)
        self.logger.info(f'length of segmentations: {len(sentences)}, After spliting puncs: {sentences}', extra={"ipaddr":""})
        result = []
        for seg in sentences:
            if self.language == 'mix':
                tag, content = seg
                print(f'tag: {tag}, content: {content}')
                if content == '':
                    continue
                if tag == 'en':
                    frontend = en_frontend.en_frontend()
                    phonemes, status = frontend.get_phonemes(content)
                    if status == False:
                        self.logger.error(f'Error transforming: {content}, result: {phonemes}', extra={"ipaddr":""})
                        return [], False
                    result.append(phonemes)
                if tag == 'zh':
                    frontend = zh_frontend.zh_frontend()
                    phonemes, status = frontend.get_phonemes(content)
                    if status == False:
                        self.logger.error(f'Error transforming: {content}, result: {phonemes}', extra={"ipaddr":""})
                        return [], False
                    result.append(phonemes)
                if tag == 't':
                    frontend = tw_frontend.tw_frontend(g2p_model="tw")
                    phonemes, status = frontend.get_phonemes(content)
                    if status == False:
                        self.logger.error(f'Error transforming: {content}, result: {phonemes}', extra={"ipaddr":""})
                        return [], False
                    result.append(phonemes)
                if tag == 'ha':
                    frontend = hakka_frontend.hakka_frontend(g2p_model='hedusi')
                    phonemes, status = frontend.get_phonemes(content)
                    if status == False:
                        self.logger.error(f'Error transforming: {content}, result: {phonemes}', extra={"ipaddr":""})
                        return [], False
                    result.append(phonemes)
                if tag == 'id':
                    frontend = id_frontend.id_frontend()
                    phonemes, status = frontend.get_phonemes(content)
                    if status == False:
                        self.logger.error(f'Error transforming: {content}, result: {phonemes}', extra={"ipaddr":""})
                        return [], False
                    result.append(phonemes)

                
            else:
                if seg == '':
                    continue
                phonemes, status = self.frontend.get_phonemes(seg)
                if status == False:
                    self.logger.error(f'Error transforming: {seg}, result: {phonemes}', extra={"ipaddr":""})
                    return [], False
                result.append(phonemes)

        if self.language == 'mix':
            final_list = []
            for each in result:
                for ph in each:
                    final_list.append(ph)
            print('after mix')
            print(final_list)
            return [final_list], True
        print(f'phonemes: {result}')
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
                self.logger.error(f'None existing {symbol}, continue', extra={"ipaddr":""})
                symbol_id = 0
            sequence += [symbol_id]
        return sequence

   