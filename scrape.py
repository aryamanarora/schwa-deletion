# scrape words from the digitzed Learner's Hindi-English Dictionary
# clean up Wiktionary translit

from bs4 import BeautifulSoup
import urllib.request
import unicodedata
from transliterate import nasal_assim

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

conv = {
    'k': 'k', 'kh': 'kh', 'g': 'g', 'gh': 'gh', 'ṅ': 'ng',
    'c': 'c', 'ch': 'ch', 'j': 'j', 'jh': 'jh', 'ñ': 'n',
    'ṭ': 'tt', 'ṭh': 'tth', 'ḍ': 'dd', 'ḍh': 'ddh', 'ṇ': 'n',
    't': 't', 'th': 'th', 'd': 'd', 'dh': 'dh', 'n': 'n',
    'p': 'p', 'ph': 'ph', 'b': 'b', 'bh': 'bh', 'm': 'm',
    'y': 'y', 'r': 'r', 'l' : 'l', 'v': 'v', 'w': 'v',
    'sh': 'sh', 'ṣ': 'sh', 's': 's', 'h': 'h', 'ś': 'sh',

    'q': 'q', 'ḵẖ': 'x', 'G': 'Gh', 'f': 'f', 'z': 'z', 'Kh': 'x',

    'ṛ': 'rr', 'ṛh': 'rrh',

    'a': 'a', 'ā': 'aa', 'â': 'aa',
    'i': 'i', 'ī': 'ii', 'î': 'ii', 'ï': 'i',
    'u': 'u', 'ū': 'uu', 'û': 'uu', 'ü': 'u',
    'e': 'e', 'ai': 'E', 'ê': 'e',
    'o': 'o', 'au': 'O', 'ô': 'o',
    'ă': '@',

    '·': '', '-': '-', '~': '~', 'ḥ': 'h',
    '̥': 'i', 'ʾ': '', '+': '-',
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

def scrape(dic, PAGES):
    with open("hi_pron.csv", "a") as fout:
        for page in range(1, PAGES + 1):
            print(page)
            link = "https://dsalsrv04.uchicago.edu/cgi-bin/app/" + dic + "_query.py?page=" + str(page)
            with urllib.request.urlopen(link) as resp:
                soup = BeautifulSoup(resp, 'html.parser')
                for s in soup.find_all("hw"):
                    s.extract()
                    word = str(s.find('deva'))[6:-7]
                    pron = str(s.find('tran'))[6:-7]
                    fout.write(word + ',' + pron + '\n')

                    # pron.replace('jñ', 'gy')

                    # res = []
                    # i = 0
                    # l = len(pron)
                    # work = True
                    # n = []
                    # while i != l:
                    #     for j in range(min(l - 1, i + 1), i - 1, -1):
                    #         if pron[i:j + 1] in conv:
                    #             res.append(conv[pron[i:j + 1]])
                    #             i = j + 1
                    #             break
                    #     else:
                    #         if pron[i] == 'ṁ' or pron[i] == 'ṃ':
                    #             res.append('~')
                    #             if i != l - 1:
                    #                 n.append(len(res) - 1)
                    #             i += 1
                    #         else:
                    #             print('Error normalizing', word, pron, 'char', pron[i])
                    #             work = False
                    #             break

                    # if work:
                    #     for pos in n:
                    #         if res[pos + 1] in nasal_assim:
                    #             res[pos] = nasal_assim[res[pos + 1]]
                    #         elif pos + 2 < len(res) and res[pos + 2] in nasal_assim:
                    #             res[pos] = nasal_assim[res[pos + 2]]
                    #     fout.write(word + ', ' + ' '.join(res) + '\n')

def wiktionary_transliterate(pron):
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
            raise Exception('Error normalizing ' + pron + ' char ' + pron[i])
    return res

if __name__ == "__main__":
    scrape("mcgregor", 1082)