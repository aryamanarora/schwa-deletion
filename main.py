# needed data: orthographic forms and phonetic forms
# convert to IPA or use existing system
#
# 1. align Hindi orthographic with phonetic representation

import numpy as np
import pandas as pd
import transliterate as tr

# read in the data
fin = "hi_ur_pron.tsv"
df = pd.read_csv(fin, header=0, sep='\t')

for i in range(847):
    res = tr.force_align(df.hindi[i], df.phon[i])
    print(df.hindi[i], res)