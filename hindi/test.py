import sys
import numpy as np
import pandas as pd
import transliterate as tr
import scrape
import os
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier, plot_tree
from sklearn.metrics import accuracy_score, recall_score, f1_score, precision_score
from sklearn.model_selection import GridSearchCV
from joblib import dump, load
from matplotlib.pylab import rcParams
from matplotlib import pyplot as plt
import other.wiktionary as wikt
import re

UNK_CHAR = '🆒'

espeak = {
    'k': 'k', 'kh': 'kH', 'g': 'g', 'gh': 'gH', 'ng': 'N',
    'c': 'tS', 'ch': 'tSH', 'j': 'dZ', 'jh': 'dZH',
    'tt': 't.', 'tth': 't.H', 'dd': 'd.', 'ddh': 'd.H', 'nn': 'n.',
    't': 't[', 'th': 't[H', 'd': 'd[', 'dh': 'd[H', 'n': 'n',
    'p': 'p', "ph": 'f', 'b': 'b', 'bh': 'bH', 'm': 'm',
    'y': 'j', 'r': 'R', 'l': 'l', 'v': 'v',
    'sh': 'S', 's': 's',
    'h': 'H',
    'q': 'k', 'x': 'kH', 'Gh': 'g', 'z': 'z', 'rr': 'r.', 'rrh': 'r.H', 'f': 'f',

    'a': '@', 'aa': 'a:', 'i': 'I', 'ii': 'i:', 'u': 'U', 'uu': 'u:',
    'e': 'e:', 'E': 'E:', 'o': 'o:', 'O': 'O:', '~': '~'
}

def conv(word):
    left, right = 5, 5
    model = load('models/xgboost/xgboost_nophon.joblib')
    chars = load('models/xgboost/xgboost_nophon_chars.joblib')

    if word[-1] == 'ं':
        word = word[:-1] + 'ँ'

    # print(chars)
    transliteration = tr.transliterate(word)
    transformed_instances = []
    for i, phone in enumerate(transliteration):
        if phone == 'a':
            x = []
            for j in range(i - left, i + right + 1):
                if j == i: continue
                for char in chars:
                    if j < 0 or j >= len(transliteration): 
                        if char == UNK_CHAR: x.append(1)
                        else: x.append(0)
                    else:
                        if char == transliteration[j]: x.append(1)
                        else: x.append(0)
            transformed_instances.append(x)

    col = []
    for i in list(range(-left, 0)) + list(range(1, right + 1)):
        for j in chars:
            col.append('s' + str(i) + '_' + str(j))

    X = pd.DataFrame(transformed_instances,
        columns=col)
    Y = []
    if len(X) > 0: Y = model.predict(X)
    pos = 0
    res = []
    for phone in transliteration:
        if phone == 'a':
            if Y[pos]:
                res.append(espeak['a'])
            pos += 1
        else:
            res.append(espeak[phone])
    return ''.join(res)

def main():
    words = input()
    res = ''
    for word in words.split():
        res += conv(word) + ' '
    res = res.replace(':~', '~:')
    print(res)
    os.system(f'espeak -vhi "[[{res}]]" -x -s 150')

if __name__ == '__main__':
    main()