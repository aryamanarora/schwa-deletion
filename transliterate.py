# conversion from Devanagari to Latin script without any schwa-dropping using Google's scheme
# https://github.com/google/language-resources/tree/master/hi_ur

# shortcuts for combining Devanagari diacritics
NUQTA = '़'
VIRAMA = '्'

# miscellaneous
UNK_CHAR = '🆒'

# keys for transliteration, mapping Devanagari to Latin
# TODO: figure out how to transliterate the rare nasal consonants
con = {
    'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ng',
    'च': 'c', 'छ': 'ch', 'ज': 'j', 'झ': 'jh', 'ञ': '?',
    'ट': 'tt', 'ठ': 'tth', 'ड': 'dd', 'ढ': 'ddh', 'ण': 'n',
    'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
    'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm',
    'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v',
    'श': 'sh', 'ष': 'sh', 'स': 's',
    'ह': 'h',
}
vow = {
    'अ': 'a', 'आ': 'aa',
    'इ': 'i', 'ई': 'ii',
    'उ': 'u', 'ऊ': 'uu',
    'ए': 'e', 'ऐ': 'E', 'ऍ': 'E',
    'ओ': 'o', 'औ': 'O', 'ऑ': 'O',
    'ँ': '~', 'ं': 'ng'
}
matra = {
    'ा': 'aa',
    'ि': 'i', 'ी': 'ii',
    'ु': 'u', 'ू': 'uu',
    'े': 'e', 'ै': 'E', 'ॅ': 'E',
    'ो': 'o', 'ौ': 'O', 'ॉ': 'O'
}
nuqta = {
    'k': 'q', 'kh': 'x', 'g': 'Gh', 'ph': 'f', 'j': 'z', 'jh': 'Zh',
    'dd': 'rr', 'ddh': 'rrh'
}

# how the anusvara is assimilated to the next consonant
nasal_assim = {
    'k': '~', 'kh': '~', 'g': 'ng', 'gh': 'ng', 'ng': 'ng',
    'c': 'n', 'ch': 'n', 'j': 'n', 'jh': 'n', 'n': 'n',
    'tt': 'n', 'tth': 'n', 'dd': 'n', 'ddh': 'n', 
    't': 'n', 'th': 'n', 'd': 'n', 'dh': 'n', 
    'p': 'm', 'ph': 'm', 'b': 'm', 'bh': 'm', 'm': 'm',
    'y': '~', 'r': '~', 'l': '~', 'v': '~',
    'sh': 'n', 's': 'n',
    'h': '~',

    'q': '~', 'x': '~', 'Gh': 'ng', 'f': '~', 'z': '~', 'jh': '~',
    'rr': '~', 'rrh': '~'
}

# articulation
art = {
    'u': ['k', 'kh', 'g', 'gh', 'ng', 'x', 'Gh', 'q'], # velar/uvular
    'p': ['c', 'ch', 'j', 'jh'], # palatal
    'r': ['tt', 'tth', 'dd', 'ddh', 'rr', 'rrh'], # retroflex
    'd': ['t', 'th', 'd', 'dh', 'n'], # dental
    'l': ['p', 'ph', 'b', 'bh', 'm'], # labial
    'g': ['y', 'v'], # semivowels/glides
    'li': ['r', 'l'], # liquids
    'h': ['h'], # glottal
    's': ['s', 'sh'] # sibilants
}

phonological_features = {
    'a': ['mid', 'central', 'unrounded', 'short', 'vowel'],
    'aa': ['open', 'central', 'unrounded', 'long', 'vowel'],
    'i': ['near-close', 'front', 'unrounded', 'short', 'vowel'],
    'ii': ['close', 'front', 'unrounded', 'long', 'vowel'],
    'u': ['near-close', 'back', 'rounded', 'short', 'vowel'],
    'uu': ['close', 'back', 'rounded', 'long', 'vowel'],
    'e': ['close-mid', 'front', 'unrounded', 'long', 'vowel'],
    'E': ['open-mid', 'front', 'unrounded', 'long', 'vowel'],
    'o': ['close-mid', 'back', 'rounded', 'long', 'vowel'],
    'O': ['open-mid', 'back', 'rounded', 'long', 'vowel'],
    'k': ['voiceless', 'unaspirated', 'velar', 'stop'],
    'kh': ['voiceless', 'aspirated', 'velar', 'stop'],
    'g': ['voiced', 'unaspirated', 'velar', 'stop'],
    'gh': ['voiced', 'aspirated', 'velar', 'stop'],
    'ng': ['voiced', 'unaspirated', 'velar', 'nasal'],
    'c': ['voiceless', 'unaspirated', 'palatal', 'sibilant affricate'],
    'ch': ['voiceless', 'aspirated', 'palatal', 'sibilant affricate'],
    'j': ['voiced', 'unaspirated', 'palatal', 'sibilant affricate'],
    'jh': ['voiced', 'aspirated', 'palatal', 'sibilant affricate'],
    'tt': ['voiceless', 'unaspirated', 'retroflex', 'stop'],
    'tth': ['voiceless', 'aspirated', 'retroflex', 'stop'],
    'dd': ['voiced', 'unaspirated', 'retroflex', 'stop'],
    'ddh': ['voiced', 'aspirated', 'retroflex', 'stop'],
    't': ['voiceless', 'unaspirated', 'dental', 'stop'],
    'th': ['voiceless', 'aspirated', 'dental', 'stop'],
    'd': ['voiced', 'unaspirated', 'dental', 'stop'],
    'dh': ['voiced', 'aspirated', 'dental', 'stop'],
    'n': ['voiced', 'unaspirated', 'dental', 'nasal'],
    'p': ['voiceless', 'unaspirated', 'bilabial', 'stop'],
    'ph': ['voiceless', 'aspirated', 'bilabial', 'stop'],
    'b': ['voiced', 'unaspirated', 'bilabial', 'stop'],
    'bh': ['voiced', 'aspirated', 'bilabial', 'stop'],
    'm': ['voiced', 'unaspirated', 'bilabial', 'nasal'],
    'y': ['voiced', 'unaspirated', 'palatal', 'approximant'],
    'r': ['voiced', 'unaspirated', 'dental', 'flap'],
    'l': ['voiced', 'unaspirated', 'dental', 'approximant'],
    'v': ['voiced', 'unaspirated', 'labiodental', 'approximant'],
    'sh': ['voiceless', 'unaspirated', 'palatal', 'sibilant fricative'],
    's': ['voiceless', 'unaspirated', 'dental', 'sibilant fricative'],
    'h': ['voiced', 'aspirated', 'glottal', 'non-sibilant fricative'],
    '~': ['voiceless', 'unaspirated', 'nasal'],
    'z': ['voiced', 'unaspirated', 'dental', 'sibilant fricative'],
    'f': ['voiced', 'unaspirated', 'bilabial', 'non-sibilant fricative'],
    'rr': ['voiced', 'unaspirated', 'retroflex', 'flap'],
    'rrh': ['voiced', 'aspirated', 'retroflex', 'flap'],
    'Zh': ['voiced', 'unaspirated', 'dental', 'sibilant fricative'],
    'q': ['voiceless', 'unaspirated', 'uvular', 'stop'],
    'x': ['voiceless', 'unaspirated', 'velar', 'non-sibilant fricative'],
    'Gh': ['voiced', 'unaspirated', 'velar', 'non-sibilant fricative'],
    UNK_CHAR: []
}

