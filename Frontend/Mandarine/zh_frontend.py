from pypinyin import lazy_pinyin, Style
import CKIP as ckip
from typing import Any, List
import re
from opencc import OpenCC
import number_normalization as text_normalizer

class zh_frontend():
    def __init__(self) -> None:
        self.punc = "：，；。？！“”‘’':,;.?!"

    def _get_initials_finals(self, word: str) -> List[List[str]]:
        initials = []
        finals = []

        
        orig_initials = lazy_pinyin(word, neutral_tone_with_five=True, style=Style.INITIALS)
        orig_finals = lazy_pinyin(word, neutral_tone_with_five=True, style=Style.FINALS_TONE3)
        print('ori=====', orig_initials)
        print('final===', orig_finals)
    
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
    
        return initials, finals

    def _g2p(self,sentences: List[str]) -> List[List[str]]:

        phones_list = []
        for seg in sentences:
            phones = []
            # Replace all English words in the sentence
            seg = re.sub('[a-zA-Z]+', '', seg)
            seg_cut = ckip.call_ckip([seg])
            print('CKIP = ', seg_cut)
            initials = []
            finals = []
        
            for word, pos in seg_cut:
                if pos == 'FW':
                    continue
                sub_initials, sub_finals = self._get_initials_finals(word)
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

        return phones_list

    def get_phonemes(self, sentence: str) -> List[List[str]]:
        # convert numbers and dates in sentence to Chinese
        sentences = [text_normalizer.askForService(language='ch', chinese = sentence)]
        
        # convert simplified Chinese to traditional Chinese
        cc = OpenCC('s2twp')
        for index, sentence in enumerate(sentences):
            sentences[index] = cc.convert(sentence)
            print('Sentence befor g2p', sentences)
        phonemes = self._g2p(sentences)
        return phonemes[0]
    
if __name__ == "__main__":
    frontend = zh_frontend()
    sentence = '你好啊朋友'
    phonemes = frontend.get_phonemes(sentence)
    print(phonemes)