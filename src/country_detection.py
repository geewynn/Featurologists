import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pickle


def prepare_input(data_path):
    df = pd.read_csv(data_path)
    df.dropna(axis=0, inplace=True)
    X = df.drop([
        'InvoiceNo', 'StockCode', 'Description', 'InvoiceDate', 'Country',
        'Geography'
    ],
        axis=1)
    X = pd.get_dummies(X, prefix_sep='_')
    Y = df['Country']
    Y = LabelEncoder().fit_transform(Y)
    X2 = StandardScaler().fit_transform(X)
    return X2, Y


def train_model(data_path="data/features_no_live_data.csv"):
    X2, Y = prepare_input(data_path)

    X_Train, X_Test, Y_Train, Y_Test = train_test_split(X2,
                                                        Y,
                                                        test_size=0.30,
                                                        random_state=101)

    trainedmodel = LogisticRegression().fit(X_Train, Y_Train)
    predictions = trainedmodel.predict(X_Test)
    print("Logistic Regression Accuracy: ",
          trainedmodel.score(X_Train, Y_Train))
    pickle.dump(trainedmodel, open("models/country_detection.pkl", 'wb'))


def test_model(data_path="data/features_raw_live_data.csv", model_path="models/country_detection.pkl"):
    X2, Y = prepare_input(data_path)
    loaded_model = pickle.load(open(model_path, 'rb'))
    result = loaded_model.score(X2, Y)
    print("Live data accuracy: ", result)


train_model()
test_model()
