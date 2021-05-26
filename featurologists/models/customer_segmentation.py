import json
import pickle
import random
from pathlib import Path
from typing import Dict, Optional, Union

import lightgbm
import xgboost
from customer_segmentation_toolkit.data_zoo import download_data_csv
from sklearn import model_selection
from sklearn.metrics import roc_auc_score


def load_data(random_seed: int = 42):
    random.seed(random_seed)

    csv = "no_live_data__cleaned__purchase_clusters__train__customer_clusters.csv"
    selected_customers = download_data_csv(
        f"data/output/04_data_analyse_customers/{csv}"
    )
    # columns: [CustomerID,count,min,max,mean,sum,categ_0,categ_1,categ_2,categ_3,
    #           categ_4,LastPurchase,FirstPurchase,cluster]

    columns = ["mean", "categ_0", "categ_1", "categ_2", "categ_3", "categ_4"]
    X = selected_customers[columns]
    Y = selected_customers["cluster"]

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
    model = lightgbm.train(
        params,
        d_train,
    )
    return model


def predict_proba(model, X_test, **kwargs):
    try:
        Y_prob = model.predict_proba(X_test)
    except AttributeError:
        # LightGBM model doesn't have method predict_proba
        Y_prob = model.predict(X_test)
    return Y_prob


def calc_score_roc_auc(model, X_test, Y_test, **kwargs):
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
