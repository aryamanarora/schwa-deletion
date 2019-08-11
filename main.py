import sys
import numpy as np
import pandas as pd
import transliterate as tr
import scrape
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, recall_score, f1_score

UNK_CHAR = "🆒"

def main(input_filename, left=4, right=4, sep=None):
    data = pd.read_csv(input_filename, header=0, sep=sep) if sep else pd.read_csv(input_filename, header=0)

    # force align the predicted orthographic transliteration (without schwa dropping)
    # with the actual phonetic transliteration (schwa dropping) to created training/test data
    schwa_instances = []
    for _, row in data.iterrows():
        print(chr(27) + "[2J")
        print('Processing row', _)
        try:
            schwa_instances += [[tr.narrow_categorize(row.hindi), schwa_instance[1], schwa_instance[0]]
                    for schwa_instance in tr.force_align(tr.transliterate(row.hindi), str(row.phon))]
        except Exception as e:
            # print(e)
            continue
    
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
                     columns=["s" + str(i) for i in list(range(-left, 0)) + list(range(1, right + 1))])
    X = pd.get_dummies(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42)

    model = LogisticRegression(solver='liblinear', max_iter=1000)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    # for i in zip(transformed_instances, y_pred, y_test):
    #     print(i)

    print("Logistic regression:", [accuracy_score(y_pred, y_test), recall_score(y_pred, y_test), f1_score(y_pred, y_test)])

# compare wiktionary transliterations with actual
def compare_wiktionary():
    data = pd.read_csv('hi_ur_pron.tsv', header=0, sep='\t')
    wikt = pd.read_csv('hi_ur_pron_wikt.tsv', header=0, sep='\t')

    instances = []
    for i, row in data.iterrows():
        w = ''.join(scrape.wiktionary_transliterate(wikt.iloc[i]['wikt']))
        x = row.phon.replace('.', '').replace(' ', '')
        if w != x:
            print(w, x)

if __name__ == "__main__":
    main('hi_ur_pron.tsv', 4, 4, '\t')
    # compare_wiktionary()
