import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import datetime
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim


class Latent_Embed(nn.Module):
    def __init__(self, vocab_size, embedding_dim):
        super(Latent_Embed, self).__init__()
        self.embeddings = nn.Embedding(vocab_size, embedding_dim)
        self.linear1 = nn.Linear(3, 2)
        self.linear2 = nn.Linear(2, 1)

    def forward(self, inputs):
        embeds = self.embeddings(inputs)
        out = F.relu(self.linear1(embeds))
        out = F.relu(self.linear2(out))
        return out


def feature_maker(data_path='../data/no_live_data.csv'):
    df = pd.read_csv(data_path, encoding="ISO-8859-1",
                     dtype={'CustomerID': str, 'InvoiceID': str})
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

    df.dropna(axis=0, subset=['CustomerID'], inplace=True)
    df.drop_duplicates(inplace=True)

    df['year'] = df['InvoiceDate'].dt.year
    df['month'] = df['InvoiceDate'].dt.month
    df['day'] = df['InvoiceDate'].dt.day

    df['Log_UnitPrice'] = (
        df['UnitPrice'] - df['UnitPrice'].min() + 1).transform(np.log)
    df['Geography'] = np.select([df.Country == 'United Kingdom'],
                                ['UK'],
                                default='Rest of the World')

    df['Price Ranges'] = pd.cut(df['UnitPrice'], bins=[
                                0, 100, 200, 38970], labels=["Low", "Medium", "High"])
    size = len(df.Description)
    encoder, scaler = LabelEncoder(), MinMaxScaler()
    aut = encoder.fit_transform(df.Description)
    rat = scaler.fit_transform(df[['UnitPrice']])
    aut_t = torch.tensor(aut).long()  # .to(torch.int64)
    rat_t = torch.tensor(rat).long()  # .to(torch.int64)
    loss_function = nn.MSELoss()
    model = Latent_Embed(size, 3)
    optimizer = optim.SGD(model.parameters(), lr=0.001)

    for epoch in range(2):
        total_loss = 0
        for context, target in zip(aut_t, rat_t):
            model.zero_grad()
            log_probs = model(context)
            loss = loss_function(log_probs.double(), target.view(1).double())
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print("Loss: ", total_loss/len(aut_t))

    embedding_weights = pd.DataFrame(model.embeddings.weight.detach().numpy())
    embedding_weights.columns = ['X1', 'X2', 'X3']
    pca = PCA(n_components=3)
    X_pca = pca.fit_transform(df.drop(
        ['Description', 'StockCode', 'InvoiceNo', 'InvoiceDate', 'Country', 'Geography', 'Price Ranges'], axis=1))
    PCA_df = pd.DataFrame(data=X_pca, columns=['PC1', 'PC2', 'PC3'])
    df['pca_dec_1'] = PCA_df['PC1']
    df['pca_dec_2'] = PCA_df['PC2']
    df['pca_dec_3'] = PCA_df['PC3']
    df['embed_dec_1'] = embedding_weights['X1']
    df['embed_dec_2'] = embedding_weights['X2']
    df['embed_dec_3'] = embedding_weights['X3']
    set_entrainement = df[df['InvoiceDate'].dt.date <
                          datetime.date(2011, 10, 1)]
    raw_live_data = df[df['InvoiceDate'].dt.date >= datetime.date(2011, 10, 1)]
    set_entrainement.to_csv('../data/features_no_live_data.csv', index=False)
    raw_live_data.to_csv('../data/features_raw_live_data.csv', index=False)
    print("Original df shape: ", df.shape)
    print("Training Features shape: ", set_entrainement.shape)
    print("Live Features shape: ", raw_live_data.shape)


feature_maker(data_path='../data/no_live_data.csv')
