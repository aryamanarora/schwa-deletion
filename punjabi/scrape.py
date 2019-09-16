# scrape words from the digitzed Learner's Hindi-English Dictionary
# clean up Wiktionary translit

from bs4 import BeautifulSoup
import urllib.request
import unicodedata
import re

conv = {
    'A': 'a', 'Á': 'aa', 'AI': 'E', 'AU': 'O', 'Ā': 'aa', 'Ạ': 'a',
    'B': 'b', 'BH': 'bh',
    'CH': 'c', 'CHH': 'ch',
    'D': 'd', 'Ḍ': 'dd', 'DH': 'dh', 'ḌH': 'ddh', 'ḊH': 'dh',
    'E': 'e',
    'F': 'ph',
    'G': 'g', 'GH': 'gh',
    'H': 'h',
    'I': 'i', 'Í': 'ii', 'Ī': 'ii', 'Ì': 'i', 'İ': 'i',
    'J': 'j', 'JH': 'jh',
    'K': 'k', 'KH': 'kh',
    'L': 'l',
    'M': 'm',
    'N': 'n', 'Ṉ': 'nn', 'Ṅ': 'nn', 'Ṇ': 'ng',
    'O': 'o', 'Ó': 'o',
    'P': 'p', 'PH': 'ph',
    'R': 'r', 'Ṛ': 'rr', 'ṚH': 'rrh',
    'S': 's', 'SH': 'sh', 'ṢH': 'sh',
    'T': 't', 'TH': 'th', 'Ṭ': 'tt', 'ṬH': 'tth',
    'U': 'u', 'Ú': 'uu', 'Ū': 'uu', 'Ù': 'uu',
    'W': 'v', 'V': 'v',
    'Y': 'y',
    '-': '-', '.': ''
}

def scrape(dic, PAGES):
    with open('data/temp.csv', 'w') as fout:
        for page in range(1, PAGES + 1):
            print(page)
            link = 'https://dsalsrv04.uchicago.edu/cgi-bin/app/' + dic + '_query.py?page=' + str(page)
            with urllib.request.urlopen(link) as resp:
                soup = str(BeautifulSoup(resp, 'html.parser'))
                for s in re.findall(r'[^\s]* <pan>.*?</pan>', soup):
                    s = s.split()
                    if len(s) != 2:
                        continue
                    fout.write(s[1][5:-6] + ',' + s[0] + '\n')

def normalize(inp, outp):
    data = []
    with open(inp, 'r') as fin:
        data = fin.readlines()
    for position, line in enumerate(data):
        word, translit = line.strip().split(',')
        new_translit = []
        i = 0
        while i < len(translit):
            for j in range(min(len(translit) - i, 3), 0, -1):
                if translit[i:i + j] in conv:
                    new_translit.append(conv[translit[i:i + j]])
                    i = i + j
                    break
            else:
                print('Unable to normalize', word, translit)
                data[position] = word + ','
                break
            data[position] = word + ',' + ' '.join(new_translit) + '\n'
    
    with open(outp, 'w') as fout:
        fout.writelines(data)

if __name__ == '__main__':
    # scrape('singh', 1220)
    normalize('data/large.csv', 'data/large.csv')
