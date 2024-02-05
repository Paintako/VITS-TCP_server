from typing import Dict
from typing import List
from typing import Tuple

# processing pipeline
from .phoneme_process.ch2hak import askForService as ch2hak

import sys
import os
sys.path.append(f'{os.path.dirname(os.path.abspath(__file__))}/../../')
from logs.service_logger import service_logger

class hakka_frontend():
    def __init__(self, g2p_model: str):
        self.punc = "：，；。？！“”‘’':,;.?!"
        self.g2p_model = g2p_model
        self.logger = service_logger()
        self.ch2hak = ch2hak

    def _get_initials_finals(self, sentence: str) -> Tuple[List[List[str]], str]:
        initials = []
        finals = []
        # tts_client = TTSClient()
        if self.g2p_model == "hakka_hailu": 
            # tts_client.set_language(model='heduhai')
            accent = 'heduhai'
        else:
            # tts_client.set_language(model='hedusi')
            accent = 'hedusi'

        print('sentence = ', sentence)
        # hakka_pinyin = tts_client.askForService(text=sentence)
        hakka_pinyin = self.ch2hak(text=sentence, accent=accent, direction='hkji2pin')
        if (hakka_pinyin['hakkaTRN'] == 'Exceptions occurs'):
            self.logger.error(f'Error transforming: {sentence}, result: {hakka_pinyin["hakkaTRN"]}', extra={"ipaddr":""})
            return [], [], False
        hakka_pinyin = hakka_pinyin['hakkaTRN'][-2]
        hakka_pinyin = hakka_pinyin.replace(' 25 ', ' ， ')
        hakka_pinyin = hakka_pinyin.replace(' 23 ', ' ， ')
        hakka_pinyin = hakka_pinyin.replace("XXX", '，' )
        self.logger.info(f'Transforming: {sentence}, result: {hakka_pinyin}', extra={"ipaddr":""})

        orig_initials, orig_finals = self._cut_vowel(hakka_pinyin)
        
        # print(f'orig_initials = {orig_initials}, orig_finals = {orig_finals}')
        for c, v in zip(orig_initials, orig_finals):
            if c and c not in self.punc:
                initials.append(c+'2')
            else:
                initials.append(c)
            if v not in self.punc:
                finals.append(v)
            else:
                finals.append(v)
        print(f"initials = {initials}, finals = {finals}")
        return initials, finals, True

    def _g2p(self,
             sentences: List[str]) -> Tuple[List[List[str]], str]:
        phones_list = []

        initials, finals, status = self._get_initials_finals(sentences)
        if status == False:
            return [], False

        for c, v in zip(initials, finals):
            if c and c not in self.punc:
                phones_list.append(c)
            if c and c in self.punc:
                # phones_list.append('sp')
                pass
            if v and v not in self.punc:
                phones_list.append(v)
        
        return phones_list, True
    
    def _cut_vowel(self, sentence):
        vowel_list = ['a', 'e', 'i', 'o', 'u']
        initials = []
        finals = []
        flag = True
        word_lst = sentence.split()
        for word in word_lst:
            if word in self.punc:
                initials.append(word)
                finals.append('')
                
            for i, char in enumerate(word):
                if char in vowel_list:
                    initials.append(word[: i].strip())
                    finals.append(word[i :].strip())
                    flag = False
                    break
            if flag:
                for i, char in enumerate(word):
                    if char in ['m', 'n']:
                        initials.append(word[: i].strip())
                        finals.append(word[i :].strip())
                        flag = False
                        break
            flag = True

        return initials, finals

    def get_phonemes(self,
                     sentence: str,
                     print_info: bool=True) -> Tuple[List[List[str]], str]:
        
        phonemes, status = self._g2p(sentence)
        if status == False:
            return [], False
        self.logger.info(f'Converting {sentence} to phonemes: {phonemes}', extra={"ipaddr":""})
        return phonemes, True

if __name__ == "__main__":
    frontend = ha_frontend(g2p_model="hakka_hailu")
    sentence = '我是台灣人'
    phonemes = frontend.get_phonemes(sentence)
    print(phonemes)

