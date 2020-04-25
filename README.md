# schwa-deletion

Machine learning models for [schwa deletion](https://en.wikipedia.org/wiki/Schwa_deletion_in_Indo-Aryan_languages) in Hindi and Punjabi.

Pre-generated models, which achieve state-of-the-art performance, using scikit-learn's `MLPClassifier` and `LogisticRegression`, as well as XGBoost's `XGBClassifier` are included in the `models` subfolder in each language's directory.

The results of this research are presented in the paper below:

> "Supervised Grapheme-to-Phoneme Conversion of Orthographic Schwas in Hindi and Punjabi", Aryaman Arora, Luke Gessler, and Nathan Schneider. In arXiv:2004.10353 (2020). URL: https://arxiv.org/abs/2004.10353

## Usage

Ensure that you are using the most recent Python 3 version.

Clone repo and install requirements:

```bash
git clone https://github.com/aryamanarora/schwa-deletion.git
cd schwa-deletion
pip install -r requirements.txt
```

Testing the pretrained Hindi XGBoost model:

```bash
cd hindi
python test.py
```

You can see `test.py` for an idea of how to use the `main.py` script as a module.
