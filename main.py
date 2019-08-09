# needed data: orthographic forms and phonetic forms
# convert to IPA or use existing system
#
# 1. align Hindi orthographic with phonetic representation

import sys
import numpy as np
import pandas as pd
import transliterate as tr
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, recall_score, f1_score

UNK_CHAR = "🆒"

# read in the data
def main(input_filename, left=4, right=4, sep=None):
    csv_data = pd.read_csv(input_filename, header=0, sep=sep) if sep else pd.read_csv(input_filename, header=0)

    instances = []
    for _, row in csv_data.iterrows():
        try:
            instances += [[tr.narrow_categorize(row.hindi), schwa_instance[1], schwa_instance[0]]
                    for schwa_instance in tr.force_align(str(row.hindi), str(row.phon))]
        except Exception as e:
            # print(e)
            continue
    
    # print(len(instances))
    # input()

    y = []
    transformed_instances = []
    for s, schwa_index, schwa_was_deleted in instances:
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

    model = LogisticRegression(solver='liblinear')
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    # for i in zip(transformed_instances, y_pred, y_test):
    #     print(i)

    return [accuracy_score(y_pred, y_test), recall_score(y_pred, y_test), f1_score(y_pred, y_test)]


if __name__ == "__main__":
    for i in range(1, 11):
        print(main('hi_pron.csv', i, i))
