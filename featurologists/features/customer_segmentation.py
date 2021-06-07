import pandas as pd

from customer_segmentation_toolkit.analyse_customers import compute_customer_clusters, add_customer_clusters_info
from customer_segmentation_toolkit.analyse_customers import (
    convert_customers_df_to_np,
    analyse_customers_pca,
)
from customer_segmentation_toolkit.analyse_customers import build_transactions_per_user

import datetime
from customer_segmentation_toolkit.analyse_purchases import build_product_list

from customer_segmentation_toolkit.clean_rows import clean_data_rows
from customer_segmentation_toolkit.analyse_purchases import build_keywords_matrix
from customer_segmentation_toolkit.analyse_purchases import compute_purchase_clusters

from sklearn.metrics import silhouette_samples, silhouette_score
from customer_segmentation_toolkit.analyse_purchases import plot_silhouette
from customer_segmentation_toolkit.analyse_purchases import add_purchase_clusters_info

from customer_segmentation_toolkit.load_split import split_by_invoice_date


def transform(no_live_data: pd.DataFrame) -> pd.DataFrame:
    df = no_live_data.copy()

    N_PURCHASE_CLUSTERS = 5
    N_CUSTOMER_CLUSTERS = 11
    THRESHOLD = [0, 1, 2, 3, 5, 10]

    # Clean bad data entries
    df_cleaned = clean_data_rows(df)

    # Analysing purchases
    list_products = build_product_list(df_cleaned)
    matrix = build_keywords_matrix(df_cleaned, list_products, THRESHOLD)
    clusters = compute_purchase_clusters(matrix, N_PURCHASE_CLUSTERS)

    df_with_clusters = add_purchase_clusters_info(df_cleaned, clusters, N_PURCHASE_CLUSTERS)

    # Analysing customers
    # NOTE: here we do different from the original notebook: we don't split train-test here, we'll do it later
    basket_price = df_with_clusters
    transactions_per_user = build_transactions_per_user(basket_price, n_purchase_clusters=N_PURCHASE_CLUSTERS)
    matrix = convert_customers_df_to_np(transactions_per_user, N_PURCHASE_CLUSTERS)
    scaled_matrix, pca = analyse_customers_pca(matrix)
    clusters_clients = compute_customer_clusters(scaled_matrix, N_CUSTOMER_CLUSTERS)

    merged_df = add_customer_clusters_info(transactions_per_user, clusters_clients)

    # done
    return merged_df
