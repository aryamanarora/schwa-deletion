# needed data: orthographic forms and phonetic forms
# convert to IPA or use existing system
#
# 1. align Hindi orthographic with phonetic representation

import numpy as np
import pandas as pd
import transliterate as tr
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, recall_score, f1_score


CHAR_WINDOW = 4
UNK_CHAR = "🆒"

# read in the data

def main(input_filename="hi_ur_pron.tsv"):
    csv_data = pd.read_csv(input_filename, header=0, sep='\t')

    instances = []
    for _, row in csv_data.iterrows():
        instances += [[tr.transliterate(row.hindi), schwa_instance[1], schwa_instance[0]]
                  for schwa_instance in tr.force_align(row.hindi, row.phon)]

    y = []
    transformed_instances = []
    for s, schwa_index, schwa_was_deleted in instances:
        x = []
        for i in range(schwa_index - CHAR_WINDOW, schwa_index + CHAR_WINDOW + 1):
            if i == schwa_index:
                continue

            if i < 0 or i >= len(s):
                x.append(UNK_CHAR)
            else:
                x.append(s[i])

        transformed_instances.append(x)
        y.append(schwa_was_deleted)

    X = pd.DataFrame(transformed_instances,
                     columns=["s-4", "s-3", "s-2", "s-1", "s+1", "s+2", "s+3", "s+4"])
    X = pd.get_dummies(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42)

    model = LogisticRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    print(accuracy_score(y_pred, y_test))
    print(recall_score(y_pred, y_test))
    print(f1_score(y_pred, y_test))


if __name__ == "__main__":
    main()
