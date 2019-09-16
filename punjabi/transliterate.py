# conversion from Gurmukhi to Latin script without any schwa-dropping using Google's scheme
# https://github.com/google/language-resources/tree/master/hi_ur

# shortcuts for combining Gurmukhi diacritics
NUQTA = '਼'
HALANT = '੍'
ADDAK = 'ੱ'

# miscellaneous
UNK_CHAR = '🆒'

# keys for transliteration, mapping Gurmukhi to Latin
# conversion from Gurmukhi to Latin script without any schwa-dropping using Google's scheme
# https://github.com/google/language-resources/tree/master/hi_ur

# shortcuts for combining Devanagari diacritics
NUQTA = '਼'
VIRAMA = '੍'

# miscellaneous
UNK_CHAR = '🆒'

# keys for transliteration, mapping Devanagari to Latin
# TODO: figure out how to transliterate the rare nasal consonants
con = {
    'ਕ': 'k', 'ਖ': 'kh', 'ਗ': 'g', 'ਘ': 'gh', 'ਙ': 'ng',
    'ਚ': 'c', 'ਛ': 'ch', 'ਜ': 'j', 'ਝ': 'jh', 'ਞ': '?',
    'ਟ': 'tt', 'ਠ': 'tth', 'ਡ': 'dd', 'ਢ': 'ddh', 'ਣ': 'nn',
    'ਤ': 't', 'ਥ': 'th', 'ਦ': 'd', 'ਧ': 'dh', 'ਨ': 'n',
    'ਪ': 'p', 'ਫ': 'ph', 'ਬ': 'b', 'ਭ': 'bh', 'ਮ': 'm',
    'ਯ': 'y', 'ਰ': 'r', 'ਲ': 'l', 'ਵ': 'v',
    'ਸ': 's', 'ਸ਼': 'sh',
    'ਹ': 'h',

    'ਖ਼': 'x', 'ਗ਼': 'Gh', 'ਜ਼': 'z', 'ਡ਼': 'rr', 'ਡ਼੍ਹ': 'rrh', 'ਫ਼': 'f', 'ਲ਼': 'll',
    'ੜ': 'rr', 'ੜ੍ਹ': 'rrh'
}
vow = {
    'ਅ': 'a', 'ਆ': 'aa',
    'ਇ': 'i', 'ਈ': 'ii',
    'ਉ': 'u', 'ਊ': 'uu',
    'ਏ': 'e', 'ਐ': 'E',
    'ਓ': 'o', 'ਔ': 'O',
    'ੰ': 'ng', 'ਂ': 'ng'
}
matra = {
    'ਾ': 'aa',
    'ਿ': 'i', 'ੀ': 'ii',
    'ੁ': 'u', 'ੂ': 'uu',
    'ੇ': 'e', 'ੈ': 'E',
    'ੋ': 'o', 'ੌ': 'O'
}
nuqta = {
    'k': 'q', 'kh': 'x', 'g': 'Gh', 'ph': 'f', 'j': 'z', 'jh': 'Zh',
    'dd': 'rr', 'ddh': 'rrh'
}

def transliterate(word):

    # traverse the string, creating the transliteration char by char
    addak = False
    res = []
    for char in word:

        if char == HALANT:
            # halant suppresses the inherent schwa
            res.pop()
        
        elif char == '-':
            if char in con:
                res.append(con[char])

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
        
        elif char == ADDAK:
            # the addak geminates the succeeding consonant, no aspiration
            addak = True

        elif char in con:
            # consonant (with inherent schwa)
            if addak:
                if con[char][-1] == 'h':
                    res.append(con[char][:-1])
                else:
                    res.append(con[char])
                    addak = False;
            res.append(con[char])
            res.append('a')

        elif char in vow:
            # vowel sign
            res.append(vow[char])

        elif char in matra:
            # vowel matra (replaces the schwa after a consonant)
            res.pop()
            res.append(matra[char])

    return res

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
        elif ortho[i] in [UNK_CHAR, '-']:
            i += 1
        else:
            raise Exception('Unable to force-align {}, phon {}\nCompare {} and {}'.format(ortho, phon, ortho[i], phon[j]))
    
    return res