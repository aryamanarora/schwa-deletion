import main

while True:
    word = input()
    main.test(
        [word],
        'models/xgboost/xgboost.joblib',
        'models/xgboost/xgboost_chars.joblib',
        'models/xgboost/xgboost_phons.joblib',
        5,
        5
    )