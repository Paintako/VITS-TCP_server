from typing import Dict
from typing import List

# processing pipeline
import phoneme_process.number_normalization as num_nor
import phoneme_process.ch2tl as ch2tl
import phoneme_process.sandhi_client as sandhi
import phoneme_process.tl2ctl_client as tl2ctl

class Frontend():
    def __init__(self, g2p_model: str):
        self.punc = "：，；。？！“”‘’':,;.?!"
        self.g2p_model = g2p_model

    def _get_initials_finals(self, sentence: str) -> List[List[str]]:
        initials = []
        finals = []
        tl_sandhi = sentence
        if self.g2p_model != "taiwanese_CTL":
            sentence = num_nor.askForService(language='tl', chinese=sentence)
            tl_text = ch2tl.askForService(text=sentence)
            tl_sandhi = sandhi.askForService(tai_luo=tl_text['tailuo'])
            
        ctl_text = tl2ctl.askForService(tai_luo=tl_sandhi)
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
    
        return initials, finals

    def _g2p(self, sentences: List[str]) -> List[List[str]]:
        phones_list = []

        initials, finals = self._get_initials_finals(sentences)

        for c, v in zip(initials, finals):
            if c and c not in self.punc:
                phones_list.append(c)
            if c and c in self.punc:
                phones_list.append('sp')
            if v and v not in self.punc:
                phones_list.append(v)
        
        return phones_list
    
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
        phonemes = self._g2p(sentence)
        return phonemes
    
if __name__ == "__main__":
    frontend = Frontend(g2p_model="tw")
    print(frontend.get_phonemes("我想回家"))