def transliterate(word):
    # normalize "ri" vowel
    word = word.replace('ऋ', 'रि').replace('ृ', '्रि')

    # traverse the string, creating the transliteration char by char
    res = []
    for char in word:

        if char == VIRAMA:
            # virama suppresses the inherent schwa
            res.pop()

        elif char == NUQTA:
            # nuqta transforms a consonant, so we remove the schwa, change the consonant,
            # then add the schwa again
            if res[-1] == 'a':
                res.pop()
                l = res.pop()
                res.append(l if l not in nuqta else nuqta[l]) 
                res.append('a')
            else:
                l = res.pop()
                res.append(l if l not in nuqta else nuqta[l])

        elif char in con:
            # consonant (with inherent schwa)
            res.append(con[char])
            res.append('a')

        elif char in vow:
            # vowel sign
            res.append(vow[char])

        elif char in matra:
            # vowel matra (replaces the schwa after a consonant)
            res.pop()
            res.append(matra[char])
    
    # handle assimilation of the anusvara to the next consonant
    # word-finally it is the same as a chandrabindu
    for i in range(len(res)):
        if res[i] == 'ng':
            if i + 1 == len(res): res[i] = '~'
            else: res[i] = nasal_assim[res[i + 1]]

    return res

# converts to short vowel, long vowel, or consonant for each sound in a Hindi word
def broad_categorize(word):
    word = transliterate(word)
    for i, unit in enumerate(word):
        if unit == 'a':
            continue
        elif unit in vow.values():
            word[i] = ('V' if len(unit) == 2 or unit.isupper() else 'v')
        else:
            word[i] = 'C'
    return word

# converts to place of articulation
def narrow_categorize(word):
    word = transliterate(word)
    for i, unit in enumerate(word):
        if unit == 'a':
            continue
        elif unit in vow.values():
            word[i] = ('V' if len(unit) == 2 or unit.isupper() else 'v')
        else:
            for key, val in art.items():
                if unit in val:
                    word[i] = key
    return word

# returns an array of boolean-int pairs, one for each schwa in the orthographic transliteration
# with True meaning the schwa is kept, False meaning it is dropped
# and the second element being the position where it is dropped
def force_align(ortho, phon):
    # clean up phonetic
    phon = phon.replace('. ', '')
    phon = phon.split()

    # two pointer technique, compares in linear time
    i, j = 0, 0
    n, m = len(ortho), len(phon)
    res = []
    while i < n:
        if j >= m:
            res.append([False, i])
            i += 1
        elif ortho[i] == phon[j]:
            if ortho[i] == 'a': res.append([True, i])
            i += 1
            j += 1
        elif ortho[i] == 'a':
            res.append([False, i])
            i += 1
        else:
            raise Exception('Unable to force-align {}, phon {}'.format(ortho, phon))
    
    return res

# force_align but with weakened schwas as well
def force_align_weak(ortho, phon):
    # clean up phonetic
    phon = phon.replace('. ', '')
    phon = phon.replace('  ', ' ')
    phon = phon.replace('-', '')
    phon = phon.split()

    # two pointer technique, compares in linear time
    i, j = 0, 0
    n, m = len(ortho), len(phon)
    res = []
    while i < n:
        if j >= m:
            res.append([2, i])
            i += 1
        elif ortho[i] == phon[j]:
            if ortho[i] == 'a': res.append([0, i])
            i += 1
            j += 1
        elif ortho[i] == 'a':
            res.append([1 if phon[j] == '@' else 2, i])
            if phon[j] == '@': j += 1
            i += 1
        else:
            raise Exception('Unable to force-align {}, phon {}\nCompare {} and {}'.format(ortho, phon, ortho[i], phon[j]))
    
    return res