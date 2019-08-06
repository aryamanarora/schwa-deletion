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
    'k': 'q', 'kh': 'x', 'g': 'Gh', 'ph': 'f', 'j': 'z',
    'dd': 'rr', 'ddh': 'rrh'
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

    return ' '.join(res)