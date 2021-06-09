import logging

import pandas as pd
from customer_segmentation_toolkit.analyse_customers import (
    add_customer_clusters_info,
    analyse_customers_pca,
    build_transactions_per_user,
    compute_customer_clusters,
    convert_customers_df_to_np,
)
from customer_segmentation_toolkit.analyse_purchases import (
    add_purchase_clusters_info,
    build_keywords_matrix,
    build_product_list,
    compute_purchase_clusters,
)
from customer_segmentation_toolkit.clean_rows import clean_data_rows


def build_client_clusters(no_live_data: pd.DataFrame) -> pd.DataFrame:  # type: ignore
    """
    Transforms taken from the Customer segmentation toolkit:
      https://github.com/artemlops/customer-segmentation-toolkit/
      (see index.ipynb)

    In general, it uses PCA to compute clusters of products
    (using keywords in Descriptions) and of customers, and
    returns a copy data frame.
    """

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

    df_with_clusters = add_purchase_clusters_info(
        df_cleaned, clusters, N_PURCHASE_CLUSTERS
    )

    # Analysing customers
    # NOTE: here we do different from the original notebook:
    #  we don't split train-test here, we'll do it later
    basket_price = df_with_clusters
    transactions_per_user = build_transactions_per_user(
        basket_price, n_purchase_clusters=N_PURCHASE_CLUSTERS
    )
    matrix = convert_customers_df_to_np(transactions_per_user, N_PURCHASE_CLUSTERS)
    scaled_matrix, pca = analyse_customers_pca(matrix)
    clusters_clients = compute_customer_clusters(scaled_matrix, N_CUSTOMER_CLUSTERS)

    merged_df = add_customer_clusters_info(transactions_per_user, clusters_clients)

    # done
    return merged_df


def _fix_too_small_clusters(df):
    """Since train_test_split with stratify=Y requires each class to be of size
    at least 2, we duplicate rows for those clusters that have size 1.
    """
    offline_clusters = df

    def _get_size_one_clusters(offline_clusters):
        cluster_sizes = offline_clusters.groupby(by=["cluster"])["cluster"].count()
        cluster_sizes_df = pd.DataFrame(
            {"cluster": cluster_sizes.index, "cluster_size": cluster_sizes.values}
        )
        logging.info(f"Cluster sizes: {cluster_sizes_df}")

        zero_size = cluster_sizes_df[cluster_sizes_df.cluster_size == 0]["cluster"]
        assert (
            len(zero_size) == 0
        ), zero_size  # PCA can't produce a cluster of size 0, right?

        one_size = cluster_sizes_df[cluster_sizes_df.cluster_size == 1]["cluster"]
        return list(one_size)

    size_one_df = _get_size_one_clusters(offline_clusters)
    if size_one_df:
        logging.warning(
            f"Detected {len(size_one_df)} clusters with 1 element: {size_one_df}"
        )

    rows = offline_clusters[offline_clusters.cluster.isin(size_one_df)]
    result = pd.concat([offline_clusters, rows], ignore_index=True)
    return result


def clean_client_clusters(df):
    df = _fix_too_small_clusters(df)
    return df
