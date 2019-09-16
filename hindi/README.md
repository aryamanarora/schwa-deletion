# Schwa Deletion

## Notes

Wiktionary has 93.75% accuracy on the short wordlist.

The best performance so far on the short wordlist the the lblinear logistic regressor with a window of 3 or 5 (it's tied) on each side and with the text run through `narrow_categorize` conversion. It gets an accuracy score of 95.45%.

On the long wordlist it is the same except with a window of 6 phones on either side, with a score of 94.31%.

