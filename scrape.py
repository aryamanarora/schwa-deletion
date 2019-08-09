# scrape words from the digitzed Learner's Hindi-English Dictionary

from bs4 import BeautifulSoup
import urllib.request
import unicodedata

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

conv = {
    'k': 'k', 'kh': 'kh', 'g': 'g', 'gh': 'gh', 'ṅ': 'ng',
    'ch': 'c', 'chh': 'ch', 'j': 'j', 'jh': 'jh', 'ñ': 'n',
    'ṭ': 'tt', 'ṭh': 'tth', 'ḍ': 'dd', 'ḍh': 'ddh', 'ṇ': 'n',
    't': 't', 'th': 'th', 'd': 'd', 'dh': 'dh', 'n': 'n',
    'p': 'p', 'ph': 'ph', 'b': 'b', 'bh': 'bh', 'm': 'm',
    'y': 'y', 'r': 'r', 'l' : 'l', 'v': 'v', 'w': 'v',
    'sh': 'sh', 'ṣ': 'sh', 's': 's', 'h': 'h',

    'q': 'q', 'ḵẖ': 'x', 'G': 'Gh', 'f': 'f', 'z': 'z',

    'ṛ': 'rr', 'ṛh': 'rrh',

    'a': 'a', 'ā': 'aa',
    'i': 'i', 'ī': 'ii',
    'u': 'u', 'ū': 'uu',
    'e': 'e', 'āī': 'E',
    'o': 'o', 'āū': 'O',

    '·': '', '-': '', '~': '~'
}

PAGES = 708
with open("hi_pron.csv", "a") as fout:
    for page in range(1, PAGES + 1):
        print(page)
        link = "https://dsalsrv04.uchicago.edu/cgi-bin/app/bahri_query.py?page=" + str(page)
        with urllib.request.urlopen(link) as resp:
            soup = BeautifulSoup(resp, 'html.parser')
            for s in soup.find_all("hw"):
                s.extract()
                word = str(s.find('head'))[6:-7]
                pron = ""
                for char in str(s.find('tn'))[4:-5]:
                    if 'COMBINING TILDE' in unicodedata.name(char):
                        pron += strip_accents(char) + '~'
                    else:
                        pron += char


                res = []
                i = 0
                l = len(pron)
                work = True
                while i != l:
                    for j in range(min(l - 1, i + 1), i - 1, -1):
                        if pron[i:j + 1] in conv:
                            res.append(conv[pron[i:j + 1]])
                            i = j + 1
                            break
                    else:
                        print('Error normalizing', word, pron, 'char', pron[i])
                        work = False
                        break

                if work: fout.write(word + ', ' + ' '.join(res) + '\n')
