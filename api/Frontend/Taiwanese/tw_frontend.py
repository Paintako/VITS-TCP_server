from typing import Dict, List, Tuple

# processing pipeline
from .phoneme_process.number_normalization import askForService as num_nor
from .phoneme_process.ch2tl import askForService as ch2tl
from .phoneme_process.sandhi_client import askForService as sandhi
from .phoneme_process.tl2ctl_client import askForService as tl2ctl

import sys
import os
sys.path.append(f'{os.path.dirname(os.path.abspath(__file__))}/../../')
from logs.service_logger import service_logger

class tw_frontend():
    def __init__(self, g2p_model: str):
        self.punc = "：，；。？！“”‘’':,;.?!"
        self.g2p_model = g2p_model
        self.logger = service_logger()

    def _get_initials_finals(self, sentence: str) -> Tuple[List[List[str]], bool]:
        initials = []
        finals = []
        tl_sandhi = sentence.replace("。", "，")
        print(f'using: {self.g2p_model}')
        if tl_sandhi == "":
            self.logger.info(f'TL_sandhi {sentence} empty, return empty list', extra={"ipaddr":""})
            return [], [], True
        try:
            if self.g2p_model != "tw_tl":
                sentence = num_nor(language='tl', chinese=sentence)
                print(sentence)
                tl_text = ch2tl(text=sentence)
                print(tl_text)
                tl_sandhi = sandhi(tai_luo=tl_text['tailuo'])
                print(tl_sandhi)
                if tl_sandhi == "":
                    self.logger.error(f'TL_sandhi {sentence} got problem', extra={"ipaddr":""})
                    return [], [], True
                
                if tl_text['tailuo'] == 'Exceptions occurs':
                    self.logger.error(f'Exceptions occurs, {sentence} got problem', extra={"ipaddr":""})
                    return [], [], False
            else:
                print(f'before: {tl_sandhi}')
                tl_sandhi = sandhi(tai_luo=tl_sandhi)
                print(f'after: {tl_sandhi}')
        except:
            self.logger.error(f'ch2phoneme pipline failed, {sentence} got problem', extra={"ipaddr":""}, exc_info=True)
            return [], [], False
        
        

        if '-' in tl_sandhi:
            tl_sandhi = tl_sandhi.replace('-', ' ')
        ctl_text = tl2ctl(tai_luo=tl_sandhi)
        print(ctl_text)
        orig_initials, orig_finals = self._cut_vowel(ctl_text)
        for c, v in zip(orig_initials, orig_finals):
            if c and c not in self.punc:
                initials.append(c+'0')
            else:
                initials.append(c)
            if v not in self.punc:
                finals.append(v[:-1]+'0'+v[-1])
            else:
                finals.append(v)
    
        return initials, finals, True

    def _g2p(self, sentences: List[str]) -> Tuple[List[List[str]], bool]:
        phones_list = []

        initials, finals, status = self._get_initials_finals(sentences)
        if status == False:
            return [], False
        for c, v in zip(initials, finals):
            if c and c not in self.punc:
                phones_list.append(c)
            if c and c in self.punc:
                phones_list.append('sp')
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

    def get_phonemes(self, sentence: str) -> List[str]:
        phonemes, status = self._g2p(sentence)
        if status == False:
            self.logger.error(f'Error transforming: {sentence}, result: {phonemes}', extra={"ipaddr":""})
            return [], False
        self.logger.info(f'Converting {sentence} to phonemes: {phonemes}', extra={"ipaddr":""})
        return phonemes, True
    
if __name__ == "__main__":
    frontend = Frontend(g2p_model="tw")
    print(frontend.get_phonemes("我想回家"))

