import sys
import numpy as np
import pandas as pd
import transliterate as tr
import scrape
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

def get_data(input_filename):
    data = pd.read_csv(input_filename, header=0)
    # force align the predicted orthographic transliteration (without schwa dropping)
    # with the actual phonetic transliteration (schwa dropping) to created training/test data
    schwa_instances = []
    for _, row in data.iterrows():
        # print(chr(27) + '[2J')
        # print('Processing row', _)
        try:
            schwa_instances += [[tr.transliterate(row.hindi), schwa_instance[1], schwa_instance[0]]
                for schwa_instance in tr.force_align(tr.transliterate(row.hindi), str(row.phon))]
            # schwa_instances += [[tr.transliterate(row.hindi), schwa_instance[1], schwa_instance[0]]
            #         for schwa_instance in tr.force_align_weak(tr.transliterate(row.hindi), str(row.phon))]
        except Exception as e:
            # print(e)
            continue
    
    return schwa_instances

def main(input_filename, use_phon, left=4, right=4):
    # get the data
    schwa_instances = get_data(input_filename)
    print(len(schwa_instances))

    # generate set of phonemes to store for later
    chars = set()
    for word in schwa_instances:
        for char in word[0]:
            chars.add(char)
    chars.add(UNK_CHAR)
    chars = list(chars)

    # if phonological features are considered we need to store them too
    phons = set()
    if use_phon:
        for phoneme, features in tr.phonological_features.items():
            for feature in features:
                phons.add(feature)
        phons = list(phons)

    chars = load('models/xgboost/xgboost_chars.joblib')
    phons = load('models/xgboost/xgboost_phons.joblib')
    
    # clean up the data
    # generate features (with or without phonological descriptions)
    y = []
    transformed_instances = []
    for s, schwa_index, schwa_was_deleted in schwa_instances:
        x = []
        for i in range(schwa_index - left, schwa_index + right + 1):
            if i == schwa_index:
                continue
            
            if use_phon:
                for phon in phons:
                    if i < 0 or i >= len(s): 
                        x.append(0)
                    else:
                        if phon in tr.phonological_features[s[i]]: x.append(1)
                        else: x.append(0)
            else:
                for char in chars:
                    if i < 0 or i >= len(s): 
                        if char == UNK_CHAR: x.append(1)
                        else: x.append(0)
                    else:
                        if char == s[i]: x.append(1)
                        else: x.append(0)

        transformed_instances.append(x)
        y.append(schwa_was_deleted)
    
    # generate the columns of our input
    # is x char/feature present at position y?
    col = []
    if use_phon:
        for i in list(range(-left, 0)) + list(range(1, right + 1)):
            for j in phons:
                col.append('s' + str(i) + '_' + str(j))
    else:
        for i in list(range(-left, 0)) + list(range(1, right + 1)):
            for j in chars:
                col.append('s' + str(i) + '_' + str(j))

    # create the input columns
    X = pd.DataFrame(transformed_instances,
        columns=col)

    # schwa retention/deletion rate
    print(y.count(True), y.count(False))

    # 20% is the final test data, 20% is for development
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, train_size=0.60, test_size=0.40, random_state=42)
    
    X_dev, y_dev = X_test[:len(X_test) // 2], y_test[:len(y_test) // 2]
    X_test, y_test = X_test[len(X_test) // 2:], y_test[len(y_test) // 2:]

    # model = LogisticRegression(solver='liblinear', max_iter=1000, verbose=True)
    # model = MLPClassifier(max_iter=1000,  learning_rate_init=1e-4, hidden_layer_sizes=(250,), verbose=True)
    model = XGBClassifier(verbosity=2, max_depth=11, n_estimators=200)






    # TUNING

    # xgboost NETWORK
    # model = MLPClassifier(max_iter=1000, verbose=True)
    # grid_values = {
    #     'learning_rate_init': [1e-4, 1e-3, 1e-2, 0.1, 0.5, 1, 5, 10],
    #     'hidden_layer_sizes': [(10), (50), (100), (200), (500), (750), (1000)],
    # }
    # grid_search_model = GridSearchCV(model, param_grid=grid_values, scoring='accuracy')
    # grid_search_model.fit(X_train, y_train)

    # print('Best parameters found by grid search:')
    # print(grid_search_model.best_params_)
    # y_pred = grid_search_model.predict(X_dev)
    # print(accuracy_score(y_pred, y_dev))




    model = load('models/xgboost/xgboost.joblib')
    # model.fit(X_train, y_train)
    # dump(model, 'models/xgboost/xgboost_nophon.joblib')
    # dump(chars, 'models/xgboost/xgboost_nophon_chars.joblib')
    # dump(phons, 'models/xgboost/xgboost_nophon_phons.joblib')
    # plot_tree(model)
    y_pred = model.predict(X_test)
    print(accuracy_score(y_pred, y_test), recall_score(y_pred, y_test), precision_score(y_pred, y_test))
    for i in range(len(X_test)):
        if y_pred[i] != y_test[i]:
            print(' '.join(schwa_instances[X_test.iloc[i].name][0]), schwa_instances[X_test.iloc[i].name][1], y_pred[i], y_test[i])

    # fig = plt.gcf()
    # fig.set_size_inches(150, 100)
    # fig.savefig('tree5.png')

# compare wiktionary transliterations with actual
def compare_wiktionary():
    data = pd.read_csv('data/extra_large.csv', header=0)
    tot, corr = 0, 0
    for _, row in data.iterrows():
        h = row.hindi.replace(' - ', '')
        p = row.phon.replace(' - ', ' ').split()
        w = ' '.join(wikt.convert(wikt.translit(h))).replace(' - ', ' ')
        w = w.split()
        i, j = 0, 0
        n, m = len(p), len(w)
        c = 1
        while i < n and j < m:
            if p[i] == w[j]:
                i += 1
                j += 1
            elif p[i] == 'a' or w[j] == 'a':
                c = 0
                if p[i] == 'a': i += 1
                else: j += 1
            else:
                c = 2
                break
        if c == 1: corr += 1
        elif c == 0: print(h)
        if c != 2: tot += 1
    print(corr / tot)
        
def corpus_freq():
    count = {}
    i = 0
    with open('corpora/monolingual.hi', 'r') as fin:
        line = fin.readline()
        while line:
            for word in re.findall(r'[ऀ-ॿa]+', line):
                if word not in count:
                    count[word] = 0
                count[word] += 1
            if i % 10000 == 0:
                print(i)
            i += 1
            line = fin.readline()
    with open('corpora/freq.csv', 'w') as fout:
        for word, freq in count.items():
            fout.write(word + ',' + str(freq) + '\n')

def test(word, model_path, chars_path, left=4, right=4):
    model = load(model_path)
    chars = load(chars_path)
    print(chars)
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
    Y = model.predict(X)
    pos = 0
    print(Y)
    for phone in transliteration:
        if phone == 'a':
            print('a' if Y[pos] else '', end='')
            pos += 1
        else:
            print(phone, end='')
    print()
    


if __name__ == '__main__':
    main('data/extra_large.csv', True, 5, 5)
    # compare_wiktionary()
    # corpus_freq()
    print('Testing:')
    while True:
        test(input(), 'models/neural_net.joblib', 'models/neural_net_chars.joblib', 5, 5)