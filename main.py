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
from sklearn.metrics import accuracy_score, recall_score, f1_score

UNK_CHAR = '🆒'

def main(input_filename, left=4, right=4):
    data = pd.read_csv(input_filename, header=0)

    # force align the predicted orthographic transliteration (without schwa dropping)
    # with the actual phonetic transliteration (schwa dropping) to created training/test data
    schwa_instances = []
    for _, row in data.iterrows():
        # print(chr(27) + '[2J')
        # print('Processing row', _)
        try:
            # schwa_instances += [[tr.transliterate(row.hindi), schwa_instance[1], schwa_instance[0]]
            #     for schwa_instance in tr.force_align(tr.transliterate(row.hindi), str(row.phon))]
            schwa_instances += [[tr.transliterate(row.hindi), schwa_instance[1], schwa_instances[0]]
                    for schwa_instance in tr.force_align_weak(tr.transliterate(row.hindi), str(row.phon))]
        except Exception as e:
            print(e)
            continue
    
    print(len(schwa_instances))
    
    # clean up the data
    y = []
    transformed_instances = []
    for s, schwa_index, schwa_was_deleted in schwa_instances:
        x = []
        for i in range(schwa_index - left, schwa_index + right + 1):
            if i == schwa_index:
                continue

            if i < 0 or i >= len(s):
                x.append(UNK_CHAR)
            else:
                x.append(s[i])

        transformed_instances.append(x)
        y.append(schwa_was_deleted)

    X = pd.DataFrame(transformed_instances,
        columns=['s' + str(i) for i in list(range(-left, 0)) + list(range(1, right + 1))])
    X_old = X
    X = pd.get_dummies(X)

    print(y.count(True), y.count(False))

    # 20% is the final test data, 20% is for development
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, train_size=0.60, test_size=0.40, random_state=42)
    
    X_dev, y_dev = X_test[:len(X_test) // 2], y_test[:len(y_test) // 2]
    X_test, y_test = X_test[len(X_test) // 2:], y_test[len(y_test) // 2:]

    model = LogisticRegression(solver='liblinear', max_iter=1000, verbose=True)
    # model = MLPClassifier(max_iter=1000,  learning_rate_init=1e-4, hidden_layer_sizes=(250,), verbose=True)
    # model = XGBClassifier(verbosity=1, max_depth=10, n_estimators=100)

    model.fit(X_train, y_train)
    y_pred = model.predict(X_dev)

    print(i, "estimators:", accuracy_score(y_pred, y_dev), recall_score(y_pred, y_dev))

    # print(X_dev)
    # print incorrect predictions
    # for i, row in np.ndenumerate(y_pred):
    #     if y_pred[i[0]] != y_dev[i[0]]:
    #         dat = X_old.iloc[X_dev.iloc[i[0]].name].to_list()
    #         print(str(i[0]) + ':', ' '.join(dat[:left]) + ' [a] ' + ' '.join(dat[left:]), y_pred[i[0]], y_dev[i[0]])
    
    # for i in zip(transformed_instances, y_pred, y_test):
    #     print(i)

# compare wiktionary transliterations with actual
def compare_wiktionary():
    data = pd.read_csv('data/small.csv', header=0)
    wikt = pd.read_csv('data/small_wiktionary.csv', header=0)

    instances = []
    for i, row in data.iterrows():
        w = ''.join(scrape.wiktionary_transliterate(wikt.iloc[i]['wikt']))
        x = row.phon.replace('.', '').replace(' ', '')
        if w != x:
            print(w, x)

if __name__ == '__main__':
    main('data/extra_large.csv', 5, 5)
    input()