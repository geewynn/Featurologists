import json
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd
import sklearn.model_selection
import xgboost
from sklearn.preprocessing import LabelEncoder


def build_country_encoder(countries: List[str]):
    enc = LabelEncoder()
    enc.fit(countries)
    # TODO: save/load
    # numpy.save('classes.npy', le.classes_)
    # encoder = LabelEncoder()
    # encoder.classes_ = numpy.load('classes.npy')
    return enc


def save_country_encoder(enc: LabelEncoder, path: Union[Path, str]):  # type: ignore
    np.save(path, enc.classes_)


def load_country_encoder(path: Union[Path, str]):
    encoder = LabelEncoder()
    encoder.classes_ = np.load(path, allow_pickle=True)
    return encoder


def preprocess(offline_cleaned_df: pd.DataFrame, env: LabelEncoder):  # type: ignore
    # Cleanup: drop or rename bad columns
    df_orig = offline_cleaned_df

    df = pd.DataFrame()

    df["Quantity"] = df_orig["Quantity"]
    df["UnitPrice"] = df_orig["UnitPrice"]

    df["Country"] = env.transform(df_orig["Country"])

    dfdt = pd.to_datetime(df_orig["InvoiceDate"])
    df["InvoiceDate_year"] = dfdt.dt.year
    df["InvoiceDate_month"] = dfdt.dt.month
    df["InvoiceDate_day"] = dfdt.dt.day
    df["InvoiceDate_hour"] = dfdt.dt.hour
    df["InvoiceDate_minute"] = dfdt.dt.minute
    df["InvoiceDate_second"] = dfdt.dt.second

    # target variable: 'IsCancelled'
    df["IsCancelled"] = (df_orig["QuantityCanceled"] > 0).astype(int)

    return df


def train_test_split(data, train_size=0.6):
    ycol = "IsCancelled"
    # 'Country',
    X = data.drop(columns=ycol)
    Y = data[ycol]

    X_train, X_test, Y_train, Y_test = sklearn.model_selection.train_test_split(
        X,
        Y,
        train_size=train_size,
        shuffle=True,
        stratify=Y,
    )
    return X_train, X_test, Y_train, Y_test


def train_xgboost(X_train, Y_train):
    model = xgboost.XGBClassifier(
        # max_depth=50,
        # min_child_weight=1,
        n_estimators=200,
        learning_rate=0.15,
        use_label_encoder=False,
        eval_metric="aucpr",
    )
    model.fit(X_train, Y_train)
    return model


def calc_score(model, X_test, Y_test):
    return model.score(X_test, Y_test)


def predict(model, X_test, return_proba=False):
    Y_prob = model.predict_proba(X_test)
    Y_pred = np.argmax(Y_prob, 1)
    if return_proba:
        return Y_pred, Y_prob
    else:
        return Y_pred


def get_least_and_most_confident_predictions(Y_prob):
    y = np.apply_along_axis(np.max, 1, Y_prob)
    least = y.min().item()
    most = y.max().item()
    return least, most


def calc_all_metrics(model, X_test, Y_test):
    Y_pred, Y_prob = predict(model, X_test, return_proba=True)

    acc = calc_accuracy(Y_pred, Y_test)
    roc_auc = calc_roc_auc(Y_test, Y_pred)
    mse = calc_mse(Y_test, Y_pred)
    r2 = calc_r2(Y_test, Y_pred)

    least, most = get_least_and_most_confident_predictions(Y_prob)

    p_positive_count = count_positive_answers(Y_pred)
    p_negative_count = count_negative_answers(Y_pred)
    p_positive_to_negative_fraction = p_positive_count / p_negative_count

    g_positive_count = count_positive_answers(Y_test)
    g_negative_count = count_negative_answers(Y_test)
    g_positive_to_negative_fraction = g_positive_count / g_negative_count

    p_to_g_negative_fraction = p_positive_count / g_positive_count

    meta = {
        "score_accuracy": acc,
        "score_roc_auc": roc_auc,
        "error_mse": mse,
        "error_r2": r2,
        "confidence_least": least,
        "confidence_most": most,
        "predicted_positive_count": p_positive_count,
        "predicted_negative_count": p_negative_count,
        "predicted_positive_to_negative_fraction": p_positive_to_negative_fraction,
        "groundtruth_positive_count": g_positive_count,
        "groundtruth_negative_count": g_negative_count,
        "groundtruth_positive_to_negative_fraction": g_positive_to_negative_fraction,
        "predicted_positive_to_groundtruth_negative_fraction": p_to_g_negative_fraction,
    }
    return meta


def calc_accuracy(Y_test, Y_pred):
    acc = sklearn.metrics.accuracy_score(Y_test, Y_pred)
    return acc.item()


def calc_mse(Y_test, Y_pred):
    mse = sklearn.metrics.mean_squared_error(Y_test, Y_pred)
    return mse.item()


def calc_r2(Y_test, Y_pred):
    r2 = sklearn.metrics.r2_score(Y_test, Y_pred)
    return r2.item()


def calc_roc_auc(Y_test, Y_pred):
    roc_auc = sklearn.metrics.roc_auc_score(Y_test, Y_pred)
    return roc_auc.item()


def count_positive_answers(Y):
    return Y[Y > 0].size


def count_negative_answers(Y):
    return Y[Y == 0].size


def save_model(model, target_dir: Union[str, Path], metadata: Optional[Dict] = None):
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True)
    with (target_dir / "model.pkl").open("wb") as f:
        pickle.dump(model, f)
    (target_dir / "metadata.json").write_text(json.dumps(metadata, indent=4))
