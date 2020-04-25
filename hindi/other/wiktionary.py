import re
import unicodedata
import transliterate as tr
from sklearn.metrics import accuracy_score, recall_score, f1_score, precision_score

UNK_CHAR = '🆒'

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

conv = {
    # consonants
    'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ṅ', 
    'च': 'c', 'छ': 'ch', 'ज': 'j', 'झ': 'jh', 'ञ': 'ñ', 
    'ट': 'ṭ', 'ठ': 'ṭh', 'ड': 'ḍ', 'ढ': 'ḍh', 'ण': 'ṇ',
    'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
    'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm', 
    'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v', 'ळ': 'ḷ',
    'श': 'ś', 'ष': 'ṣ', 'स': 's', 'ह': 'h',
    'क़': 'q', 'ख़': 'x', 'ग़': 'ġ', 'ऴ': 'ḻ',
    'ज़': 'z', 'ष़': 'ḻ', 'झ़': 'ž', 'ड़': 'ṛ', 'ढ़': 'ṛh',
    'फ़': 'f', 'थ़': 'θ', 'ऩ': 'ṉ', 'ऱ': 'ṟ',

    # vowel diacritics
    'ि': 'i', 'ु': 'u', 'े': 'e', 'ो': 'o',
    'ॊ': 'ǒ', 'ॆ': 'ě',
    'ा': 'ā', 'ी': 'ī', 'ू': 'ū', 
    'ृ': 'ŕ',
    'ै': 'ai', 'ौ': 'au',
    'ॉ': 'ŏ',
    'ॅ': 'ĕ',

    # vowel signs
    'अ': 'a', 'इ': 'i', 'उ': 'u', 'ए': 'e', 'ओ': 'o',
    'आ': 'ā', 'ई': 'ī', 'ऊ': 'ū', 'ऎ': 'ě', 'ऒ': 'ǒ',
    'ऋ': 'ŕ', 
    'ऐ': 'ai', 'औ': 'au', 
    'ऑ': 'ŏ',
    'ऍ': 'ĕ',
    
    'ॐ': 'om',
    
    # chandrabindu
    'ँ': '̃',
    
    # anusvara
    'ं': 'ṁ',
    
    # visarga
    'ः': 'ḥ',
    
    # virama
    '्': '',
    
    # numerals
    '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
    '५': '5', '६': '6', '७': '7', '८': '8', '९': '9',
    
    # punctuation
    '।': '.', # danda
    '॥': '.', # double danda
    '+': '', # compound separator
    
    # abbreviation sign
    '॰': '.',
}

conv_wikt = {
    'k': 'k', 'kh': 'kh', 'g': 'g', 'gh': 'gh', 'ṅ': 'ng',
    'c': 'c', 'ch': 'ch', 'j': 'j', 'jh': 'jh', 'ñ': 'n',
    'ṭ': 'tt', 'ṭh': 'tth', 'ḍ': 'dd', 'ḍh': 'ddh', 'ṇ': 'n',
    't': 't', 'th': 'th', 'd': 'd', 'dh': 'dh', 'n': 'n',
    'p': 'p', 'ph': 'ph', 'b': 'b', 'bh': 'bh', 'm': 'm',
    'y': 'y', 'r': 'r', 'l' : 'l', 'v': 'v', 'w': 'v',
    'ś': 'sh', 'ṣ': 'sh', 's': 's', 'h': 'h',

    'q': 'q', 'x': 'x', 'ġ': 'Gh', 'f': 'f', 'z': 'z', 'ž': 'Zh',
    'ḥ': 'h', 'ś': 'sh',

    'ṛ': 'rr', 'ṛh': 'rrh',

    'a': 'a', 'ā': 'aa',
    'i': 'i', 'ī': 'ii',
    'u': 'u', 'ū': 'uu',
    'e': 'e', 'ai': 'E',
    'o': 'o', 'au': 'O',
    'ŏ': 'O',

    '·': '', '~': '~',
}

nasal_assim = {
    'क': 'ङ', 'ख': 'ङ', 'ग': 'ङ', 'घ': 'ङ', 
    'च': 'ञ', 'छ': 'ञ', 'ज': 'ञ', 'झ': 'ञ',  
    'ट': 'ण', 'ठ': 'ण', 'ड': 'ण', 'ढ': 'ण',
    'प': 'म', 'फ': 'म', 'ब': 'म', 'भ': 'म', 'म': 'म',
    'व': 'ँ', 'य': 'ँ', 'ष': 'न', 'श': 'न', 'स': 'न'
}

perm_cl = {
    'म्ल': True, 'व्ल': True, 'न्ल': True,	
}

