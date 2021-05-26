# import pickle
import random

import xgboost as xgb
from customer_segmentation_toolkit.data_zoo import download_data_csv
from sklearn import model_selection
from sklearn.metrics import roc_auc_score


# import catboost
# import lightgbm as lgb
# import matplotlib.cm as cm
# import matplotlib.pyplot as plt
# import numpy as np
# import pandas as pd
# from sklearn import metrics, model_selection, preprocessing
# from sklearn.ensemble import AdaBoostClassifier
# from sklearn.linear_model import LogisticRegression
# from sklearn.metrics import mean_squared_error, precision_score, roc_auc_score
# from sklearn.model_selection import GridSearchCV


def load_data(shuffle: bool = True, random_seed: int = 42):
    csv = "no_live_data__cleaned__purchase_clusters__train__customer_clusters.csv"
    selected_customers = download_data_csv(
        f"data/output/04_data_analyse_customers/{csv}"
    )
    # columns: [CustomerID,count,min,max,mean,sum,categ_0,categ_1,categ_2,categ_3,
    #           categ_4,LastPurchase,FirstPurchase,cluster]

    columns = ["mean", "categ_0", "categ_1", "categ_2", "categ_3", "categ_4"]
    X = selected_customers[columns]
    Y = selected_customers["cluster"]

    if shuffle:
        random.seed(random_seed)
    X_train, X_test, Y_train, Y_test = model_selection.train_test_split(
        X, Y, train_size=0.8, shuffle=shuffle
    )
    return X_train, X_test, Y_train, Y_test


# clf = AdaBoostClassifier(n_estimators=100, random_state=0)
# clf.fit(X_train, Y_train)

# clf.score(X_test, Y_test)

# Y_prob = clf.predict_proba(X_test)
# #Y_prob = [np.argmax(line) for line in Y_prob]

# macro_roc_auc_ovo = roc_auc_score(Y_test.values, Y_prob, multi_class="ovo",
#                                   average="macro")
# print("One-vs-One ROC AUC scores:\n{:.6f} (macro)"
#       .format(macro_roc_auc_ovo))


def train(X_train, Y_train, **kwargs):
    # Train XGboost
    model = xgb.XGBClassifier(
        max_depth=50,
        min_child_weight=1,
        n_estimators=100,
        learning_rate=0.16,
        use_label_encoder=False,
        eval_metric="mlogloss",
    )
    model.fit(X_train, Y_train)

    # print(model.score(X_test, Y_test))
    return model


def calc_score(model, X_test, Y_test, **kwargs):
    Y_prob = model.predict_proba(X_test)
    macro_roc_auc_ovo = roc_auc_score(
        Y_test, Y_prob, multi_class="ovo", average="macro"
    )
    return macro_roc_auc_ovo
