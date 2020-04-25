import sys
import numpy as np
import pandas as pd
import transliterate as tr
import scrape
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, recall_score, f1_score, precision_score
from joblib import dump, load
import re

UNK_CHAR = '🆒'

def main(input_filename, use_phon, left=4, right=4):
    data = pd.read_csv(input_filename, header=0)

    # force align the predicted orthographic transliteration (without schwa dropping)
    # with the actual phonetic transliteration (schwa dropping) to created training/test data
    schwa_instances = []
    for _, row in data.iterrows():
        # print(chr(27) + '[2J')
        # print('Processing row', _)
        try:
            schwa_instances += [[tr.transliterate(row.punjabi), schwa_instance[1], schwa_instance[0]]
                for schwa_instance in tr.force_align(tr.transliterate(row.punjabi), str(row.phon))]
            # schwa_instances += [[tr.transliterate(row.punjabi), schwa_instance[1], schwa_instance[0]]
            #         for schwa_instance in tr.force_align_weak(tr.transliterate(row.punjabi), str(row.phon))]
        except Exception as e:
            print(e)
            continue
    
    print(len(schwa_instances))
    chars = set()
    for word in schwa_instances:
        for char in word[0]:
            chars.add(char)
    chars.add(UNK_CHAR)
    chars = list(chars)
    phons = set()

    if use_phon:
        for phoneme, features in tr.phonological_features.items():
            for feature in features:
                phons.add(feature)
        phons = list(phons)

    chars = load('models/neural/neural_chars.joblib')
    phons = load('models/neural/neural_phons.joblib')
    
    # clean up the data
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
    
    col = []
    if use_phon:
        for i in list(range(-left, 0)) + list(range(1, right + 1)):
            for j in phons:
                col.append('s' + str(i) + '_' + str(j))
    else:
        for i in list(range(-left, 0)) + list(range(1, right + 1)):
            for j in chars:
                col.append('s' + str(i) + '_' + str(j))

    X = pd.DataFrame(transformed_instances,
        columns=col)

    print(y.count(True), y.count(False))

    # 20% is the final test data, 20% is for development
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, train_size=0.60, test_size=0.40, random_state=42)
    
    X_dev, y_dev = X_test[:len(X_test) // 2], y_test[:len(y_test) // 2]
    X_test, y_test = X_test[len(X_test) // 2:], y_test[len(y_test) // 2:]

    # model = LogisticRegression(solver='liblinear', max_iter=1000, verbose=True)
    model = MLPClassifier(max_iter=1000,  learning_rate_init=1e-4, hidden_layer_sizes=(250,), verbose=True)
    # model = XGBClassifier(verbosity=2, max_depth=11, n_estimators=200)

    model = load('models/neural/neural.joblib')
    model.fit(X_train, y_train)
    # dump(model, 'models/neural/neural.joblib')
    # dump(chars, 'models/neural/neural_chars.joblib')
    # dump(phons, 'models/neural/neural_phons.joblib')
    y_pred = model.predict(X_test)

    print(
        accuracy_score(y_test, y_pred),
        precision_score(y_test, y_pred),
        recall_score(y_test, y_pred))
    
    misses = set()
    all_words = set()
    for i in range(len(X_test)):
        all_words.add(' '.join(schwa_instances[X_test.iloc[i].name][0]))
        if y_pred[i] != y_test[i]:
            misses.add(' '.join(schwa_instances[X_test.iloc[i].name][0]))
            print(' '.join(schwa_instances[X_test.iloc[i].name][0]), schwa_instances[X_test.iloc[i].name][1], y_pred[i], y_test[i])
    print(f"{len(misses)} words missed out of {len(all_words)}")

if __name__ == "__main__":
    main('data/large.csv', False, 5, 5)