all_cons, special_cons = 'कखगघङचछजझञटठडढतथदधपफबभशषसयरलवहणनम', 'यरलवहनम'
vowel, vowel_sign = 'aिुृेोाीूैौॉॅॆॊ', 'अइउएओआईऊऋऐऔऑऍ'
syncope_pattern = r'([' + vowel + vowel_sign + r'])(़?[' + all_cons + r'])a(़?[' + all_cons.replace("य", "") + r'])([ंँ]?[' + vowel + vowel_sign + r'])'

def magic(x):
    return (((re.search(r'[' + special_cons + ']', x.group(1)) and re.search(r'्', x.group(2))
        and not ((x.group(2) + x.group(3) + x.group(4)) in perm_cl))
        or re.search(r'य[ीेै]', x.group(2) + x.group(3)))
        and 'a' or '') + x.group(1) + x.group(2) + x.group(3) + x.group(4)
    

def translit(text):
    # adds inherent schwas wherever they are possible
    text = unicodedata.normalize('NFD', text)
    text = re.sub('([' + all_cons + ']़?)([' + vowel + '्]?)',
        lambda x: x.group(1) + ('a' if x.group(2) == "" else x.group(2)), text)
    for word in re.findall(r"[ऀ-ॿa]+", text):
        orig_word = word
        word = word[::-1]
        word = re.sub(r'^a(़?)([' + all_cons + r'])(.)(.?)', magic, word)
        while re.search(syncope_pattern, word):
            word = re.sub(syncope_pattern, r'\1\2\3\4', word)
        word = re.sub(r'(.?)ं(.)', lambda x:
            x.group(1) + (x.group(1) + x.group(2) == "a" and "्म" or 
            (x.group(1) == "" and re.search(r'[' + vowel + r']', x.group(2)) and "̃" or (nasal_assim[x.group(1)] if x.group(1) in nasal_assim else "n"))) + x.group(2), word)
        text = re.sub(orig_word, word[::-1], text)
    text = re.sub(r'.़?', lambda x: conv[x.group(0)] if x.group(0) in conv else x.group(0), text)
    text = re.sub(r'a([iu])̃', r'a͠\1', text)
    text = re.sub(r'jñ', r'gy', text)
    text = re.sub(r'ñz', r'nz', text)
    return text

# converts from the Wiktionary translit scheme to our scheme
def convert(pron):
    pron = pron.replace('ŕ', 'ri')
    temp = ""
    for char in pron:
        if 'TILDE' in unicodedata.name(char):
            temp += strip_accents(char) + '~'
        else:
            temp += char
    pron = temp

    res = []
    i = 0
    l = len(pron)
    while i != l:
        for j in range(min(l - 1, i + 1), i - 1, -1):
            if pron[i:j + 1] in conv_wikt:
                res.append(conv_wikt[pron[i:j + 1]])
                i = j + 1
                break
        else:
            res.append(pron[i])
            i += 1
    return res

def force_align(ortho, phon):
    # two pointer technique, compares in linear time
    i, j = 0, 0
    n, m = len(ortho), len(phon)
    res = []
    while i < n:
        if j >= m:
            res.append([True, False])
            i += 1
        elif ortho[i] == phon[j]:
            if ortho[i] == 'a': res.append([True, True])
            i += 1
            j += 1
        elif phon[j] == 'a':
            res.append([False, True])
            j += 1
        elif ortho[i] == 'a':
            res.append([True, False])
            i += 1
        elif ortho[i] in [UNK_CHAR, '-']:
            i += 1
        else:
            raise Exception('Unable to force-align {}, phon {}\nCompare {} and {}'.format(ortho, phon, ortho[i], phon[j]))
    
    return res

if __name__ == "__main__":
    X, Y = [], []
    bad, total = 0, 0
    with open('../data/extra_large.csv', 'r') as fin:
        # fout.write("Word,Translit,Normalized\n")
        for i, line in enumerate(fin):
            if i == 0: continue
            try:
                word, phon = line.strip().split(',')
                trans = tr.transliterate(word)
                con = convert(translit(word))
                phon = phon.replace('@', '')
                print(word, ''.join(trans), phon.replace(' ', ''), ''.join(con))
                res = [x[1] for x in force_align(trans, phon.split())]
                res2 = [x[1] for x in force_align(trans, con)]
                good = True
                for a, b in zip(res, res2):
                    X.append(a)
                    Y.append(b)
                    if a != b:
                        good = False
                if not good: bad += 1
                total += 1
            except Exception as e:
                print(e)
                continue
    print(f"Word Accuracy: {1 - bad/total}")
    print(f"Accuracy: {accuracy_score(X, Y)}\nRecall: {recall_score(X, Y)}\nPrecision: {precision_score(X, Y)}")
    
    