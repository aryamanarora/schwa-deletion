# conversion from Devanagari to Latin script without any schwa-dropping using Google's scheme
# https://github.com/google/language-resources/tree/master/hi_ur

# shortcuts for combining Devanagari diacritics
NUQTA = '़'
VIRAMA = '्'

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
    'k': '~', 'kh': '~', 'g': 'ng', 'gh': 'ng',
    'c': 'n', 'ch': 'n', 'j': 'n', 'jh': 'n',
    'tt': 'n', 'tth': 'n', 'dd': 'n', 'ddh': 'n', 
    't': 'n', 'th': 'n', 'd': 'n', 'dh': 'n', 
    'p': 'm', 'ph': 'm', 'b': 'm', 'bh': 'm',
    'y': '~', 'r': '~', 'l': '~', 'v': '~',
    'sh': 'n', 's': 'n',
    'h': '~',

    'q': '~', 'x': '~', 'Gh': 'ng', 'f': '~', 'z': '~', 'jh': '~',
    'rr': '~', 'rrh': '~'
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
            res.pop()
            res.append(nuqta[res.pop()])
            res.append('a')

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

# returns an array of boolean-int pairs, one for each schwa in the orthographic transliteration
# with True meaning the schwa is kept, False meaning it is dropped
# and the second element being the position where it is dropped
def force_align(word, phon):
    ortho = transliterate(word)

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
            print('Unable to force-align', word)
            print('Orthographic:', ortho)
            print('Phonetic:', phon)
            break
    
    return res