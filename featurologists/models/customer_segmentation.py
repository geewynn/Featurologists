import json
import pickle
from pathlib import Path
from typing import Dict, Optional, Union

import lightgbm
import numpy as np
import pandas as pd
import xgboost
from sklearn import model_selection
from sklearn.metrics import accuracy_score, roc_auc_score

from ..data_transforms import build_client_clusters


def train_test_split(df):
    columns = ["mean", "categ_0", "categ_1", "categ_2", "categ_3", "categ_4"]
    X = df[columns]
    Y = df["cluster"]

    X_train, X_test, Y_train, Y_test = model_selection.train_test_split(
        X,
        Y,
        train_size=0.8,
        shuffle=True,
        stratify=Y,
    )
    return X_train, X_test, Y_train, Y_test


def train_xgboost(X_train, Y_train, **kwargs):
    model = xgboost.XGBClassifier(
        max_depth=kwargs.pop("max_depth", 50),
        min_child_weight=kwargs.pop("min_child_weight", 1),
        n_estimators=kwargs.pop("n_estimators", 100),
        learning_rate=kwargs.pop("learning_rate", 0.16),
        use_label_encoder=kwargs.pop("use_label_encoder", False),
        eval_metric=kwargs.pop("eval_metric", "aucpr"),
    )
    model.fit(X_train, Y_train)
    return model


def train_lightgbm(X_train, Y_train, **kwargs):
    params = {
        "max_depth": kwargs.pop("max_depth", 50),
        "learning_rate": kwargs.pop("learning_rate", 0.16),
        "num_leaves": kwargs.pop("num_leaves", 900),
        "n_estimators": kwargs.pop("n_estimators", 100),
        "boosting_type": kwargs.pop("boosting_type", "gbdt"),
        "objective": kwargs.pop("objective", "multiclass"),
        "num_class": kwargs.pop("num_class", 11),
        "verbosity": -1,
    }
    d_train = lightgbm.Dataset(X_train, label=Y_train)
    model = lightgbm.train(params, d_train)
    return model


def predict_proba(model, X_test):
    try:
        Y_prob = model.predict_proba(X_test)
    except AttributeError:
        # LightGBM model doesn't have method predict_proba
        Y_prob = model.predict(X_test)
    return Y_prob


def predict(model, no_live_data_batch: pd.DataFrame):  # type: ignore
    X_test = build_client_clusters(no_live_data_batch)
    # print(f"X_test shape: {X_test.shape}")
    Y_prob = predict_proba(model, X_test)
    Y_pred = np.argmax(Y_prob, 1)
    return Y_pred


def calc_score_accuracy(model, X_test, Y_test):
    Y_pred = predict(model, X_test)
    score = accuracy_score(Y_test, Y_pred)
    return score


def calc_score_roc_auc(model, X_test, Y_test, **kwargs):
    # Note: failing with ValueError: Number of classes
    # in y_true not equal to the number of columns in 'y_score'
    Y_prob = predict_proba(model, X_test)
    score = roc_auc_score(
        Y_test,
        Y_prob,
        multi_class=kwargs.pop("multi_class", "ovo"),
        average=kwargs.pop("average", "macro"),
    )
    return score


def save_model(model, target_dir: Union[str, Path], metadata: Optional[Dict] = None):
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True)
    with (target_dir / "model.pkl").open("wb") as f:
        pickle.dump(model, f)
    (target_dir / "metadata.json").write_text(json.dumps(metadata, indent=4))
