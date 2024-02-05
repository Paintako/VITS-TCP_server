from pypinyin import lazy_pinyin, Style
from . import CKIP, number_normalization
from typing import Any, List, Tuple
import re
from opencc import OpenCC

import json
import sys
import os
sys.path.append(f'{os.path.dirname(os.path.abspath(__file__))}/../../')
sys.path.append(f'{os.path.dirname(os.path.abspath(__file__))}')
from logs.service_logger import service_logger
class zh_frontend():
    def __init__(self) -> None:
        self.punc = "：，；。？！“”‘’':,;.?!"
        self.logger = service_logger()
        print(os.getcwd())
        # with open(f'./Frontend/Mandarine/rb_dict.txt', 'r', encoding='utf-8') as f:
        # TODO, change to relative path
        self.rb_dict = {
            "睡不著" : "睡不着",
            '睡覺': '睡着',
            '活著': '活着',
            '洗髮': '洗法',
            '頭髮': '頭法',
            '垃圾': '樂色',
            '跌' : '蝶',
            '摩' : '魔',
        }
    
    def _get_initials_finals(self, word: str) -> Tuple[List[List[str]], bool]:
        initials = []
        finals = []
        try:
            word = word.replace(" ","") # remove space
            
            orig_initials = lazy_pinyin(word, neutral_tone_with_five=True, style=Style.INITIALS)
            orig_finals = lazy_pinyin(word, neutral_tone_with_five=True, style=Style.FINALS_TONE3)
        
            # NOTE: post process for pypinyin outputs
            # we discriminate i, ii and iii
            for c, v in zip(orig_initials, orig_finals):
                if re.match(r'i\d', v):
                    if c in ['z', 'c', 's']:
                        v = re.sub('i', 'ii', v)
                    elif c in ['zh', 'ch', 'sh', 'r']:
                        v = re.sub('i', 'iii', v)
                if c and c not in self.punc:
                    initials.append(c+'1')
                else:
                    initials.append(c)
                if v not in self.punc:
                    finals.append(v[:-1]+'1'+v[-1])
                else:
                    finals.append(v)
        
            return initials, finals, True

        except:
            self.logger.error(f'Error transforming: {word}', extra={"ipaddr":""}, exc_info=True)
            return [], [], False

    def _g2p(self,sentences: List[str]) ->  Tuple[List[List[str]], bool]:

        phones_list = []
        for seg in sentences:
            phones = []
            # Replace all English words in the sentence
            seg = re.sub('[a-zA-Z]+', '', seg)
            seg_cut = CKIP.call_ckip([seg])
            initials = []
            finals = []
        
            for word, pos in seg_cut:
                if pos == 'FW':
                    continue
                sub_initials, sub_finals, status = self._get_initials_finals(word)
                if status == False:
                    return [], False
                initials.append(sub_initials)
                finals.append(sub_finals)
                # assert len(sub_initials) == len(sub_finals) == len(word)
            initials = sum(initials, [])
            finals = sum(finals, [])

            for c, v in zip(initials, finals):
                if c and c not in self.punc:
                    phones.append(c)
                if c and c in self.punc:
                    phones.append('sp')
                if v and v not in self.punc:
                    phones.append(v)

            phones_list.append(phones)

        return phones_list, True

    def get_phonemes(self, sentence: str) ->  Tuple[List[List[str]], bool]:
        # convert numbers and dates in sentence to Chinese
        sentences = [number_normalization.askForService(language='ch', chinese = sentence)]
        
        # convert simplified Chinese to traditional Chinese
        cc = OpenCC('s2twp')
        for index, sentence in enumerate(sentences):
            sentences[index] = cc.convert(sentence)
        print(f'before replace: {sentences}')
        for index, sentence in enumerate(sentences):
            for key, value in self.rb_dict.items():
                sentences[index] = sentences[index].replace(key, value)
        print(f'after replace: {sentences}')
        phonemes, status = self._g2p(sentences)
        if status == False:
            return [], False
        self.logger.info(f'Converting {sentence} to phonemes: {phonemes[0]}', extra={"ipaddr":""})
        return phonemes[0], True
    
if __name__ == "__main__":
    frontend = zh_frontend()
    sentence = '你好啊朋友'
    phonemes = frontend.get_phonemes(sentence)
    print(phonemes)