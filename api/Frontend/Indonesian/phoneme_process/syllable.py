'''
Jika di tengah kata ada vokal yang berurutan, 
pemenggalan itu dilakukan di antara kedua huruf vokal itu. 
Misalnya: ma-in, sa-at, bu-ah
Huruf diftong ai, au, dan oi tidak pernah diceraikan 
sehingga pemenggalan kata tidak dilakukan di antara kedua huruf itu.
'''

'''
Jika di tengah kata ada huruf konsonan, termasuk gabungan-huruf
konsonan, di antara dua buah huruf vokal, pemenggalan dilakukan sebelum huruf konsonan.
'''

'''
Jika di tengah kata ada dua huruf konsonan yang berurutan, 
pemenggalan dilakukan di antara kedua huruf konsonan itu. 
Gabungan huruf konsonan tidak pernah diceraikan.
'''

VOWELS = list('aiueo*()-')
DIFTONG = list('*()-')
PREFIX = [
    'me',
    'mem',
    'ber',
    'ter',
    'ke',
    'se',
    'di',
    'per',
]
SUFFIX = [
    'kan',
    'i',
    'an',
    'ku',
    'mu',
    'nya',
    'kah',
    'lah',
    'tah',
    'pun',
]
# Extra combination = 'tr', 'gr', 'str', 'fr' ???
# Assuming fr is included in combination
COMBINATION = {
    # 'str':'~',
    'kh':'!',
    'ng':'@',
    'ny':'#',
    'sy':'$',
    'tr':'%',
    'gr':'^',
    'fr':'&',
    'ai':'*',
    'au':'(',
    'ei':')',
    'oi':'-',
}


def _encode(word):
    for letters, symbol in COMBINATION.items():
        word = word.replace(letters, symbol)

    # Special case:
    # 1st: diftong must be separated if the combination of the last syllables is [diftong + single consonant]
    # ex = ajaib, main, egois, laut, air
    # 2nd: for 3 char words diftong must be separated if the combination of the last syllables is [single consonant + diftong]
    # ex = mau, bau
    if (len(word) > 2 and word[-2] in DIFTONG and word[-1] not in VOWELS):
        word = word[:-2] + _decode(word[-2]) + word[-1]
    elif (len(word) == 2 and word[0] not in VOWELS and word[1] in DIFTONG):
        word = word[0] + _decode(word[1])

    return word


def _decode(syllable):
    for letters, symbol in COMBINATION.items():
        syllable = syllable.replace(symbol, letters)
    return syllable


def _split_word(encoded_word):
    syllables = list(encoded_word)
    result = []
    i = 0

    # Split using rules
    while i < len(syllables):
        if syllables[i] not in VOWELS and i != len(syllables) - 1:
            # 1st rule = for every consonant if the next letter is vowel then keep them together
            if syllables[i+1] in VOWELS:
                result.append(syllables[i] + syllables[i+1])
                i += 1
            # 2nd rule = for every consonant if the next letter is consonant then separate them
            else:
                result.append(syllables[i])
        # 3rd rule = for every first selected letter in loop is vowel then keep vowel alone
        else:
            result.append(syllables[i])
        i += 1

    # print(result)

    return result


def _combine_syllable(syllables):
    syllable = ""
    result = []
    i = 0
    
    # Not perfect!!! 
    # 1st: need to add special case for prefix(ek, eks), middle(st, str), prefix(tran, trans), middle(sk)
    # 2nd: need to check for the root words like: belajar (ajar) => bel.a.jar not be.la.jar
    # 3rd: need to separate the words with root words and its prefix, suffix 
    while i < len(syllables):
        syllable = syllables[i]
        # if current syllable has vowel then check for the next syllable
        if _vowel_exist(syllables[i]):
            # if the successive syllable(s) is only consonant then combine them together as one syllable
            while i != len(syllables) - 1 and not _vowel_exist(syllables[i+1]):
                syllable += syllables[i+1]
                i += 1
        # else if current syllable is consonant and next syllable first char is also consonant then combine them
        # ex: flu -> f.lu -> flu
        elif i != len(syllables) - 1 and syllables[i+1][0] not in VOWELS:    
            syllable += syllables[i+1]
            i += 1
        i += 1
        result.append(syllable)
    
    return result

        
def _vowel_exist(syllable):
    for vowel in VOWELS:
        if vowel in syllable:
            return True
    return False


def get_syllable(sentence):
    decoded_words = []
    for word in sentence.split():
        encoded_syllables = _combine_syllable(_split_word(_encode(word)))
        decoded_syllables = []
        for syllable in encoded_syllables:
            decoded_syllables.append(_decode(syllable))
        decoded_words.append(' '.join(decoded_syllables))
    return ' '.join(decoded_words)


def get_syllable_slices(sentence):
    decoded_words_slices = []
    for word in sentence.split():
        encoded_syllables = _combine_syllable(_split_word(_encode(word)))
        syllable_slices = []
        decoded_slices = []
        for syllable in encoded_syllables:
            for s in list(syllable):
                syllable_slices.append(s)
        for slice in syllable_slices:
            decoded_slices.append(_decode(slice))
        decoded_words_slices.append(' '.join(decoded_slices))
    return ' '.join(decoded_words_slices)


if __name__ == '__main__':
    words = input('input: ').split()
    for word in words:
        print(get_syllable(word))